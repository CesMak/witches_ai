import random

# Author Markus Lamprecht (www.simact.de) 08.12.2019
# A card game named Witches:

# Rules:
#	60	   Cards(4xJoker, 1-14 in Yellow, Green, Red, Blue)
#	Red    Cards give -1 Point (except Red 11)
#	Blue   Cards do nothing    (except Blue 11 if you have it in your offhand deletes all Green -Points)
#	Green  Cards			   (except Green 11 -5 and Green 12 -10 Points)
# 	Yellow Cards do nothing    (except Yellow 11 +5)
#	A joker can be placed anytime otherwise you have to give the same color as the first player
#	Aim:	Have a minimum of minus Points!
# 	Note: Number 15 is a Joker


# TODO:
#       implement Giving cards (2cards to right, 2cards left, 2cards straigth) [for 4 Players]
#		Add additional plus points(2) if your offhand is empty!

#Done:	0.0		Joker working (if played as first or second card)
#				11 does not give a minus point
#				added player style random and minimum


#Links:
# Basic code for Card Games
#	from: https://github.com/eli-byers/Deck-Of-Cards-Python/blob/master/deckofcards.py
# Schafkopf
#	is available at: https://github.com/bornabesic/belot
#	RL: https://github.com/bornabesic/belot/blob/master/players/PlayerRL/policy.py
# BlackJack card game explained with many pytorch algorithms:
#			https://books.google.de/books?id=JUC7DwAAQBAJ&pg=PA98&lpg=PA98&dq=pytorch+card+game&source=bl&ots=FR7Jsuclds&sig=ACfU3U3diiR0kR-zlEWNFg8XNZ4aJiWDcA&hl=de&sa=X&ved=2ahUKEwiHnrqc66XmAhXJZlAKHQFHBuUQ6AEwCHoECAkQAQ#v=onepage&q=pytorch%20card%20game&f=false
# Reinforcement Library for Card Games:
#	https://github.com/datamllab/rlcard
#	Paper: https://arxiv.org/abs/1910.04376
# Question on how to setup the input of a Card Game:
#	https://ai.stackexchange.com/questions/7049/dqn-input-representation-for-a-card-game
#	Answer1: binary
#	Another option is a single (40,) vector, with 0 being "still in deck", 1 being "in hand", 2 being "on table", 3 being "already played".
#	but a common approach for extracting actions is to have one output neuron for each possible action. To select an action, you would pick the one corresponding to the neuron with the highest output response to a given input.

#Stats:
# 		For 4 Players, played 50.000 Rounds
# 		If Player 0 has to start and plays a random card he will have a minus of -6.025 for each game
# 		Not Player 0  random	-5.85 each game
# 		Not Player 0  mini	    -5.80 each game

# RL: Deep Q-Learning Network (DQN) with replay memory
# Actions:	are basically the options of cards that can be played
# State  :  Input of NN
#			Is it my turn?:    											active_player_index
#			What cards are already played?								each players offhand
#			What cards do I have on my hand? What is my currentResult?	currentResult
#			What cards have already been played?						currentInput
#			What options do I have?										currentOptions

# Loss	 :	Evaluates how good is the prediction (action to a specific input (state))
#			NN should minimize this loss.
# Reward :  Given by red cards at each round or at the end of each game!
# NN	 :  3 Hidden Layers,
#			Inputs :
#			Outputs:
#			120 neurons, 3 dropout layers
#			to optimize generalization and reduce overfitting

class card(object):
	def __init__(self, color, val):
		self.color = color
		self.value = val

	# Implementing build in methods so that you can print a card object
	def __unicode__(self):
		return self.show()
	def __str__(self):
		return self.show()
	def __repr__(self):
		return self.show()

	def show(self):
		if self.value == 15:
			val = "Jocker"
		elif self.value == 11:
			val =">>11<<"
		elif self.value == 12 and self.color =="Green":
			val ="°12°"
		else:
			val = self.value
		return str("{} of {}".format(val, self.color))


