import sys
import edce.config

if sys.version_info.major < 3:
	print("You need to use Python 3.x, e.g. python3 <filename>")
	exit()

import edce.util
import json
from collections import OrderedDict

def alignStr(title, word):
    return "{:<40s}{:<40s}".format(title, word)

def alignNum(title, number):
    return "{:<40s}{:<40d}".format(title, number)	

player_json = ''
try:
	with open(edce.config.getString('paths', 'last_file'), "r") as f:
			player_json = f.readline()
			f.close()
except:
	"Please run edce_client.py at least once, so that it may create a last.json file."
	exit()
		
data = edce.util.edict(player_json)

station = ""
if data.commander.docked:
	station = "/" + data.lastStarport.name
	
print(alignStr("CMDR:",data.commander.name))
print(alignStr("System:",data.lastSystem.name + station))
print(alignNum("Credits:",data.commander.credits))

if "ship" in data:
	print(alignStr("Ship:",data.ship.name))

if "ships" in data:
	print("\n========== All ships: ==========")
	
	all_ships = {}
	for ship in data.ships:
		station = data.ships[ship].starsystem.name + "/" + data.ships[ship].station.name
		if not station in all_ships:
			all_ships[station]=[]
		all_ships[station].append(data.ships[ship].name)

	for s in OrderedDict(sorted(all_ships.items())):
		print(alignStr(s,", ".join(all_ships[s])))
		
if "stats" in data and "explore" in data.stats and "lastVisitedStarSystems" in data.stats.explore:
	print("\n========== Last Visited: ==========")
	for s in data.stats.explore.lastVisitedStarSystems:
		print(s)
