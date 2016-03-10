'''
Template RPS script. Feel free to write everything from scratch, but if you do
use this, all you need to edit is the rps_strategy function
'''

import random

from bot_helper import *

_TEAM_NAME = "Tyler" + str(random.randrange(1000)) # Note: change this to your team's name

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

	# There is approximately a 20% chance that it throws a random move
	if random.randrange(100) > random.randrange(20) or not history:
		return random.choice(list('rps'))

	# Otherwise do whatever their last move beats
	#  Note: this strategy is really bad if they decide to always throw the same thing
	else:
		last_mv = history[-1]
		if last_mv == 'r':
			return 's'
		elif last_mv == 'p':
			return 'r'
		elif last_mv == 's':
			return 'p'

	#
	#END YOUR CODE#

################################################################################

# Initilize the connection
bot = BotHelper(_TEAM_NAME, strategy)

raw_input("Press the any key to finish. ")
