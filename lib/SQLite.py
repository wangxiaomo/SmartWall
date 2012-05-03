#-*- coding: utf-8 -*-

DB_FILE = ".messages"

from pysqlite2 import dbapi2 as sqlite

class SQLite():

    def __init__(self, filename=DB_FILE):
        self.conn = sqlite.connect(filename)
        self.cursor = self.conn.cursor()

    def __del__(self):
        try:
            self.cursor.close()
            self.conn.close()
        except:
            raise

    def do_sql(self, sql):
        try:
            self.conn.execute(sql)
            self.conn.commit()
        except:
            raise Exception("sql: %s" % sql)

    def fetch_sql(self, sql):
        try:
            self.cursor.execute(sql)
        except:
            raise Exception("sql: %s" % sql)
        return self.cursor.fetchall()

