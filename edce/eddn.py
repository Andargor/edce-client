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
schemaVersion = 3

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
        
def postMarketData(data, system):
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
    
    # Issue 12: No market
    if "commodities" not in data:
        errstr = "Station must have a market, or no commodities found"
        raise edce.error.ErrorEDDN(errstr)
    
    try:
        utf8username = edce.util.convertUTF8(username)
        clientID = hashlib.sha224(utf8username.encode('utf-8')).hexdigest()
       
        if schemaVersion == 3:
            schema = 'https://eddn.edcd.io/schemas/commodity/3'
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
            message['message']['timestamp']         = datetime.datetime.utcnow().isoformat() + "Z"
            message['message']['systemName']        = system.strip()
            message['message']['stationName']       = data.name.strip()
            
            message['message']['commodities']       = []

            for commodity in data.commodities:           
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
