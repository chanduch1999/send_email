# Gopavasanth
# Date : 05/05/2018
from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import sending_mail

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

import auth
import mesages

SCOPES = 'https://mail.google.com/'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Gmail API Python Quickstart'
authInst = auth.auth(SCOPES,CLIENT_SECRET_FILE,APPLICATION_NAME)
credentials = authInst.get_credentials()

http = credentials.authorize(httplib2.Http())
service = discovery.build('gmail', 'v1', http=http)


my_file = open("file.txt", "r")

from datetime import date
today = str(date.today())
print("Today Date :" + today)

mssg=mesages.list_messages_matching_query(service, user_id="me", query='[foss-2017] Status Update '+ today)
#print (mssg)
print ("This required")
#user_id = mssg[1]['id']
#print (user_id)

import send_email

sendInst = send_email.send_email(service)
#message = sendInst.create_message_with_attachment('gopavasanth1999@gmail.com','p.bhanuprakash12345@gmail.com','Hello_API',my_file.read(), 'image.jpg' )
message = sendInst.create_message('gopavasanth1999@gmail.com','	lazyengineersfoss@googlegroups.com', '[foss-2017] Status Update [29-06-2018]', my_file.read())
#message = sendInst.send_message( user_id, "Hello this is Testing mail")
sendInst.send_message('me',message)
my_file.close()
