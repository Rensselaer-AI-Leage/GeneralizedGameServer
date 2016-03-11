'''
@param throws dict<idenifier, string> The string is a move in the game
@return dict<identifier, int> The int is that player's pair from the game, or None on error
'''
def game(throws): #hope there are only 2 players
	# Unpack the throws (moves)
	throw = []
	for key in throws:
		throw.append((key, throws[key]))

	# If you got invalid input, note it as a time-out

	if throw[0][1] not in list('rps'):
		throw01 = 't'
	else:
		throw01 = throw[0][1]

	if throw[1][1] not in list('rps'):
		throw11 = 't'
	else:
		throw11 = throw[1][1]

	# Check who won
	pair = throw01 + throw11
	if pair in 'tt rr pp ss'.split():
		result = [0.5, 0.5] # Draw
	elif throw[1][1] == 't' or pair in 'rs sp pr'.split():
		result = [1, 0] # Player 0 wins
	elif throw[0][1] == 't' or pair in 'rp ps sr'.split():
		result = [0, 1] # Player 1 wins
	else:
		return None # Some kind of error that should never happen

	# Match players to their pair
	out = dict()
	for i, score in enumerate(result):
		cur_player = throw[i][0]
		out[cur_player] = score

	return out

'''
@param score dict<identifier, int> The int is the score from the march
@return list<identifier> The list is in order of rank, i.e. list[0] had the highest score and list[-1] had the lowest
'''
def ranking(scores):
	ranking = []
	for p1 in scores:
		ranked = False
		for rank, p2 in enumerate(ranking):
			if scores[p1] > scores[p2]:
				ranking.insert(rank, p1)
				ranked = True
				break
		if not ranked:
			ranking.append(p1)	
	return ranking

'''
@param score dict<identifier, int> The int is the score from the march
@return dict<identifier, int> The int is that player's match score, for example 1 for win, -1 for loss, 0 for tie
'''
def scoring(scores, delta):
	match_results = {}
	rankings = ranking(scores)
		
	tied = []
	points = 0
	for rank, player in enumerate(rankings):
		tied.append(player)
		points += len(rankings) - 2 * rank - 1
		if(rank + 1 < len(rankings) and scores[player] - scores[rankings[rank+1]] >= delta):
			for p in tied:
				match_results[p] = points / float(len(tied))
			tied = []
			points = 0
		else:
			pass
	for p in tied:
		match_results[p] = points / float(len(tied))	
		
	return match_results
					
					
			
			