class deck(object):
	def __init__(self):
		self.cards = []
		self.build()

	# Display all cards in the deck
	def show(self):
		for card in self.cards:
			print(card.show())

	# Generate 60 cards
	def build(self):
		self.cards = []
		for color in ['Green', 'Yellow', 'Blue', 'Red']:
			for val in range(1, 16):
				self.cards.append(card(color, val))

	# Shuffle the deck
	def shuffle(self, num=1):
		length = len(self.cards)
		for _ in range(num):
			# This is the fisher yates shuffle algorithm
			for i in range(length-1, 0, -1):
				randi = random.randint(0, i)
				if i == randi:
					continue
				self.cards[i], self.cards[randi] = self.cards[randi], self.cards[i]
			# You can also use the build in shuffle method
			# random.shuffle(self.cards)

	# Return the top card
	def deal(self):
		return self.cards.pop()


class player(object):
	def __init__(self, name, style=0):
		self.name         = name
		self.hand         = []
		self.offhand      = [] ## contains won cards of each round (for 4 players 4 cards!)
		self.total_result = 0 # the total result as noted down in a book!
		self.player_style = style # 0: play random card, 1: play card with lowest value

	def sayHello(self):
		print ("Hi! My name is {}".format(self.name))
		return self

	# Draw n number of cards from a deck
	# Returns true in n cards are drawn, false if less then that
	def draw(self, deck, num=1):
		for _ in range(num):
			card = deck.deal()
			if card:
				self.hand.append(card)
			else:
				return False
		return True

	# Display all the cards in the players hand
	def showHand(self):
		print ("{}'s hand: {}".format(self.name, self.hand))
		return self

	def discard(self):
		# returns most upper card and removes it from the hand!
		return self.hand.pop()

	def getOptions(self, incolor, orderOptions=0):
		# incolor = None -> Narr was played played before
		# incolor = None -> You can start!
		#	In both cases return all cards!

		options = []
		if incolor is None:
			for i, card in enumerate(self.hand):
				options.append([i, card])
		else:
			for i, card in enumerate(self.hand):
				if card.color == incolor and card.value <15:
					options.append([i, card])

		# if has not color and no joker append all cards!
		if len(options)==0:
			for i, card in enumerate(self.hand):
				options.append([i, card])
		if orderOptions: return sorted(options, key = lambda x: ( x[1].color,  x[1].value))
		return options

	def getMinimumValue(self, options):
		minimum_value = options[0][1].value
		index		  = options[0][0]
		for opt in options:
			[i, card] = opt
			if card.value<minimum_value:
				minimum_value=card.value
				index        = i
		return index

	def playCard(self, incolor):
		options = (self.getOptions(incolor))
		print("Your options:", options)
		card_idx = 0
		if self.player_style==0:
			rand_card = random.randrange(len(options))
			card_idx = options[rand_card][0]
		elif self.player_style==1:
			card_idx = 	self.getMinimumValue(options)
		return self.hand.pop(card_idx)

	def hasYellowEleven(self):
		return self.hasSpecificCard(11, "Yellow")

	def hasRedEleven(self):
		return self.hasSpecificCard(11, "Red")

	def hasBlueEleven(self):
		return self.hasSpecificCard(11, "Blue")

	def hasSpecificCard(self, cardValue, cardColor):
		for stich in self.offhand:
			for card in stich:
				if card.color == cardColor and card.value == cardValue:
					return True
		return False

	def countResult(self):
		negative_result = 0
		for stich in self.offhand:
			for card in stich:
				if card.color == "Red" and card.value <15 and card.value!=11 and card.value and not self.hasRedEleven():
					negative_result -=1
				if card.color == "Red" and card.value <15 and card.value!=11 and card.value and self.hasRedEleven():
					negative_result -=1*2
				if not self.hasBlueEleven():
					if card.color == "Green" and card.value == 11:
						negative_result -= 5
					if card.color == "Green" and card.value == 12:
						negative_result -= 10
		if self.hasYellowEleven():
			negative_result+=5
		return negative_result

	def appendCards(self, stich):
		self.offhand.append(stich)

