#-*- coding: utf-8 -*-

BASE_URL = "http://weibo.cn"
LOGIN_BASE = "http://3g.sina.com.cn/prog/wapsite/sso"
LOGIN_URL = "http://3g.sina.com.cn/prog/wapsite/sso/login.php?backURL=http%3A%2F%2Fweibo.cn%2F%3Fgotoreg%3D1%26from%3Dindex%26s2w%3Dindex%26pos%3D103&backTitle=%D0%C2%C0%CB%CE%A2%B2%A9&vt=4&revalid=2&ns=1"

import re,HTMLParser
import urllib, urllib2
import config
import Helper
from Poster import Poster

log = Helper.log

class Spider():
    def __init__(self):
        self.last_time = self.get_last_message_time()
        log("get last time %s" % self.last_time)
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
            raise Exception("build request error!")
        return urllib2.urlopen(request)

    def try_login(self, username, password):
        login_page = self._request(LOGIN_URL).read()
        parser = HTMLParser.HTMLParser()
        try:
            if re.search(r'form action', login_page):
                submit_url = LOGIN_BASE + "/"+parser.unescape(re.findall(r'form action="(.*?)"', login_page)[0])
            else:
                submit_url = LOGIN_BASE+"/"+parser.unescape(re.findall(r'go href="(.*?)"', login_page)[0])
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

        auth_page = self._request(submit_url, post_data).read()
        try:
            #redirect_url = re.findall(r'go href="(.*?)"', auth_page)[0]
            #wap 方式传送回来的结果受明文/密文传送的影响，返回<a>或<go>。所以直接提取gsid来判断登陆是否成功
            gsid = re.findall(r'g=(.*?)&amp;', auth_page)[0]
        except:
            raise Exception("login failed!")
        #message_url = "http://weibo.cn/msg/?tf=5_010&vt=4&gsid=%s" % gsid
        #message_page = self._request_over_robots(message_url).read()
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
        try:
            total_page_count = int(re.findall(r'<input type="submit" value="跳页" />(?:.*?)/((?:\d)+)(?:.*?)</div>', message_page)[0])
        except:
            total_page_count = 1
        log("TOTAL_PAGE_COUNT: %s" % total_page_count)
        page_index = 1
        conversations,_ = self.get_conversations(message_page)
        if len(conversations) == 0:
            log("Already up to date")
            return
        self.latest_time = conversations[0]["time"]
        log("get latest time %s" % self.latest_time)

        while page_index<total_page_count:
            page_index += 1
            cnt_pages_conversations,status = self.fetch_conversations(page_index)
            conversations.extend(cnt_pages_conversations)
            if status:
                break
        log("Total %d Conversations!" % len(conversations))
        #TODO:base on the conversation here. we can add userinfo into the database
        poster = Poster()

        messages = []
        for conversation in conversations:
            user = conversation["p2"] if conversation["p1"] == '我' else conversation["p1"]
            user_info = poster.get_user_info(user)
            flag = Helper.add_user(user_info)
            if flag == False:
                continue
            peoples = [conversation["p1"],conversation["p2"]]
            detail = conversation["detail"]
            for i in range(int(conversation["count"])/10+1):
                message_page = self._request(BASE_URL+detail+"&page=%d" % (i+1)).read()
                cnt_pages_messages,status = self.get_messages(message_page, peoples)
                messages.extend(cnt_pages_messages)
                if status:
                    break
        self.set_last_message_time(self.latest_time)
        log("Final Message Count %d" % len(messages))
        Helper.save_2_sqlite(messages)

    def fetch_conversations(self, page_index=1):
        message_url = "http://weibo.cn/msg/chat/list?tf=5_010&vt=4&gsid=%s&page=%d" % (self.gsid, page_index)
        message_page = self._request(message_url).read()
        return self.get_conversations(message_page)

    def get_conversations(self, html):
        status = 0
        conversations = re.findall("<div class=\"c\">(.*?)</div>(?=<div class=\"(?:[cs])\"\>)", html)
        conversations = conversations[1:-2]
        parser = HTMLParser.HTMLParser()
        ret = []
        for conversation in conversations:
            item = {}
            tokens = re.findall(r'(.*?)<span class="ct">', conversation)[0]
            tokens = re.sub(r'<(?:.*?)>', '', tokens) # 去除html标记
            tokens = re.sub(r'\[(在线|忙碌|离开)\]', '', tokens) # 去除在线标记
            tokens = re.sub(r'\[\d+条新\]', '', tokens)
            tokens = re.split(r'&nbsp;', tokens)
            latest = tokens[3]
            latest = re.split(r':', latest, 1)[1]
            time = re.findall(r'<span class="ct">(.*?)</span>', conversation)[0]
            time = Helper.datetime_formater(time)
            cnt_datetime = Helper.str2date(time)
            if not cnt_datetime>self.last_time:
                status = 1
                return ret,status
            detail = re.findall(r'语音通话(?:.*?)<a href="(.*?)" class="cc">(?:.*?)</a>', conversation)[0]
            detail = parser.unescape(detail)+"&type=record"
            count = re.findall(r'共(\d+)条对话', conversation)[0]
            item.update(dict(p1=tokens[0],p2=tokens[2],latest=latest,time=time,detail=detail,count=count))
            ret.append(item)

        return ret,status

    def get_messages(self, html, peoples):
        status = 0
        conversations = re.findall("<div class=\"c\">(.*?)</div>", html)
        conversations = conversations[2:-3]
        ret = []
        for conversation in conversations:
            msg = {}
            tokens = re.findall(r'(.*?)<span', conversation)[0]
            tokens = re.sub(r'<(?:.*?)>', '', tokens) # 去除html标记
            tokens = re.sub(r'\[(在线|忙碌|离开)\]', '', tokens) # 去除在线标记
            tokens = re.sub(r'\[\d+条新\]', '', tokens)
            tokens = re.split(r':', tokens, 1)
            people = tokens[0]
            message = tokens[1]
            time = re.findall(r'<span class="ct">(.*?)</span>', conversation)[0]
            time = Helper.datetime_formater(time)
            cnt_datetime = Helper.str2date(time)
            if not cnt_datetime>self.last_time:
                status = 1
                return ret,status
            if people == peoples[0]:
                msg["dst"] = peoples[1]
            else:
                msg["dst"] = peoples[0]
            msg["src"] = people
            msg["message"] = Helper.sql_escape(message)
            msg["time"] = time
            ret.append(msg)
        return ret, status

    def get_last_message_time(self):
        return Helper.str2date(Helper.get_app_value('message_time'))

    def set_last_message_time(self, timestr):
        Helper.set_app_value('message_time', timestr)

if __name__ == '__main__':
    s = Spider()
    s.run()
