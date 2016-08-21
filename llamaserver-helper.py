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

# emails come from turns@llamaserver.net, always?

# may be able to make application handle more than one game simultaneously: dropdown list to select game, show details and controls for game?

# new config file for each game?
# shouldn't need to do this? Should just save data in a file somewhere

# data to store about games:
# name - necessary for finding game folder
# era - 'early', 'mid', 'late' - part of the generated file names, so necessary to know this to get the correct file
# nation - possibly needed to parse emails (nation name is mentioned in body), and is used in game file names; necessary as your nation may not be the only file present (also get allied nation files in server-based games)
# turn number - can get this from latest turn-email from llamaserver
# state - see above

# save old turns in a subfolder?
# delete old emails?

# command line menus:
# before making menus, display all games
# initial menu

import imaplib
import smtplib
import argparse
import configparser
import email
import os
import sys
import re
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart

# argparse stuff
# when the GUI is in, will probably want the option for logging, or to output stuff to the command line window
parser = argparse.ArgumentParser(description='Handles sending and receiving .2h files and .trn files to and from llamaserver, for Dominions PBEM games')
parser.add_argument('config', help='path to config file containing email, password and Dom4 data directory (see template)')
args = parser.parse_args()

# config parser stuff; uses the config file specified as an argument when launching the application
config = configparser.ConfigParser()
config.read(args.config)
address = config['Mail']['email']
password = config['Mail']['password']
datadir = config['Game']['datadir']
earlyNationsFile = config['Data']['early_nations']
midNationsFile = config['Data']['mid_nations']
lateNationsFile = config['Data']['late_nations']

# test using details to log in to email, first?

gameName = ""
nation = ""
era = ""
currentTurn = 0 # update this when we get a turn email

eras = {'early':'early', 'ea':'early', 'early age':'early', 'early ages':'early', 'mid':'mid', 'ma':'mid', 'middle age':'mid', 'middle ages':'mid', 'late':'late', 'la':'late', 'late age':'late', 'late ages':'late'}

# dicts setting up 'proper' nation names as used in save files
# these get their alias:nation name pairs from data files listed in the config file. By default these are pointed at files included with the application
earlyNations = {}
for line in open(earlyNationsFile, 'r'):
	alias, nationName = line.split(':')
	earlyNations[alias] = nationName.strip()
midNations = {}
for line in open(midNationsFile, 'r'):
	alias, nationName = line.split(':')
	midNations[alias] = nationName.strip()
lateNations = {}
for line in open(lateNationsFile, 'r'):
	alias, nationName = line.split(':')
	lateNations[alias] = nationName.strip()

# regex for matching text of pretender-confirmation email
# match groups, in order: nation, game name
pretender_reply_email_text_regex = re.compile(r"This is just to confirm that I've received a pretender file from you for (\w+) in the game (\w+), and everything seems to be fine with it\.", re.IGNORECASE)

# regex for matching subject of game-start email
# match group: game name
first_turn_email_subject_regex = re.compile(r"(\w+) started! First turn attached", re.IGNORECASE)

# regex for matching first-turn file email
# match groups, in order: turn due time, timezone, day, month, day-date, ordinal indicator
# the last probably isn't necessary but is hard to match otherwise?
#first_turn_email_text_regex = re.compile(r"Hello! The Dominions 4 game (\w+) has just started, and your first turn file is attached\. Please send your 2h file back to this address \(turns@llamaserver.net\)\. It doesn't matter what you put as the subject or in the message text\. If you want, you can zip the 2h file up first \(\.zip, \.rar or \.gz files are fine\)\. The first turn is due in by (\d\d:\d\d) (\w\w\w) on (Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday) (January|February|March|April|May|June|July|August|September|October|November|December) (\d+)(th|nd|rd|st)\.", re.IGNORECASE)
first_turn_email_text_regex = re.compile(r"The first turn is due in by (\d\d:\d\d) (\w\w\w) on (Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday) (January|February|March|April|May|June|July|August|September|October|November|December) (\d+)(th|nd|rd|st)\.", re.IGNORECASE)

# regex for matching subject of .trn file confirmation emails from llamaserver
# match groups, in order: game name, turn number, nation
turn_received_email_subject_regex = re.compile(r"(\w+): Turn (\d+) received for (\w+)", re.IGNORECASE)

# regex for matching subject of second and onwards .trn file emails from llamaserver
# match groups, in order: game name, nation, turn number
turn_file_email_subject_regex = re.compile(r"New turn file: (\w+), (\w+) turn (\d+)", re.IGNORECASE)

