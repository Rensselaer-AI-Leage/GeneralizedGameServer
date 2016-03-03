'''
@param throw1 string single character: r, p, or s
@param throw2 string single character: r, p, or s
@return int -1 for draw, else which player wins
'''
def game(*throw):
	#hope there are only 2 players
	throw0, throw1 = tuple([i[1].lower() for i in throw])
	#throw0, throw1 = throw0.lower(), throw1.lower()
	if throw0 not in list('rps'): throw0 = 't'
	if throw1 not in list('rps'): throw1 = 't'
	result = throw0 + throw1
	if result in 'tt rr pp ss'.split():
		return -1 #draw
	elif throw1 == 't' or result in 'rs sp pr'.split():
		return 0 #player 0 wins
	elif throw0 == 't' or result in 'rp ps sr'.split():
		return 1 #player 1 wins
