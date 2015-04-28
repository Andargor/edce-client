import sys
if sys.version_info.major < 3:
	print("You need to use Python 3.x, e.g. python3 <filename>")
	exit()

import json	
import datetime
import lzma

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

def writeLog(data):
	logfile = "log/edce-{:%Y%m%d%H%M%S}.xz".format(datetime.datetime.utcnow())
	with lzma.open(logfile, "w") as f:
		f.write(bytes(data, 'UTF-8'))