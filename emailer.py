#!/usr/bin/env python
#
# ease-of-use wrapper for email and smtplib libraries
#
# Author: Joshua A Haas, Jonathan E Frederickson

import smtplib,imaplib
from email.mime.text import MIMEText

class Emailer:

  def __init__(self,username,password,smtp=None,port=465,imap=None):
    """create a new Emailer that will login to the given account"""
    
    self.smtp = smtp
    self.user = username
    self.pword = password
    self.port = port
    self.iserv = imap
    self.imap = None

  def send(self,text,addr,sub=None):
    """send an e-mail with body 'text' to addr"""
      
    msg = MIMEText(text)
    
    if sub is None:
      sub = 'Python'
    msg['Subject'] = sub
    msg['From'] = self.user
    msg['To'] = addr
    
    server = smtplib.SMTP_SSL(self.smtp,self.port)
    server.login(self.user,self.pword)
    server.sendmail(self.user.split('@')[0], addr, msg.as_string())
    server.quit()

  def connect(self):
    """return an imap connection"""

    self.imap = imaplib.IMAP4_SSL(self.iserv)
    self.imap.login(self.user,self.pword)
    self.imap.select()

  def disconnect(self):
    """end the imap connection"""
    
    self.imap.close()
    self.imap.logout()
    self.imap = None

  def getmsg(self):
    """return (body,sender) for the most recent email
    or None if there are no emails
    """
    
    if self.imap is None:
      self.connect()
    
    self.imap.recent()
    (typ, data) = self.imap.search(None, 'ALL')
    if data[0] == '':
        return None
    (typ, data) = self.imap.fetch(1,'(RFC822)')
    msg = data[0][1].split('\r\n\r\n')
    
    index = 0
    while(True):
        if "text/plain" in msg[index]:
            break
        index += 1
    body = msg[index+1]

    index = 0
    while(True):
        if 'Return-Path' in msg[index]:
            break
        index += 1
    sender = msg[index]

    start = sender.find('<')
    end = sender.find('>',start)
    sender = sender[start+1:end]

    return (body,sender)

  def delmsg(self):
    """delete the most recent email"""

    self.imap.store(1,'+FLAGS','\\Deleted')
    self.imap.expunge()

