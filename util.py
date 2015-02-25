#!/usr/bin/env python
#
# miscellaneous functions I couldn't fit in other modules
#
# Author: Joshua A Haas

import os
from subprocess import Popen,PIPE

def getusers():
  """return a list of users"""

  users = os.listdir('/home')
  users.remove('share')
  users.sort(key=str.lower)
  return users

def who():
  """return a list of logged in users"""

  p = Popen('who',stdout=PIPE,stderr=PIPE)
  (out,err) = p.communicate()
  out = out.strip()
  users = [l[:l.find(' ')] for l in out.split('\n')]
  users = list(set(users))
  if '' in users:
    users.remove('')
  users.sort()
  return users

def inany(keys,s):
  """return true if any key is in s"""
  
  for key in keys:
    if key in s:
      return True
  return False

def findinlist(s,l,start=0,stop=-1):
  """return the index of the first instance of s in l"""

  if stop==-1:
    stop = len(l)
  for (i,x) in enumerate(l[start:stop]):
    if s in x:
      return (i+start,x.find(s))
  return (-1,None)

def findallinlist(s,l,start=0,stop=-1):
  """return a list of indices of s in l"""

  if stop==-1:
    stop = len(l)
  found = []
  current = start
  while True:
    (i,x) = findinlist(s,l,current)
    if i==-1 or i>=stop:
      break
    found.append((i,x))
    current = i+1
  return found

def list2str(l):
  """print the list without [] or '' for strings"""

  s = ''
  for x in l:
    s += (str(x)+', ')
  return s[:-2]

def rlistdir(path):
  """list files recursively"""

  allfiles = []                                                               
  for (cur_path,dirnames,filenames) in os.walk(path):
    for filename in filenames:
      allfiles.append(os.path.join(cur_path,filename))
  return allfiles

def blankdict(keys):
  """make a dict with the specified keys where each value is none"""

  d = {}
  for key in keys:
    d[key] = None
  return d

def checkdict(d,keys):
  """make sure the dict d has all keys in keys"""

  if len(keys)!=len(d.keys()):
    raise KeyError('Input dict has wrong number of keys')

  for key in keys:
    if key not in d.keys():
      raise KeyError('Input dict is missing the key "'+key)

def updatedict(old,new):
  """update the values in old with those in new"""
  
  for key in new.keys():
    if key not in old.keys():
      raise KeyError('The key "'+key+' is invalid')
    old[key] = new[key]
  return old

def fillargs(opts,default):
  """Initialize defaults and replace with user specified"""

  result = {}
  for key in default:
    result[key] = default[key]
  if opts is not None:
    for key in opts:
      result[key] = opts[key]
  return result

def matrix(rows,cols,value=None):
  """create a list of lists with all cells set to value"""
    
  mat = []
  for i in range(0,rows):
    row = []
    for i in range(0,cols):
      row.append(value)
    mat.append(row)
  return mat

def replaceall(s,olds,new):
  """replace all elements in olds with new in string s"""
  
  for old in olds:
    s.replace(old,new)