# regex for getting next turn deadline from second and onwards .trn file emails from llamaserver
# match groups, in order: turn due time, timezone, day, month, day-date, ordinal indicator
turn_file_email_text_regex = re.compile(r"The next 2h file is due in by (\d\d:\d\d) (\w\w\w) on (Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday) (January|February|March|April|May|June|July|August|September|October|November|December) (\d+)(th|nd|rd|st)")

def getGamesList(data_dir):
	games_list = []
	games_list = [os.path.basename(x[0]) for x in os.walk(os.path.join(data_dir, "savedgames"))]
	# remove guaranteed subfolders that aren't actually games
	games_list.remove("newlords")
	games_list.remove("savedgames")
	#print(games_list)
	return games_list

def getGameStatus(gameName):
	# for now this just returns 'unknown', but later on it should be able to determine game status (probably from emails?)
	return "unknown"
	
def listPretenders():
	pretenderPath = os.path.join(datadir, "savedgames", "newlords")
	# get all 2h files in here, put in list, return list
	return
	
def getPretender():
	return

def sendPretender(game, pretenderFile):
	pretenderPath = os.path.join(datadir, "savedgames", "newlords", pretenderFile)
	# in spite of checking isfile, still get an error if a wrong pretenderFfile name is supplied
	if os.path.isfile(pretenderPath):
		# send pretender file to pretenders@llamaserver.net
		sendEmail(game, "pretenders@llamaserver.net", pretenderPath)
	else:
		# error here; file doesn't exist (or can't be accessed)
		print("Error: file not found")
	return

def sendTurn(gameName, era, nation):
	#gameDir = os.path.join(datadir, "savedgames", gameName) # add 'era+"_"+nation+".2h"' to the end for full path to game, instead?
	# find correct 2h file here; don't forget game folder can contain more than one 2h, so we need to know nation to do this properly
	# name format is [early/mid/late]_[nation].2h but all 2h files present should have the same era prefix
	turnFile = os.path.join(datadir, "savedgames", gameName, era+"_"+nation+".2h")
	#print(turnFile)
	if os.path.isfile(turnFile):
		# send .2h file to turns@llamaserver.net
		sendEmail(gameName, "turns@llamaserver.net", turnFile)
	else:
		# error here; file doesn't exist (or can't be accessed)
		print("Error: file not found")
	return

# this can explode  if it can't connect
def getTurnFile(raw_email, game):
	email_message = email.message_from_bytes(raw_email)
	# create game folder if it doesn't exist?
	if not os.path.exists(os.path.join(datadir, "savedgames", game)):
		os.makedirs(os.path.join(datadir, "savedgames", game))
	# remove old old turn file
	if os.path.exists(os.path.join(datadir, "savedgames", game, era+"_"+nation+"_old.trn")):
		if os.path.isfile(os.path.join(datadir, "savedgames", game, era+"_"+nation+"_old.trn")):
			os.remove(os.path.join(datadir, "savedgames", game, era+"_"+nation+"_old.trn"))
	# rename previous turn file to old, if it exists
	if os.path.exists(os.path.join(datadir, "savedgames", game, era+"_"+nation+".trn")):
		if os.path.isfile(os.path.join(datadir, "savedgames", game, era+"_"+nation+".trn")):
			os.rename(os.path.join(datadir, "savedgames", game, era+"_"+nation+".trn"), os.path.join(datadir, "savedgames", game, era+"_"+nation+"_old.trn"))
	# get new turn file from email
	saveAttachment(email_message, os.path.join(datadir, "savedgames", game))

def getLatestTurn(gameName):
	mail.select("inbox")
	result, data = mail.uid('search', None, 'SUBJECT "turn" SUBJECT "' + gameName + '" NOT SUBJECT "received"') # might return other games with the given name as a partial part of the other game's name?
	email_uids = data[0].split()
	# we get emails in order earliest to latest, so email_uids[-1] should always be the latest email found
	latest_uid = email_uids[-1]
	# get attachment and copy attachment to game folder
	raw_email = getEmail(latest_uid)
	# prints name of email it'll get the attachment from
	print(getSubject(raw_email))
	return getTurnFile(raw_email, gameName)

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
	#if email_message['To'] is not None:
	# only check emails from llamaserver: all llamaserver emails come from turns@llamaserver.net
	if email.utils.parseaddr(email_message['From'])[1] == 'turns@llamaserver.net': 
		email_to = email_message['To']
		email_from = email.utils.parseaddr(email_message['From']) # for parsing "Yuji Tomita" <yuji@grovemade.com>
		email_subject = email_message['Subject']
		email_text = get_first_text_block(email_message)
	# should this return the to/from/subject/text details, or should it branch out and do stuff depending on email content?
	# I think it should do stuff; use regex to check type
	return

# function mostly just for testing, here
def printMail(raw_email):
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
	return

