'''
Template GENERIC script. Feel free to write everything from scratch, but if you
do use this, all you need to edit is the strategy function


In order to run this:
1. copy template to bots/<game>/<your_script_name>
2. python -m bots.<game>.<your_script_name> <server> <port>

'''

import random

from bot_helper import *

# Note: change this to your team's name
_TEAM_NAME = "YourName_" + str(random.randrange(1000))

################################################################################

'''
@description: Decides which move to make
@param history list<string> all the moves your opponent has made so far
@return string your move
'''
def strategy(history=None):
	# Extract moves from history
	if history is not None:
		history = [move.split(';')[1] for move in history]

	#YOUR CODE HERE#
	#

	print len(history)
	return random.choice(list('qwertyuiopasdfghjklzxcvbnm')) # or just make random moves, if you're lame

	#
	#END YOUR CODE#

################################################################################

# Initilize the connection
bot = BotHelper(_TEAM_NAME, strategy)

raw_input("Press the any key to finish. ")
