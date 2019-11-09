#!/usr/bin/env python
#
# Module to help with writing webpages in python
#
# Author: Joshua A Haas

def comment(lines):
  """comment the given lines"""
  
  return ['<!--' + l + '-->' for l in lines]

def br(n):
  """return the given number of <br/> tags"""
  
  return '<br/>' * n

def space(n):
  """return the given number of &nbsp;"""
  
  return '&nbsp;' * n

def tab(lines):
  """add the tab character to the beginning of each line"""
  
  TAB = '  '
  return [TAB + l for l in lines]

def tag(tagname, content, attribs=None):
  """add the tag as elements before and after the list content"""
  
  opentag = '<' + tagname
  if attribs is not None:
    for key in attribs:
      opentag += ' ' + key
      if attribs[key] is not None:
        opentag += '="' + attribs[key] + '"'
  opentag += '>'
  return [opentag] + content + ['</' + tagname + '>']

def tags(tagname, content, attribs=None):
  """add the tag before and after the string content"""
  
  opentag = '<' + tagname
  if attribs is not None:
    for key in attribs:
      opentag += ' ' + key
      if attribs[key] is not None:
        opentag += '="' + attribs[key] + '"'
  opentag += '>'
  return opentag + content + '</' + tagname + '>'

def css(names,props):
  """create multi-line css given tag names and the dict props"""

  lines = [list2str(names) + ' {']
  for key in props:
    lines += tab([key + ': ' + props[key] + ';'])
  lines += ['}']
  return lines

def list2str(l):
  """return the list l as a string formatted for the css() function"""
  
  if isinstance(l, str):
    return l
  return str(l)[1:-1].replace("'", "")
