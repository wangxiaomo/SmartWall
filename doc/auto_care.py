# -*- coding: utf-8 -*-

import urllib, urllib2, cookielib, hashlib,threading
import re, os, time, random

import sys
reload(sys)
sys.setdefaultencoding('utf8')

def log(s):
        s = "\n" + str(s)
        f = open('log.txt', 'a+')
        f.write(s)
        f.close()
        sys.stdout.write(s)
        sys.stdout.flush()


class WeiboCn:
        all = ('关注你啦~~~~','果断关注~','不知道你有没有发现你的粉丝多了一个?,哈哈！')
        url = 'http://www.weibo.com'
        header = {
                'User-Agent' : 'Mozilla/5.0 (Windows NT 5.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
        }
        def __init__(self, username, password, keyword = None, *args):
                self.user = username
                self.keyword = keyword
                self.all = args or self.all
                self.cj = cookielib.LWPCookieJar()
                self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
                urllib2.install_opener(self.opener)
                self.tryLogin(username, password)

        def tryLogin(self, username, password):
                bodies = dict(_=int(time.time()),callback='sinaSSOController.preloginCallBack',client='ssologin.js(v1.3.12)',entry='miniblog',user='jiangjia@1616.net')
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
                        self.afterLogin()
        
        def afterLogin(self):
                content = self._request('http://weibo.com')[1].read()
                self.uid = re.findall('\$uid.*?"(\d+)"', content)[0]

        def care(self):
                url = 'http://weibo.com/pub/news?source=toptray'
                if self.keyword:
                        url = 'http://weibo.com/k/%s?Refer=Index_header' % urllib.quote(urllib.quote(self.keyword))
                log(url)
                content = self._request(url)[1].read()
                match = re.findall('loadCommentByRid\((.*?)\)', content)
                for x in match:
                        ownerUid,productId,productName,resourceId,resTitle,resInfo,some,listInDiv,forward,some2 = eval("(%s)" % x)
                        bodies = dict(uid=ownerUid,fromuid=self.uid,refer_sort='profile',atnId='profile')
                        result = self._request('http://weibo.com/attention/aj_addfollow.php?refer_sort=profile&atnId=profile&rnd=%f' % random.random(), bodies, dict(Referer = 'http://weibo.com/'))[1].read()
                        if 'A00006' in result:
                                log("<%s>关注<%d>成功！" % (self.user,ownerUid))
                                content = self.all[random.randint(0, len(self.all)-1)]
                                bodies = dict(content=content,uid=self.uid,ownerUid=ownerUid,productId=productId,productName=productName,resourceId=resourceId,resTitle=resTitle,resInfo=resInfo,some=some,listInDiv=listInDiv,forward=forward,some2=some2)
                                result = self._request('http://weibo.com/comment/addcomment.php?f=1&rnd=%f' % random.random(), bodies, dict(Referer='http://weibo.com/pub/news?source=toptray'))[1].read()
                                if 'A00006' in result:
                                        log("<%s>评论<%d>成功！<%s>" % (self.user,ownerUid, content))
                                else:
                                        log("<%s>评论<%d>失败！" % (self.user,ownerUid))
                                time.sleep(random.randint(30, 4 * 60))
                        else:
                                log("<%s>关注<%d>失败！" % (self.user,ownerUid))
                                raise Exception,"关注<%d>失败！" % ownerUid
        
        def unCare(self):
                content = self._request('http://weibo.com/%s/follow' % str(self.uid))[1].read()
                pages = re.findall('<em>(\d+)<\/em>', content)
                log(pages)
                if len(pages) == 0:
                        return
                p = apply(max,[int(i) for i in pages])
                for i in range(p,0,-1):
                        log(i)
                        content = self._request('http://weibo.com/attention/att_list.php?action=0&tag=&page=%d' % i)[1].read()
                        cancel = re.findall('粉丝<strong>(.*?)</strong>.*?followcancel\(\'(\d+)', content, re.S)
                        headers = {'Content-Type':'application/x-www-form-urlencoded', 'Origin':'http://weibo.com','Referer':'http://weibo.com/attention/att_list.php?action=0&tag=&page=%d' % i}
                        url = 'http://weibo.com/attention/aj_delfollow.php?rnd=%f' % random.random()
                        for fans,id in cancel:
                                if int(fans) > 2000: 
                                        log("取消关注%s失败，原因：粉丝数%s大于2000" % (id, fans))
                                        continue
                                result = self._request(url, dict(touid=id,fromuid=self.uid),headers)[1].read()
                                if 'A00006' in result:
                                        log("取消关注%s成功！" % id)
                                else:
                                        log("取消关注%s失败！" % id)
                        time.sleep(10)
                
        def _request(self, url, bodies = {}, headers = {}):
                request = urllib2.Request(url, urllib.urlencode(bodies), headers = headers)
                return (request, self.opener.open(request))

        def _readMainPage(self):
                return self._request(self.url)[1].read()

class timer(threading.Thread):

        def __init__(self, weibo):
                threading.Thread.__init__(self)
                self.weibo = weibo 

        def run(self):
                #log (">>>>>>当前用户<%s>线程<%s>" % (self.weibo.user,self.getName()))
                #t = int(time.strftime('%H'))
                #looptime = 6 * 6 if t < 22 and t > 8 else 60 * 60 * 5
                '''
                try:
                        self.weibo.care()
                        log ("当前用户<%s>线程<%s>关注完一页, 休息%d小时，稍后继续~~" % (self.weibo.user,self.getName(), looptime/3600))
                except Exception, e:
                        log(str(e))
                        log ("当前用户<%s>线程<%s>出现异常，可能是关注超过上限, 休息%d小时，稍后继续尝试~~" % (self.weibo.user,self.getName(), looptime/3600))
                '''
                self.weibo.unCare()
                #time.sleep(looptime)
                #self.run()

def run(userinc):
        f = open(userinc).readlines()
        if len(f) < 1 : log("配置文件为空！")
        m = re.compile('\|')
        userlist = []
        for line in f:
                if line.startswith('#'):continue
                line = m.split(line.strip())
                userlist.append(line)
        allWeibo = [apply(WeiboCn,u) for u in userlist]
        pound = []
        for w in allWeibo:
                w = timer(w)
                w.setDaemon(True)
                w.start()
                pound.append(w)
        #time.sleep(10)
        for x in pound:
                x.join()
                

if __name__ == '__main__':
        run(os.path.join(os.path.dirname(__file__), 'user.txt'))
        '''
        while True:
                m.runtimes += 1 
                m.run()
        '''
