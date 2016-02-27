import collections

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

#replace constants with a config file?

#Server requests to clients
_SERVER =  {'ACK': 'AK',         # check if you're still alive,            proper response: Ack
			'Token': 'ID',       # player's token,                         proper response: Ack
			'GameState': 'GS',   # current gamestate after player moves,   proper response: Ack
			'Result': 'CR',      # cumulative results,                     proper response: Ack
			'Termination': 'TN', # notification of connection termination, proper response: Ack
			'Move': 'MV',        # request for a move,                     proper response: Move
			'Name': 'NM',        # request for your nickname,              proper response: Name
                        'OpMove': 'OM'       # notification of opponent's move,        proper response: Ack
			}
			
#client requests to server (unnecessary?)
_CLIENT =  {'ACK': 'AK',        # make sure you're still alive, proper response: Ack
			'Move': 'MV',       # send the server your move,    proper response: Move or Ack
			'Name': 'NM',       # send the server your name,    proper response: Ack
			'GameState': 'GS'   # request the gamestate,        proper response: GameState
			}

_MSG_LEN = 1024
_MAC_LEN = 256
_NON_LEN = 64
_CYP_LEN = _MSG_LEN + _MAC_LEN

def encode(*tup):
	#tup usually looks like this: (type, body, token)
	return (('%s:' * len(tup))[:-1] % tup).ljust(_MSG_LEN)

def decode(string):
	return tuple(string.strip().split(':'))
	
def encrypt(key, string):
	return string
	
def decrypt(key, string):
	return string
	
def MAC(key, string):
	return  ' ' * _MAC_LEN

def vrfy(key, string, mac):
	return MAC(key, string) == mac

#the best of compression algorithms
comp = '''
def compress(str):
	return str
'''	
exec comp
exec comp.replace('com', 'decom')

	
'''
@description Generates a random string.
@param len integer length of the token to be generated
@return string random token of length len
'''
def gen_token(length):
	#token can be made up of majiscules, miniscules, and integers
	token = ''
	alphabet = list('qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890+_()!@#$%^&*{}[]|<>,.?/~`')
	
	#generate token
	for i in range(length):
		token += random.choice(alphabet)
	
	#most important part
	return token
	
class Message:
	def __init__(self, connection, encrypt_key, vrfy_key):
		self.connection = connection
		self.ekey = encrypt_key
		self.vkey = vrfy_key
		self.msgNum = 0
		self.lastMsgs = collections.deque([])
		#self.lastNonce = collections.deque([])
		
	def send(self, *tup):
		#TODO: fix nonces
		if(len(self.lastMsgs) == 0):
			nonce = gen_token(_NON_LEN)
		else:
			nonce = self.lastMsgs[0][2]
		tup += (nonce)
		msg = compress(encode(*tup))
	        mac = MAC(self.vkey, msg)
		data = msg + mac
	        cyp = encrypt(self.ekey,  data)
		self.lastMsgs.append((self.msgNum, cyp, nonce))
		self.msgNum += 1
		return self.connection.send(cyp)
		
	def recv(self):
		#TODO: fix nonces
		cyp = self.connection.recv(_CYP_LEN)
		data = decrypt(self.ekey, cyp)
		msg = data[:_MSG_LEN]
		mac = data[:-_MAC_LEN]
		if vrfy(key, msg, mac):
			tup = decode(decompress(msg))
			nonceR = tup[-1]
			if(len(self.lastMsgs) == 0):
				self.lastMsgs.append((self.msgNum, cyp, nonce))
				self.msgNum += 1
				return tup[:-1]
			else:
				nonce = self.lastMsgs[0][2]
				if nonceR == nonce:
					self.lastMsgs.pop()
					return tup[:-1]
		return None
		
	def getToken(self):
		pass
		
	def sendID(self, ident):
		pass
		
	def sendACK(self):
		self.send(_SERVER['Ack'])
	
	def sendMove(self, move):
		pass
		
	def sendRequest(self, request):
		self.sendMove(self, request)
		
	def sendName(self, name):
		pass
	
	def sendResults(self, results):
		pass
		
	def sendGameState(self, gamestate):
		pass
		
	
'''
msg.sendACK('abc')
msg.sendMove
'''

# temp
def poll_move(player0, player1):
	# get throws
	try:
		throw0 = player0.recv(1)
	except Exception as t:
		throw0 = 'T'
		
	try:
		throw1 = player1.recv(1)
	except Exception as t:
		throw1 = 'T'
	
	# exchange throws
	try:
		player0.send(throw1)
	except:
		pass
		
	try:
		player1.send(throw0)
	except:
		pass
	
	# return throws
	return (throw0, throw1)