#!/usr/bin/env python
#
# functions for interacting with webpages
#
# Author: Joshua A Haas

import urllib2

def get(url):
    """return the webpage as a list of strings
    or return None if there is an error"""

    user_agent = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:31.0) Gecko/20100101 Firefox/31.0'
    headers = {'User-Agent':user_agent}
    req = urllib2.Request(url, None, headers);
    try:
        response = urllib2.urlopen(req)
        page = response.read()
        return page.split('\n')
    except:
        return None
