import math
import time
import logging as log

import numpy as np

import tags
import database as db

_questions = []
_descriptions = []


def ask(question_id, object, game, answer_data, answers, pO, Pi, p_tags, objects):
	# Takes best question and updates all object probabilies based on the answer

	probabilityD = get_tval()
	question_tag = tags.get(question_id)
	#answer = raw_input("Does it have " + tags[question_id-1] + "? (yes/no) ")
	#answer = answer.lower()
	answer = answer_data[object.id-1][question_id-1]
	#print game_folder, object.id,objectlist[object.id-1][0],'qt->'+question_tag+' ' ,'ans->'+answer


	for objectID in range(0, 17):
		T = get_t(objectID+1, question_id)
		N = objects[objectID][question_id][0]
		D = objects[objectID][question_id][1]

		if answer == 'yes':
			answers.append(True)
			K = probabilityD[T] + (N + 1)/(D + 2.0)
			if Pi[0][question_id-1] == -1:
				multiplier = K / 2
			else:
				multiplier = (K + Pi[objectID][question_id-1]) / 3
		else:
			answers.append(False)
			K = (1 - probabilityD[T]) + (D - N + 1)/(D + 2.0)
			if Pi[0][question_id-1] == -1:
				multiplier = K / 2
			else:
				multiplier = (K + 1 - Pi[objectID][question_id-1]) / 3

		pO[objectID] = pO[objectID] * multiplier
	
	# Normalize the probabilities so that all object probabilities will sum to 1
	pO = pO / np.sum(pO)

	# Save the qustions to each answer and the updated probabilities
	with open("example.txt", "a") as myfile:
		myfile.write(question_tag + " -> " + answer+ " \n")
		myfile.write(str(pO) + "\n")

	return pO, answers


def get_p_tags():
	# The P tag is the number of times a question has been answered true for a specific object
	# IE black and scissors has its own P tag
	p_tags = []

	db.cursor.execute('SELECT qid, answer, COUNT(*) FROM answers GROUP BY qid, answer')
	for row in db.cursor.fetchall():
		if len(p_tags) == row[0]-1:
			p_tags.append({0: 0, 1: 0})
		p_tags[row[0]-1][row[1]] = row[2]

	return p_tags


def get_best(game, objects, asked_questions, pO, Pi, p_tags, start):
	# Finds the question that best splits our current subset of objects
	tvals = get_tval()

	# Get top and bottom halves of current subset
	top = (17 - start - 1)/2 + start + 1
	bottom = 17 - top
	bestDifference = 10
	bestD = 0

	probabilities_yes = []
	probabilities_no = []
	for i in range(0, 17):
		probabilities_yes.append(0)
		probabilities_no.append(0)

	# We only consider objects beyond the start index when deciding
	# Objects below the index are still updated when the question is asked and can shift back into play, but decisions are not made based on them while they're below start
	pO_sorted = np.argsort(pO)
	objects_considered = pO_sorted[start:]
	for i in range(0,len(objects_considered)):
		objects_considered[i] += 1

	# Look over all tags
	for j in range(1, 290):
		yes = 0
		no = 0

		p_for_yes = 0
		p_for_no = 0

		pi_given_yes_times_log = 0
		pi_given_no_times_log = 0

		# Don't reask questions
		if j not in asked_questions:
			# Only look at objects in the correct subset
			for i in objects_considered:

				T = get_t(i, j)
				num_yes = objects[i-1][j][0]
				length = objects[i-1][j][1]

				if Pi[i-1][j-1] == -1:
					probabilities_yes[i-1] = pO[i-1] * (tvals[T] + (num_yes + 1.0)/(length + 2.0)) / 2
					probabilities_no[i-1] = pO[i-1] * ((1 - tvals[T]) + (length - num_yes + 1.0)/(length + 2.0)) / 2
				else:
					probabilities_yes[i-1] = pO[i-1] * (tvals[T] + (num_yes + 1.0)/(length + 2.0) + Pi[i-1][j-1]) / 3
					probabilities_no[i-1] = pO[i-1] * ((1 - tvals[T]) + (length - num_yes + 1.0)/(length + 2.0) + 1 - Pi[i-1][j-1]) / 3

			# Normalize the probabilities
			probabilities_yes = np.asarray(probabilities_yes)
			probabilities_no = np.asarray(probabilities_no)
			probabilities_yes = probabilities_yes / sum(probabilities_yes)
			probabilities_no = probabilities_no / sum(probabilities_no)

			# Do some fancy math to find out which tag lowers total entropy the most (AKA it gives us the most knowledge)
			for i in objects_considered:
				num_yes = objects[i-1][j][0]
				length = objects[i-1][j][1]

				p_for_yes += pO[i-1] * num_yes / length
				p_for_no += pO[i-1] * (length - num_yes) / length

				yes  += probabilities_yes[i-1]
				no += probabilities_no[i-1]

				pi_given_yes_times_log += probabilities_yes[i-1] * math.log(probabilities_yes[i-1], 2)
				pi_given_no_times_log += probabilities_no[i-1] * math.log(probabilities_no[i-1], 2)

			entropy = -p_for_yes * pi_given_yes_times_log - p_for_no * pi_given_no_times_log
			if entropy < bestDifference:
				bestD = j
				bestDifference = entropy

	return bestD


