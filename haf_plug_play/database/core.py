import os
import psycopg2

from haf_plug_play.config import Config

config = Config.config

class DbSession:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=config['db_host'],
            database=config['db_name'],
            user=config['db_username'],
            password=config['db_password'],
            connect_timeout=3,
            keepalives=1,
            keepalives_idle=5,
            keepalives_interval=2,
            keepalives_count=2
        )
        self.conn.autocommit = False

    def select(self, sql):
        cur = self.conn.cursor()
        try:
            cur.execute(sql)
            res = cur.fetchall()
            cur.close()
        except Exception as e:
            print(e)
            print(f"SQL:  {sql}")
            self.conn.rollback()
            cur.close()
            raise Exception ('DB error occurred')
        if len(res) == 0:
            return None
        else:
            return res

    def execute(self, sql,  data=None):
        cur = self.conn.cursor()
        try:
            if data:
                cur.execute(sql, data)
            else:
                cur.execute(sql)
            cur.close()
        except Exception as e:
            print(e)
            print(f"SQL:  {sql}")
            print(f"DATA:   {data}")
            self.conn.rollback()
            cur.close()
            raise Exception ('DB error occurred')

    def commit(self):
        self.conn.commit()


class DbSetup:

    @classmethod
    def check_db(cls):
        try:
            cls.conn = psycopg2.connect(
            host=config['db_host'],
            database=config['db_name'],
            user=config['db_username'],
            password=config['db_password'],
            connect_timeout=3,
            keepalives=1,
            keepalives_idle=5,
            keepalives_interval=2,
            keepalives_count=2
        )
        except psycopg2.OperationalError as e:
            if config['db_name'] in e.args[0] and "does not exist" in e.args[0]:
                print(f"No database found. Please create a '{config['db_name']}' database in PostgreSQL.")
                os._exit(1)
            else:
                print(e)
                os._exit(1)