#-*- coding: utf-8 -*-

import re
from lib.SQLite import SQLite

def log(mesg):
    print mesg

def sql_escape(string):
    return string.replace('\\', '\\\\').replace('\'', '\'\'')

def is_message_exists(message):
    sql = "SELECT * FROM sw_messages WHERE src='%s' AND dst='%s' AND message='%s' AND time='%s'" % \
        (message["src"], message["dst"], message["message"], message["time"])
    db = SQLite()
    rows = db.fetch_sql(sql)
    if rows:
        return True
    else:
        return False

def save_2_sqlite(messages):
    db = SQLite()
    count = 0
    for message in messages:
        if is_message_exists(message):
            count += 1
            continue
        sql = "INSERT INTO sw_messages(src,dst,message,time) VALUES('%s', '%s', '%s', '%s')" % \
            (message["src"], message["dst"], message["message"], message["time"])
        db.do_sql(sql)

    log("%d messages existed!" % count)
