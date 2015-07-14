import os
import sys
import time
import logging as log

from game import Game
import models
import questions
import database as db

class Main:

	def __init__(self):
		"""
		Entry point of the simulation
		"""

		self._config()
		import config

		self.number_of_objects = 17 #will eventually be adding unknown objects, so this will change based on the number of objects in the field
		self._init_logger()

		db.init_driver()
		db.connect(config.db['address'], config.db['username'], config.db['password'], config.db['database'], unix_socket=config.db['socket'])

		if config.setup:
			self.setup()

		start = time.time()
		self.simulate()
		end = time.time()

		log.info('Simulation complete! (Took %ds)', int(end - start))


	def simulate(self):
		"""
		Run the simulation
		"""

		log.info('Starting simulation')

		games_folder = os.getcwd() + '/Human_Games'

		wins = 0
		losses = 0
		num_questions = 0
		avg_win = 0
		avg_lose = 0
		questions_asked = {}
		question_answers = {}

		for number in range(16, 31):
			game = Game(number)

			game_wins, game_losses, game_num_questions, game_win_avg, game_lose_avg, game_answers, game_questions = game.playGame(self.number_of_objects)

			questions_asked[game.id] = game_questions
			question_answers[game.id] = game_answers
			wins += game_wins
			losses += game_losses
			num_questions += game_num_questions
			avg_win += game_win_avg
			avg_lose += game_lose_avg

			models.build(game, 3, self.number_of_objects, questions_asked, question_answers)


	def setup(self):
		"""
		Perform optional pre-simulation tasks
		"""

		log.info('Performing setup')
		db.cursor.execute('DELETE FROM Pqd')
		db.connection.commit()
		questions.copy_into_answers()
		questions.build_pqd(self.number_of_objects)

		# Necessary to build the very first models
		models.build(Game(0), 3, self.number_of_objects)

		# We then train the models using games 1-15
		models.build(Game(15), 3, self.number_of_objects)


		#for number in range(16, 31):
		#	models.evaluation_1(Game(number), self.number_of_objects)

	def _init_logger(self):
		"""
		Setup logger
		"""

		log.basicConfig(level='DEBUG', format='[ %(levelname)-5.5s]  %(message)s')
		rootLogger = log.getLogger()

		fileFormatter = log.Formatter('%(asctime)s [ %(levelname)-5.5s]  %(message)s')
		fileHandler = log.FileHandler('log.txt')
		fileHandler.setFormatter(fileFormatter)
		rootLogger.addHandler(fileHandler)

		log.info('\n'*8 + '='*31 + '| NEW SIMULATION |' + '='*31 + '\n')

	def _config(self):
		"""
		Imports config.py or generates a default one if it doesn't exist
		"""

		try:
			import config
		except ImportError:
			print "config.py doesn't exist. Generating..."
			f = open('config.py', 'w')
			f.write("db = {\n\t'address': 'localhost',\n\t'username': 'root',\n\t'password': 'root',\n\t'database': 'iSpy_features',\n\t'socket': '/var/run/mysqld/mysqld.sock'\n}\n\nsetup = False")
			f.close()
			print 'Edit config.py and restart'
			sys.exit(0)



if __name__ == '__main__':
	Main()
