#-*- coding: utf-8 -*-

import re,time,datetime
import config
from lib.SQLite import SQLite

def log(mesg):
    print mesg

def sql_escape(string):
    return string.replace('\\', '\\\\').replace('\'', '\'\'')

def set_app_value(cfg_name, cfg_value):
    """set cfg_name's value."""
    sql = "UPDATE sw_app SET cfg_value='%s' WHERE cfg_name='%s'" % (cfg_value, cfg_name)
    db = SQLite(config.DB_FILE)
    db.do_sql(sql)

def get_app_value(cfg_name):
    """get cfg_name's value."""
    sql = "SELECT cfg_value FROM sw_app WHERE cfg_name='%s'" % cfg_name
    db = SQLite(config.DB_FILE)
    rows = db.fetch_sql(sql)
    return rows[0][0]

def is_user_exists(screen_name):
    sql = "SELECT * FROM sw_users WHERE screen_name='%s'" % screen_name
    db = SQLite(config.DB_FILE)
    rows = db.fetch_sql(sql)
    if rows:
        return True
    else:
        return False

def add_user(user):
    try:
        if not is_user_exists(user["name"]):
            sql = "INSERT INTO sw_users(user_id, screen_name, sex, school) VALUES('%s', '%s', '%s', '%s')" \
                % (user["id"],user["name"],user["sex"],user["school"])
            db = SQLite(config.DB_FILE)
            db.do_sql(sql)
            log("add user %s!" % user["name"])
            return True
    except:
        return False

def get_status(last_post_time):
    sql = "SELECT sex,school,message FROM sw_messages,sw_users WHERE src!='%s' AND src=screen_name AND pub_time>'%s' ORDER BY pub_time" % ('我'.decode('utf-8'),last_post_time)
    db = SQLite(config.DB_FILE)
    rows = db.fetch_sql(sql)
    # write the time back
    now = datetime.datetime.strftime(datetime.datetime.now(),"%Y-%m-%d %H:%M:%S") 
    sql = "UPDATE sw_app SET cfg_value='%s' WHERE cfg_name='post_time'" % now
    db.do_sql(sql)
    return rows
    

def is_message_exists(message):
    sql = "SELECT * FROM sw_messages WHERE src='%s' AND dst='%s' AND message='%s' AND pub_time='%s'" % \
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
        sql = "INSERT INTO sw_messages(src,dst,message,pub_time) VALUES('%s', '%s', '%s', '%s')" % \
            (message["src"], message["dst"], message["message"], message["time"])
        log(sql)
        db.do_sql(sql)

    log("%d messages existed!" % count)

def drop_table(table_name='sw_messages'):
    sql = "DELETE FROM %s" % table_name
    db = SQLite(config.DB_FILE)
    db.do_sql(sql)

def datetime_formater(date_string):
    log("Soving Date String: %s" % date_string)
    """ datetime formater """
    if re.search(r'\d{4}(-\d{2}){2} \d{2}:\d{2}:\d{2}',date_string):
        return date_string
    elif re.search(r'分钟前', date_string):
        mins_ago = re.findall(r'(\d{1,})分钟前', date_string)[0]
        d = datetime.datetime.now()-datetime.timedelta(minutes=int(mins_ago))
        return datetime.datetime.strftime(d, "%Y-%m-%d %H:%M:%S")
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
            
        

def str2date(string):
    return datetime.datetime.strptime(string, "%Y-%m-%d %H:%M:%S")

if __name__ == '__main__':
    drop_table()
