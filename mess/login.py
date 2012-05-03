# -*- coding: utf-8 -*-

import urllib, urllib2, cookielib, hashlib
import re, time

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
    url = 'http://www.weibo.com'
    header = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 5.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
    }
    def __init__(self, username, password, keyword = None, *args):
        self.user = username
        self.keyword = keyword
        self.cj = cookielib.LWPCookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
        urllib2.install_opener(self.opener)
        self.tryLogin(username, password)


    def tryLogin(self, username, password):
        bodies = dict(_=int(time.time()),callback='sinaSSOController.preloginCallBack',client='ssologin.js(v1.3.12)',entry='miniblog',user=username)
        print "预登录，获取servertime & nonce参数(用来加密生成密码)"
        preloadurl = 'http://login.sina.com.cn/sso/prelogin.php?' + urllib.urlencode(bodies)
        content = self._request(preloadurl)[1].read()
        bodies = eval(re.findall('\{.*?\}',content)[0])
        password = hashlib.sha1(hashlib.sha1(hashlib.sha1(password).hexdigest()).hexdigest() + str(bodies['servertime']) + bodies['nonce']).hexdigest()
        print "加密获得密码<%s>" % password
        bodies.update(dict(client='ssologin.js(v1.3.12)',encoding='utf-8',entry='miniblog',gateway='1',password=password,pwencode='wsse',returntype='META',savestate='7',service='miniblog',ssosimplelogin='1',url='http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',username=username,useticket=1))
        response = self._request('http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.3.12)', bodies)[1]
        content = response.read()
        moreurl = re.findall('replace\([\'|"](.*?)[\'|"]\)', content)
        if len(moreurl) == 0: print "登录失败!"
        content = self._request(moreurl[0], dict(Referer='http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.3.12)',Host='weibo.com'))[1].read()
        if username in content:
            print "登录成功！"
        else:
            print "登陆失败！"
            return

        response = self._request("http://weibo.com/messages?topnav=1&wvr=3.6&ajaxpagelet=1&_t=1335969631369")[1]
        content = response.read()
        print content
        
    def _request(self, url, bodies = {}, headers = {}):
        request = urllib2.Request(url, urllib.urlencode(bodies), headers = headers)
        return (request, self.opener.open(request))

    def refresh_cookie(self):
        self.cj = sqlite2cookie(COOKIE_DB)
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
        urllibe2.install_opener(self.opener)

if __name__ == '__main__':
    s = Spider('497052184@qq.com', 'Wj2201367')
