#-*- coding: utf-8 -*-

"""
segment class
"""

import sys
sys.path.insert(0, "..")

import config
from urllib import urlencode,urlopen

class Segment():

    def __init__(self):
        self.host = "http://%s:%d/?" % (config.SEGMENT_HOST,config.SEGMENT_PORT)

    def seg_txt(self, txt):
        seg_path = "%s%s" % (self.host, urlencode(dict(w=txt.decode("utf-8").encode("gb2312"))))
        ret = urlopen(seg_path).read().decode("gb2312")
        return ret.split(' ')

if __name__ == '__main__':
    print "Segment"
    parser = Segment()
    txt = parser.seg_txt("你好，我来自哈尔滨")
    for w in txt:
        print w
