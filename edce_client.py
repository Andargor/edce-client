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

try:
	res = edce.query.performQuery()
	edce.util.writeLog(res)
	
	json_res = edce.util.edict(res)
	shipId = "%s" % json_res.commander.currentShipId
	station = ""
	if json_res.commander.docked:
		station = " Last Station: " + json_res.lastStarport.name
	print("CMDR: " + json_res.commander.name + " System: " + json_res.lastSystem.name + station + " Ship: " + json_res.ships[shipId].name)
	
	print("Attempting to post market data to EDDN...")
	edce.eddn.postMarketData(json_res)
	print("Done.")
	
except edce.error.Error as e:
	print("EDCE: " + e.message)
except:
	print("Unexpected error:", sys.exc_info()[0])
	raise


