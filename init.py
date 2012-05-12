#-*- coding: utf-8 -*-

"""
init the app
"""

from os import system
import config
from Spider import Spider
from Poster import Poster

db_file = config.DB_FILE
system("rm %s" % db_file)
system("sqlite3 %s<db_file.sql" % db_file)

spider = Spider()
poster = Poster()
