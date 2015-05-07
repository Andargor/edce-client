import sys
if sys.version_info.major < 3:
	print("You need to use Python 3.x, e.g. python3 <filename>")
	exit()

import configparser
import requests
import json
import getpass
import time
import math

from http.cookiejar import LWPCookieJar

import edce.error
import edce.config
import edce.globals
import edce.util


# This is hardcoded to be nice with the FD server
minimumDelay = 120

def checkInteractive():
	ok = True
	try:
		if edce.globals.interactive == False:
			if edce.config.getString('login','username') == '' or edce.config.getString('login','password') == '':
				ok = False
	except:
		ok = False
	if not ok:
		raise edce.error.Error('Cannot run in non-interactive mode if either the username or password is not set. Set edce.globals.interactive=True, or run setup.py and enter a username and password')

def submitProfile(s):
	if edce.globals.debug:
		print(">>>>>>>>>>>>>>>> submitProfile")
	url = edce.config.getString('urls','url_profile')
	r = s.get(url, verify=True)
	if r.status_code == requests.codes.ok:
		s.cookies.save()
		return r.text
	else:
		errstr = "Error: submitProfile FAIL %s" % r.status_code
		if edce.globals.debug and edce.globals.interactive:
			print(errstr)
		raise edce.error.ErrorProfile(errstr)

def submitLogin(s, u, p):
	if edce.globals.debug:
		print(">>>>>>>>>>>>>>>> submitLogin")
	url = edce.config.getString('urls','url_login')
	payload = { 'email' : u, 'password' : p }
	r = s.post(url, data=payload, verify=True)
	if r.status_code == requests.codes.ok:
		s.cookies.save()
		return r.text
	else:
		errstr = "Error: submitLogin FAIL %s" % r.status_code
		if edce.globals.debug and edce.globals.interactive:
			print(errstr)
		raise edce.error.ErrorLogin(errstr)
		
		
def submitVerification(s):
	if edce.globals.debug:
		print(">>>>>>>>>>>>>>>> submitVerification")
	code_raw = input("Verification Code required. You will receive an email from Frontier with a code in it. Enter it here: ")
	code = code_raw.strip()
	
	if code:
		url = edce.config.getString('urls','url_verification')
		payload = { 'code' : code }
		r = s.post(url, data=payload, verify=True)
		if r.status_code == requests.codes.ok:
			s.cookies.save()
			return r.text
		else:
			errstr = "Error: submitVerification FAIL %s" % r.status_code
			if edce.globals.debug and edce.globals.interactive:
				print(errstr)
			raise edce.error.ErrorVerification(errstr)					
	else:
		errstr = "Error: You must input a code. submitVerification FAIL %s" % r.status_code
		if edce.globals.debug and edce.globals.interactive:
			print(errstr)
		raise edce.error.ErrorVerification(errstr)		

def checkLogin(data):
	if data:
		if data.find("Password")>=0:
			return True
	else:
		return False
		
def checkProfileData(data):
	if data:
		if data.find("commander")>=0:
			return True
	else:
		return False

def checkRequireVerification(data):
	if data:
		if data.find("verification code")>=0:
			return True
	else:
		return False		

def initSession():
	if edce.globals.debug:
		print(">>>>>>>>>>>>>>>> initSession")
		
	cookie_filename = "cookies.txt"

	session = requests.Session()
	session.headers['User-Agent'] = 'Mozilla/5.0 (iPhone; CPU iPhone OS 7_1_2 like Mac OS X) AppleWebKit/537.51.2 (KHTML, like Gecko) Mobile/11D257'
	
	session.cookies = LWPCookieJar(cookie_filename)
	try:
		session.cookies.load(ignore_discard=True)
	except FileNotFoundError:
		session.cookies.save()

	return session
		
def readQueryTime():
	try:
		with open("last.time", "r") as f:
			t = int(f.readline())
			f.close()
			if edce.globals.debug:
				print(">>>>>>>>>>>>>>>> readQueryTime %s" % t)			
			return t
	except FileNotFoundError:
		pass
	return 0
		
def performQuery(s=None):
	if edce.globals.debug:
		print(">>>>>>>>>>>>>>>> performQuery")

	# This is to be nice with FD servers
	t = readQueryTime()
	delta = time.time() - t
	if delta <= minimumDelay:
		errstr = "Error: To avoid overloading the FD servers, you must wait %s seconds before your next query" % math.floor(minimumDelay - delta)
		if edce.globals.debug and edce.globals.interactive:
			print(errstr)
		raise edce.error.ErrorQueryTimeout(errstr)			
		
	session = s
	
	if session is None:
		session = initSession()
	
	username=edce.config.getString('login','username')
	password=edce.config.getString('login','password')	
	
	checkInteractive()
	
	if edce.globals.interactive == True:
		if username.strip() == '':
			username = input("Username: ").strip()
		if password.strip() == '':
			password = getpass.getpass('Password: ').strip()
		if username  == '' or password  == '':
			errstr = "Error: No username or password specified."
			if edce.globals.debug and edce.globals.interactive:
				print(errstr)		
			raise edce.error.ErrorQuery(errstr)			
	
	res = submitLogin(session, username, password)
	if checkRequireVerification(res):	
		submitVerification(session)
		res = submitLogin(session, username, password)
		if checkRequireVerification(res):
			errstr = "Error: Verification failed."
			if edce.globals.debug and edce.globals.interactive:
				print(errstr)		
			raise edce.error.ErrorQuery(errstr)				
	
	if checkLogin(res):	
		errstr = "Error: Invalid login credentials."
		if edce.globals.debug and edce.globals.interactive:
			print(errstr)		
		raise edce.error.ErrorQuery(errstr)			
	
	res = submitProfile(session)

	if checkProfileData(res):
		utf8res = edce.util.convertUTF8(res)
		edce.util.writeUTF8("last.json",utf8res)
		edce.util.writeUTF8("last.time","%d" % time.time())
		return utf8res

