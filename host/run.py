import importlib
import sys

from server import *

if __name__ == "__main__":
	# Get what game we're using from command line
	#  might change this to use the config file
	if not len(sys.argv) == 2:
		# Improper usage, terminate
		print "Usage:\n%s [game_module]" % argv[0]
		sys.exit(1)
	else:
		# Never used importlib before, this might not work... needs testing
		mod_name = "GGS.host.games.%s" % argv[1]
		try:
			# Import the library as RAIL
			RAIL = importlib.import_module(mod_name)
		except:
			# Module doesn't exist, terminate
			print "Error importing module: %s" % (mod_name)
			sys.exit(1)

	# Attempt to initiate the server with the dynamically imported game
	server = Server(RAIL.game)
	server.init()
	server.go()
