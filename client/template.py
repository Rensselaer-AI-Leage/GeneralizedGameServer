'''
Template GENERIC script. Feel free to write everything from scratch, but if you
do use this, all you need to edit is the strategy function


In order to run this:
1. copy template.py to bots/<game>/<your_script_name>.py
2. edit the code as you see fit
3. python -m bots.<game>.<your_script_name> <server> <port>
4. there is no step number 4

'''

import random

from bot_helper import *

# Note: change this to your team's name
_TEAM_NAME = "YourName_" + str(random.randrange(1000))

################################################################################

'''
@description: Decides which move to make
@param gamestate ? current game state
@return string your move
'''
def strategy(gamestate=None):
	# Extract moves from gamestate
	if gamestate is not None:
		gamestate = [move.split(';')[1] for move in gamestate]

	#YOUR CODE HERE#
	#

	print len(gamestate)
	return random.choice(list('qwertyuiopasdfghjklzxcvbnm')) # or just make random moves, if you're lame

	#
	#END YOUR CODE#

################################################################################

# Initilize the connection
bot = BotHelper(_TEAM_NAME, strategy)

raw_input("Press the any key to finish. ")
