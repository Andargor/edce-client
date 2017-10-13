import sys
if sys.version_info.major < 3:
	print("You need to use Python 3.x, e.g. python3 <filename>")
	exit()

import configparser
import edce.query
import edce.error
import edce.util
import edce.eddn
import edce.config
import edce.globals

import json

edce.globals.interactive = True
edce.globals.debug = False
edce.eddn.testSchema = False
edce.eddn.schemaVersion = 3

try:
#New for cAPI 2.4, will perform three queries and combine them in one string
#New paths data.commander -> data.profile.commander

	res = edce.query.performQuery()
		
	data = edce.util.edict(res)
	edce.util.writeJSONLog(data.profile.commander.name,data.profile.lastSystem.name,data)
	
	station = ""
	if data.profile.commander.docked:
		station = "/" + data.profile.lastStarport.name
	print("CMDR:\t" + data.profile.commander.name)
	print("System:\t" + data.profile.lastSystem.name + station)

	if "ship" in data.profile:
		if "shipName" in data.profile.ship:
			print("Ship:\t" + data.profile.ship.shipName + " (" + data.profile.ship.name + ")")
		else:
			print("Ship:\t" + data.profile.ship.name)
	
	if edce.config.getString('preferences','enable_eddn').lower().find('y') >= 0:
		if data.profile.commander.docked:
			print("Attempting to post market data to EDDN, this may take a minute...")
			edce.eddn.postMarketData(data.market, data.profile.lastSystem.name)
			print("Done.")
	
except edce.error.Error as e:
	print("EDCE: " + e.message)
except:
	print("Unexpected error:", sys.exc_info()[0])
	raise


