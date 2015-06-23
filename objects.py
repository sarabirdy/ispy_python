import os
import time
import logging as log

import numpy as np

import questions
import tags
import database as db

_objects = []

class Object:

	def play(self, game, Pi):
		"""
		Play this object
		"""

		log.info('Playing object %d in game %d', self.id, game.id)
		# Generate dictionary of initial probabilities in the form of
		# {object_id: {question_id: [0/1, 0/1]}}, e.g.:
		# {1 : {1: [0 0 1], 2: [1 0 1], ... 289: [0 0 0 1]} ... 17: {...}}
		objects = self.gen_init_prob()

		folder =  os.getcwd()

		# Get values necessary to score tag/objects for a Pqd value
		p_tags = questions.get_p_tags()

		# Get answer data for question/object pairs from specific games (1-30)
		# Should really all be coming from DB since they're all there, anyway
		answer_data = np.genfromtxt(folder+'/Answers/Game'+str(game.id)+'.csv',dtype=str, delimiter='\t')
		NoOfQuestions = 0
		#game_folder = all_games + '/Game' + str(gameID)

		#print "+++++++++++++++" + game_folder + "+++++++++++++++"

		# All objects start as equally likely
		# pO is an array of probabilities. Index corresponds to object value corresponds to probability [0, 1]
		pO = np.array([1/17.0] * 17)

		askedQuestions = []
		answers = []
		split = 0
		#answer_data = np.genfromtxt('/local2/awh0047/iSpy/ispy_python/Answers/Game' + str(gameID) + '.csv',dtype=str, delimiter='\t')

		# The most likely object must be .15 more likely than the second most likely object before the system will make a guess
		# We call this the 'confidence threshold'
		# Basically sorts the probabilities and gets the largest (pO.size - 1) and second-largest (pO.size - 2),
		# and checks continues [asking questions]? until their difference is >= 0.15
		log.info('Asking questions')
		while np.sort(pO)[pO.size - 1] - np.sort(pO)[pO.size - 2] < 0.15:
			# Find best question (aka gives most info)
			best_question = questions.get_best(game, objects, askedQuestions, pO, Pi, p_tags, split)
			# Save under questions already asked
			askedQuestions.append(best_question)
			# Get updated probabilies based on the answer to the question
			pO, answers = questions.ask(best_question, self, game, answer_data, answers, pO, Pi, p_tags, objects)
			# Split the current subset into two more subsets
			split = questions.get_subset_split(pO)
		log.info('Finished asking %d questions', len(askedQuestions))

		# Get most likely object
		minimum=np.max(pO)
		itemindexes =[i for i,x in enumerate(pO) if x==minimum]
		A = np.asarray([[o] for o in get_all()])
		guess = A[itemindexes][0][0]

		# Guess object (Compare what the system thinks is most likely to object currenly in play)
		result = self._guess_object(guess)

		# Save results
		self._record_results(game, answers, askedQuestions, guess, result)

		return result, len(askedQuestions), answers, askedQuestions


	def gen_init_prob(self):
		"""
		Fetches the proportions of yes answers
		Returns a list containing 17 sub-lists, each list corresponding to an object
		Each sub-list contains 289 tuples, one per question
		Each tuple is in the form of (yes_answers, total_answers)
		"""

		log.info('Generating initial probabilities')
		objects = [[]] * 17

		db.cursor.execute('SELECT qid, oid, SUM(answer), COUNT(*) FROM answers GROUP BY oid, qid')
		for row in db.cursor.fetchall():
			objects[row[1]-1].append((int(row[2]), int(row[3])))

		return objects


	def _record_results(self, game, game_answers, game_questions, guess, result):
		"""
		Puts results into the DB as well as writing them to file for examination
		"""

		log.info('Recording object results')
		for i in range(0, len(game_questions)):
			T = questions.get_t(self.id, game_questions[i])
			if game_answers[i] == True:
				db.cursor.execute("SELECT yes_answers FROM Pqd where t_value = %s", (T,))
				yes_count = db.cursor.fetchone()[0]
				#print yes_count, 'yes'
				db.cursor.execute("UPDATE Pqd SET yes_answers = %s WHERE t_value = %s", (yes_count + 1, T))

			db.cursor.execute("SELECT total_answers FROM Pqd where t_value = %s", (T,))
			total_count = db.cursor.fetchone()[0]
			#print total_count
			db.cursor.execute("UPDATE Pqd SET total_answers = %s WHERE t_value = %s", (total_count + 1, T))

			db.cursor.execute("INSERT INTO answers (oid, qid, answer) VALUES (%s, %s, %s)", (str(self.id), game_questions[i], game_answers[i]))

			db.connection.commit()

		if result == 0:
			result = 'lose'
		else:
			result = 'win'

		with open("game.txt", "a") as myfile:
			myfile.write(str(game.id)+','+ str(self.id) +','+ str(guess.name)+"," + str(len(game_questions)) + "," + result  +  "\n")
		myfile.close()

		with open("answers.txt", "a") as answerfile:
			answerfile.write("\n" + str(game.id) + " " + str(self.id) + " " + result + "\n")
			for i in range(0, len(game_questions)):
				answerfile.write(tags.get(game_questions[i]) + " -> " + str(game_answers[i]) + "\n")
		answerfile.close()


	def _guess_object(self, guess):
		"""
		Compare the object that the system thinks is most likely to the object currently in play
		"""

		if self.id == guess.id:
			log.info('Win [Guess: %s | Actual: %s]', guess.name, self.name)
			return 1
		else:
<<<<<<< HEAD
		    log.info('Lose [Guess: %s | Actual: %s]', guess.name, self.name)
		    return 0
=======
			log.info('Lose [Guess: %s | Actual: %s]', guess.name, self.name)
			return 0
>>>>>>> 58104511b675b9cd61f5684f8f74a0308d18f8ba


	def __init__(self, id, name):
		self.id = id
		self.name = name


def get(object_id):
	"""
	Get a specific object based on id
	"""
	
	global _objects
	return get_all()[object_id-1]


def get_all():
	"""
	Returns a list of all objects
	"""

	global _objects
	if not _objects:
		db.cursor.execute('SELECT DISTINCT(observation_id), name FROM NameInfo')
		for obj in db.cursor.fetchall():
			_objects.append(Object(obj[0], obj[1]))
	return _objects
			