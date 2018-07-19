import httplib2
import os
import oauth2client
from oauth2client import client, tools
import base64
from email import encoders
from oauth2client.file import Storage

#needed for attachment
import smtplib
import mimetypes
from email import encoders
from email.message import Message
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
#List of all mimetype per extension: http://help.dottoro.com/lapuadlp.php  or http://mime.ritey.com/

from apiclient import errors, discovery  #needed for gmail service

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

SCOPES = 'https://mail.google.com'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Gmail API Python3 Sender!'

def get_credentials():
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,'gmail-python-quickstart.json')
    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


## Get creds, prepare message and send it
def create_message_and_send(sender, to, subject,  message_text_plain, message_text_html, attached_file):
    credentials = get_credentials()
    # Create an httplib2.Http object to handle our HTTP requests, and authorize it using credentials.authorize()
    http = httplib2.Http()
    # http is the authorized httplib2.Http()
    http = credentials.authorize(http)        #or: http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)
    ## without attachment
    # message_without_attachment = create_message_without_attachment(sender, to, subject, message_text_html, message_text_plain)
    # send_Message_without_attachment(service, "me", message_without_attachment, message_text_plain)
    ## with attachment
    message_with_attachment = create_Message_with_attachment(sender, to, subject, message_text_plain, message_text_html, attached_file)
    send_Message_with_attachment(service, "me", message_with_attachment, message_text_plain,attached_file)

# def create_message_without_attachment (sender, to, subject, message_text_html, message_text_plain):
    # #Create message container
    # message = MIMEMultipart('alternative') # needed for both plain & HTML (the MIME type is multipart/alternative)
    # message['Subject'] = subject
    # message['From'] = sender
    # message['To'] = to

    # #Create the body of the message (a plain-text and an HTML version)
    # message.attach(MIMEText(message_text_plain, 'plain'))
    # message.attach(MIMEText(message_text_html, 'html'))

    # raw_message_no_attachment = base64.urlsafe_b64encode(message.as_bytes())
    # raw_message_no_attachment = raw_message_no_attachment.decode()
    # body  = {'raw': raw_message_no_attachment}
    # return body


def create_Message_with_attachment(sender, to, subject, message_text_plain, message_text_html, attached_file):
    """Create a message for an email.
    message_text: The text of the email message.
    attached_file: The path to the file to be attached.
    Returns:
    An object containing a base64url encoded email object.
    """

    ##An email is composed of 3 part :
        #part 1: create the message container using a dictionary { to, from, subject }
        #part 2: attach the message_text with .attach() (could be plain and/or html)
        #part 3(optional): an attachment added with .attach()

    ## Part 1
    message = MIMEMultipart() #when alternative: no attach, but only plain_text
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject

    ## Part 2   (the message_text)
    # The order count: the first (html) will be use for email, the second will be attached (unless you comment it)
    message.attach(MIMEText(message_text_html, 'html'))
    message.attach(MIMEText(message_text_plain, 'plain'))

    ## Part 3 (attachment)
    # # to attach a text file you containing "test" you would do:
    # # message.attach(MIMEText("test", 'plain'))

    #-----About MimeTypes:
    # It tells gmail which application it should use to read the attachment (it acts like an extension for windows).
    # If you dont provide it, you just wont be able to read the attachment (eg. a text) within gmail. You'll have to download it to read it (windows will know how to read it with it's extension).

    #-----3.1 get MimeType of attachment
        #option 1: if you want to attach the same file just specify it’s mime types

        #option 2: if you want to attach any file use mimetypes.guess_type(attached_file)

    my_mimetype, encoding = mimetypes.guess_type(attached_file)

    # If the extension is not recognized it will return: (None, None)
    # If it's an .mp3, it will return: (audio/mp3, None) (None is for the encoding)
    #for unrecognized extension it set my_mimetypes to  'application/octet-stream' (so it won't return None again).
    if my_mimetype is None or encoding is not None:
        my_mimetype = 'application/octet-stream'


    main_type, sub_type = my_mimetype.split('/', 1)# split only at the first '/'
    # if my_mimetype is audio/mp3: main_type=audio sub_type=mp3

    #-----3.2  creating the attachment
        #you don't really "attach" the file but you attach a variable that contains the "binary content" of the file you want to attach

        #option 1: use MIMEBase for all my_mimetype (cf below)  - this is the easiest one to understand
        #option 2: use the specific MIME (ex for .mp3 = MIMEAudio)   - it's a shorcut version of MIMEBase

    #this part is used to tell how the file should be read and stored (r, or rb, etc.)
    if main_type == 'text':
        print("text")
        temp = open(attached_file, 'r')  # 'rb' will send this error: 'bytes' object has no attribute 'encode'
        attachment = MIMEText(temp.read(), _subtype=sub_type)
        temp.close()

    elif main_type == 'image':
        print("image")
        temp = open(attached_file, 'rb')
        attachment = MIMEImage(temp.read(), _subtype=sub_type)
        temp.close()

    elif main_type == 'audio':
        print("audio")
        temp = open(attached_file, 'rb')
        attachment = MIMEAudio(temp.read(), _subtype=sub_type)
        temp.close()

    elif main_type == 'application' and sub_type == 'pdf':
        temp = open(attached_file, 'rb')
        attachment = MIMEApplication(temp.read(), _subtype=sub_type)
        temp.close()

    else:
        attachment = MIMEBase(main_type, sub_type)
        temp = open(attached_file, 'rb')
        attachment.set_payload(temp.read())
        temp.close()

    #-----3.3 encode the attachment, add a header and attach it to the message
    encoders.encode_base64(attachment)  #https://docs.python.org/3/library/email-examples.html
    filename = os.path.basename(attached_file)
    attachment.add_header('Content-Disposition', 'attachment', filename=filename) # name preview in email
    message.attach(attachment)


    ## Part 4 encode the message (the message should be in bytes)
    message_as_bytes = message.as_bytes() # the message should converted from string to bytes.
    message_as_base64 = base64.urlsafe_b64encode(message_as_bytes) #encode in base64 (printable letters coding)
    raw = message_as_base64.decode()  # need to JSON serializable (no idea what does it means)
    return {'raw': raw}



# def send_Message_without_attachment(service, user_id, body, message_text_plain):
    # try:
        # message_sent = (service.users().messages().send(userId=user_id, body=body).execute())
        # message_id = message_sent['id']
        # # print(attached_file)
        # print (f'Message sent (without attachment) \n\n Message Id: {message_id}\n\n Message:\n\n {message_text_plain}')
        # # return body
    # except errors.HttpError as error:
        # print (f'An error occurred: {error}')

def send_Message_with_attachment(service, user_id, message_with_attachment, message_text_plain, attached_file):
    """Send an email message.
    Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me" can be used to indicate the authenticated user.
    message: Message to be sent.
    Returns:
    Sent Message.
    """
    try:
        message_sent = (service.users().messages().send(userId=user_id, body=message_with_attachment).execute())
        message_id = message_sent['id']
        # print(attached_file)

        # return message_sent
    except errors.HttpError as error:
        print ("An error occurred: {error}")


def main():
    to = "chanduch1999@gmail.com"
    sender = "chandu"
    subject = "Testing"
    message_text_html  = r'Hi'
    message_text_plain = " image attached"
    attached_file = r'background.jpg'
    create_message_and_send(sender, to, subject, message_text_plain, message_text_html, attached_file)


if __name__ == '__main__':
    main()
