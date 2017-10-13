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
if data.profile.commander.docked:
    station = "/" + data.profile.lastStarport.name
    
print(alignStr("CMDR:",data.profile.commander.name))
print(alignStr("System:",data.profile.lastSystem.name + station))
print(alignNum("Credits:",data.profile.commander.credits))

if "ship" in data.profile:
    print(alignStr("Ship:",data.profile.ship.name))

if "ships" in data.profile:
    print("\n========== All ships: ==========")
    
    all_ships = {}
    for ship, shipEntry in data.profile.ships.items():
        starsystem = shipEntry.starsystem
        starsystem_station = shipEntry.station
        if starsystem and starsystem_station:
            station = starsystem.name + "/" + starsystem_station.name
            if not station in all_ships:
                all_ships[station]=[]
            
            all_ships[station].append(shipEntry.name)

    for s in OrderedDict(sorted(all_ships.items())):
        print(alignStr(s,", ".join(all_ships[s])))
        
if "stats" in data and "explore" in data.profile.stats and "lastVisitedStarSystems" in data.profile.stats.explore:
    print("\n========== Last Visited: ==========")
    for s in data.profile.stats.explore.lastVisitedStarSystems:
        print(s)
