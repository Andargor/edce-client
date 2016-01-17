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

try:
	res = edce.query.performQuery()
		
	data = edce.util.edict(res)
	edce.util.writeJSONLog(data.commander.name,data.lastSystem.name,data)
	
	station = ""
	if data.commander.docked:
		station = "/" + data.lastStarport.name
	print("CMDR:\t" + data.commander.name)
	print("System:\t" + data.lastSystem.name + station)

	if "ship" in data:
		print("Ship:\t" + data.ship.name)
	
	if edce.config.getString('preferences','enable_eddn').lower().find('y') >= 0:
		if data.commander.docked:
			print("Attempting to post market data to EDDN, this may take a minute...")
			edce.eddn.postMarketData(data)
			print("Done.")
	
except edce.error.Error as e:
	print("EDCE: " + e.message)
except:
	print("Unexpected error:", sys.exc_info()[0])
	raise


