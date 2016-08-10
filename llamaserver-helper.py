# push button, send pretender to llamaserver
# push button, send turn to llamaserver
# push button, pull turnfile from GMail?
# also check for turn file emails or other stuff from GMail
# llamaserver details: http://z7.invisionfree.com/Dom3mods/index.php?showtopic=1890

# https://docs.python.org/3/library/imaplib.html
# https://www.reddit.com/r/learnpython/comments/3u39i0/is_sending_emails_with_gmail_supported_with/
# https://support.google.com/mail/troubleshooter/1668960?hl=en-GB&rd=1
# https://yuji.wordpress.com/2011/06/22/python-imaplib-imap-example-with-gmail/
# http://robertwdempsey.com/python3-email-with-attachments-using-gmail/

# http://www.tutorialspoint.com/python3/python_multithreading.htm - threading
# http://tkinter.unpythonic.net/wiki/tkFileDialog - file dialogue

# playing by e-mail:
# game names cannot have spaces - they use underscores; should match game folder name?
# file extension for pretenders is .2h; these are sent to pretenders@llamaserver.net (found in newlords folder)
# file extension for finished turns is .2h; these are sent to turns@llamaserver.net (2h, 2 host, to host)
# file extension for received turns is .trn; these are sent to the user's email address, needs to be copied to game directory
# Game progression:
# 1. Game is set up on llamaserver
# 2. players send in pretender files for their nation (to pretenders@llamaserver.net) - subject line should match game name exactly
# 3. llamaserver replies with an email confirming the pretender has been received (there's probably an e-mail saying a nation has already been claimed?)
# 4. llamaserver sents an email stating the game has begun, with the first .trn file attached; it also outputs a deadline for turning turns in (always, or only when set?). Turn file can be compressed to zip, rar or gz format
#		EG. 'The first turn is due in by 00:23 GMT on Wednesday August 10th' - does this vary based on time zone? This may not always be present?
#		Apparently from this point the subject doesn't matter, either; possibly it reads the .trn file
# 5. player copies .trn file into game folder for Dominions 4, loads it and completes turn
# 6. player sends .2h file from game folder to turns@llamaserver.net
#		There's an error message here for sending in the wrong turn; application should definitely be able to react to this
# 7. llamaserver sends an email with the next .trn file
# Steps 5 to 7 repeat until game is over

# states:
# player needs to send pretender
# waiting for llamaserver confirmation of pretender
# waiting for game start
# player needs to complete and send turn
# waiting for llamaserver confirmation of .2h file
# waiting for llamaserver next turn
# game ended

# emails come from turns@llamaserver.com, always?

# may be able to make application handle more than one game simultaneously: dropdown list to select game, show details and controls for game?

# new config file for each game?
# shouldn't need to do this? Should just save data in a file somewhere

# data to store about games:
# name - necessary for finding game folder
# era - 'early', 'mid', 'late' - part of the generated file names, so necessary to know this to get the correct file
# nation - possibly needed to parse emails (nation name is mentioned in body), and is used in game file names; necessary as your nation may not be the only file present (also get allied nation files in server-based games)
# turn number - can get this from latest turn-email from llamaserver
# state - see above

import imaplib
import smtplib
import configparser
import email
import os
import sys
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart

config = configparser.ConfigParser()
config.read('config.ini')
address = config['Mail']['email']
password = config['Mail']['password']
datadir = config['Game']['datadir']
game = config['Game']['gamename']

# note that if you want to get text content (body) and the email contains
# multiple payloads (plaintext/ html), you must parse each message separately.
# use something like the following: (taken from a stackoverflow post)
# feld - need to understand this
def get_first_text_block(email_message_instance):
	maintype = email_message_instance.get_content_maintype()
	if maintype == 'multipart':
		for part in email_message_instance.get_payload():
			if part.get_content_maintype() == 'text':
				return part.get_payload()
	elif maintype == 'text':
		return email_message_instance.get_payload()

# works, but gives out a duplicate of the main text message
def getTextBlocks(email_message_instance):
	blocks = []
	maintype = email_message_instance.get_content_maintype()
	if maintype == 'multipart':
		for part in email_message_instance.get_payload():
			if part.get_content_maintype() == 'text':
				blocks.append(part.get_payload())
	elif maintype == 'text':
		blocks.append(email_message_instance.get_payload())
	return blocks
	
