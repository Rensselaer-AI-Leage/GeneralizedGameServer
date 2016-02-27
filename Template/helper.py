import sys
import socket
import random as r

import message as msg

class BotHelper:
	def __init__(self, name, strategy):
		# Get server ip and port from commandline
		try:
			server_info = (sys.argv[1], int(sys.argv[2]))
		except:
			# How did you mess this up?
			print "Usage:\n%s [ip] [port]" % sys.argv[0]
			raw_input("Press the any key to finish.")
			sys.exit(1)

		# Check if ip is in ipv4 format or ipv6 format
		ipv4 = False
		if '.' in server_info[0]: #this works, screw regex
			ipv4 = True
		
		# Connect to server
		if ipv4:
			self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		else:
			self.server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
		
		# Initialize other member variables
		self.name = name
		self.message = Message(server)
		self.strategy = strategy
		self.history = []
		self.gamestate = None
		
		# Connect to the server
		server.connect(server_info)
		
		# Start waiting for server requests
		self.run()
		
	def self.run(self):
		# Only send an ACK as a response to an ACK once, don't want to enter an infinite ACK loop
		done_with_ack = False
		while True:
			# Wait for a message from the server
			type, body = self.message.recv()
			
			if type == msg._SERVER["ACK"] and not done_with_ack:
				self.message.sendAck()
				done_with_ack = True
			elif type == msg._SERVER["Name"]:
				self.message.sendName(self.name)
				done_with_ack = False
			elif type == msg._SERVER["Move"]:
				self.throw()
				done_with_ack = False
			elif type == msg._SERVER["OppMove"]:
				self.history.append(body)
				self.message.sendAck()
				done_with_ack = False
			elif type == msg._SERVER["GameState"]:
				self.gamestate = body
				self.message.sendAck()
				done_with_ack = False
			elif type == msg._SERVER["Termination"]:
				self.message.sendAck()
				done_with_ack = False
				self.cleanup()
				break
			else:
				print "Unkown command type '%s', body: %s" % (type, body)
				continue # unknown command, ignore
	
	def throw(self):
		move = self.strategy(self.history)
		self.message.sendMove(move)
		
	def cleanup(self):
		server.close()
