class Player:
	self.rating = 1500  # Actual rating
	self.rd = 350       # Rating deviation
	self.sigma = 0.06   # Volatility

	self.mu = None
	self.phi = None

class Glicko2:
	self.tau = 1.0 # Should be between 0.3 and 1.2, use higher numbers for more predicatable games

	def step2(self, player):
		player.mu = (player.rating-1500)/173.7178
		player.phi = player.sigma/173.7178

	def g(phi):
		return 1/math.sqrt(1 + 3*phi*phi/9.86960440109) # 9.869... is Pi squared

	def E(mu, mu_j, phi_j):
		return 1/(1 + math.exp(-1 * g(phi_j) * (mu - mu_j)))

	def step3(self, player, opponents):
		v = 0
		for opponent in opponents:
			e_j = E(player.mu, opponent.mu, opponent.phi)
			v += g(opponent.phi)**2 * e_j * (1 - e_j)
		return v

	# Outcomes is an associative array from opponent id to outcome
	def step4(self, player, opponents, outcomes):
		d = 0
		for (opponent in opponents):
			e_j = E(player.mu, opponent.mu, opponent.phi)
			d += g(opponent.phi)*(outcomes[opponent.id] - e_j)
		d = v*d
