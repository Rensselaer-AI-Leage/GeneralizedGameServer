from helpers import message

class Player:
	def __init__(self, token, address, connection):
		self.token = token
		self.name = None

		self.address = address
		self.con = message.Message(connection, '', '') # Use as a socket connection

		self.in_game = False # Set to false when initialization is complete
		self.timed_out = False
		self.score = 0
		self.matches = 0

		self.glicko = 1500 # Rating systems yay

	def is_ready(self):
		return self.name is not None and not self.in_game and not self.timed_out

	def timeout(self):
		self.timed_out = True

	def untimeout(self):
		self.timed_out = False
