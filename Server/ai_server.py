'''
IMPORTANT: Do not use this, not ready or even functional yet

TODO:
	threading for multiple connections
	bracket / round robin support
	destructor to close connections and terminate threads
	make server handle poll_input (for token support)
	unique names?
	
	replace all sending and things with message.py's funcitons
'''

import sys
import time
import random
import socket
import threading

# mostly just a struct to hold player information
class Player:
	def __init__(self, token, name, address, connection):
		self.token = token
		self.name = name
		self.address = address
		self.connection = connection
		self.in_game = False

class Match:
	def __init__(self, players):
		self.names = [player.name for player in players]
		self.winner = -1
		self.results = ''
		
# Server class handles all communication between this program and client scripts		
class Server:

	'''
	@description Constructor, initializes data members and ensures correct usage.
	@param game function(list<string>,list<connection>,string,dict,threading.Event) what game to run
	'''
	def __init__(self, game):
		self.players = [] 
		# self.match_lock = threading.Mutex()
		self.matches = dict()
		self.threads = []
		
		self.alive = threading.Event() # set in run_match
		
		self.game = game
		
		# TODO: replace this with a config file
		self.address = "" # localhost
		# get port from command-line arguments
		try:
			self.port = int(sys.argv[1])
		except:
			# improper usage, terminate
			self.report("Usage:\n%s [port]" % sys.argv[0])
			sys.exit(1)
			
	'''
	@description Prints a message to a log, in this case just the terminal.
	@param msg string what message to print
	@return string the passed message
	'''
	def report(self, msg):
		# this function is too complicated to properly comment
		print msg
		return msg
	
	'''
	@description Attempts to send a message to one of the players. Logs failures.
	@param receiver Player who is recieving the payload
	@param type string what kind of information is being sent
	@param payload string data to be sent
	@return int number of bytes sent or -1 on failure
	'''
	def send(self, receiver, type, payload):
		'''
		Types: 
			ID - player's token
			OM - opponent's move
			GS - new gamestate after player moves
			RS - result of a match (not a game)
			TN - end of connection
			RQ - request for a move
			RN - request for a name
			AK - check if you're still alive
		'''
		
		# construct and send message
		msg = "%s:%s" % (type, payload)
		try:
			size = receiver.connection.send(msg)
			
			# log
			self.report("Sent %i bytes of data to %s" % (size, receiver.name))
			return size
		except:
			# log
			self.report("Failed to send %i bytes of data to %s" % (len(msg), receiver.name))
			
		return -1
	
	'''
	@description Multithreaded poll for multiple recipients
	@param recipient_infos list<tuple(Player, string, int)> information about who is receiving the poll and what kind of poll it is
	@return dict of players to poll results
	'''
	def poll_all(self, recipient_infos):
		# recipient_info entries are of form: (player, type, size)
		results = []
		threads = []
		
		# go through each player to poll
		for info in recipient_infos:
			res = []
			results.append(res)
			
			# unpack info since res also needs to be passed
			receiver, type, size = info
			
			# run polls on separte threads since they wait for input
			ping_thread = threading.Thread(target=self.poll, args=(receiver, type, size, res))
			ping_thread.start()
			threads.append(ping_thread)
			
		# wait for threads to complete (response received)
		for thread in threads:
			thread.join()
			
		# print reses # debug
		# return dict(zip([key[0] for key in reses], [val[1] for val in reses])) # this is better but whatever
		return dict(reses)
	
	'''
	@description Sends a player a request for input, then waits for a response. Validates received data with a token.
	@param type string what kind of request it is
	@param size how long the data is expected to be (including headers and token)
	@return string message received, None on failure
	'''
	def poll(self, sender, type, size, res=None):
		# TODO: timeout if no response received after 1 second
		self.report("Sending request %s to %s, expected size %i" % (type, sender.name, size))
		err = self.send(sender, type, "Requesting a response")
		
		# if the request didn't get send, the connection is lost
		if err == -1:
			res = [sender, None]
		
		# wait for response
		msg = sender.connection.recv(size)
		
		
		# get token out of the message
		# this will eventually be handled by message.py
		parts = msg.split(':')
		
		# if the token is invalide, return None, else return the response
		if not len(parts) == 3 or not parts[1] == sender.token:
				self.report("Recieved invalid response from %s: %s" % (sender.name, msg))
				res = [sender, None]
		else:
			res = [sender, parts[0] + ':' + parts[2]]
			
		return res
			
	'''
	@description Creates a player object from a connection, then sends that player's token over the connection.
	@param name string player's nickname
	@param address string player's ip address
	@param connection player's connection to the socket
	@modifies self.players
	@effects appends a new player to self.players
	@return Player player object created
	'''
	def init_player(self, name, address, connection):
		# create unique (probably) token for player
		token = msg.gen_token(64)
		
		# create player object, append to player deque
		player = Player(token, name, address, connection)
		self.players.append(player)
		
		# log
		self.report("New player %s joined from %s" % (name, address))
		
		# inform player of his token
		self.send(player, 'ID', token)
		
		# return player object
		return player
	
	'''
	@description Creates a socket and starts to listen for connections. Maximum 1 queued connection.
	@modifies self.sock
	@effects sets self.sock to be localhost:argv[1]
	'''
	def init(self):
		# create socket
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server_address = (self.address, self.port)
		self.sock.bind(server_address)

		# start looking for connections
		self.sock.listen(1)		
	
	'''
	@description Take a pool of players and create a groups
	@param players list<Player> list of connected players not in a game
	@param ppm int number of players per match
	@return list<Player> group of players, size ppm
	'''
	def random_pairings(self, players, ppm):
		# get a random selection of ppm players to be in the game
		playing_players = random.sample(players, ppm)			
		
		return playing_players
		
	'''
	@description Goes through list of players and removes everyone who is disconnected
	@modifies self.players
	@effects removes all disconnected players from self.players
	'''
	def prune_players(self):
		# new list for connected players
		new_playerlist = []
			
		# ping players with ACK to mae sure the connection is still valid
		tuples = [(player, 'AK', 128) for player in self.players]
		reses = self.poll_all(tuples)
	
		# get a list of all players who are in a game
		new_playerlist = [res for res in reses if not reses[res] == None]
		self.players = new_playerlist
			
	'''
	@description Makes random groups of players, ensuring that no player is in more than one game at a time.
	@param ppm int players per match
	@param timeout double seconds to wait before autoloss of game (not match)
	@modifies self.matches
	@effects creates a new entry in matches, key is random
	@modifies self.threads
	@effects runs each match on a new thread
	'''
	def setup_matches(self, ppm, timeout, pairing_method):
		# TODO: implement bracket and round-robin
		PRUNE = 10
		
		ct = 0
		while self.alive.isSet():
			ct += 1
			# check that all players are still connected every PRUNE loops
			if not ct % PRUNE:
				self.prune_players()
				
			# get a list of all players who are in a game
			in_queue = [player for player in self.players if not player.in_game] # todo: replace with self.in_queue
			if len(in_queue) > ppm: # enough players to start a match
			
				# matchmake players
				playing_players = pairing_method(in_queue)
				
				# generate unique key to identify match
				uniqid = msg.gen_token(64)
				self.matches[uniqid] = []
		
				# set timeouts
				# IMPORTANT: game is in charge of reverting these values
				for player in playing_players:
					player.connection.settimeout(timeout)
					player.in_game = True
				
				# make new thread for the match
				match = threading.Thread(target=self.game, args=(playing_players, uniqid, self.matches, self.alive))
				match.start()
				self.threads.append(match)
				
			# wait a second between making new games
			time.sleep(1)
	
	'''
	@description
	@param active_players list<Player> list of players in the game
	@param min_games int minimum number of games to play in the match (replace with config?)
	@param max_games int maximum number of games to play in the match (replace with config?)
	@param win_by int minimum number of games first place player must win by (replace with config?)
	@param game_logic function(*moves) function to run the actual game logic
	@return list<tuple(Player, score)> list of tuples of players and their scores after the match
	'''
	def match(self, active_players, min_games, max_games, win_by, game_logic):
		# initiate score to zero
		scores = [(player, 0) for player in active_players]

		# play games until max_games have been played
		games = 0
		while games < max_games:
			# only check for a win if at least min_games have been played
			if games >= min_games:
				# check how much first place is winning by 
				
				# get two highest scores
				scores.sort(key=lambda x: x[1])
				first_place, second_place = score[:2]
				
				# check if the difference between the first two highest scores is at least win_by
				diff = first_place[1] - second_place[1]
				if diff >= win_by:
					# all criteria has been met to end the game
					return scores
			
			# request moves from all players
			tuples = [(player, 'RQ', 128) for player in active_players]
			moves = self.poll_all(tuples)
			
			# get results based on polled moves
			results = game_logic(*moves)
			
			# one more game has been played
			games += 1
			
			# update scores based on game logic
			# this would be better if score was a dict, but then getting high scores would be worse
			for res in results:
				for score in scores:
					if res[0] == score[0]:
						score[1] += res[1]
						break
			
		# we are done, return score
		return score

	'''
	@description Starts the server proper.
	@modifies threads
	@effects starts matchmaking on a new thread
	'''
	def go(self):
		self.alive.set() # begin the match

		try:
			# create a new thread for pairing players
			match_maker = threading.Thread(target=self.setup_matches, args=(2, 0.1, self.random_pairings))
			match_maker.start()
			self.threads.append(match_maker)
			
			# log
			self.report("Server started on port: " + str(self.port))
			
			# todo: threading for 2 connections
			while self.alive.isSet():
				# poll for connection, add them to player queue
				connection, client_address = self.sock.accept()
				
				# TODO: change this to use self.poll
				name = connection.recv(1024)
				
				# create player object, append to players deque, inform player of his token
				self.init_player(name, client_address, connection)
				
		finally:
			self.cleanup()
			
	'''
	@description Joins all threads. Closes all connections.
	@modifies self.threads
	@effects empties list
	'''
	def cleanup(slef):
		# clean up threads
		self.report("Attempting to close threads...")
		self.alive.clear() # unset alive
		for thread in self.threads:
			thread.join()
		threads = []
		self.report("Threads successfully closed")	
		
		# clean up sockets
		self.report("Terminating active connections...")
		for player in self.players:
			self.send(player, "TN", "You don't have to go home, but you can't stay here")
			player.connection.close()
		self.report("Active connections terminated")
		
		
'''
Flavor text here
'''