import sys
import socket
import threading
from collections import deque
from do_rps import *

def trycatch(f, *a):
	try:
		return f(*a)
	except:
		return None

def poll_move(player0, player1):
	#get throws
	try:
		throw0 = player0.recv(1)
	except Exception as t:
		throw0 = 'T'
		
	try:
		throw1 = player1.recv(1)
	except Exception as t:
		throw1 = 'T'
	
	#exchange throws
	player0.send(throw1)
	player1.send(throw0)
	
	#return throws
	return (throw0, throw1)

def play_match(player0, player1, matches, alive):
	p0s = player0[1].send
	p1s = player1[1].send
	trycatch(p0s, player1[0])
	trycatch(p1s, player0[0])
	#player0[1].send(player1[0])
	#player1[1].send(player0[0])	
	result = match(player0[1], player1[1], poll_move)
	trycatch(p0s, 'D')
	trycatch(p1s, 'D')
	#player0[1].send(player1[0] + ' ' + str(result[0]) + ' ' + str(result[1]) + ' ' + str(result[2]))
	#player1[1].send(player0[0] + ' ' + str(result[1]) + ' ' + str(result[0]) + ' ' + str(result[2]))
	trycatch(p0s, player1[0] + ' ' + str(result[0]) + ' ' + str(result[1]) + ' ' + str(result[2]))
	trycatch(p1s, player0[0] + ' ' + str(result[1]) + ' ' + str(result[0]) + ' ' + str(result[2]))	
	if result[0] > result[1]:
		#player 0 won
		result = [player0[0], player1[0]] + result
	elif result[0] < result[1]:
		#player 1 won
		result = (player1[0], player0[0], result[1], result[0], result[2])
	else:
		#tie
		result = [player0[0], player1[0]] + result
	result = tuple(result)
	matches.append(result)
	print 'Match between %s and %s finished, final score: %d %d %d' % result

def setup_matches(players, matches, threads, alive):
	timeout = 0.1
	while alive.is_set():
		if len(players) >= 2:
			p0 = players.popleft()
			p1 = players.popleft()
			p0[1].settimeout(timeout)
			p1[1].settimeout(timeout)
			match = threading.Thread(target=play_match, args=(p0, p1, matches, alive))
			match.start()
			threads.append(match)			
			

try:
	port = int(sys.argv[1])
except:
	print 'Usage:\n%s [port]' % sys.argv[0]
	sys.exit(1)

#create socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('', port) #start on localhost
sock.bind(server_address)

#start looking for connections
sock.listen(1)

players = deque([])
matches = []
threads = []
alive = threading.Event()
alive.set()

try:
	match_maker = threading.Thread(target=setup_matches, args=(players, matches, threads, alive))
	match_maker.start()
	threads.append(match_maker)
	print 'Server started on port: %d' % port
	#todo: threading for 2 connections
	while True:
		#poll for connection, add them to player queue
		connection, client_address = sock.accept()
		name = connection.recv(1024)
		players.append((name, connection))
		print '%s joined from %s' % (name, client_address)
		
		'''connection, client_address = sock.accept()
		try:
			while True:
				#get data, 4 byte buffer size
				data = connection.recv(4)
				if data:
					#if when you get data, send it back
					connection.sendall(data)
				else:
					break
		finally:
			#simple enough
			connection.close()'''
except:
	print "attempting to close threads"
	alive.clear()
	for t in threads:
		t.join()
	print "threads successfully closed"    	