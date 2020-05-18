#!/usr/bin/env python
#
# functions for common file manipulations
#
# Author: Joshua A Haas

def read(name):
    """read the file name as a string"""

    with open(name, 'r') as f:
        return f.read()

def reads(name, s):
    """read the file name as a string
    and remove every instance of s"""

    return read(name).replace(s, '')

def readlines(name):
    """read lines from the file as a list"""

    with open(name, 'r') as f:
        return f.readlines()

def readlinesrs(name):
    """as readlines() but also rstrip()"""

    lines = readlines(name)
    return [l.rstrip() for l in lines]

def readlinesls(name):
    """as readlines() but also lstrip()"""

    lines = readlines(name)
    return [l.lstrip() for l in lines]

def readlinesbs(name):
    """as readlines() but also strip()"""

    lines = readlines(name)
    return [l.strip() for l in lines]

def write(s, name):
    """write the string s to the file name"""

    with open(name, 'w') as f:
        f.write(s)

def writelines(lines, name):
    """write the list lines to the file name"""

    with open(name, 'w') as f:
        f.writelines(lines)

def writelinesn(lines, name):
    """as writelines() but add \\n to each"""

    lines = [l + '\n' for l in lines]
    writelines(lines, name)

def append(s, name):
    """append the string s to the file name"""

    with open(name, 'a') as f:
        f.write(s)

def appendlines(lines, name):
    """append the list lines to the file name"""

    with open(name, 'a') as f:
        f.write(lines)

def appendlinesn(lines, name):
    """as appendlines() but add \\n to each"""

    lines = [l + '\n' for l in lines]
    appendlines(lines, name)
