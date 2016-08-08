# push button, send pretender to llamaserver
# push button, send turn to llamaserver
# push button, pull turnfile from GMail?
# also check for turn file emails or other stuff from GMail
# llamaserver details: http://z7.invisionfree.com/Dom3mods/index.php?showtopic=1890

# https://docs.python.org/3/library/imaplib.html
# https://www.reddit.com/r/learnpython/comments/3u39i0/is_sending_emails_with_gmail_supported_with/
# https://support.google.com/mail/troubleshooter/1668960?hl=en-GB&rd=1
# https://yuji.wordpress.com/2011/06/22/python-imaplib-imap-example-with-gmail/
# http://naelshiab.com/tutorial-send-email-python/ - includes how to send email with attachment

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

# may be able to make application handle more than one game simultaneously: dropdown list to select game, show details and controls for game?

# new config file for each game?

import imaplib
import smtplib
import configparser
import email
#from email.MIMEMultipart import MIMEMultipart # gets error, 'No module named email.MIMEMultipart'
#from email.MIMEText import MIMEText
#from email.MIMEBase import MIMEBase
#from email import encoders

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
	
def getMail():
	return

def parseMail(raw_email):
	email_message = email.message_from_bytes(raw_email)
	if email_message['To'] is not None:
		email_to = email_message['To']
		email_from = email.utils.parseaddr(email_message['From']) # for parsing "Yuji Tomita" <yuji@grovemade.com>
		email_subject = email_message['Subject']
		email_text = get_first_text_block(email_message)
		print(email_to)
		print(email_from)
		print(email_subject)
		print(email_text)
		#for textblock in getTextBlocks(email_message):
		#	print(textblock)
		print('-----')
	# should obviously do other things, here, but for now it's nice it iterates through
	return
	
def listPretenders():
	return
	
def getPretender():
	return
	
def sendPretender():
	try:
		outmail.login(email, password)
	except:
		print("Unexpected error:", sys.exc_info()[0])
		raise
	# create email here
	msg = MIMEMultipart()
	msg['From'] = address
	msg['To'] = 'pretenders@llamaserver.net'
	msg['Subject'] = "SUBJECT OF THE EMAIL" # needs to be game name
	# make sure it gets and attaches the correct .2h file; should be something like mid_machaka.2h - age_nation.2h; pretender file, though
	# should be in \savedgames\newlords under datadir
	# send to llamaserver here
	outmail.quit()
	return
	
def sendTurn():
	try:
		outmail.login(email, password)
	except:
		print("Unexpected error:", sys.exc_info()[0])
		raise
	# create email here; subject needs to be game name
	msg = MIMEMultipart()
	msg['From'] = address
	msg['To'] = 'turns@llamaserver.net'
	msg['Subject'] = "SUBJECT OF THE EMAIL" # needs to be game name
	# make sure it gets and attaches the correct .2h file; should be something like mid_machaka.2h - age_nation.2h
	# should be in \savedgames\game_name under datadir
	# send to llamaserver here
	outmail.quit()
	return

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
latest_email_uid = data[0].split()[-1] # ditch the [-1], get list of mail IDs? Or do result, data already hold everything?
result, data = mail.uid('fetch', latest_email_uid, '(RFC822)')
#print(result) # 'OK'
#for thing in data:
#	print(thing)
# (b'1 (UID 5 RFC822 {3332}', text of email 
# b')'
raw_email = data[0][1]
parseMail(raw_email)

# https://yuji.wordpress.com/2011/06/22/python-imaplib-imap-example-with-gmail/ mentions we need to do other stuff to get at the text of it. Not sure how to get at the attachment, as we may not care about the text