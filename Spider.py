#-*- coding: utf-8 -*-

BASE_URL = "http://weibo.cn"
LOGIN_URL = "http://3g.sina.com.cn/prog/wapsite/sso/login.php?backURL=http%3A%2F%2Fweibo.cn%2F%3Fgotoreg%3D1%26from%3Dindex%26s2w%3Dindex%26pos%3D103&backTitle=%D0%C2%C0%CB%CE%A2%B2%A9&vt=4&revalid=2&ns=1"

import re,HTMLParser
import cookielib
import urllib,urllib2
import Helper

def log(msg):
    print msg

def show_data(table):
    for k in table.keys():
        print k, table[k]

class Spider():
    def __init__(self):
        self.cj = cookielib.LWPCookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
        urllib2.install_opener(self.opener)
        log("build opener success!")
        try:
            with open(".gsid") as f:
                self.gsid = f.read().rstrip()
        except:
            log("Haven't Been Authorizationed!")
            self.try_login(config.USERNAME, config.PASSWORD)

    def _request(self, url, bodies={}, headers={}):
        log("request %s!" % url)
        #request = urllib2.Request(url, urllib.urlencode(bodies))
        #return self.opener.open(request)
        return self._request_over_robots(url, bodies, headers)

    def _request_over_robots(self, url, bodies={}, headers={}):
        try:
            request = urllib2.Request(url, urllib.urlencode(bodies))
            request.add_header('User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:12.0) Gecko/20100101 Firefox/12.0')
        except:
            pass
        return self.opener.open(request)

    def try_login(self, username, password):
        if self.gsid:
            print "Already Authorizationed!Will overwrite it!"
        login_page = self._request(LOGIN_URL).read()
        try:
            if re.search(r'form action', login_page):
                submit_url = BASE_URL+"/"+re.findall(r'form action="(.*?)"', login_page)[0]
            else:
                submit_url = BASE_URL+"/"+re.findall(r'go href="(.*?)"', login_page)[0]
        except:
            raise Exception("can not get the submit url.")
        post_data = {}
        vk = re.findall(r'name="vk" value="(.*?)"', login_page)[0]
        post_data["vk"] = vk
        post_data["remember"] = "on"
        post_data["backURL"] = "http://3g.sina.com.cn/"
        post_data["backTitle"] = "手机新浪网"
        post_data["submit"] = 1
        vk_num = re.split(r'_', vk)[0]
        post_data["mobile"] = username
        post_data["password_%s" % vk_num] = password
        log("build auth header success!")       
        show_data(post_data)
        auth_page = self._request(submit_url, post_data).read()
        print auth_page
        try:
            #redirect_url = re.findall(r'go href="(.*?)"', auth_page)[0]
            #wap 方式传送回来的结果受明文/密文传送的影响，返回<a>或<go>。所以直接提取gsid来判断登陆是否成功
            gsid = re.findall(r'gsid=(.*?)&amp;', auth_page)[0]
        except:
            raise Exception("login failed!")
        #message_url = "http://weibo.cn/msg/?tf=5_010&vt=4&gsid=%s" % gsid
        #message_page = self._request_over_robots(message_url).read()
        #print message_page
        self.user = username
        return self.save_gsid(gsid)

    def save_gsid(self, gsid):
        self.gsid = gsid
        with open(".gsid", "w") as f:
            f.write(gsid)
        return gsid

    def run(self):
        message_url = "http://weibo.cn/msg/chat/list?tf=5_010&vt=4&gsid=%s" % self.gsid
        message_page = self._request(message_url).read()
        #TODO:
        try:
            total_page_count = int(re.findall(r'<input type="submit" value="跳页" />(?:.*?)/((?:\d)+)(?:.*?)</div>', message_page)[0])
        except:
            raise Exception("got an error!")
        log("TOTAL_PAGE_COUNT: %s" % total_page_count)
        page_index = 1
        conversations = self.get_conversations(message_page)

        while page_index<total_page_count:
            page_index += 1
            conversations.extend(self.fetch_conversations(page_index))
        log("Total %d Conversations!" % len(conversations))

        messages = []
        for conversation in conversations:
            peoples = [conversation["p1"],conversation["p2"]]
            detail = conversation["detail"]
            message_page = self._request(BASE_URL+detail).read()
            messages.extend(self.get_messages(message_page, peoples))
        log("Messages Total %d Counts!" % len(messages))
        Helper.save_2_sqlite(messages)

    def fetch_conversations(self, page_index=1):
        message_url = "http://weibo.cn/msg/chat/list?tf=5_010&vt=4&gsid=%s&page=%d" % (self.gsid, page_index)
        message_page = self._request(message_url).read()
        return self.get_conversations(message_page)

    def get_conversations(self, html):
        conversations = re.findall("<div class=\"c\">(.*?)</div>(?=<div class=\"(?:[cs])\"\>)", html)
        conversations = conversations[1:-2]
        parser = HTMLParser.HTMLParser()
        ret = []
        for conversation in conversations:
            item = {}
            people = re.findall(r'<span class="cmt">(.*?)</span>', conversation)[0]
            people = re.sub(r'<(?:.*?)>(.*?)</(?:.*?)>', lambda m: m.group(1), people) # 去除html成对标记
            people = re.sub(r'<(?:.*?)/>', '', people) # 去除html单向标记
            people = re.split(r'&nbsp;', people)
            latest = re.findall(r'(?:</span>)(.*?)(?=<span)', conversation)[0]
            time = re.findall(r'<span class="ct">(.*?)</span>', conversation)[0]
            detail = re.findall(r'<a href="(.*?)" class="cc">(?:.*?)</a>', conversation)[1]
            detail = parser.unescape(detail)
            count = re.findall(r'共(\d+)条对话', conversation)[0]
            item.update(dict(p1=people[0],p2=people[2],latest=latest,time=time,detail=detail,count=count))
            ret.append(item)

        return ret

    def get_messages(self, html, peoples):
        conversations = re.findall("<div class=\"c\">(.*?)</div>(?=<div class=\"(?:[cs])\"\>)", html)
        conversations = conversations[2:-1]
        ret = []
        for conversation in conversations:
            msg = {}
            people = re.findall(r'<span class="cmt">(.*?)</span>', conversation)[0]
            people = re.sub(r'<(?:.*?)>(.*?)</(?:.*?)>', lambda m: m.group(1), people)
            people = re.sub(r'<(?:.*?)/>', '', people)
            people = re.sub(r'[:]', '', people)
            message = re.findall(r'(?:</span>)(.*?)(?=<span)', conversation)[0]
            time = re.findall(r'<span class="ct">(.*?)</span>', conversation)[0]

            if people == peoples[0]:
                msg["dst"] = peoples[1]
            else:
                msg["dst"] = peoples[0]
            msg["src"] = people
            msg["message"] = Helper.sql_escape(message)
            msg["time"] = time
            ret.append(msg)
        return ret

if __name__ == '__main__':
    s = Spider()
    s.run()
