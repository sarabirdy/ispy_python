import os
import time
import logging as log

import numpy as np

import questions
import tags
import database as db
from robot import robot

_objects = []
_answers = []

class Object:

	def playObject(self, game, Pi, number_of_objects, sim, using_robot):
		"""
		Play this object
		"""

		log.info('Playing object %d in game %d', self.id, game.id)
		objects = self.gen_init_prob(number_of_objects)

		folder =  os.getcwd()
		answer_data = get_all_answers(number_of_objects)
		NoOfQuestions = 0

		pO = np.array([1/float(number_of_objects)] * number_of_objects)

		askedQuestions = []
		answers = []
		split = 0

		while np.sort(pO)[pO.size - 1] - np.sort(pO)[pO.size - 2] < 0.15 and len(askedQuestions) < 15:
			# Find best question (aka gives most info)
			best_question = questions.get_best(game, objects, askedQuestions, pO, Pi, split, number_of_objects)
			# Save under questions already asked
			askedQuestions.append(best_question)
			# Get updated probabilies based on the answer to the question
			pO, answers = questions.ask(best_question, self, game, answers, pO, Pi, objects, number_of_objects, answer_data, sim, using_robot)
			# Split the current subset into two more subsets
			split = questions.get_subset_split(pO, number_of_objects)
		log.info('Finished asking %d questions', len(askedQuestions))

		# Get most likely object
		minimum=np.max(pO)
		itemindexes =[i for i,x in enumerate(pO) if x==minimum]
		A = np.asarray([[o] for o in get_all()])
		guess = A[itemindexes][0][0]

		# Guess object (Compare what the system thinks is most likely to object currenly in play)
		result = self._guess_object(guess, sim, using_robot)

		# Save results
		self._record_results(game, answers, askedQuestions, guess, result, number_of_objects)

		return result, len(askedQuestions), answers, askedQuestions


	def gen_init_prob(self, number_of_objects):
		"""
		Fetches the proportions of yes answers
		Returns a list containing sub-lists, each corresponding to an object
		Each sub-list contains 289 tuples, one per question
		Each tuple is in the form of (yes_answers, total_answers)
		"""

		objects = []
		for i in range(number_of_objects):
			objects.append([])

		obj = 0

		db.cursor.execute('SELECT qid, oid, SUM(answer), COUNT(*) FROM answers GROUP BY oid, qid')
		for row in db.cursor.fetchall():
			objects[int(row[1])-1].append((int(row[2]), int(row[3])))

		return objects


	def _record_results(self, game, game_answers, game_questions, guess, result, number_of_objects):
		"""
		Puts results into the DB as well as writing them to file for examination
		"""

		log.info('Recording object results to the database')
		for i in range(0, len(game_questions)):
			T = questions.get_t(self.id, game_questions[i], number_of_objects)
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
			myfile.write(str(game.id)+','+ str(self.id) +','+ str(guess.name)+"," + str(self.name) + "," + str(len(game_questions)) + "," + result  +  "\n")
		myfile.close()

		with open("answers.txt", "a") as answerfile:
			answerfile.write("\n" + str(game.id) + " " + str(self.id) + " " + result + "\n")
			for i in range(0, len(game_questions)):
				answerfile.write(tags.get(game_questions[i]) + " -> " + str(game_answers[i]) + "\n")
		answerfile.close()


	def _guess_object(self, guess, sim, using_robot):
		"""
		Compare the object that the system thinks is most likely to the object currently in play
		"""
		if sim:
			obj_id, obj_name = get_actual(guess, using_robot)
		else:
			obj_id = self.id
			obj_name = self.name
		if obj_id == guess.id:
			log.info('Win [Guess: %s | Actual: %s]', guess.name, obj_name)
			return 1
		else:
			log.info('Lose [Guess: %s | Actual: %s]', guess.name, obj_name)
			return 0

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

def get_actual(guess, using_robot):

	global _objects
	if using_robot:
		yn = robot().ask("My guess is %s. Was I right?" % guess.name)
	else:
		yn = raw_input("My guess is %s. Was I right? (yes/no) " % guess.name)
		yn = yn.lower()
		while yn != "yes" and yn != "no":
			yn = raw_input("Try typing that again. ")

	if yn == "yes":
		obj_name = guess.name
		obj_id = guess.id
	else:
		if using_robot:
			robot().askObject()
			print "\nObject names:\n"
			for j in range(len(_objects)):
				print _objects[j].name
		obj_name = raw_input("\nWhat was your object? Remember to type it exactly as you saw above. ")
		while True:
			for i in range(len(_objects)):
				if _objects[i].name == obj_name:
					check = True
					obj_id = _objects[i].id
					break
			if check == True:
				break
			obj_name = raw_input("It seems as though you mistyped. Please try typing the name of your object again. ")
	return obj_id, obj_name

def get_all_answers(number_of_objects):
	"""
	Returns a list of sublists pertaining to each game
	For each game's sublist there is a sublist for each object
	Each object's sublist contains the answers for all 289 possible questions about the object
	"""

	global _answers
	if not _answers:
		#_answers = [[[[]] * 289]*number_of_objects] * 15 #number of games
		_answers = []
		#print _answers
		db.cursor.execute('SELECT answer FROM QuestionAnswers')
		questionanswers = db.cursor.fetchall()
		#questionanswers = ((1,),(2,),(3,),(4,),(5,),(6,),(7,),(8,),(9,),(10,),(11,),(12,),(13,),(14,),(15,))
		#print questionanswers
		answercnt = 0

		for gamecnt in range(15):
			_answers.append([])
			for objcnt in range(17):
				_answers[gamecnt].append([])
				for tagcnt in range(289):
					#print "gamecnt, objcnt, tagcnt, answercnt", gamecnt, objcnt, tagcnt, answercnt
					_answers[gamecnt][objcnt].append(int(questionanswers[answercnt][0]))
					#print _answers[gamecnt][objcnt][tagcnt]
					#tagcnt += 1
					answercnt += 1
					#print _answers

		total_length = 0
		for i in range(15):
			for j in range(number_of_objects):
				total_length += len(_answers[i][j])

	return _answers
