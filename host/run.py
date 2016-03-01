import importlib
import sys

from server import *

if __name__ == "__main__":
	if not len(sys.argv) == 2:
		print "Usage:\n%s [game_module]" % argv[0]
		sys.exit(1)
	else:
		try:
			RAIL = importlib.import_module(argv[1], __NAME__)
		catch:
			print "Error importing module: %s" % (__NAME__ + argv[1],)
			sys.exit(1)

	server = Server(RAIL.game)
	server.init()
	server.go()
