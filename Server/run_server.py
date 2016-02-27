from ai_server import *
import my_game as RAIL

if __name__ == "__main__":
	server = Server(RAIL.game)
	server.init()
	server.go()