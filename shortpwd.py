#!/usr/bin/env python
#
# Shortens the PWD to "/folder/.../folder"
# Also replaces "/home/user" with "~"
#
# Add the following line to the end of ~/.profile to use this
# export PROMPT_COMMAND='PS1="$(python /home/laptopdude/bin/shortpwd.py)"'
#
# Author: Joshua A Haas

import os
from commands import getoutput
from socket import gethostname

def shorten(pwd):
    """shorten the bash prompt to only contain
    the first and last folders for deep entries
    """

    homedir = os.path.expanduser('~')
    pwd = pwd.replace(homedir, '~', 1)

    first = pwd.find('/',1)
    second = pwd.find('/',first+1)
    last = pwd.rfind('/')

    if first>-1 and second>-1:
        pwd = pwd[:first+1]+'...'+pwd[last:]
    return pwd

if __name__ == '__main__':
    hostname = gethostname()
    username = os.environ['USER']
    pwd = os.getcwd()
    print '[%s@%s:%s] ' % (username, hostname, shorten(pwd))
