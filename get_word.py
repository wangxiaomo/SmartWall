#-*- coding: utf-8 -*-

import re
import HTMLParser

"""
words = []
pat = re.compile(r"(?:\\u[a-f0-9]{4})+")

log = "log"
lineno = 0
for line in file(log):
    m = pat.findall(line)
    lineno += 1
    if len(m) == 0:
        continue
    print "lineno: %d\twords: %d" % (lineno, len(m))
    words.extend(m)

print "\n\n\nTotal Words: %d" % len(words)
words = [eval(u"u'%s'" % w) for w in words]
with open('words', 'w') as f:
    for w in words:
        f.write(w.encode('utf-8')+"\n")

"""

with open("log2") as f:
    html = f.read().strip()

all_groups = re.findall("<div class=\"c\">(.*?)</div>(?=<div class=\"(?:[cs])\"\>)", html)
all_groups = all_groups[2:-1]
print len(all_groups)

parser = HTMLParser.HTMLParser()

group = all_groups[0]
i = group
people = re.findall(r'<span class="cmt">(.*?)</span>', i)[0]
latest = re.findall(r'(?:</span>)(.*?)(?=<span)', i)[0]
time = re.findall(r'<span class="ct">(.*?)</span>', i)[0]
print people,latest,time
