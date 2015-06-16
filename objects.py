import os
import time
import logging as log

import numpy as np

import questions as _questions
import tags as _tags

_objects = []

class Object:

	def play(self, game, Pi):
		log.info('--Playing object %d in game %d--', self.id, game.id)
		# Generate dictionary of initial probabilities in the form of
		# {object_id: {question_id: [0/1, 0/1]}}, e.g.:
		# {1 : {1: [0 0 1], 2: [1 0 1], ... 289: [0 0 0 1]} ... 17: {...}}
		objects = self.gen_init_prob(game.cursor)

		folder =  os.getcwd()

		# Get values necessary to score tag/objects for a Pqd value
		p_tags = _questions.get_p_tags(game.cursor)

		# Get answer data for question/object pairs from specific games (1-30)
		# Should really all be coming from DB since they're all there, anyway
		log.info('Pulling answer data from .csv')
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
		while np.sort(pO)[pO.size - 1] - np.sort(pO)[pO.size - 2] < 0.15:
			# Find best question (aka gives most info)
			best_question = _questions.get_best(game, objects, askedQuestions, pO, Pi, p_tags, split)
			# Save under questions already asked
			askedQuestions.append(best_question)
			# Get updated probabilies based on the answer to the question
			pO, answers = _questions.ask(best_question, self, game, answer_data, answers, pO, Pi, p_tags, objects)
			# Split the current subset into two more subsets
			split = get_subset_split(pO)

		# Get most likely object
		minimum=np.max(pO)
		itemindexes =[i for i,x in enumerate(pO) if x==minimum]
		A = np.asarray([[o.name] for o in get_all(game.cursor)])
		guess = A[itemindexes]
		guess2say =  guess[0][0]

		# Guess object (Compare what the system thinks is most likely to object currenly in play)
		result = guess_object(pO, self.name, guess2say)

		# Save results
		record_object_results(game, self, answers, askedQuestions, guess2say, result)

		return result, len(askedQuestions), answers, askedQuestions

	#Original takes ~20 seconds (must be used with questions.ask_old)
	def gen_init_prob_original(self, cursor):
		log.info('Generating initial probabilities')
		start = time.time()
		objects = {}

		# Generate list of answers for every question for every object
		for i in range(1, 18):
			objects[i] = self.get_questions_answers(i, cursor)

		end = time.time()
		log.info('Done (%.2fs)', end - start)
		return objects


	#Old takes ~4.72 seconds (must be used with questions.ask_old)
	def gen_init_prob_old(self, cursor):
		log.info('Generating initial probabilities')
		start = time.time()
		objects = {}

		cursor.execute('SELECT qid, oid, answer FROM answers')
		for row in cursor.fetchall():
			if not row[1] in objects:
				objects[row[1]] = {}
			if not row[0] in objects[row[1]]:
				objects[row[1]][row[0]] = []
			objects[row[1]][row[0]].append(row[2])

		end = time.time()
		log.info('Done (%.2fs)', end - start)
		return objects

	#New 
	def gen_init_prob(self, cursor):
		log.info('Generating initial probabilities')
		start = time.time()
		objects = [[]] * 17

		cursor.execute('SELECT qid, oid, SUM(answer), COUNT(*) FROM answers GROUP BY oid, qid')
		for row in cursor.fetchall():
			objects[row[1]-1].append((int(row[2]), int(row[3])))

		end = time.time()
		log.info('Done (%.2fs)', end - start)
		return objects


	def get_questions_answers(self, object_id, cursor):
		# Get question id (which corresponds to an actual text question),
		# object id (which corresponds to an actual object name), and
		# answer (which is a 1 or 0, yes or no)
		# TODO:/NOTE TO SELF:
		#	Right now its keeping track of individual yes/no answers
		#	Wouldn't it be easier to instead keep track of totals?
		cursor.execute('SELECT qid, oid, answer from answers where oid = %s', (object_id))

		results = cursor.fetchall()

		# Make a really big empty dictionary in the form of {1: [], 2: [], ... 289: []}
		# There are 289 questions in the database
		questions_answers = {}
		for i in range(1, 290):
			questions_answers[i] = []

		# Each dict entry corresponds to a question
		# Each entry is a list with a bunch of 1s and 0s
		# 1 dictionary per object, 1 entry per question
		for qid, oid, answer in results:
			for i in range(1, 290):
				if int(qid) == i:
					questions_answers[i].append(int(answer))

		return questions_answers


	def __init__(self, id, name):
		self.id = id
		self.name = name

def get_subset_split(pO):
    # When probabilities ordered least to greatest, returns index of largest difference between probabilities
    # System asks questions to try to split subset in half each time, so the split should move closer to the max probability each time
    bestDifference = 0

    pO_sorted = np.sort(pO)
    pO_args_sorted = np.argsort(pO)

   # for x in range(0,17):
        #print str(pO_args_sorted[x]) + " -> " + str(pO_sorted[x])

    diff = 0
    bestDiff = 0

    for x in range(0, pO_sorted.size-1):
        if pO_sorted[x+1] - pO_sorted[x] > diff:
            diff = pO_sorted[x+1] - pO_sorted[x]
            bestDiff = x

    return bestDiff


def record_object_results(game, object, answers, questions, guess2say, result):
    # Puts results into the DB as well as writing them to file for examination
    log.info("Recording object results")
    cursor = game.cursor
    for i in range(0, len(questions)):
        T = _questions.get_t(object.id, questions[i], cursor)
        #print object_id, questions[i], answers[i]
        if answers[i] == True:
            cursor.execute("SELECT yes_answers FROM Pqd where t_value = %s", T)
            yes_count = cursor.fetchone()[0]
            #print yes_count, 'yes'
            cursor.execute("UPDATE Pqd SET yes_answers = %s WHERE t_value = %s", (yes_count + 1, T))

        cursor.execute("SELECT total_answers FROM Pqd where t_value = %s", (T))
        total_count = cursor.fetchone()[0]
        #print total_count
        cursor.execute("UPDATE Pqd SET total_answers = %s WHERE t_value = %s", (total_count + 1, T))

        cursor.execute("INSERT INTO answers (oid, qid, answer) VALUES (%s, %s, %s)", (str(object.id), questions[i], answers[i]))

        game.db.connection.commit()

    if result == 0:
        result = 'lose'
    else:
        result = 'win'

    with open("game.txt", "a") as myfile:
        myfile.write(str(game.id)+','+ str(object.id) +','+ str(guess2say)+"," + str(len(questions)) + "," + result  +  "\n")
    myfile.close()

    with open("answers.txt", "a") as answerfile:
        answerfile.write("\n" + str(game.id) + " " + str(object.id) + " " + result + "\n")
        for i in range(0, len(questions)):
            answerfile.write(_tags.get(questions[i], cursor) + " -> " + str(answers[i]) + "\n")
    answerfile.close()


def guess_object(pO, object_guess, guess2say):
    # Simply compare the object that the system thinks is most likely to the object currently in play

    if object_guess == guess2say:
        log.info('Win [Guess: %s | Actual: %s]', guess2say, object_guess)
        return 1
    else:
        log.info('Lose [Guess: %s | Actual: %s]', guess2say, object_guess)
        return 0


def get_all(cursor):
	"""
	Returns a list of all objects
	"""

	global _objects
	if not _objects:
		cursor.execute('SELECT DISTINCT(observation_id), name FROM NameInfo')
		for obj in cursor.fetchall():
			_objects.append(Object(obj[0], obj[1]))
	return _objects
			