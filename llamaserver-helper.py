# push button, send pretender to llamaserver
# push button, send turn to llamaserver
# push button, pull turnfile from GMail?
# also check for turn file emails or other stuff from GMail
# llamaserver details: http://z7.invisionfree.com/Dom3mods/index.php?showtopic=1890

import imaplib
import smtplib
import configparser
import email

config = configparser.ConfigParser()
config.read('config.ini')
address = config['Mail']['email']
password = config['Mail']['password']
	
def sendPretender():
	return
	
def sendTurn():
	return

# https://docs.python.org/3/library/imaplib.html
# https://www.reddit.com/r/learnpython/comments/3u39i0/is_sending_emails_with_gmail_supported_with/
# https://support.google.com/mail/troubleshooter/1668960?hl=en-GB&rd=1
# https://yuji.wordpress.com/2011/06/22/python-imaplib-imap-example-with-gmail/
mail = imaplib.IMAP4_SSL('imap.gmail.com')
try:
	mail.login(address, password)
except:
	print("Unexpected error:", sys.exc_info()[0])
	raise
	
mail.select("inbox") # possibly put this in config

# not useful, currently
# outmail = smtplib.SMTP('smtp.gmail.com:587')
# outmail.starttls()
# try:
	# outmail.login(email, password)
# except:
	# print("Unexpected error:", sys.exc_info()[0])
	# raise

result, data = mail.uid('search', None, "ALL") # search and return uids instead
latest_email_uid = data[0].split()[-1]
result, data = mail.uid('fetch', latest_email_uid, '(RFC822)')
raw_email = data[0][1]

email_message = email.message_from_bytes(raw_email)
 
print(email_message['To'])
print(email.utils.parseaddr(email_message['From'])) # for parsing "Yuji Tomita" <yuji@grovemade.com>
print(email_message['Subject'])
#print(email_message['Subject'])

# for key in email_message:
	# print(key)

#print(email_message.items()) # print all headers

# https://yuji.wordpress.com/2011/06/22/python-imaplib-imap-example-with-gmail/ mentions we need to do other stuff to get at the text of it. Not sure how to get at the attachment, as we may not care about the text
	
#outmail.quit()