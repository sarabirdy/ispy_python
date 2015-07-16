import os
import time
import logging as log
import getpass
import argparse

from game import Game
import models
import questions
import database as db
import robot

config = None

class Main:

	def __init__(self):
		"""
		Entry point of the simulation
		"""

		global config
		config = self._config()

		self.number_of_objects = 17 #will eventually be adding unknown objects, so this will change based on the number of objects in the field
		self.use_image_models = config.args.imagemodels

		if config.args.robot:
			robot.connect(config.args.address)

		self._init_logger()

		db.init_driver()
		db.connect(config.args.dbaddress, config.args.username, config.args.password, config.args.database, unix_socket=config.args.socket)

		if config.args.setup:
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

		sim = config.args.notsimulated
		using_robot = config.args.robot

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

			if self.use_image_models:
				models.build(game, 3, self.number_of_objects, questions_asked, question_answers)
			if sim:
				quit = None
				while quit != "yes" and quit != "no":
					if using_robot:
						quit = robot.r.ask("Would you like to stop playing completely? There are %d games left. " % (30 - number))
					else:
						quit = raw_input("Would you like to stop playing completely? (yes/no) \nThere are %d games left. " % (30 - number))
						quit = quit.lower()

				if quit == "yes":
					break
		log.info("Overall Wins: %d Overall Losses: %d", wins, losses)
		log.info("Overall Accuracy: %d%%", int((float(wins)/(wins + losses)) * 100))
		if wins != 0:
			log.info("Average number of questions for a win: %.2f", float(avg_win)/wins)
		if losses != 0:
			log.info("Average number of questions for a loss: %.2f", float(avg_lose)/losses)


	def setup(self):
		"""
		Perform optional pre-simulation tasks
		"""

		log.info('Performing setup')
		db.cursor.execute('DELETE FROM Pqd')
		db.connection.commit()
		db.cursor.execute('DELETE FROM answers')
		questions.copy_into_answers()
		questions.build_pqd(self.number_of_objects)
		if self.use_image_models:
			models.build(Game(0), 3, self.number_of_objects)
			models.build(Game(15), 3, self.number_of_objects)


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
		Also parses command line arguments
		"""

		try:
			import config
		except ImportError:
			f = open('config.py', 'w')
			f.write("db = {\n\t'address': 'localhost',\n\t'username': 'root',\n\t'password': 'root',\n\t'database': 'iSpy_features',\n\t'socket': '/var/run/mysqld/mysqld.sock'\n}\n\nrobot = {\n\t'address': 'bobby.local'\n}")
			f.close()
			import config

		parser = argparse.ArgumentParser()
		parser.add_argument("-i", "--imagemodels", action="store_true", help="use image models")
		parser.add_argument("-s", "--setup", action="store_true", help="run setup")
		parser.add_argument("-n", "--notsimulated", action="store_true", help="user provides responses")
		parser.add_argument("-u", "--username", help="database username", default=config.db["username"])
		parser.add_argument("-p", "--password", help="database password", default=config.db["password"])
		parser.add_argument("-d", "--database", help="choose which database to use", default=config.db["database"])
		parser.add_argument("-a", "--dbaddress", help="address of MySQL server", default=config.db["address"])
		parser.add_argument("-t", "--socket", help="path to MySQL socket", default=config.db["socket"])
		parser.add_argument("-r", "--robot", action="store_true", help="runs code using robot")
		parser.add_argument("--address", help="the robot's ip address", default=config.robot["address"])

		args = parser.parse_args()

		if args.robot:
			args.notsimulated = True

		config.args = args

		return config

if __name__ == '__main__':
	Main()
