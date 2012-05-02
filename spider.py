#-*- coding: utf-8 -*-

"""
spider for sina weibo.
fetch user's private mailbox and
    save them to the database.
"""

from mechanize import Browser

WEIBO_URL = "http://weibo.com"
USERNAME = '497052184@qq.com'
PASSWORD = 'Wj2201367'

class Spider(object):
    def __init__(self):
        self.br = Browser()
        self.br.set_handle_equiv(False)
        self.br.set_handle_robots(False)

    def login(self, username, password):
        self.br.open(WEIBO_URL)
        resp = self.br.response()
        print resp
        print dir(resp)
        print resp.get_data()

if __name__ == '__main__':
    spider = Spider()
    spider.login(USERNAME, PASSWORD)
