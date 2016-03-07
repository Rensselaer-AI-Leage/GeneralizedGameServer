import importlib
import sys

from server import *
from helpers import config as cfg

if __name__ == "__main__":
	# Get what game we're using from command line
	#  might change this to use the config file
	if not len(sys.argv) == 2:
		# Improper usage, terminate
		print "Usage:\n%s [game_module]" % sys.argv[0]
		sys.exit(1)
	else:
		# Never used importlib before, this might not work... needs testing
		mod_name = "host.games.%s" % sys.argv[1]
		try:
			# Import the library as RAIL
			RAIL = importlib.import_module(mod_name)
		except:
			# Module doesn't exist, terminate
			print "Error importing module: %s" % (mod_name)
			sys.exit(1)

	# Get the proper config file based on game
	cfg_file = "host/games/%s.cfg" % sys.argv[1]
	settings = cfg.load(cfg_file)

	# Attempt to initiate the server with the dynamically imported game
	server = Server(RAIL.game, settings)
	server.init()
	server.go()