def getEmail(uid):
	result, data = mail.uid('fetch', uid, '(RFC822)')
	raw_email = data[0][1]
	return raw_email

def parseMail(raw_email):
	email_message = email.message_from_bytes(raw_email)
	if email_message['To'] is not None:
		# only check emails from llamaserver: all llamaserver emails seem to come from turns@llamaserver.com
		#if email.utils.parseaddr(email_message['From'])[1] == 'turns@llamaserver.com': 
		email_to = email_message['To']
		email_from = email.utils.parseaddr(email_message['From']) # for parsing "Yuji Tomita" <yuji@grovemade.com>
		email_subject = email_message['Subject']
		email_text = get_first_text_block(email_message)
		print(email_to)
		print(email_from)
		print(email_subject)
		print(email_text.strip())
		#for textblock in getTextBlocks(email_message):
		#	print(textblock)
		print('-----')
	# should obviously do other things, here, but for now it's nice it iterates through
	return
	
def listPretenders():
	return
	
def getPretender():
	return
	
def sendEmailWithAttachment(attachment_path, subject, recipient_address):
	# attachment_path: full path
	# subject: needs to be the game name, for at least pretender
	# recipient address: pretenders@llamaserver.net for pretenders, turns@llamaserver.net for turns
	# create email here
	outer = MIMEMultipart()
	outer['From'] = address
	outer['To'] = recipient_address
	outer['Subject'] = subject # needs to be game name
	# make sure it gets and attaches the correct .2h file; should be something like mid_machaka.2h - age_nation.2h; pretender file, though
	# should be in \savedgames\newlords under datadir
	recipient = recipient_address
	try:
		with open(attachment_path, 'rb') as fp:
			msg = MIMEBase("application", "octet-stream")
			msg.set_payload(fp.read())
		encoders.encode_base64(msg)
		msg.add_header("Content-Disposition", "attachment", filename=os.path.basename(attachment_path))
		outer.attach(msg)
	except:
		print("Unable to open one of the attachments. Error: ", sys.exc_info()[0])
		raise
	
	composed = outer.as_string()
	
	# send to recipient (llamaserver) here
	try:
		with smtplib.SMTP('smtp.gmail.com', 587) as s:
			s.ehlo()
			s.starttls()
			s.ehlo()
			s.login(address, password)
			s.sendmail(address, recipient, composed)
			s.close()
		print("Email sent!")
	except:
		print("Unable to send the email. Error: ", sys.exc_info()[0])
		raise

mail = imaplib.IMAP4_SSL('imap.gmail.com') # possibly allow users to change that in config, for other email sources
try:
	mail.login(address, password)
except:
	print("Unexpected error:", sys.exc_info()[0])
	raise
	
mail.select("inbox") # possibly put this in config

outmail = smtplib.SMTP('smtp.gmail.com:587')
outmail.starttls()

# only gets the latest email in inbox (or other folder); if the latest e-mail is deleted or moved it'll go for the new latest e-mail
# though this is useful if we know the file for the turn is going to be the latest e-mail
# http://stackoverflow.com/questions/2983647/how-do-you-iterate-through-each-email-in-your-inbox-using-python has an example for iterating through a mailbox
result, data = mail.uid('search', None, "ALL") 
#latest_email_uid = data[0].split()[-1] # ditch the [-1], get list of mail IDs? Or do result, data already hold everything?
#raw_email = getEmail(latest_email_uid)
#parseMail(raw_email)

# gets all emails in the current mailbox; the inbox, in this case
email_uids = data[0].split()
for uid in email_uids:
	raw_email = getEmail(uid)
	parseMail(raw_email)

sendEmailWithAttachment(r"C:\Users\Rebecca\AppData\Roaming\Dominions4\savedgames\newlords\mid_ys_0.2h", "test_game", "rpaliwoda@googlemail.com")

# https://yuji.wordpress.com/2011/06/22/python-imaplib-imap-example-with-gmail/ mentions we need to do other stuff to get at the text of it. Not sure how to get at the attachment, as we may not care about the text