def copy_into_answers():
	# QuestionAnswers holds just the answer set data
	# Copies the pure data into a table that will be appended to throughout gameplay
	log.info('Copying into answers')
	db.cursor.execute('SELECT tag, answer, object from QuestionAnswers')
	results = db.cursor.fetchall()

	for result in results:
		db.cursor.execute('SELECT id from Tags where tag = %s', (result[0],))
		qid = db.cursor.fetchone()[0]
		db.cursor.execute('INSERT INTO answers (qid, oid, answer) VALUES (%s, %s, %s)', (qid, result[2], result[1]))

	db.connection.commit()


def build_pqd():
	# Pqd is the probability that an the answer will be yes to a keyword asked about an object where the keyword shows up X number of times in the descriptions
	# Summed over all objects where a keyword shows up X number of times
	log.info('Building Pqd')
	probabilityD = [0,0,0,0,0,0,0]
	denominator = [0,0,0,0,0,0,0]

	all_tags = tags.get_all()

	for objectID in range(1,18):
		log.info("	Object %d", objectID)
		for tag in range(0, 289):
			db.cursor.execute('SELECT * FROM Descriptions WHERE description like "%' + all_tags[tag] + '%" AND objectID = ' + str(objectID))
			T = len(db.cursor.fetchall())

			#T is a based on a tag and an object description. T is how many times a tag is used in an object's description. It can be 0-6

			db.cursor.execute('SELECT * FROM QuestionAnswers WHERE tag = "' + all_tags[tag] + '" AND object = ' + str(objectID) + ' AND answer = TRUE')
			count = len(db.cursor.fetchall())

			#count is the number of times someone answered yes to a tag/object pair

			db.cursor.execute('SELECT * FROM QuestionAnswers WHERE tag = "' + all_tags[tag] + '" AND object = ' + str(objectID))
			D = len(db.cursor.fetchall())

			#D is the total number of times a tag/object pair has been asked (yesses and nos)

			probabilityD[T] = probabilityD[T] + count
			denominator[T] = denominator[T] + D
		#For the T value based on the specific tag/object pair, update the probability of all tag/object pairs with the same T value
		    
	for freq in range(0,7):
		#This puts the sum of the yes answers and the total answers into the row that corresponds with the T value
		db.cursor.execute('INSERT INTO Pqd (t_value, yes_answers, total_answers) VALUES (%s, %s, %s)', (freq, probabilityD[freq], denominator[freq]))
		db.connection.commit()
		print probabilityD[freq]


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


def get_tval():
	db.cursor.execute('SELECT yes_answers/total_answers FROM Pqd')

	result = db.cursor.fetchall()

	tvals = []
	for r in result:
		tvals.append(float(r[0]))

	# Basically a list of 14 proportions of yes answers. 1 entry per t_value
	return tvals


def get_t(object_id, question_id):
	global _descriptions

	if not _descriptions:
		_descriptions = [{} for _ in range(17)]
		all_tags = tags.get_all()
		db.cursor.execute('SELECT description, objectID, descNum FROM Descriptions')
		for row in db.cursor.fetchall():
			for tag in all_tags:
				if tag in row[0]:
					if not tag in _descriptions[row[1]-1]:
						_descriptions[row[1]-1][tag] = 1
					else:
						_descriptions[row[1]-1][tag] += 1

	tag = tags.get(question_id)
	object_id = int(object_id)
	o = _descriptions[object_id-1]
	if not tag in o:
		return 0
	return o[tag]