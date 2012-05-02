#-*- coding: utf-8 -*-

import cookielib
import mechanize

def sqlite2cookie(filename):
    from cStringIO import StringIO
    from pysqlite2 import dbapi2 as sqlite
    con = sqlite.connect(filename)
    cur = con.cursor()
    sql = "SELECT host,path,isSecure,expiry,name,value from moz_cookies"
    cur.execute(sql)

    ftstr = ['FALSE', 'TRUE']
    s = StringIO()
    s.write("""\
# Netscape HTTP Cookie File
# http://www.netscape.com/newsref/std/cookie_spec.html
# This is a generated file!  Do not edit.
""" )
    for item in cur.fetchall():
        s.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (
            item[0], ftstr[item[0].startswith('.')], item[1],
            ftstr[item[2]], item[3], item[4], item[5]))
    s.seek(0)
    cookie_jar = cookielib.MozillaCookieJar()
    cookie_jar._really_load(s,'',True,True)
    return cookie_jar

COOKIE_DB = "/home/xiaomo/.mozilla/firefox/15c1lj03.default/cookies.sqlite"

class Spider:
    def __init__(self):
        self.br = mechanize.Browser()
        self.br.set_handle_equiv(False)
        self.br.set_handle_robots(False)

    def debug(self, flag):
        self.br.set_debug_http(flag)
        self.br.set_debug_redirects(flag)
        self.br.set_debug_responses(flag)

    def set_cookie_jar(self, cookiejar):
        self.br.set_cookie_jar(cookiejar)

    def set_cookie(self, filename):
        cookiejar = sqlite2cookie(filename)
        self.set_cookie_jar(cookiejar)

if __name__ == '__main__':
    s = Spider()
    cj = sqlite2cookie(COOKIE_DB)
    s.set_cookie_jar(cj)
