#-*- coding: utf-8 -*-

"""
writer to save data.
"""

class Writer(object):
    def __init__(self, filename):
        self.hdl = open(filename, 'w')

    def __del__(self):
        self.hdl.close()

    def append(self, text):
        self.hdl.write(text + "\n")
