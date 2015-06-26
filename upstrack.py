#!/usr/bin/env python
#
# sends an e-mail when the tracking info of a UPS package changes
#
# Author: Joshua A Haas

import re,time,sys
import webpage,prettytime

class Tracker:

  def __init__(self,emailer,addr,tracknum,log='upstrack.txt'):
    
    self.emailer = emailer
    self.addr = addr
    self.tracknum = tracknum
    self.log = log
    
    self.URL = ('http://wwwapps.ups.com/WebTracking/track?track=yes&trackNums=' +
        self.tracknum + '&loc=en_us')

  def run(self):
    
    try:
      with open(self.log,'r') as f:
        old = f.read()
    except IOError:
      old = ''
      with open(self.log,'w') as f:
        f.write(old)

    while True:
      """if the most recent status has changed
      for the tracknum send an email to addr"""
      
      try:
        success = False
        while not success:
          lines = webpage.get(self.url)
          success = lines is not None
        page = '\n'.join(lines)

        start = page.find('Activity')
        matchobj = re.search('\d\d/\d\d/\d\d\d\d',page[start:])
        start = start + matchobj.start(0)
        newdate = matchobj.group(0)

        matchobj = re.search('\d+:\d\d [AP]\.M\.',page[start:])
        start = start + matchobj.start(0)
        newtime = matchobj.group(0)
        new = newdate + ' ' + newtime
        matchobj = re.search('<td>(.*)$',page[start:],re.M)
        activity = matchobj.group(1)
        
        t = prettytime.gettimestr()

        if old!=new:
          print t + ' - ' + activity + ' - ' + new
          outfile = open(self.log,'w')
          outfile.write(new)
          outfile.close()
          old = new
          emailer.send(activity,self.addr)
        else:
          print t

        time.sleep(60)
      except:
        emailer.send('Error',self.addr)
        sys.exit()