def getSubject(raw_email):
	email_message = email.message_from_bytes(raw_email)
	return email_message['Subject']
	
def sendEmail(subject, recipient_address, attachment_path=None):
	# attachment_path: full path
	# subject: needs to be the game name, for at least pretender
	# recipient address: pretenders@llamaserver.net for pretenders, turns@llamaserver.net for turns
	# create email here
	outer = MIMEMultipart()
	outer['From'] = address
	outer['To'] = recipient_address
	outer['Subject'] = subject # needs to be game name, for pretender file; for turn 2h files apparently doesn't matter
	# make sure it gets and attaches the correct .2h file; should be something like mid_machaka.2h - age_nation.2h; pretender file, though
	# should be in \savedgames\newlords under datadir
	recipient = recipient_address
	if attachment_path is not None:
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
	
	# send to recipient here
	try:
		with smtplib.SMTP('smtp.gmail.com', 587) as s:
			s.starttls()
			s.login(address, password)
			s.sendmail(address, recipient, composed)
			s.close()
		print("Email sent!")
	except:
		print("Unable to send the email. Error: ", sys.exc_info()[0])
		raise

def saveAttachment(msg, download_folder="/tmp"):
	# from http://stackoverflow.com/questions/6225763/downloading-multiple-attachments-using-imaplib
	att_path = "No attachment found."
	for part in msg.walk():
		if part.get_content_maintype() == 'multipart':
			continue
		if part.get('Content-Disposition') is None:
			continue

		filename = part.get_filename()
		att_path = os.path.join(download_folder, filename)

		if not os.path.isfile(att_path):
			fp = open(att_path, 'wb')
			fp.write(part.get_payload(decode=True))
			fp.close()
	return att_path
	
def setEra(tempEra):
	if tempEra != "":
		global era
		if tempEra.lower() in eras:
			era = eras[tempEra.lower()]

def setNation(tempNation):
	if tempNation != "":
		global nation
		global earlyNations
		global midNations
		global lateNations
		# sanity-check based on dicts populated at beginning
		if era == 'early':
			if tempNation.lower() in earlyNations:
				nation = earlyNations[tempNation.lower()]
		elif era == 'mid':
			if tempNation.lower() in midNations:
				nation = midNations[tempNation.lower()]
		elif era == 'late':
			if tempNation.lower() in lateNations:
				nation = lateNations[tempNation.lower()]

def setGameName(tempGameName):
	if tempGameName != "":
		global gameName
		# sanity checks here - replace spaces with _s
		# is there anything else llamaserver and/or dom4 enforce in game names?
		gameName = tempGameName

mail = imaplib.IMAP4_SSL('imap.gmail.com', 993) # possibly allow users to change that in config, for other email sources
try:
	mail.login(address, password)
except:
	print("Unexpected error:", sys.exc_info()[0])
	raise
	
mail.select("inbox") # possibly put the mailbox to use in config

while True:
	if gameName == "" or era == "" or nation == "":
		if gameName == "":
			tempName = input("Game name: ")
			setGameName(tempName)
		if era == "":
			tempEra = input("Era (early/mid/late): ")
			setEra(tempEra)
		if nation == "":
			tempNation = input("Nation: ")
			setNation(tempNation)
	else:
		print("\nCurrently managing game:", gameName)
		print("Era:", era)
		print("Nation:", nation, "\n")
		print("1. Get latest .trn file from inbox (" + address + ")")
		print("2. Send .2h turn file to llamaserver")
		print("3. Send pretender to llamaserver")
		print("4. Change managed game")
		print("0. Quit\n")
		option = input("> ")
		if option == "0":
			quit()
		elif option == "1": # get latest .trn
			getLatestTurn(gameName)
		elif option == "2": # send latest 2h
			sendTurn(gameName, era, nation)
		elif option == "3": # send pretender
			pretenderFile = input("Pretender file name? ")
			sendPretender(gameName, pretenderFile)
		elif option == "4":
			print("Press return without entering anything to keep current value")
			tempName = input("New game name: ")
			setGameName(tempName)
			tempEra = input("Era (early/mid/late): ")
			setEra(tempEra)
			tempNation = input("Nation: ")
			setNation(tempNation)

# usage notes:
# sending pretender files works
# sending .2h files works
# getting latest .trn file works; problem was python didn't want to overwrite the existing one, despite 'wb' apparently doing that normally?
# mostly works; gmail seems to return previous turn as latest sometimes?
# solved: needed to reselect mailbox first
# falls over more often, now, though
# solved: didn't like that I hadn't specified a port, for some reason

# may not be creating folders for new games, in some circumstances? Jant reported an issue but it worked the next time he tried, to get the error text
# make pretenders submenu, with list pretenders and send pretender options