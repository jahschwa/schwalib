#!/usr/bin/env python
#
# ease-of-use wrapper for email and smtplib libraries
#
# Author: Joshua A Haas, Jonathan E Frederickson

import imaplib
import smtplib
from email.mime.text import MIMEText

class Emailer:

  def __init__(self, username, password, smtp=None, port=None,
    imap=None, imap_port=None, starttls=True):
    """create a new Emailer that will login to the given account"""

    self.user = username
    domain = username.split('@')[-1]

    self.pword = password
    self.smtp = smtp or 'smtp.' + domain
    self.port = port or (587 if starttls else 465)
    self.iserv = imap or 'imap.' + domain
    self.iport = imap_port or (143 if starttls else 993)
    self.starttls = starttls

    self.imap = None

  def send(self, text, addr, sub=None):
    """send an e-mail with body 'text' to addr"""

    msg = MIMEText(text)

    if sub is None:
      sub = 'Python'
    msg['Subject'] = sub
    msg['From'] = self.user
    msg['To'] = addr

    if self.starttls:
      server = smtplib.SMTP(self.smtp, self.port)
      server.starttls()
    else:
      server = smtplib.SMTP_SSL(self.smtp, self.port)

    server.login(self.user, self.pword)
    server.sendmail(self.user.split('@')[0], addr, msg.as_string())
    server.quit()

  def connect(self):
    """return an imap connection"""

    if self.starttls:
      self.imap = imaplib.IMAP4(self.iserv, self.iport)
      self.imap.starttls()
    else:
      self.imap = imaplib.IMAP4_SSL(self.iserv, self.iport)

    self.imap.login(self.user, self.pword)
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
    (typ, data) = self.imap.fetch(1, '(RFC822)')
    msg = data[0][1].split('\r\n\r\n')

    index = 0
    while(True):
        if "text/plain" in msg[index]:
            break
        index += 1
    body = msg[index + 1]

    index = 0
    while(True):
        if 'Return-Path' in msg[index]:
            break
        index += 1
    sender = msg[index]

    start = sender.find('<')
    end = sender.find('>', start)
    sender = sender[start+1:end]

    return (body, sender)

  def delmsg(self):
    """delete the most recent email"""

    self.imap.store(1, '+FLAGS', '\\Deleted')
    self.imap.expunge()
