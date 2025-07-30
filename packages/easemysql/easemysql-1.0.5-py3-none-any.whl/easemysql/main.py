import re
import time
import pymysql
import warnings
from typing import Optional, List, Dict
from pymysql.converters import escape_string
from dbutils.pooled_db import PooledDB
from .utils import where_simple

warnings.filterwarnings('ignore', category=pymysql.Warning)

"""
pip install pymysql --upgrade
pip install DBUtils --upgrade

注意1：
select * from test where nickname like "%风行水上%" 
不能直接执行这样的SQL，会提示：not enough arguments for format string
需要使用：cursor.execute('select * from test where nickname like %s', ["%风行水上%"])
原因是：
    pymysql 将字符串中的 % 视为需要格式化的占位符
    占位符：在 pymysql 中，参数化查询的占位符使用 %s，不论数据类型都统一写作 %s
    传入的参数以列表或字典形式提供给 cursor.execute() 方法
"""


def singleton(cls):
    instances = {}

    def get_instance(*args, **kwargs):
        key = "{}@{}".format(kwargs['host'], kwargs['database'])
        if key not in instances:
            instances[key] = cls(*args, **kwargs)
        return instances[key]

    return get_instance


@singleton
class SQLSession:
    # SQLSession(host='', user='', password='', database='')
    def __init__(self, **kwargs):
        conf = kwargs
        t1 = time.time()
        self.pool = PooledDB(
            creator=pymysql,
            maxconnections=conf.get('maxconnections', 10),  # 允许的最大连接数，超过时新请求将会等待连接被释放
            mincached=conf.get('mincached', 1),  # 启动时的初始连接数
            maxcached=conf.get('maxcached', 10),  # 最大空闲连接数量，超出的连接将会被关闭
            blocking=conf.get('blocking', True),  # 当连接数达到 maxconnections 并且没有空闲连接可用时，是否等待连接被释放。否则将抛出异常
            cursorclass=pymysql.cursors.DictCursor,  # 设置查询结果为字典
            # conv={
            #     pymysql.converters.FIELD_TYPE.DATETIME: str
            # },
            use_unicode=True,
            host=conf['host'],
            user=conf['user'],
            password=conf['password'],
            database=conf['database']
        )
        self.log = ['{} 初始化连接，用时：{}'.format(time.time(), time.time() - t1)]
        self.execute_cnt = 0

    def __connection(self):
        # 如果你不调用 conn.close()，连接会保持开放状态，直到 PooledDB 的连接池自行处理（即回收或重用）这些连接。
        # 由于你使用了连接池，不调用 conn.close() 也不会导致资源泄漏，连接池会管理连接的生命周期。
        return self.pool.connection()

    def __cursor_execute(self, conn, cursor, sql, args):
        self.execute_cnt += 1
        try:
            cursor.execute(sql, args)
        except Exception as e:
            conn.rollback()
            # print(e)
            # print(sql)
            # print(args)
            # exit()
            raise Exception('{e} \n SLQ:{sql}; \n args:{args}'.format(e=e, sql=sql, args=args))

    def execute(self, sql, args=None):
        conn = self.__connection()
        with conn.cursor() as cursor:
            self.__cursor_execute(conn, cursor, sql, args)
            cnt = cursor.rowcount
            _id = cursor.lastrowid
        conn.commit()
        return _id, cnt

    def fetchone(self, sql, args=None):
        conn = self.__connection()
        with conn.cursor() as cursor:
            self.__cursor_execute(conn, cursor, sql, args)
            result = cursor.fetchone()
        return result

    def fetchall(self, sql, args=None):
        conn = self.__connection()
        with conn.cursor() as cursor:
            self.__cursor_execute(conn, cursor, sql, args)
            result = cursor.fetchall()
        return result


