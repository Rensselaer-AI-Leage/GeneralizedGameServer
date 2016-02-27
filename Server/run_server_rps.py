'''
WHat does this file do
?

*makes a server object
*defines the game to give to server
*give server a game
*start server
'''

import sys
import socket
import threading
import random

from ai_server import *
from do_rps import *
from message import *

#IMPORTANT: game() is in charge of reverting timeout and setting in_game
def game(players, key, matches, alive):

	#only 2 players, get their info
	n0 = players[0].name
	n1 = players[1].name
	p0 = players[0].connection
	p1 = players[1].connection
		
	try:
		p0.send(n1)
		p1.send(n0)
	except Exception as e:
		#error
		print e
	
	result = match(p0, p1, poll_move, rps)
	
	try:
		p0.send('D')
		p1.send('D')
	except Exception as e:
		#error
		print e
	
	p0_payload = n1 + ' ' + str(result[0]) + ' ' + str(result[1]) + ' ' + str(result[2])
	p1_payload = n0 + ' ' + str(result[1]) + ' ' + str(result[0]) + ' ' + str(result[2])
	
	try:
		p0.send(p0_payload)
		p1.send(p1_payload)
	except Exception as e:
		#error
		print e
	
	end_result = (n0, n1, key, result[1], result[0], result[2])
	matches[key].append(end_result)
	
	print "Match between %s and %s (id: %s ) finished, final score: %d %d %d" % end_result
	sys.stdout.flush()
	
	for player in players:
		player.connection.settimeout(0)
		player.in_game = False
	
	alive.clear() #temporary so the program doesn't run forever
	

if __name__ == "__main__":
	server = Server(game)
	server.init()
	server.go()