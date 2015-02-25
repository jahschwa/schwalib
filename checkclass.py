#!/usr/bin/env python
#
# Continually check the Rowan catalogue page at URL
# and send an email to ADDR if the number of students
# registered changes. Also send an email on errors.
#
# Author: Joshua A Haas

import time,urllib2,sys
import webpage,emailer,prettytime

WAIT = 60
ADDR = '9083997913@vtext.com'
URL = 'https://adminweb.rowan.edu/PROD/bwckschd.p_disp_detail_sched?term_in=201520&crn_in=23324'
LOGFILE = '/home/laptopdude/bin/checkclass.log'

while True:
    with open(LOGFILE,'r') as f:
        old = int(f.read().rstrip())
    lines = webpage.get(URL)
    if lines is None:
        emailer.send('ERROR: webpage None',ADDR)
        sys.exit()
    try:
        remainline = lines[123]
        start = remainline.find(">")
        end = remainline.find("<",start+1)
        remainstr = remainline[start+1:end]
        remain = int(remainstr)
        t = prettytime.gettimestr()
        print(t+' - Remaining: '+str(remain))
        if remain != old:
             emailer.send('Embedded\nOld: '+str(old)+'\nNew: '+str(remain),ADDR)
             with open(LOGFILE,'w') as f:
                 f.write(str(remain))
        time.sleep(WAIT)
    except KeyboardInterrupt:
        sys.exit()
    except:
        emailer.send('ERROR: unknown',ADDR)
        sys.exit()
