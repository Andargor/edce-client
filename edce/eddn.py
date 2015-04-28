import sys
if sys.version_info.major < 3:
	print("You need to use Python 3.x, e.g. python3 <filename>")
	exit()

import json	
import hashlib
import time
import datetime
import requests
import math

import edce.config
import edce.globals
import edce.error

def submitEDDN(data):
	if edce.globals.debug:
		print(">>>>>>>>>>>>>>>> submitEDDN")
	url = edce.config.ConfigSectionMap('urls')['url_eddn']
	headers = { 'content-type' : 'application/json; charset=utf8' }
	r = requests.post(url, data=json.dumps(data), verify=True)
	if r.status_code == requests.codes.ok:
		return r.text
	else:
		errstr = "Error: EDDN submitEDDN FAIL %s" % r.status_code
		raise edce.error.ErrorEDDN(errstr)	

def getBracket(level):
	if level == 1:
		return "Low"
	elif level == 2:
		return "Med"
	elif level == 3:
		return "High"
	return ""
		
def postMarketData(data):
	if edce.globals.debug:
		print(">>>>>>>>>>>>>>>> postMarketData")

	enable = edce.config.ConfigSectionMap('preferences')['enable_eddn']
	if enable.lower() != 'yes':
		errstr = "Error: EDDN postMarketData FAIL, EDDN is disabled in edce.ini"
		raise edce.error.ErrorEDDN(errstr)		
		
	username=edce.config.ConfigSectionMap('login')['username']
	if username == '':
		errstr = "Error: EDDN postMarketData FAIL no username"
		raise edce.error.ErrorEDDN(errstr)
	
	if "docked" in data.commander and data.commander.docked:
		pass
	else:
		errstr = "Error: EDDN postMarketData FAIL pilot must be docked"
		raise edce.error.ErrorEDDN(errstr)
	
	try:
		clientID = hashlib.sha224(username.encode('utf-8')).hexdigest()
		st = datetime.datetime.utcnow().isoformat()
		system = data.lastSystem.name
		station = data.lastStarport.name
		
		for commodity in data.lastStarport.commodities:
			message = {"header": {"softwareVersion": edce.globals.version, "softwareName": edce.globals.name, "uploaderID": clientID}, "$schemaRef": "http://schemas.elite-markets.net/eddn/commodity/1/test", "message": {"buyPrice": math.floor(commodity.buyPrice), "timestamp": st, "stationStock": math.floor(commodity.stock), "systemName": system, "stationName": station, "demand":  math.floor(commodity.demand), "sellPrice": math.floor(commodity.sellPrice), "itemName": commodity.name}}
			if commodity.demandBracket > 0:
				message['message']['demandLevel'] = getBracket(commodity.demandBracket)
			elif commodity.stockBracket > 0:
				message['message']['supplyLevel'] = getBracket(commodity.stockBracket)
			submitEDDN(message)
	except:
		errstr = "Error: EDDN postMarketData FAIL submit error"
		raise edce.error.ErrorEDDN(errstr)
		