class game(object):
	def __init__(self, names_player):
		self.names_player      = names_player
		self.nu_players        = len(self.names_player)
		self.current_round     = 0
		self.total_rounds      = int(60/self.nu_players)
		#self.current_score = [0]*self.nu_players # is an attribute of a player!
		self.players           = []  # stores players object
		self.cards_of_round    = []  # stores the cards of this round
		self.active_player     =  0  # stores which player is active (has to give a card)
		self.played_cards      = []  # of one game # see also in players offhand!
		self.first_played_card = None # added for AI-Gamer
		self.card_before	   = None # added for AI-Gamer
		self.ai_player_idx     = 1    # added for AI-Gamer
		self.player_idx        = []   # added for AI-Gamer
		self.start_player      = 0    # added for AI-Gamer
		self.setup_game()

	# generate a Game:
	def setup_game(self):
		myDeck = deck()
		myDeck.shuffle()
		for i in range (self.nu_players-1):
			play = player(self.names_player[i])
			play.draw(myDeck, self.total_rounds)
			self.players.append(play)

		# add one player that plays the minimum card always
		playx = player(self.names_player[i+1], style=1)
		playx.draw(myDeck, self.total_rounds)
		self.players.append(playx)

		for p in self.players:
			p.sayHello()
			p.showHand()
		print("The Deck is now:", myDeck.show(), " empty \n \n")

	def reset_game(self):
		myDeck = deck()
		myDeck.shuffle()
		for player in self.players:
			player.draw(myDeck, self.total_rounds)
			player.total_result +=player.countResult()
			player.offhand = []
		self.played_cards  = []

	def evaluate_winner(self, incolor, cards):
		highest_value = 0
		winning_card = cards[0]
		tmp = 0
		for i, card in enumerate(cards):
			# Note 15 is a Jocker
			if card.value > highest_value and card.color == incolor and card.value<15:
				highest_value = card.value
				winning_card = card
				tmp = i
		return winning_card, tmp

	def getNextPlayer(self):
		if self.active_player < self.nu_players-1:
			self.active_player+=1
		else:
			self.active_player = 0
		return self.active_player

	def playFirstCard(self):
		print("inside play first card")
		self.player_idx = [self.start_player]
		if self.start_player >= (self.nu_players):
			print("Error this player does not exist:", player_to_start, " only", len(self.nu_players), " availabe")
			return None
		self.active_player = self.start_player
		self.first_played_card = self.players[self.active_player].playCard(None)
		self.cards_of_round.append(self.first_played_card)
		self.played_cards.append(self.first_played_card)
		self.card_before = self.first_played_card
		print("Player: ", self.active_player, self.names_player[self.active_player], ":\t", self.first_played_card, " curr result", self.players[self.active_player].countResult())

	def playOtherCard(self):
		print("inside play other card")
		incolor = self.first_played_card.color
		if self.card_before.value == 15: # in case of a Narr!
			incolor = None
		curr_card = self.players[self.active_player].playCard(incolor)
		self.card_before = curr_card
		self.player_idx.append(self.active_player)
		self.played_cards.append(curr_card)
		print("Player: ", self.active_player, self.names_player[self.active_player], ":\t", curr_card, " curr result", self.players[self.active_player].countResult())
		self.cards_of_round.append(curr_card)

	def play_ai_card(self, first_move=0, player_to_start=0):
		print("play ai card")
		if first_move:
			self.player_idx = [player_to_start]
			if player_to_start >= (self.nu_players):
				print("Error this player does not exist:", player_to_start, " only", len(self.nu_players), " availabe")
				return None
			self.active_player = player_to_start
			# TODO:
			self.first_played_card = self.players[self.active_player].playCard(None)
			#
			self.cards_of_round.append(self.first_played_card)
			self.played_cards.append(self.first_played_card)
			self.card_before = self.first_played_card
			self.players[self.active_player].countResult()
		else:
			incolor = self.first_played_card.color
			if self.card_before.value == 15: # in case of a Narr!
				incolor = None
			# TODO:
			curr_card = self.players[self.active_player].playCard(incolor)
			#
			self.card_before = curr_card
			self.player_idx.append(self.active_player)
			self.played_cards.append(curr_card)
			print("Player: ", self.active_player, self.names_player[self.active_player], ":\t", curr_card, " curr result", self.players[self.active_player].countResult())
			self.cards_of_round.append(curr_card)

	def finishRound(self, player_to_start = 0, state_for_ai_move=None):
		print("inside finish Round!")

		#AI has first move?
		if len(self.cards_of_round) == 0:
			print("AI has first move")
			self.play_ai_card(player_to_start, first_move=1)

			# do other moves:
			for i in range(self.nu_players-len(self.cards_of_round)):
				self.active_player = self.getNextPlayer()
				self.playOtherCard()
		else:
			for i in range(self.nu_players-len(self.cards_of_round)):
				if i != 0: self.active_player = self.getNextPlayer()
				if self.active_player == self.ai_player_idx:
					print("return go out here with state! Its now ai players turn")
					self.play_ai_card(first_move=0)
					return
				else:
					self.playOtherCard()
		# give score etc back here!
		#reset round (player_to_start etc!) -> evaluate winner!

	def play_round_until_ai(self):
		print("inside play_round_until_ai round")

		# First Move:
		if self.active_player != self.ai_player_idx:
			self.playFirstCard()
		else:
			print("Get out of here?! Its now ai players turn")
			return

		# Other Moves:
		for i in range(1, self.nu_players):
			self.active_player = self.getNextPlayer()
			if self.active_player == self.ai_player_idx:
				print("return go out here with state! Its now ai players turn")
				return
			else:
				self.playOtherCard()

	def play_round(self, player_to_start=0):
		player_idx = [player_to_start] # to evaluate the next player!

		#1. Active Player plays a card:
		if player_to_start >= (self.nu_players):
			print("Error this player does not exist:", player_to_start, " only", len(self.nu_players), " availabe")
			return None
		self.active_player = player_to_start
		first_played_card = self.players[self.active_player].playCard(None)
		self.cards_of_round.append(first_played_card)
		self.played_cards.append(first_played_card)
		print("Player: ", self.active_player, self.names_player[self.active_player], ":\t", first_played_card, " curr result", self.players[self.active_player].countResult())

		card_before = first_played_card
		for i in range(1, self.nu_players):
			#2. Next Player plays a card which is allowed!
			incolor = first_played_card.color
			if card_before.value == 15: # in case of a Narr!
				incolor = None
			self.active_player = self.getNextPlayer()
			curr_card = self.players[self.active_player].playCard(incolor)
			card_before = curr_card
			player_idx.append(self.active_player)
			self.played_cards.append(curr_card)
			print("Player: ", self.active_player, self.names_player[self.active_player], ":\t", curr_card, " curr result", self.players[self.active_player].countResult())
			self.cards_of_round.append(curr_card)

		winning_card, i = self.evaluate_winner(first_played_card.color, self.cards_of_round)
		next_player = player_idx[i]
		print("Wining Card:", winning_card, "Player that won:", next_player)
		self.players[next_player].appendCards(self.cards_of_round)
		self.cards_of_round = []
		self.current_round +=1
		return next_player # give the player back which plays next!

	def getCardIndex(self, card):
		result_idx = 0
		if card.color == "Blue":
			result_idx = card.value-1
		elif card.color =="Green":
			result_idx =15+card.value-1
		elif card.color =="Red":
			result_idx = 15*2+card.value-1
		elif card.color =="Yellow":
			result_idx = 15*3+card.value-1
		return result_idx

	def getState(self):
		# get Current State as bool (binary) values
		# 15*4 card x is currently on the table				see self.cards_of_round
		# 15*4 card x is currently in ai hand				see self.player.hand
		# 15*4 card x is already in offhand (being played)	see self.played_cards
		# sort by: (alphabet:) Blue, Green, Red, Yellow
		# 180 Input vector!
		state = [0]*180
		print("inside get Current State, len(state):", len(state))
		for card in self.cards_of_round:
			state[self.getCardIndex(card)]    = 1

		for card in self.players[self.ai_player_idx].hand:
			state[self.getCardIndex(card)+60] = 1

		for card in self.played_cards:
			state[self.getCardIndex(card)+120] = 1
		return state

	def play_one_game(self, start_player=0):
		j = 0
		for i in range(0, self.total_rounds):
			print("\nRound", i, "Player to start:", j)
			j = self.play_round(player_to_start=j)

		print("\nGame finished with:")
		for player in self.players:
			print(player.name, "Hand:", player.hand, "Result:", player.countResult(), "\noffHand:", player.offhand, "\n\n")

		return self.getNextPlayer()

	def play_multiple_games(self, nu_games):
		curr_player = 0
		for i in range(0, nu_games):
			print("\nGame", i, "Player to start:", curr_player)
			curr_player = self.play_one_game(start_player=curr_player)
			self.reset_game()

		for player in self.players:
			print(player.name, "\tTotal Result:", player.total_result)

# my_game = game(["Tim", "Bob", "Lena", "Anja"])
# my_game.play_round_until_ai(player_to_start=2)
#my_game.play_multiple_games(1)
