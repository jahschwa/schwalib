#!/usr/bin/env python
#
# sends an e-mail when the tracking info of a UPS package changes
#
# Author: Joshua A Haas

import re
import sys
import time

import prettytime
import webpage

class Tracker:

  def __init__(self, emailer, addr, tracknum, log='upstrack.log', wait=60):

    self.emailer = emailer
    self.addr = addr
    self.tracknum = tracknum
    self.log = log
    self.wait = wait

    self.URL = ('http://wwwapps.ups.com/WebTracking/track?track=yes&trackNums=' +
        self.tracknum + '&loc=en_us')

  def run(self):

    try:
      with open(self.log, 'r') as f:
        old = f.read()
    except IOError:
      old = ''
      with open(self.log, 'w') as f:
        f.write(old)

    # if the most recent status has changed for the tracknum send an email to addr
    while True:

      try:
        success = False
        while not success:
          time.sleep(self.wait)
          lines = webpage.get(self.URL)
          success = lines is not None
        page = '\n'.join(lines)

        start = page.find('Activity')
        (location, start) = self.getcell(start + 1,page)
        (newdate, start) = self.getcell(start +1,page)
        (newtime, start) = self.getcell(start + 1,page)
        (activity, start) = self.getcell(start + 1,page)

        new = newdate + ' ' + newtime
        t = prettytime.gettimestr()

        if old != new:
          print t + ' - ' + location + ' - ' + activity + ' - ' + new
          outfile = open(self.log, 'w')
          outfile.write(new)
          outfile.close()
          old = new
          self.emailer.send(location + ' - ' + activity, self.addr)
        else:
          print t

      except Exception as e:
        self.emailer.send('UPSTrack Error', self.addr)
        with open(self.log, 'w') as f:
          f.write(str(e))
        sys.exit()

  def getcell(self, start, page):
    """return the formatted contents of the next table cell and its end index"""

    start = page.find('<td', start + 1)
    start = page.find('>', start + 1)
    stop = page.find('</td>', start + 1)
    s = page[start+1:stop].strip()
    s = s.replace('\n', ' ').replace('\t', ' ')
    return (' '.join(s.split()), stop)
