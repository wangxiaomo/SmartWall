#-*- coding: utf-8 -*-

import re

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
