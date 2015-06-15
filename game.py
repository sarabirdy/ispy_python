import logging as log

class Game:
	"""
	Main class that handles game logic
	"""

	def play(self):
		"""
		Play the game
		"""
		log.info('Playing game %d', self.number)


	def __init__(self, number, cursor):
		self.number = number
		self.cursor = cursor
