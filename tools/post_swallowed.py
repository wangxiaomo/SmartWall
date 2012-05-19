#-*- coding: utf-8 -*-

import sys
sys.path.insert(0, "..")
sys.path.insert(1, "weibo_backup")

import HTMLParser
import Helper
import config
from lib.SQLite import SQLite
from weibo_backup.run import WeiboBackup 

parser = HTMLParser.HTMLParser()

sql = "SELECT message FROM sw_messages"
db = SQLite("../"+config.DB_FILE)
rows = db.fetch_sql(sql)
total_status = [parser.unescape(r[0]) for r in rows]
Helper.log("Total %d Status in DataBase!" % len(total_status))

fetcher = WeiboBackup()
post_status = [w.decode("utf-8") for w in fetcher.backup('大学秘密')]
Helper.log("Total %d Status Posted!" % len(post_status))

diff = [w for w in total_status if w not in post_status]
Helper.log("%d Status Swallowed!" % len(diff))

from Poster import Poster
poster = Poster()
for w in diff:
    poster.post_status(w)
