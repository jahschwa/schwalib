#!/usr/bin/env python
#
# Functions to make common time manupulations easier
#
# Author: Joshua A Haas

import time

TIMEFORMAT = '%Y/%m/%d - %H:%M:%S'

def gettime():
    """returns the local time_struct"""

    return time.localtime()

def totimestr(t):
    """return the given time as a string; works
    for time_structs or seconds since linux epoch
    """

    if isinstance(t,float):
        t = time.localtime(t)

    return time.strftime(TIMEFORMAT,t)

def gettimestr():
    """return the current local time as a string"""

    return totimestr(time.localtime())

def getdiff(now,then):
    """return the difference between now and then
    in seconds where the inputs are time_structs
    or seconds since linux epoch; note that the answer
    will be negative if then is later than now
    """

    if not isinstance(now,float):
        now = time.mktime(now)
    if not isinstance(then,float):
        then = time.mktime(then)
    return now-then

def getdiffnow(then):
    """same as getdiff() but subtract then from
    the current time
    """

    return getdiff(time.time(),then)

def getdiffstr(now,then):
    """return the difference between the two times
    as a readable string; if the difference is less
    than one minute it returns 'now'
    """

    secs = getdiff(now,then)
    mins = int(secs/60)
    hours = int(mins/60)
    days = int(hours/24)
    mons = int(days/30)
    years = int(days/365)

    if years>0:
        num = years
        nam = 'year'
    elif mons>0:
        num = mons
        nam = 'month'
    elif days>0:
        num = days
        nam = 'day'
    elif hours>0:
        num = hours
        nam = 'hour'
    elif mins>0:
        num = mins
        nam = 'min'
    else:
        return 'now'

    s = str(num)+' '+nam
    if num>1:
        s = s+'s'
    return s

def getdiffnowstr(then):
    """same as getdiffstr() but subtract then
    from the current time
    """

    return getdiffstr(time.time(),then)

def mon2str(month):
    """return the name of the month of the
    specified number in the range [1,12]
    """

    months = ['January','February','March','April','May','June','July',
        'August','September','October','November','December']
    return months[month-1]

def mon2abrev(month):
    """as mon2str() but truncate to 3 letters"""
    
    return mon2str(month)[:3]

def str2mon(month):
    """return the number of the month in the
    range [1,12]; will work with full names
    and standard 3-letter abbreviations and
    is also case insensitive
    """

    months = ['january','february','march','april','may','june','july',
        'august','september','october','november','december']
    return [e for (e,m) in enumerate(months) if month.lower() in m][0]+1

def str2time(t):
    """return a time_struct for the input
    string t
    """

    return time.strptime(t,TIMEFORMAT)

if __name__ == '__main__':
    print gettimestr()
