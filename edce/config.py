import sys
if sys.version_info.major < 3:
	print("You need to use Python 3.x, e.g. python3 <filename>")
	exit()

import configparser
import getpass
import edce.error

Config = configparser.RawConfigParser()
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

def getString(section, key):
	res = ''
	try:
		res = edce.config.ConfigSectionMap(section)[key]
	except:
		raise edce.error.ErrorConfig('Please run client-setup.py to generate the configuration file.')	
	return res
	
def performSetup():
	print("Enter your Frontier Store credentials here. You can leave your username or password empty, however you will be prompted every time you run the edce_client.py script.")
	username = input("Frontier Store Username: ").strip()
	password = getpass.getpass('Frontier Store Password: ').strip()
	enableEDDN = input("Send market data to EDDN. No private information is sent. [Y/n]: ").strip().lower()
		
	Config = configparser.RawConfigParser()
	
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