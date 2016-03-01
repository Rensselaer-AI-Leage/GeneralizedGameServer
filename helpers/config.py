'''
@description Function to load settings from a config file
@param filen string the name of the confg file
@return map of settings to values
'''
def load(filen):
	config = dict()
	with open(filen) as cfg:
		for line in cfg:
			parts = line.split(':')
			config[parts[0]] = parts[1]
	return config
