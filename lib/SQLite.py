#-*- coding: utf-8 -*-

from pysqlite2 import dbapi2 as sqlite

class SQLite():

    def __init__(self, filename):
        try:
            self.conn = sqlite.connect(filename)
            self.cursor = self.conn.cursor()
        except:
            raise Exception("Connect To The SQLite Failed!")

    def __del__(self):
        try:
            self.cursor.close()
            self.conn.close()
        except:
            raise Exception("Close The SQLite Failed!")

    def do_sql(self, sql):
        try:
            self.conn.execute(sql)
            self.conn.commit()
        except:
            raise Exception("do sql: %s" % sql)

    def fetch_sql(self, sql):
        try:
            self.cursor.execute(sql)
        except:
            raise Exception("fetch sql: %s" % sql)
        return self.cursor.fetchall()

