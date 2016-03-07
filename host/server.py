'''
TODO:
	threading for multiple connections
	bracket / round robin support
	destructor to close connections and terminate threads
	make server handle poll_input (for token support)
	unique names?

	replace all sending and things with message.py's funcitons
	replace all tuples with structs

	write exception logging function to call whenever an exception is caught
'''

import sys
import time
import random
import socket
import threading
import datetime

from helpers import message

# Mostly just a struct to hold player information
class Player:
	def __init__(self, token, address, connection):
		self.token = token
		self.name = "Unknown Player"
		self.address = address
		self.connection = connection
		self.msg = message.Message(connection, '', '')
		self.in_game = True # Set to false when initialization is complete

# Mostly just a struct to hold match information
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
	@param settings dict<string, string> what settings to use for the server
	'''
	def __init__(self, game, settings):
		self.players = []
		# self.match_lock = threading.Mutex()
		self.matches = dict()
		self.threads = []
		self.alive = threading.Event() # Set in run_match
		self.game = game

		# Load settings from config file
		self.ppm = int(settings["ppm"])
		self.port = int(settings["port"])
		self.address = settings["address"][:-1] #strip newline character
		self.prune = int(settings["prune"])
		self.sleep = int(settings["sleep"])
		self.win_by = int(settings["win_by"])
		self.timeout = float(settings["timeout"])
		self.min_games = int(settings["min_games"])
		self.max_games = int(settings["max_games"])
		self.listen_queue = int(settings["listen_queue"])

		# Error log
		self.log_file = "logs/act/" + str(datetime.datetime.now()) + ".log"
		self.err_file = "logs/err/" + str(datetime.datetime.now()) + ".log"
		self.log_file = self.log_file.replace(':', '-')
		self.err_file = self.err_file.replace(':', '-')
		with open(self.log_file, 'w') as f:
			f.write("Activity log for RAIL GGS:\n---------------------\n")
		with open(self.err_file, 'w') as f:
			f.write("Error log for RAIL GGS:\n---------------------\n")

	'''
	@description Prints a message to a log, in this case just the terminal.
	@param msg string what message to print
	@return string the passed message
	'''
	def report(self, msg):
		# This function is too complicated to properly comment
		sys.stdout.flush()
		print msg

		with open(self.log_file, 'a') as f:
			f.write(msg + '\n')

		return msg

	def handle_exception(self, e):
		with open(self.log_file, 'a') as f:
			f.write(str(e) + ': ')
			f.write(sys.exc_info()[0] + '\n')
		self.report("An exception has been raised: %s" % (e,))

	'''
	@description Attempts to send a message to one of the players. Logs failures.
	@param receiver Player who is recieving the payload
	@param type string what kind of information is being sent
	@param payload string data to be sent
	@return int number of bytes sent or -1 on failure
	'''
	def send(self, receiver, msg_type, msg_body):
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

		# Check if the server is still active
		if not self.alive.isSet():
			return -1

		# Construct and send message
		try:
			size = receiver.msg.send(msg_type, msg_body)

			#Log
			self.report("Sent %i bytes of data to %s" % (size, receiver.name))
			return size
		except Exception as e:
			# Log
			size = len(msg_type) + len(msg_body) + 2
			self.handle_exception(e)
			self.report("Failed to send %i bytes of data to %s" % (size, receiver.name))

		return -1 # An error occured, return -1

	'''
	@description Multithreaded poll for multiple recipients
	@param recipient_infos list<tuple(Player, string, int)> information about who is receiving the poll and what kind of poll it is
	@return dict of players to poll results
	'''
	def poll_all(self, recipient_infos):
		# Recipient_info entries are of form: (player, type, size)
		results = []
		threads = []

		# Replace the inner-workings of the for-loop with a closure to prevent scoping issues
		def in_loop(msg_info):
			res = []
			results.append(res)

			# Unpack info since res also needs to be passed
			receiver, rq_type, size = msg_info

			# Run polls on separte threads since they wait for input
			poll_thread = threading.Thread(target=self.poll, args=(receiver, rq_type, size, res))
			poll_thread.start()
			threads.append(poll_thread)

		# Go through each player to poll
		for info in recipient_infos:
			in_loop(info)

		# Wait for threads to complete (response received)
		for thread in threads:
			thread.join()

		print results # debug
		# Return a dict of players to their response
		return zip([key[0] for key in results], [val[1] for val in results])
		#return dict(results)

	'''
	@description Sends a player a request for input, then waits for a response. Validates received data with a token.
	@param sender Player which player is being polled
	@param rq_type string what kind of request it is
	@param size how long the data is expected to be (including headers and token)
	@param out tuple<Player, tuple<string, string> where to send the result
	@return tuple<Player, tuple<string, string> tuple of sender and either the response received or None on failure
	'''
	def poll(self, sender, rq_type, size, out=None):
		# TODO: timeout if no response received after 1 second
		self.report("Sending request %s to %s, expected size %i" % (rq_type, sender.name, size))

		err = self.send(sender, rq_type, "Requesting a response")

		# If the request didn't get send, the connection is lost
		if err == -1:
			out = (sender, None)
		else:
			# Wait for response
			try:
				response = sender.msg.recv()
				out = (sender, response)
				print response
			except Exception as e:
				out = (sender, None)
				self.handle_exception(e)

		# Return the response
		return out

	'''
	@description Creates a player object from a connection, then sends that player's token over the connection.
	@param name string player's nickname
	@param address string player's ip address
	@param connection player's connection to the socket
	@modifies self.players
	@effects appends a new player to self.players
	@return Player player object created
	'''
	def init_player(self, address, connection):
		# Create unique (probably) token for player
		token = message.gen_token(64)

		# Create player object, append to player deque
		player = Player(token, address, connection)
		self.players.append(player)

		# Inform player of his token
		#self.send(player, 'ID', token)

		# Return player object
		return player

	'''
	@description Creates a socket and starts to listen for connections. Maximum 1 queued connection.
	@modifies self.sock
	@effects sets self.sock to be localhost:argv[1]
	'''
	def init(self):
		# Create socket
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server_address = (self.address, self.port)
		self.sock.bind(server_address)

		# Start looking for connections
		self.sock.listen(self.listen_queue)

	'''
	@description Take a pool of players and create a groups
	@param players list<Player> list of connected players not in a game
	@param ppm int number of players per match
	@return list<Player> group of players, size ppm
	'''
	def random_pairings(self, players, ppm):
		# Get a random selection of ppm players to be in the game
		playing_players = random.sample(players, ppm)
		# Return that random selection
		return playing_players

	'''
	@description Goes through list of players and removes everyone who is disconnected
	@modifies self.players
	@effects removes all disconnected players from self.players
	'''
	def prune_players(self):
		# New list for connected players
		new_playerlist = []

		# Ping players with ACK to mae sure the connection is still valid
		tuples = [(player, 'AK', 128) for player in self.players]
		reses = self.poll_all(tuples)

		# Get a list of all players who are in a game
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
		ct = 0
		while self.alive.isSet():
			ct += 1
			# Check that all players are still connected every PRUNE loops
			if not ct % self.prune:
				self.prune_players()

			# Get a list of all players who are in a game
			in_queue = [player for player in self.players if not player.in_game] # TODO: replace with self.in_queue
			if len(in_queue) > ppm: # Enough players to start a match

				# Matchmake players
				playing_players = pairing_method(in_queue)

				# Generate unique key to identify match
				uniqid = msg.gen_token(64)
				self.matches[uniqid] = []

				# Set timeouts
				# !IMPORTANT: game is in charge of reverting these values
				for player in playing_players:
					player.connection.settimeout(timeout)
					player.in_game = True

				# Make new thread for the match
				match = threading.Thread(target=self.match, args=(playing_players, uniqid))
				match.start()
				self.threads.append(match)

			# Wait one second between making new games
			time.sleep(self.sleep)

	'''
	@description
	@param active_players list<Player> list of players in the game
	@param min_games int minimum number of games to play in the match (replace with config?)
	@param max_games int maximum number of games to play in the match (replace with config?)
	@param win_by int minimum number of games first place player must win by (replace with config?)
	@param game_logic function(*moves) function to run the actual game logic
	@return list<tuple(Player, score)> list of tuples of players and their scores after the match
	'''
	def match(self, active_players, match_id):
		# Initiate score to zero
		scores = [(player, 0) for player in active_players]

		# Play games until max_games have been played
		games = 0
		while games < self.max_games:
			# Only check for a win if at least min_games have been played
			if games >= self.min_games:
				# Check how much first place is winning by

				# Get two highest scores
				scores.sort(key=lambda x: x[1])
				first_place, second_place = score[:2]

				# Check if the difference between the first two highest scores is at least win_by
				diff = first_place[1] - second_place[1]
				if diff >= self.win_by:
					# All criteria has been met to end the game
					return scores

			# Request moves from all players
			tuples = [(player, "MV", 128) for player in active_players]
			moves = self.poll_all(tuples)

			# Get results based on polled moves
			results = self.game(*moves)

			# One more game has been played
			games += 1

			# Update scores based on game logic
			#  This would be better if score was a dict, but then getting high scores would be worse
			for res in results:
				for score in scores:
					if res[0] == score[0]:
						score[1] += res[1]
						break

		# We are done, return score
		return score

	'''
	@description Starts the server proper.
	@modifies threads
	@effects starts matchmaking on a new thread
	'''
	def go(self):
		self.alive.set() # Begin the match

		try:
			# Create a new thread for pairing players
			match_maker = threading.Thread(target=self.setup_matches, args=(self.ppm, self.timeout, self.random_pairings))
			match_maker.start()
			self.threads.append(match_maker)

			# Log
			self.report("Server started on port: " + str(self.port))

			# TODO: threading for 2 connections
			while self.alive.isSet():
				# Poll for connection, add them to player queue
				connection, client_address = self.sock.accept()

				# Create player object, append to self.players, inform player of his token
				player = self.init_player(client_address, connection)

				try:
					name = self.poll(player, "NM", 1024)
					print name[1][1]
					player.name = name[1][1]
					self.report("New player %s connected from %s" % (player.name, player.address))
				except Exception as e:
					self.handle_exception(e)
					self.report("Could not establish a player's connection.")
					self.players.remove(player)
					continue

		except Exception as a:
			self.handle_exception(e)
		self.cleanup()

	'''
	@description Joins all threads. Closes all connections.
	@modifies self.threads
	@effects empties list
	'''
	def cleanup(self):
		# Clean up threads
		self.report("Attempting to close threads...")
		self.alive.clear() # Unset alive, this informs the class that no more server actions should take place
		for thread in self.threads:
			thread.join()
		threads = []
		self.report("Threads successfully closed")

		# Clean up sockets
		self.report("Terminating active connections...")
		for player in self.players:
			self.send(player, "TN", "You don't have to go home, but you can't stay here")
			player.connection.close()
		self.report("Active connections terminated")


'''
Why is this server code so complicated? I can make an RPS server in like 100 lines.
Don't worry, we'll fix it in the flavor text.
'''
