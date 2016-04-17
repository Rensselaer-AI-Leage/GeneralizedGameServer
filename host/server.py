import os
import sys
import time
import random
import socket
import threading
import datetime
from multiprocessing.pool import ThreadPool

sys.path.append('..')
from helpers import message
from helpers.filelock import FileLock
from player import Player

# Mostly just a struct to hold match information
class Match:
	def __init__(self, players):
		self.names = [player.name for player in players]
		self.winner = -1
		self.results = ''

class Server:
	''' Server class handles all communication between this program and client scripts ''' # <- Docstring

	'''
	@description Constructor, initializes data members and ensures correct usage.
	@param game function(list<string>,list<connection>,string,dict,threading.Event) what game to run
	@param settings dict<string, string> what settings to use for the server
	'''
	def __init__(self, game, settings):
		self.players = []
		# self.match_lock = threading.Mutex() # Make sure your threads don't lock much
		self.matches = dict()
		self.threads = []
		self.alive = threading.Event() # Set in run_match
		self.game = game
		#self.scoring = game.scoring # Get scoring system from game

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
		self.verbose = int(settings["verbose"])
		self.log_folder = os.path.realpath(settings["log_folder"])
		self.err_folder = os.path.realpath(settings["error_folder"])
		self.res_folder = os.path.realpath(settings["results_folder"])
		
		if not os.path.exists(self.log_folder):
			os.makedirs(self.log_folder)
		if not os.path.exists(self.err_folder):
			os.makedirs(self.err_folder)	
		if not os.path.exists(self.res_folder):
			os.makedirs(self.res_folder)
			
		self.now = lambda: str(datetime.datetime.now())

		# Error log
		fname = self.now().replace(':', '-') + ".log"

		self.log_file = os.path.join(self.log_folder, fname)
		self.err_file = os.path.join(self.err_folder, fname)
		self.res_file = os.path.join(self.res_folder, fname)

		with open(self.log_file, 'w') as f:
			f.write("Activity log for RAIL GGS:\n---------------------\n")
		with open(self.err_file, 'w') as f:
			f.write("Error log for RAIL GGS:\n---------------------\n")
		with open(self.res_file, 'w') as f:
			f.write("Results log for RAIL GGS:\n---------------------\n")

	# TODO: Implement locks on files since everything is asynchronous
	'''
	@description Prints a message to a log, in this case just the terminal.
	@param msg string what message to print
	@return string the passed message
	'''
	def report(self, msg):
		# This function is too complicated to properly comment
		sys.stdout.flush()

		now = str(datetime.datetime.now())
		
		# Grab the lock
		with FileLock(self.log_file), open(self.log_file, 'a') as f:
			f.write(self.now() + ':\t')
			f.write(msg + '\n')

		return msg

	'''
	@description Prints a message to a log.
	@param msg string what message to print
	@return string the passed message
	'''
	def log(self, msg, log_level=0):
		if log_level <= self.verbose:
			print msg
			return self.report(msg)
		else:
			return msg # This is pythonic

	'''
	@description Prints a error to a log.
	@param e Exception the exception being logged
	@return Exception the exception passed as an arg
	'''
	def log_error(self, e):
		# Grab the lock
		with FileLock(self.err_file), open(self.err_file, 'a') as f:
			f.write(self.now() + ':\t')
			f.write(str(e) + ('\n'))
		#self.report("An exception has been raised: %s" % (e,))
		return e

	'''
	@description Prints results of a match to a log.
	@param results string what the results were
	@return string the passed results
	'''
	def log_result(self, results):
		# Grab the lock
		with FileLock(self.res_file), open(self.res_file, 'a') as f:
			f.write(self.now() + ':\t')
			f.write(results + '\n')
		return self.log(results, 2)
		#return results

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
			size = receiver.con.send(msg_type, msg_body)

			#Log
			self.log("Sent %i bytes of data to %s" % (size, receiver.name), 10)
			return size
		except Exception as e:
			# Log
			size = len(msg_type) + len(msg_body) + 2
			self.log_error(e)
			self.log("Failed to send %i bytes of data to %s" % (size, receiver.name), 9)

		return -1 # An error occured, return -1

	'''
	@description Multithreaded poll for multiple recipients
	@param recipient_infos list<tuple(Player, string, string)> information about who is receiving the poll and what kind of poll it is
	@return dict of players to poll results
	'''
	def poll_all(self, recipient_infos):
		# Recipient_info entries are of form: (player, type, body)
		results = dict()
		threads = dict()

		# For each recipient, make an asynchronous process to handle their response
		num_reqs = len(recipient_infos)
		pool = ThreadPool(processes=num_reqs)
		for info in recipient_infos:
			# Unpack poll() args
			receiver = info[0]
			rq_type  = info[1]
			body     = info[2]

			# Run each poll on a separate thread
			threads[receiver] = pool.apply_async(self.poll, (receiver, rq_type, body,))

		# Get the results, store them in a dict
		# Seems like it defeats the purpose of polling asynchronously, but it doesn't (brain teaser?)
		for info in recipient_infos:
			receiver = info[0]
			try:
				results[receiver] = threads[receiver].get(timeout=self.timeout)
			except Exception as e:
				self.log_error(e)
				results[receiver] = None # Worry about this later

		# Clean up those threads
		pool.close()
		pool.join()

		# Return the dict
		return results

	'''
	@description Sends a player a request for input, then waits for a response. Validates received data with a token.
	@param sender Player which player is being polled
	@param rq_type string what kind of request it is
	@param size how long the data is expected to be (including headers and token)
	@param out tuple<Player, tuple<string, string> where to send the result
	@return tuple<Player, tuple<string, string> tuple of sender and either the response received or None on failure
	'''
	def poll(self, sender, rq_type, body):
		# TODO: timeout if no response received after 1 second
		self.log("Sending request %s to %s: %s" % (rq_type, sender.name, body), 10)
		err = self.send(sender, rq_type, body)

		# If the request didn't get send, the connection is lost
		if err == -1:
			out = (sender, None)
		else:
			# Wait for response
			try:
				response = sender.con.recv()
				if response[1] is not None:
					response_msg = response[1][0]
				else:
					response_msg = "None"
				self.log("Received response %s from %s" % (response_msg, sender.name), 10)
				out = (sender, response)
			except Exception as e:
				out = (sender, None)
				self.log_error(e)
				
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

		# TODO: get token from player's message object

		# Return player object
		return player

	'''
	@description Creates a socket and starts to listen for connections. Maximum 1 queued connection.
	@modifies self.sock
	@effects sets self.sock to be localhost:argv[1]
	'''
	def init(self):
		# Create socket
		try:
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			server_address = (self.address, self.port)
			self.sock.bind(server_address)

			# Start looking for connections
			self.sock.listen(self.listen_queue)
		except Exception as e:
			self.log_error(e)
			self.alive.clear()

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
		return self.players # TODO: fix prune_players
		# New list for connected players
		new_playerlist = []

		# Ping players with ACK to mae sure the connection is still valid
		tuples = [(player, message._MSGTYP["Ack"], "ACK") for player in self.players]
		reses = self.poll_all(tuples)

		# Get a list of all players who are in a game
		new_playerlist = [res for res in reses if not reses[res] == None] # Could be if reses[res], but that wouldn't be Pythonic
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
			in_queue = [player for player in self.players if player.is_ready()] # TODO: replace with self.in_queue
			#print in_queue
			if len(in_queue) >= ppm + 1: # Enough players to start a match plus one to advoid repairings after a match

				# Matchmake players
				playing_players = pairing_method(in_queue, ppm)

				# Generate unique key to identify match
				uniqid = message.gen_token(64)
				self.matches[uniqid] = []

				# Set timeouts
				# !IMPORTANT: self.match is in charge of reverting these values
				for player in playing_players:
					player.con.connection.settimeout(timeout)
					player.in_game = True

				# Make new thread for the match
				match = threading.Thread(target=self.match, args=(playing_players, uniqid))
				match.start()
				self.threads.append(match)

			# Wait one second between making new games
			time.sleep(self.sleep)

	'''
	TODO: fix this documentation
	@description
	@param active_players list<Player> list of players in the game
	@param match_id unique identifier by which to distinguish the match
	@return list<tuple(Player, score)> list of tuples of players and their scores after the match
	TODO: break up this function
	'''
	def match(self, active_players, match_id):
		# Get the names of all players, used for logging
		names = ''
		for i, player in enumerate(active_players):
			if i+1 == len(active_players): # If this is the last player, slap an "and" in there
				names += "and " + player.name
			else:
				names += player.name + ", "

		# Inform all players that they have started a match
		tuples = [(player, message._MSGTYP["Note"], "Starting a new match between %s" % (names)) for player in active_players]
		self.poll_all(tuples) # We don't care about these responses

		self.log("Starting a new match between %s" % (names))

		# Initialize all scores to zero
		scores = dict()
		for player in active_players:
			scores[player] = 0

		games = 0
		while games < self.max_games:
			if games >= self.min_games:
				# Check if someone has yet won by win_by yet
				#  Note: we don't need to keep track of players, but it might be urgent later so we do so anyway (we did that on purpose)
				first = (None, 0)
				second = (None, 0)
				for player in scores:
					score = scores[player]
					if score > first[1]:
						second, first = first, (player, score)
					elif score > second[1]:
						second = (player, score)

				if first[1] - second[1] >= self.win_by:
					# Yay, we're done!
					break

			# Request moves from all players
			tuples = [(player, message._MSGTYP["Move"], "What is your move?") for player in active_players]
			responses = self.poll_all(tuples)

			### New Function Here ###
			# Responses is a dict<Players, tuple<Player, tuple<Type of response(MV), move>>
			moves = dict()
			for response in responses:
				# Track moves
				msg = responses[response]

				try:
					# Get the move
					if not msg or not msg[1]: # 't' is reserved as a timeout signal
						mv = 't'
						response.timeout()
					else:
						mv = msg[1][1]
						response.untimeout()
				except:
					mv = 't'
					continue

				moves[response] = mv

				# Let other players know about this move
				players_to_inform = [player for player in active_players if not player is response]
				tuples = [(player, message._MSGTYP["OppMove"], "%s;%s" % (response.name, mv)) for player in players_to_inform]
				self.poll_all(tuples)

			# Run the actual game
			results = self.game.game(moves)

			# Game has been played
			games += 1

			# Parse results
			if not results:
				return None # We'll handle that later
			else:
				for player in results:
					result = results[player]
					scores[player] += result

		scores_str = ""
		for score in scores:
			scores_str += "[%s, %s] " % (score.name, str(scores[score]))

		self.log_result("Match ended between %s. Results: %s" % (names, scores_str))

		### New function here ###
		# Inform the player of the result
		tuples = [(player, message._MSGTYP["Note"], "Match ended between %s. Results - %s" % (names, scores_str)) for player in active_players]
		responses = self.poll_all(tuples)
		scoring = self.game.scoring(scores, self.win_by)
		for player in active_players:
			# Free the players so they can compete once more
			player.score += scoring[player]
			player.matches += 1

			player.in_game = False
			player.con.connection.settimeout(self.timeout)

		scores = {}
		for player in self.players:
			if player.matches > 0: scores[player] = player.score / float(player.matches)
		ranking = self.game.ranking(scores)

		self.log_result('The current standings:')
		for rank, player in enumerate(ranking):
			if player.matches > 0: self.log_result('%d\t%s\t%f' % (rank, player.name, player.score / float(player.matches)))
		return scores

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
			self.log("Server started on port: " + str(self.port), 0)

			# TODO: threading for 2 connections
			while self.alive.isSet():
				# Poll for connection, add them to player queue
				connection, client_address = self.sock.accept()

				# Create player object, append to self.players, inform player of his token
				player = self.init_player(client_address, connection)

				try:
					# Get player's name, this also informs the player that they have connected
					name = self.poll(player, message._MSGTYP["Name"], "What is your name?")
					player.name = name[1][1]
					self.log("New player %s connected from %s" % (player.name, player.address), 1)
				except Exception as e:
					self.log_error(e)
					self.log("Could not establish a player's connection.", 1)
					self.players.remove(player)
					continue

		except Exception as e:
			self.log_error(e)
		self.cleanup()

	'''
	@description Joins all threads. Closes all connections.
	@modifies self.threads
	@effects empties list
	'''
	def cleanup(self):
		# Clean up threads
		self.log("Attempting to close threads...", 10)
		self.alive.clear() # Unset alive, this informs the class that no more server actions should take place
		for thread in self.threads:
			thread.join()
		threads = []
		self.log("Threads successfully closed", 10)

		# Clean up sockets
		self.log("Terminating active connections...", 10)
		for player in self.players:
			self.send(player, message._MSGTYP["Termination"], "You don't have to go home, but you can't stay here")
			player.con.connection.close()
		self.log("Active connections terminated", 10)


'''
Why is this server code so complicated? I can make an RPS server in like 100 lines.
Don't worry, we'll fix it in the flavor text.
'''
