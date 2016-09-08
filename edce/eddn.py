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

testSchema = False
schemaVersion = 2

def convertCategoryEDDN(name):
    commoditiesCategory                 = {}
    commoditiesCategory['Narcotics']    = 'Legal Drugs'
    commoditiesCategory['Slaves']       = 'Slavery'
    
    if name in commoditiesCategory:
        return commoditiesCategory[name]
    
    return name


def convertCommodityEDDN(name):
    commodities                                 = {}
    
    commodities['Agricultural Medicines']       = 'Agri-Medicines'
    commodities['Atmospheric Extractors']       = 'Atmospheric Processors'
    commodities['Auto Fabricators']             = 'Auto-Fabricators'
    commodities['Basic Narcotics']              = 'Narcotics' #Issue #4
    commodities['Bio Reducing Lichen']          = 'Bioreducing Lichen' #Issue #4
    commodities['Hazardous Environment Suits']  = 'H.E. Suits'
    commodities['Heliostatic Furnaces']         = 'Microbial Furnaces'
    commodities['Marine Supplies']              = 'Marine Equipment'
    commodities['Non Lethal Weapons']           = 'Non-lethal Weapons'
    commodities['S A P8 Core Container']        = 'SAP 8 Core Container'
    commodities['Terrain Enrichment Systems']   = 'Land Enrichment Systems'
    
    if name in commodities:
        return commodities[name]
    
    return name

    
def submitEDDN(data):
    if edce.globals.debug:
        print(">>>>>>>>>>>>>>>> submitEDDN")
    url = edce.config.getString('urls','url_eddn')
    headers = { 'content-type' : 'application/json; charset=utf8' }
    r = requests.post(url, data=json.dumps(data, ensure_ascii=False).encode('utf8'), verify=True)
    if r.status_code == requests.codes.ok:
        return r.text
    else:
        errstr = "Status Code %s error: %s" % (r.status_code, r.text)
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

    enable = edce.config.getString('preferences','enable_eddn')
    if enable.lower() != 'yes':
        errstr = "EDDN is disabled in edce.ini"
        raise edce.error.ErrorEDDN(errstr)        
        
    username=edce.config.getString('login','username')
    if username == '':
        errstr = "No username"
        raise edce.error.ErrorEDDN(errstr)
    
    if "docked" in data.commander and data.commander.docked:
        pass
    else:
        errstr = "Pilot must be docked"
        raise edce.error.ErrorEDDN(errstr)
    
    # Issue 12: No market
    if "commodities" not in data.lastStarport:
        errstr = "Station must have a market"
        raise edce.error.ErrorEDDN(errstr)
    
    try:
        utf8username = edce.util.convertUTF8(username)
        clientID = hashlib.sha224(utf8username.encode('utf-8')).hexdigest()
       
        if schemaVersion == 2:
            schema = 'http://schemas.elite-markets.net/eddn/commodity/2'
            if testSchema:
                schema = schema + '/test'
            
            if edce.globals.debug:
                print("Using schema " + schema)            
            
            message                                 = {}
            message['$schemaRef']                   = schema
            
            message['header']                       = {}
            message['header']['softwareVersion']    = edce.globals.version.strip()
            message['header']['softwareName']       = edce.globals.name.strip()
            message['header']['uploaderID']         = clientID
            
            message['message']                      = {}
            message['message']['timestamp']         = datetime.datetime.utcnow().isoformat()
            message['message']['systemName']        = data.lastSystem.name.strip()
            message['message']['stationName']       = data.lastStarport.name.strip()
            
            message['message']['commodities']       = []
                 
            for commodity in data.lastStarport.commodities:
                tmpCommodity = {}
            
                if "categoryname" in commodity and commodity.categoryname != "NonMarketable" and commodity.stockBracket != '' and commodity.demandBracket != '':
                    tmpCommodity["name"]        = convertCommodityEDDN(commodity.name.strip()).strip()
                    
                    tmpCommodity["buyPrice"]    = math.floor(commodity.buyPrice)
                    tmpCommodity["sellPrice"]   = math.floor(commodity.sellPrice)
                                
                    tmpCommodity["supply"]      = commodity.stockBracket and math.floor(commodity.stock)
                    if commodity.stockBracket > 0:
                        tmpCommodity['supplyLevel'] = getBracket(commodity.stockBracket)
                            
                    tmpCommodity["demand"]      = commodity.demandBracket and math.floor(commodity.demand)
                    if commodity.demandBracket > 0:
                        tmpCommodity['demandLevel'] = getBracket(commodity.demandBracket)
                        
                    message['message']['commodities'].append(tmpCommodity)
                        
                else:
                    if edce.globals.debug:
                        print(">>>>>>>>>>>>>>>> postMarketData skipped " + commodity.name)
                        
                del tmpCommodity

        elif schemaVersion == 3:
            schema = 'http://schemas.elite-markets.net/eddn/commodity/3'
            if testSchema:
                schema = schema + '/test'
            
            if edce.globals.debug:
                print("Using schema " + schema)            
            
            message                                 = {}
            message['$schemaRef']                   = schema
            
            message['header']                       = {}
            message['header']['softwareVersion']    = edce.globals.version.strip()
            message['header']['softwareName']       = edce.globals.name.strip()
            message['header']['uploaderID']         = clientID
            
            message['message']                      = {}
            message['message']['timestamp']         = datetime.datetime.utcnow().isoformat()
            message['message']['systemName']        = data.lastSystem.name.strip()
            message['message']['stationName']       = data.lastStarport.name.strip()
            
            message['message']['commodities']       = []
                 
            for commodity in data.lastStarport.commodities:           
                tmpCommodity = {}
                
                if "categoryname" in commodity and commodity.categoryname != "NonMarketable" and commodity.stockBracket != '' and commodity.demandBracket != '':
                    tmpCommodity["name"] = commodity.name
                    tmpCommodity["meanPrice"] = int(commodity.meanPrice)
                    tmpCommodity["buyPrice"] = int(commodity.buyPrice)
                    tmpCommodity["stock"] = int(commodity.stock)
                    tmpCommodity["stockBracket"] = commodity.stockBracket
                    tmpCommodity["sellPrice"] = int(commodity.sellPrice)
                    tmpCommodity["demand"] = int(commodity.demand)
                    tmpCommodity["demandBracket"] = commodity.demandBracket
                    
                    if len(commodity.statusFlags) > 0:
                        tmpCommodity["statusFlags"] = commodity.statusFlags                
                
                    message['message']['commodities'].append(tmpCommodity)
                else:
                    if edce.globals.debug:
                        print(">>>>>>>>>>>>>>>> postMarketData skipped " + commodity.name)

                del tmpCommodity
                
        else:
            errstr = "Invalid schema version"
            raise edce.error.ErrorEDDN(errstr)

        submitEDDN(message)
     
    except Exception as error:
        errstr = "Error: EDDN postMarketData FAIL submit error: %s " % error
        raise edce.error.ErrorEDDN(errstr)
