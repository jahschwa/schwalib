#!/usr/bin/env python

import sys
import time

import quickfile as qf

def main(username):
  
  path = '/home/' + username + '/pelican/'
  
  text = qf.read(path + 'publishconf.py')
  qf.write(text.replace('~share', '~' + username), path + 'publishconf.py')
  
  lines = qf.readlinesrs(path + 'pelicanconf.py')
  newlines = []
  for l in lines:
    if 'MY_AUTHOR' in l:
      author = raw_input('Author name for the blog: ').replace("'", "\\\'")
      newlines.append("AUTHOR = u'" + author + "'")
    elif 'SITENAME' in l:
      sitename = raw_input('Title for the blog: ').replace("'", "\\\'")
      newlines.append("SITENAME = u'" + sitename + "'")
    elif 'SITEURL' in l:
      newlines.append("SITEURL = '" + "http://grandline.jahschwa.com/~" + username + "/blog'")
    elif 'TIMEZONE' in l:
      newlines.append("TIMEZONE = 'US/Eastern'")
      newlines.append("DATE_FORMATS = {'en':'%a %Y-%m-%d'}");
    elif 'DEFAULT_LANG' in l:
      newlines.append("DEFAULT_LANG = u'en'")
      newlines.append("THEME = 'notmyidea'")
      newlines.append('')
      newlines.append("OUTPUT_PATH = '/home/" + username + "/public_html/blog'")
      newlines.append("PATH = '/home/" + username + "/pelican'")
    else:
      newlines.append(l)
  qf.writelinesn(newlines, path + 'pelicanconf.py')

  lines = qf.readlinesrs(path + 'content/firstpost.md')
  newlines = []
  t = time.strftime('%Y-%m-%d %H:%M', time.localtime())
  for l in lines:
    if 'Date:' in l:
      newlines.append('Date: ' + t)
    elif 'Modified:' in l:
      newlines.append('Modified: ' + t)
    elif 'Authors:' in l:
      newlines.append('Authors: ' + author)
    else:
      newlines.append(l)
  qf.writelinesn(newlines, path + 'content/firstpost.md')

if __name__ == '__main__':
  main(sys.argv[1])
