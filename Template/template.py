'''
Template RPS script. Feel free to write everything from scratch, but if you do
use this, all you need to edit is the rps_strategy function
'''

import random

from helper import BotHelper

_TEAM_NAME = "YourName" # Note: change this to your team's name

####################################

'''
@description: Decides which move to make
@param history list<string> all the moves your opponent has made so far
@return string your move, 'R', 'P', or 'S'
'''
def strategy(history):
	#YOUR CODE HERE#
	#

	return random.choice(list('rps'))
	# ... or just use a random strategy, if you're lame...

	#
	#END YOUR CODE#

####################################

# Initilize the connection
bot = BotHelper(_TEAM_NAME, strategy)

raw_input("Press the any key to finish.")
