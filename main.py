import logging as log

from database import Database
from game import Game

class Main:
	"""
	Entry point of the simulation
	"""

	def __init__(self):
		self._init_logger()
		
		db = Database('localhost', 'root', 'root', 'iSpy_features')
		self.cursor = db.cursor

		self.setup()

		self.simulate()


	def simulate(self):
		"""
		Run the simulation
		"""

		log.info('Starting simulation')

		for number in range(16, 31):
			game = Game(number, self.cursor)
			game.play()


	def setup(self):
		"""
		Perform necessary pre-simulation tasks
		"""

		log.info('Performing setup')

	def _init_logger(self):
		log.basicConfig(level='DEBUG', format='[ %(levelname)-5.5s]  %(message)s')
		rootLogger = log.getLogger()

		fileFormatter = log.Formatter('%(asctime)s [ %(levelname)-5.5s]  %(message)s')
		fileHandler = log.FileHandler('log.txt')
		fileHandler.setFormatter(fileFormatter)
		rootLogger.addHandler(fileHandler)

		log.info('\n'*8 + '='*31 + '| NEW SIMULATION |' + '='*31 + '\n')


if __name__ == '__main__':
	Main()