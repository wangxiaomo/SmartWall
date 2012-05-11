#-*- coding: utf-8 -*-

"""
Poster: 发布微博。
"""

import sys
sys.path.insert(0, "./lib")

import re
import pickle
import urllib2
import config
from lib.weibopy.auth import OAuthHandler
from lib.weibopy.api import API
from Helper import log

USER_URL_FORMAT = "http://weibo.cn/%s/info?vt=4&wm=ig_0001_index&gsid=%s"

class Poster():

    def __init__(self):
        self.hdl = OAuthHandler(config.APP_KEY, config.APP_SECRET)
        self.api = None
        self.token = {}
        try:
            with open(config.TOKEN_FILE) as f:
                self.token = pickle.load(f)
            log("token init success!")
            log("Access Token is: " + str(self.token))
            self.hdl.setToken(
                self.token["key"],
                self.token["secret"]
            )
            self.api = API(self.hdl)
        except:
            log("Haven't Authorizationed!")
            print "Authorization URL: %s" % self.get_auth_url()
            pin = raw_input("PIN: ")
            self.auth(pin)
        try:
            with open(".gsid") as f:
                self.gsid = f.read().rstrip()
        except:
            raise Exception("Haven't Got GSID!")

    def get_auth_url(self):
        return self.hdl.get_authorization_url()

    def auth(self, pin):
        try:
            token = self.hdl.get_access_token(pin)
            self.api = API(self.hdl)
        except:
            raise Exception("OAuth Failed!")
        self.token.update(dict(key=token.key, secret=token.secret))
        log("Access Token is: " + str(self.token))
        with open(config.TOKEN_FILE, "w") as f:
            pickle.dump(self.token, f)
        log("pickle saved success!")

    def post_status(self, status):
        try:
            self.api.update_status(status=status)
        except:
            raise Exception("Post Status Failed!")

    def get_user_info(self, screen_name):
        try:
            user = {}
            ret = self.api.get_user(screen_name=screen_name)
            user_id = ret.id
            gender = ret.gender
            url = USER_URL_FORMAT % (user_id, self.gsid)
            request = urllib2.Request(url)
            request.add_header('User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:12.0) Gecko/20100101 Firefox/12.0')
            html = urllib2.urlopen(request).read()
            if re.match(r'哈尔滨工业大学|哈工大威海|哈工大（威海）|哈工大(威海)', html):
                school = '哈工大'
            elif re.match(r'山东大学|山大（威海）|山大(威海)', html):
                school = '山大'
            else:
                school = '未知'
            user.update(dict(id=user_id, name=screen_name, sex=gender, school=school))
            return user
        except:
            raise

if __name__ == '__main__':
    poster = Poster()
    poster.get_user_info("梦逝去的方向")