class SQLStatement:
    _mode_map = {
        'insert': "INSERT INTO",
        'ignore': "INSERT IGNORE INTO",
        # 注意 REPLACE 会把没有传入的字段值置成默认置
        'replace': "REPLACE INTO",
    }

    @classmethod
    def insert(cls, table_name: str, data: dict, mode='insert'):
        fields = []
        values = []
        for k, v in data.items():
            fields.append(f"`{k}`")
            if v is None:
                values.append("NULL")
            else:
                v = escape_string(str(v)).replace("%", "%%")
                values.append(f"'{v}'")
        fields_str = ', '.join(fields)
        values_str = ', '.join(values)

        sql = [cls._mode_map[mode], f"`{table_name}`", f"({fields_str})", 'VALUES', f"({values_str})"]
        return ' '.join(sql)

    @classmethod
    def insert_all(cls, table_name: str, data: List[Dict], mode='replace'):
        fields_arr = data[0].keys()
        values_arr = []
        for row in data:
            values = []
            for key in fields_arr:
                v = row[key]
                if v is None:
                    values.append('NULL')
                else:
                    values.append("'{}'".format(escape_string(str(v)).replace("%", "%%")))
            values_arr.append(f"({','.join(values)})")
        fields_str = ','.join([f'`{key}`' for key in fields_arr])
        values_str = ','.join(values_arr)

        sql = [cls._mode_map[mode], f"`{table_name}`", f"({fields_str})", 'VALUES', values_str]
        return ' '.join(sql)

    @classmethod
    def update(cls, table_name, data, condition):
        set_clause = []
        for k, v in data.items():
            if v is None:
                set_clause.append(f"`{k}` = NULL")
            else:
                v = escape_string(str(v)).replace("%", "%%")
                set_clause.append(f"`{k}` = '{v}'")
        set_clause_str = ','.join(set_clause)
        sql = ['UPDATE', f"`{table_name}`", 'SET', set_clause_str, 'WHERE', condition.replace('?', ' %s ')]
        return ' '.join(sql)

    @classmethod
    def delete(cls, table_name, condition):
        sql = ['DELETE FROM', f"`{table_name}`", 'WHERE', condition.replace('?', ' %s ')]
        return ' '.join(sql)

    @classmethod
    def select(cls, table_name, condition, field='*'):
        if type(table_name) is str:
            table_name = [table_name, []]
        main_table, join_arr = table_name

        table = cls._fmt_table(main_table)
        for item in join_arr:
            # table2,on,join = ['tabel2','','LEFT JOIN']
            if len(item) == 3:
                table2, on, join = item
            else:
                table2, on = item
                join = 'LEFT JOIN'
            table = f"{table} {join.upper()} {cls._fmt_table(table2)} ON {on}"

        # 书写顺序：SELECT -> FROM -> JOIN -> ON -> WHERE -> GROUP BY -> HAVING -> UNION -> ORDER BY -> LIMIT -> FOR UPDATE
        sql = ['SELECT', field, 'FROM', table, 'WHERE', condition.replace('?', ' %s '), ]
        return ' '.join(sql)

    @classmethod
    def _fmt_table(cls,table_str:str):
        # 去除首尾空格并规范化内部空格
        table_str = re.sub(r'\s+', ' ', table_str.strip())

        parts = table_str.split()
        if len(parts) == 2:
            # 格式: table alias
            return f"`{parts[0]}` {parts[1]}"
        elif len(parts) == 3 and parts[1].upper() == 'AS':
            # 格式: table as alias
            return f"`{parts[0]}` AS {parts[2]}"
        else:
            return table_str



class EaseMySQL:
    def __init__(self, db: Optional[SQLSession] = None, **kwargs):
        if db is None:
            self.db = SQLSession(**kwargs)

    def one(self, table_name, condition, params=(), field='*', order=None, group=None):
        condition = where_simple(condition)
        if group:
            condition += f' GROUP BY {group}'
        if order:
            condition += f' ORDER BY {order}'
        statement = SQLStatement.select(table_name, condition, field)
        return self.db.fetchone(statement, params)

    def all(self, table_name, condition, params=(), field='*', group=None, order=None, limit=None):
        condition = where_simple(condition)
        if group:
            condition += f' GROUP BY {group}'
        if order:
            condition += f' ORDER BY {order}'
        if limit:
            condition += f' LIMIT {limit}'
        statement = SQLStatement.select(table_name, condition, field)
        return self.db.fetchall(statement, params)

    def delete(self, table_name, condition, params=()):
        sql = SQLStatement.delete(table_name, where_simple(condition))
        _id, cnt = self.db.execute(sql, params)
        return cnt

    def update(self, table_name, data, condition, params=()):
        sql = SQLStatement.update(table_name, data, where_simple(condition))
        _id, cnt = self.db.execute(sql, params)
        return cnt

    def insert(self, table_name, data, params=(), mode=None):
        if not data:
            return
        if isinstance(data, dict):
            sql = SQLStatement.insert(table_name, data, mode if mode else 'insert')
            _id, cnt = self.db.execute(sql, params)
            return _id
        if isinstance(data, list):
            sql = SQLStatement.insert_all(table_name, data, mode if mode else 'replace')
            _id, cnt = self.db.execute(sql, params)
            return cnt

    def raw(self, sql, params=()):
        _id, cnt = self.db.execute(sql, params)
        return _id, cnt

    def raw_one(self, sql, params=()):
        return self.db.fetchone(sql, params)

    def raw_all(self, sql, params=()):
        return self.db.fetchall(sql, params)


if __name__ == '__main__':
    # ValueError: unsupported format character 'A' (0x41) at index 3366
    print(SQLStatement.insert('test', dict(c1=1)))
    print(SQLStatement.insert_all('test', [dict(c1=1, c2=2), dict(c1=1, c2=2)], mode='insert'))
    print(SQLStatement.delete('test', 'id = 1'))
    print(SQLStatement.update('test', dict(c1=55, c2=66), 'id > 0'))
    print(SQLStatement.select('test', 'id > 0'))

    join_tables = [
        ["stat_book_info_show_pv_uv a", "m.zs_id = a.zs_id and a.app_id = 'com.sleepsounds.dztmmd'"],
        ["stat_book_read_progress b", "m.zs_id = b.zs_id", 'left join'],
    ]
    print(SQLStatement.select(['book m', join_tables], 'id > 0'))
