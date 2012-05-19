#-*- coding: utf-8 -*-

import os
import pickle
from time import sleep

import config
from weibopy.auth import OAuthHandler
from weibopy.api import API
from writer import Writer

ALERT_MAX_TIMES = 3

class WeiboBackup(object):
    """
    新浪微博自动备份.
    """
    def __init__(self):
        self.hdl = OAuthHandler(config.APP_KEY, config.APP_SECRET)
        self.api = None
        self.writer = None
        self.token  = {}
        self.auth()

    def auth(self):
        try:
            with open("../"+config.TOKEN_FILE) as f:
                self.token = pickle.load(f)
            self.hdl.setToken(
                self.token["key"],
                self.token["secret"]
            )
            self.api = API(self.hdl)
        except Exception as e:
            print e

    def get_auth_url(self):
        return self.hdl.get_authorization_url()

    def get_data(self, screen_name, page):
        count = 200
        while True:
            try:
                res = self.api.user_timeline(
                    screen_name=screen_name,
                    count=count,
                    page=page
                )
                if len(res)==0:
                    return page
                else:
                    for status in res:
                        text = status.text
                        retweet = getattr(
                            status,
                            "retweeted_status",
                            False
                        )
                        if retweet:
                            text = text+"//"+retweet.text
                        text = text.encode("utf-8")
                        self.writer.append(text)
                page = page+1
            except Exception as e:
                print e
            

    def backup(self, screen_name, filename=""):
        if filename:
            self.writer = Writer(filename)
        else:
            self.writer = []
        page,alert_num = 1,0
        while alert_num<ALERT_MAX_TIMES:
            page = self.get_data(screen_name, page)
            alert_num += 1
        return self.writer

if __name__ == '__main__':
    obj = WeiboBackup()
    obj.auth()
    path = os.getcwd()

    obj.backup(sys.argv[1], path+"/"+sys.argv[2])
