#-*- coding: utf-8 -*-

import re,time,datetime
import config
from lib.SQLite import SQLite

def log(mesg):
    print mesg

def sql_escape(string):
    return string.replace('\\', '\\\\').replace('\'', '\'\'')

def str2date(string):
    return datetime.datetime.strptime(string, "%Y-%m-%d %H:%M:%S")

def is_message_exists(message):
    sql = "SELECT * FROM sw_messages WHERE src='%s' AND dst='%s' AND message='%s' AND time='%s'" % \
        (message["src"], message["dst"], message["message"], message["time"])
    db = SQLite(config.DB_FILE)
    rows = db.fetch_sql(sql)
    if rows:
        return True
    else:
        return False

def save_2_sqlite(messages):
    db = SQLite(config.DB_FILE)
    count = 0
    for message in messages:
        if is_message_exists(message):
            count += 1
            continue
        sql = "INSERT INTO sw_messages(src,dst,message,time) VALUES('%s', '%s', '%s', '%s')" % \
            (message["src"], message["dst"], message["message"], message["time"])
        db.do_sql(sql)

    log("%d messages existed!" % count)

def drop_table(table_name='sw_messages'):
    sql = "DELETE FROM %s" % table_name
    db = SQLite(config.DB_FILE)
    db.do_sql(sql)


def datetime_formater(date_string):
    """ datetime formater """
    if re.match(r'\d{4}(-\d{2}){2} \d{2}:\d{2}:\d{2}',date_string):
        return date_string
    else:
        if re.match(r'今天', date_string):
            date_str = time.strftime("%Y-%m-%d", time.localtime())
        else:
            year = time.strftime("%Y", time.localtime())
            month = re.findall(r'(\d{2})月', date_string)[0]
            day = re.findall(r'(\d{2})日', date_string)[0]
            date_str = "%s-%s-%s" % (year, month, day)
        time_str = re.findall(r'(\d{2}:\d{2})', date_string)[0]
        return "%s %s:00" % (date_str, time_str)

if __name__ == '__main__':
    drop_table()
