import sys
if sys.version_info.major < 3:
	print("You need to use Python 3.x, e.g. python3 <filename>")
	exit()

import configparser
import getpass
import edce.error

Config = configparser.ConfigParser()
Config.read('edce.ini')

def ConfigSectionMap(section):
	dict1 = {}
	try:
		options = Config.options(section)
		for option in options:
			try:
				dict1[option] = Config.get(section, option)
				if dict1[option] == -1:
					DebugPrint("skip: %s" % option)
			except:
				print("exception on %s!" % option)
				dict1[option] = None
				raise edce.error.ErrorConfig('Please run client-setup.py to generate the configuration file.')
	except:
		raise edce.error.ErrorConfig('Please run client-setup.py to generate the configuration file.')
	return dict1

def performSetup():
	username = input("Username (leave empty to be prompted at runtime): ").strip()
	password = getpass.getpass('Password (leave empty to be prompted at runtime): ').strip()
	enableEDDN = input("Send market data to EDDN. No private information is sent. [Y/n]: ").strip().lower()
		
	Config = configparser.ConfigParser()
	
	Config.add_section('login')
	Config.set('login','username',username)
	Config.set('login','password',password)

	Config.add_section('urls')
	Config.set('urls','url_login','https://companion.orerve.net/user/login')
	Config.set('urls','url_verification','https://companion.orerve.net/user/confirm')
	Config.set('urls','url_profile','https://companion.orerve.net/profile')
	Config.set('urls','url_eddn','http://eddn-gateway.elite-markets.net:8080/upload/')

	Config.add_section('preferences')
	if enableEDDN == '' or enableEDDN == 'y':
		Config.set('preferences','enable_eddn','Yes')
	else:
		Config.set('preferences','enable_eddn','No')
	
	cfgfile = open('edce.ini','w')
	Config.write(cfgfile)
	cfgfile.close()

	print("Setup complete. edce.ini written.")
	print("**NOTE: Your username and password are not stored encrypted. Make sure this file is protected.")