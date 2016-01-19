import sys
if sys.version_info.major < 3:
	print("You need to use Python 3.x, e.g. python3 <filename>")
	exit()

class Error(Exception):
	def __init__(self, message):
		self.message = message
	def __str__(self):
		return repr(self.message)

class ErrorConfig(Error):
	pass		
		
class ErrorQuery(Error):
	pass

class ErrorQueryTimeout(Error):
	pass	
	
class ErrorProfile(Error):
	pass

class ErrorLogin(Error):
	pass

class ErrorVerification(Error):
	pass
		
class ErrorEDDN(Error):
	pass		

class ErrorLog(Error):
	pass			