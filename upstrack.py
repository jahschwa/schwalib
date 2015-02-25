#!/usr/bin/env python
#
# sends an e-mail when the tracking info of a UPS package changes
#
# Author: Joshua A Haas

import re,time,sys
import webpage,emailer,prettytime

TRACK_NUM = '1ZY511170379208407'
ADDR = '9083997913@vtext.com'

url = 'http://wwwapps.ups.com/WebTracking/track?track=yes&trackNums=' + \
    TRACK_NUM + '&loc=en_us'
infile = open('upstrack.txt','r')
old = infile.read()
infile.close()

while True:
    """if the most recent status has changed
    for the TRACK_NUM send an email to ADDR
    """

    try:
        success = False
        while not success:
            lines = webpage.get(url)
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
            outfile = open('upstrack.txt','w')
            outfile.write(new)
            outfile.close()
            old = new
            emailer.send(ADDR,activity)
        else:
            print t

        time.sleep(60)
    except:
        emailer.send(ADDR,'Error')
        sys.exit()
