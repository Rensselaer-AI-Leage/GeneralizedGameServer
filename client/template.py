'''
Template RPS script. Feel free to write everything from scratch, but if you do
use this, all you need to edit is the rps_strategy function
'''

import random

from bot_helper import *

# Note: change this to your team's name
_TEAM_NAME = "YourName_" + str(random.randrange(1000))

################################################################################

'''
@description: Decides which move to make
@param history list<string> all the moves your opponent has made so far
@return string your move, 'R', 'P', or 'S'
'''
def strategy(history=None):
	# Extract moves from history
	if history is not None:
		history = [move.split(';')[1] for move in history]

	#YOUR CODE HERE#
	#

	return random.choice(list('rps')) # or just make random moves, if you're lame

	#
	#END YOUR CODE#

################################################################################

# Initilize the connection
bot = BotHelper(_TEAM_NAME, strategy)

raw_input("Press the any key to finish. ")
