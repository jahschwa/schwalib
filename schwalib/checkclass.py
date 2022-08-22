#!/usr/bin/env python
#
# Continually check the Rowan catalogue page at URL
# and send an email to ADDR if the number of students
# registered changes. Also send an email on errors.
#
# Author: Joshua A Haas

import sys
import time

import prettytime
import webpage

class Checker:

  def __init__(self, emailer, addr, url, log='checkclass.log', wait=60):

    self.emailer = emailer
    self.addr = addr
    self.url = url
    self.log = log
    self.wait = 60

  def run(self):

    while True:
      with open(self.log, 'r') as f:
        old = int(f.read().rstrip())
      lines = webpage.get(self.url)
      if lines is None:
        emailer.send('ERROR: webpage None', self.addr)
        sys.exit()
      try:
        remainline = lines[123]
        start = remainline.find(">")
        end = remainline.find("<", start+1)
        remainstr = remainline[start+1:end]
        remain = int(remainstr)
        t = prettytime.gettimestr()
        print(t + ' - Remaining: ' + str(remain))
        if remain != old:
           emailer.send('Embedded\nOld: ' + str(old) + '\nNew: ' + str(remain), self.addr)
           with open(self.log, 'w') as f:
             f.write(str(remain))
        time.sleep(self.wait)
      except KeyboardInterrupt:
        sys.exit()
      except:
        emailer.send('ERROR: unknown', self.addr)
        sys.exit()
