#!/usr/bin/env python
#
# ease-of-use wrapper for email and smtplib libraries
#
# Author: Joshua A Haas, Jonathan E Frederickson

import smtplib,imaplib
from email.mime.text import MIMEText

def send(text,addr):
    """send an e-mail with body 'text' to addr"""

    msg = MIMEText(text)
    
    msg['Subject'] = 'Python'
    msg['From'] = 'smartoutletbbb@gmail.com'
    msg['To'] = addr

    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login('smartoutletbbb@gmail.com', 'homeautomation')
    server.sendmail('smartoutletbbb', addr, msg.as_string())
    server.quit()

def connect(s,u,p):
    """return an imap connection"""

    imap_conn = imaplib.IMAP4_SSL(s)
    imap_conn.login(u,p)
    imap_conn.select()
    return imap_conn

def getmsg(imap_conn):
    """return (body,sender) for the most recent email
    or None if there are no emails
    """

    imap_conn.recent()
    (typ, data) = imap_conn.search(None, 'ALL')
    if data[0] == '':
        return None
    (typ, data) = imap_conn.fetch(1,'(RFC822)')
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

def delmsg(imap_conn):
    """delete the most recent email"""

    imap_conn.store(1,'+FLAGS','\\Deleted')
    imap_conn.expunge()

