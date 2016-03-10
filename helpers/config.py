'''
@description Function to load settings from a config file
@param filen string the name of the confg file
@return map of settings to values
'''
def load(filen):
	config = dict()
	try:
		with open(filen) as cfg:
			for line in cfg:
				line = line.split('#')[0] # Comments, yay!
				line = line.split('//')[0] # //Comments, yay!
				parts = line.split(':')
				if len(parts) == 2:
					config[parts[0].strip()] = parts[1].strip()
				else:
					pass # This is pythonic
			return config
	except Exception as e:
		print "Error opening file " + filen
		return None
