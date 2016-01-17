import sys
if sys.version_info.major < 3:
	print("You need to use Python 3.x, e.g. python3 <filename>")
	exit()

import json	
import datetime
import lzma
import edce.error

class edict(dict):
    # based on class dotdict(dict):  # from http://stackoverflow.com/questions/224026/dot-notation-for-dictionary-keys
    
    __setattr__= dict.__setitem__
    __delattr__= dict.__delitem__
 
    def __init__(self, data):
        if type(data) == str:
            data = json.loads( data)
        for name, value in data.items():
            setattr(self, name, self._wrap(value))
 
    def __getattr__(self, attr):
        return self.get(attr, None)
 
    def _wrap(self, value):  # from class Struct by XEye '11 http://stackoverflow.com/questions/1305532/convert-python-dict-to-object
        if isinstance(value, (tuple, list, set, frozenset)):
            return type(value)([self._wrap(v) for v in value])  # recursion!
        else:
            if isinstance(value, dict):
                return edict(value)  # is there a relative way to get class name?
            else:
                return value

def convertUTF8(str):
	if edce.globals.debug:
		print(">>>>>>>>>>>>>>>> convertUTF8")

	try:
		str.decode('utf-8')
		return str
	except AttributeError:
		return str
	except UnicodeError:
		return str.encode('utf-8')
	except UnicodeEncodeError:
		return str.encode('utf-8')
				
def writeUTF8(filename, data, compress=False):
	if edce.globals.debug:
		print(">>>>>>>>>>>>>>>> writeUTF8 " + filename)

	try:
		utf8filename = convertUTF8(filename)
		utf8data = convertUTF8(data)
		if compress:
			with lzma.open(utf8filename, "wb") as f:
				f.write(utf8data)
				f.close()
		else:
			with open(utf8filename, "w", encoding='utf8') as f:
				f.write(bytes(data, "utf-8").decode("unicode_escape"))
				f.close()			
	except:
		errstr = "Error: writeUTF8 FAIL"
		raise edce.error.ErrorLog(errstr)				
				
def writeJSONLog(name,system,data):
	if edce.globals.debug:
		print(">>>>>>>>>>>>>>>> writeJSONLog")

	try:
		logfile = "log/edce-{n}-{s}-{d:%Y%m%d%H%M%S}.xz".format(n=name, s=system, d=datetime.datetime.utcnow())
		writeUTF8(logfile, json.dumps(data, ensure_ascii=False).encode('utf8'), True)
	except:
		errstr = "Error: writeJSONLog FAIL"
		raise edce.error.ErrorLog(errstr)
