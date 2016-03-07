'''
@param throw1 string single character: r, p, or s
@param throw2 string single character: r, p, or s
@return int -1 for draw, -2 for error, else which player wins
'''
def game(*throw):
	#hope there are only 2 players

	# Unpack the throws (moves)
	throw0, throw1 = tuple([i[1].lower() for i in throw])

	# If you got invalid input, note it as a time-out
	if throw0 not in list('rps'): throw0 = 't'
	if throw1 not in list('rps'): throw1 = 't'

	# Check who won
	result = throw0 + throw1
	if result in 'tt rr pp ss'.split():
		return -1 # Draw
	elif throw1 == 't' or result in 'rs sp pr'.split():
		return 0 # Player 0 wins
	elif throw0 == 't' or result in 'rp ps sr'.split():
		return 1 # Player 1 wins
	else:
		return -2 # Some kind of error that should never happen
