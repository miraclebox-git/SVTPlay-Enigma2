def GetSVTPlayerVersion():
	try: 
		from Plugins.Extensions.SVTPlay.version import VERSION
	except: 
		VERSION="Unknown"
	return VERSION