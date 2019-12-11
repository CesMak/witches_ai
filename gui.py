from threading import Thread
from queue import Queue, Empty
import pygame
import time
from enum import Enum, auto
from witches_game import card, deck, player, game

_screenSize = _screenWidth, _screenHeight = (1300, 700)

_path_to_card_imgs = "game_gui/cards"

BACKGROUND = (15, 105, 25)
WHITE = (255, 255, 255)

class GUI(Thread):

	class MessageType(Enum):
		SURFACE = auto()
		EMPTY = auto()

	def __init__(self):
		Thread.__init__(self)

		pygame.init()
		pygame.font.init()

		self.queue = Queue()
		self.names = []
		self.list_of_cards = {0: [], 1: [], 2: [], 3: []}
		self.input_cards   = {0: 0, 1: 0, 2: 0, 3: 0}
		self.screen = pygame.display.set_mode(_screenSize)
		pygame.display.set_caption("Witches_by_M.Lamprecht")
		self.screen.fill(BACKGROUND)

	def clear(self):
		self.queue.put((GUI.MessageType.EMPTY,))

	def getCardImage(self, input_card):
			return pygame.image.load(_path_to_card_imgs+"/"+str(input_card.color)+str(input_card.value)+".png")

	def putInputCards(self):
		for key in (self.input_cards):
			card = self.input_cards[key]
			if card!= 0:
				cardImage = gui.getCardImage(card)
				imageWidth, imageHeight = cardImage.get_size()
				x = _screenWidth // 4 + imageWidth/2*key
				y = _screenHeight // 4 + imageWidth/2
				self.queue.put((GUI.MessageType.SURFACE, cardImage, (x, y), card))

	def removeInputCards(self):
		self.clear()
		for i in range(4):
			gui.dealCards(i, self.list_of_cards[i], appendCard=0)
		self.input_cards   = {0: 0, 1: 0, 2: 0, 3: 0}

	def playCard(self, input_card, player=0):
		# kind of a nasty hack:
		self.clear()

		#remove this card from the deck
		self.list_of_cards[player].remove(input_card)

		for i in range(4):
			gui.dealCards(i, self.list_of_cards[i], appendCard=0)
		self.input_cards[player] = input_card
		self.putInputCards()
		time.sleep(1)

	# Render cards
	def cardLeft(self, card, nu_cards=2, index=0):
		cardImage = gui.getCardImage(card)
		imageWidth, imageHeight = cardImage.get_size()
		x = _screenWidth // 7 - imageWidth // 2
		y = _screenHeight // nu_cards+index*37
		self.queue.put((GUI.MessageType.SURFACE, cardImage, (x, y), card))
		self.nameLeft(self.names[3])

	def cardDown(self, card, nu_cards=2, index=0):
		cardImage = gui.getCardImage(card)
		imageWidth, imageHeight = cardImage.get_size()
		x = _screenWidth // nu_cards+index*37+imageWidth  #x = _screenWidth // 2 - imageWidth // 2
		y = (_screenHeight * 4) // 5 - imageHeight // 2
		self.queue.put((GUI.MessageType.SURFACE, cardImage, (x, y), card))
		self.nameDown(self.names[2])

	def cardRight(self, card, nu_cards=2, index=0):
		cardImage = gui.getCardImage(card)
		imageWidth, imageHeight = cardImage.get_size()
		x = (_screenWidth * 4) // 4.6 - imageWidth // 2
		y = _screenHeight // nu_cards+index*37 #y = _screenHeight // 2 - imageHeight // 2
		self.queue.put((GUI.MessageType.SURFACE, cardImage, (x, y), card))
		self.nameRight(self.names[1])

	def cardUp(self, card, nu_cards=2, index=0):
		cardImage = gui.getCardImage(card)
		imageWidth, imageHeight = cardImage.get_size()
		x = _screenWidth // nu_cards+index*37+imageWidth
		y = _screenHeight // 4 - imageHeight // 2
		self.queue.put((GUI.MessageType.SURFACE, cardImage, (x, y), card))
		self.nameUp(self.names[0])

	# Render names
	def nameLeft(self, name):
		nameFont = pygame.font.SysFont("Comic Sans MS", 30)
		nameSurface = nameFont.render(name, False, WHITE)
		nameSurface = pygame.transform.rotate(nameSurface, 90)
		surface_width, surface_height = nameSurface.get_size()
		x = 10
		y = _screenHeight // 2 - surface_height // 2
		self.queue.put((GUI.MessageType.SURFACE, nameSurface, (x, y)))

	def nameDown(self, name):
		nameFont = pygame.font.SysFont("Comic Sans MS", 30)
		nameSurface = nameFont.render(name, False, WHITE)
		surface_width, surface_height = nameSurface.get_size()
		x = _screenWidth // 2 - surface_width // 2
		y = _screenHeight - surface_height - 10
		self.queue.put((GUI.MessageType.SURFACE, nameSurface, (x, y)))

	def nameRight(self, name):
		nameFont = pygame.font.SysFont("Comic Sans MS", 30)
		nameSurface = nameFont.render(name, False, WHITE)
		nameSurface = pygame.transform.rotate(nameSurface, -90)
		surface_width, surface_height = nameSurface.get_size()
		x = _screenWidth - surface_width - 10
		y = _screenHeight // 2 - surface_height // 2
		self.queue.put((GUI.MessageType.SURFACE, nameSurface, (x, y)))

	def nameUp(self, name):
		nameFont = pygame.font.SysFont("Comic Sans MS", 30)
		nameSurface = nameFont.render(name, False, WHITE)
		surface_width, surface_height = nameSurface.get_size()
		x = _screenWidth // 2 - surface_width // 2
		y = 10
		self.queue.put((GUI.MessageType.SURFACE, nameSurface, (x, y)))

	def dealCards(self, player_nu, card_list, nu_players=4, appendCard=1):
		if not nu_players==4:
			print("Error currently just 4 Players allowed!")
			return None
		if player_nu == 0:
			for i, card in enumerate(card_list):
				gui.cardUp(card, nu_cards=len(card_list), index=i)
		elif player_nu == 1:
			for i, card in enumerate(card_list):
				gui.cardRight(card, nu_cards=len(card_list), index=i)
		elif player_nu == 2:
			for i, card in enumerate(card_list):
				gui.cardDown(card, nu_cards=len(card_list), index=i)
		elif player_nu == 3:
			for i, card in enumerate(card_list):
				gui.cardLeft(card, nu_cards=len(card_list), index=i)

		if appendCard:
			self.list_of_cards[player_nu] = card_list

	def run(self):
		# läuft die ganze zeit durch die queue und malt alles was in der queue ist!
		while True:
			# Events
			close = False
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					close = True
					break
			if close:
				break

			# Message queue
			try:
				# following line removes item from queue and if possible adds it to the display
				item = self.queue.get(block = False)
				messageType = item[0]
				# Draw a surface
				if messageType is GUI.MessageType.SURFACE:
					surface = item[1]
					x, y = item[2]
					self.screen.blit(surface, (x, y))
				# Clear the screen
				elif messageType is GUI.MessageType.EMPTY:
					self.screen.fill(BACKGROUND)
			except Empty:
				pass

			# updates entire surface all at once! to new queue!
			pygame.display.flip()

		pygame.display.quit()

if __name__ == "__main__":
	gui = GUI()
	gui.start() # start thread!

	my_game = game(["Tim", "Bob", "Lena", "Anja"])
	gui.names = my_game.names_player
	for i in range(4):
		gui.dealCards(i, my_game.players[i].getHandCardsSorted())

	for j in range(10):
		for i in range(4):
			gui.playCard(my_game.players[i].getHandCardsSorted()[j], player=i)
		time.sleep(1)
		gui.removeInputCards()
