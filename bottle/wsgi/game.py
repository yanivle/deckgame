import random

card_types = []

class Card(object):
	def __init__(self, name, type, cost=0, vp=0, card=0, action=0, buy=0, coin=0, plus_coin=0):
		self.name = name
		self.type = type
		self.cost = cost
		self.vp = vp
		self.card = card
		self.action = action
		self.buy = buy
		self.coin = coin
		self.plus_coin = plus_coin
		card_types.append(self)

	def __repr__(self):
		return '%s (%d)' % (self.name, self.cost)

Card('Estate', 'VP', cost=2, vp=1)
Card('Village', 'ACTION', cost=3, card=1, action=2)
Card('Market', 'ACTION', cost=5, card=1, action=1, buy=1, plus_coin=1)
Card('Copper', 'MONEY', cost=0, coin=1)
Card('Silver', 'MONEY', cost=3, coin=2)
Card('Gold', 'MONEY', cost=6, coin=3)

class Pile(object):
	def __init__(self, card_type, count):
		self.type = card_type
		self.count = count

	def TakeOne(self):
		self.count -= 1
		return self.type

	def __repr___(self):
		return 'Pile(%s, %d)' % (self.type.name, self.count)

class Player():
	def __init__(self, id):
		self.id = id
		self.hand = []
		self.deck = [GetCard('Estate')] * 3 + [GetCard('Market')] * 7
		self.discard = []
		self.in_play = []
		self.SelectHand()

	def StartTurn(self):
		assert not self.in_play, self.in_play
		assert self.hand
		self.actions = 1
		self.buys = 1
		self.debt = 0

	def EndTurn(self):
		self.discard += self.in_play + self.hand
		self.in_play = []
		self.hand = []
		self.SelectHand()

	def SelectHand(self):
		while len(self.hand) < 5:
			card = self.GetCard()
			if not card:
				return
			self.hand.append(card)

	def GetCard(self):
		if not self.deck:
			self.deck = self.discard
			self.discard = []
		if not self.deck:
			return None
		random.shuffle(self.deck)
		return self.deck.pop()

	def GetBuyOptions(self, piles):
		return [pile.type.name for pile in piles if pile.count >= 0 and pile.type.cost <= self.GetMoney()]

	def GetMoney(self):
		return sum(card.coin for card in self.in_play + self.hand) + sum(card.plus_coin for card in self.in_play) - self.debt

	def GetPlayOptions(self):
		return [card_type.name for card_type in self.hand if card_type.type == 'ACTION']

	def Buy(self, pile):
		if not pile:
			self.buys = 0
			return
		self.buys -= 1
		self.debt += pile.type.cost
		self.discard.append(pile.TakeOne())

	def Play(self, name):
		if not name:
			self.actions = 0
			return
		self.actions -= 1
		for i in range(len(self.hand)):
			if self.hand[i].name.lower().startswith(name):
				self.in_play.append(self.hand.pop(i))
				break
		else:
			raise Exception(name)
		type = GetCard(name)
		print 'Playing', type
		print self.in_play
		self.actions += type.action
		self.buys += type.buy
		for i in range(type.card):
			card = self.GetCard()
			if not card:
				return
			self.hand.append(card)

	def VPs():
		return GetVPs(self.deck) + GetVPs(self.in_play) + GetVPs(self.discard) + GetVPs(self.hand)

	def Render(self, active):
		if active:
			return ('Player %s hand: %s ' % (self.id, self.hand) +
					str(self.in_play) + ' ' +
					'deck (%d) discard(%d) money(%d) actions(%d) buys(%d)' % (len(self.deck),
														 					  len(self.discard),
														 					  self.GetMoney(),
																			  self.actions,
																			  self.buys))
		else:
			return ('Player %s hand: %s ' % (self.id, self.hand) +
					'deck (%d) discard(%d)' % (len(self.deck),
											   len(self.discard)))


def GetCard(name_prefix):
	return next((card_type for card_type in card_types if card_type.name.lower().startswith(name_prefix.lower())), None)

class Game():
	def __init__(self):
		self.piles = [Pile(card_type, 10) for card_type in card_types]
		self.name_to_pile = {}
		for pile in self.piles:
			name = pile.type.name
			for i in range(1, len(name) + 1):
				self.name_to_pile[name[:i]] = pile
				self.name_to_pile[name[:i].lower()] = pile
		self.players = [Player(i) for i in range(2)]
		self.turn = random.choice([0, 1])
		self.players[self.turn].StartTurn()
		self.phase = 'ACTION'

	def GameOver(self):
		return len(list(pile for pile in self.piles if pile.count == 0)) >= 3

	def RenderForPlayer(self, player_id):
		options = None
		your_turn = player_id == self.turn
		player = self.players[player_id]
		if your_turn:
			if self.phase == 'ACTION':
				options = player.GetPlayOptions()
			elif self.phase == 'BUY':
				options = player.GetBuyOptions(self.piles)
		return {
			'your_turn': your_turn,
			'phase': self.phase,
			'you': self.players[player_id].Render(your_turn),
			'options': options,
		}

	def Process(self, player_input):
		player = self.players[self.turn]
		if self.phase == 'ACTION':
			player.Play(player_input)
			if not player.actions:
				self.phase = 'BUY'
		elif self.phase == 'BUY':
			pile = next((pile for pile in self.piles if player_input and pile.type.name.lower().startswith(player_input)), None)
			player.Buy(pile)
			if not player.buys:
				player.EndTurn()
				self.turn = (self.turn + 1) % 2
				self.players[self.turn].StartTurn()
				self.phase = 'ACTION'
				if self.GameOver():
					self.phase == 'GAME_OVER'
		elif self.phase == 'GAME_OVER':
			print player[0].VPs()
			print player[1].VPs()
			self.phase = 'END'
		else:
			raise 'Invalid state'

	def Run(self):
		while not self.GameOver():
			print self.turn
			print self.RenderForPlayer(0)
			print self.RenderForPlayer(1)
			self.Process(raw_input("? "))
		'''
		while not self.GameOver():
			player = self.players[self.turn]
			self.turn = 1 - self.turn
			player.StartTurn()
			print '*** Action Phase ***'
			print player
			while player.actions and player.GetPlayOptions():
				player.Play(raw_input('Play: %s' % player.GetPlayOptions()))
				print player
			print '*** Buys Phase ***'
			while player.buys and player.GetBuyOptions(self.piles):
				choice = raw_input('Buy: %s' % player.GetBuyOptions(self.piles))
				pile = next((pile for pile in self.piles if choice and pile.type.name.lower().startswith(choice)), None)
				player.Buy(pile)
				print player
			player.EndTurn()

		print player[0].VPs()
		print player[1].VPs()
'''
Game().Run()
