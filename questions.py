import math
import time
import logging as log

import numpy as np

import tags as _tags

_questions = []

def ask(question_id, object, game, answer_data, answers, pO, Pi, p_tags, objects):
	# Takes best question and updates all object probabilies based on the answer

	probabilityD = get_tval(game.cursor)
	question_tag = _tags.all(game.cursor)[question_id-1]
	#answer = raw_input("Does it have " + tags[question_id-1] + "? (yes/no) ")
	#answer = answer.lower()
	answer = answer_data[object.id-1][question_id-1]
	#print game_folder, object.id,objectlist[object.id-1][0],'qt->'+question_tag+' ' ,'ans->'+answer

	if not (answer):
		# Not sure why this is here, it's old code, never seen it actually run
		#print game_folder, object.id,'qt->'+question_tag+' ' ,'sd'+answer+'<-', objectlist[object.id-1][0]

		sys.exit()

	if answer == 'yes' or answer is 'yes':
		answers.append(True)
		# If there's an image model it has positive value, otherwise -1
		# Without image model the probability just updates based on Pq and Pqd
		if Pi[0][question_id-1] == -1:
			for objectID in range(0,17):
				T = get_t(objectID+1, question_id, game.cursor)
				N = objects[objectID][question_id][0]
				D = objects[objectID][question_id][1]
				pO[objectID] = pO[objectID] * (probabilityD[T] + (N + 1)/(D + 2.0)) / 2 #/((p_tags[question_id-1][1] + 1) / float(p_tags[question_id-1][1] + p_tags[question_id-1][0] + 2))
		else:
			for objectID in range(0,17):
				T = get_t(objectID+1, question_id, game.cursor)
				N = objects[objectID][question_id][0]
				D = objects[objectID][question_id][1]
				pO[objectID] = pO[objectID] * ((probabilityD[T] + (N + 1)/(D + 2.0) + Pi[objectID][question_id-1])) / 3 #/((p_tags[question_id-1][1] + 1) / float(p_tags[question_id-1][1] + p_tags[question_id-1][0] + 2))

	else:
		if answer =='no' or answer is 'no':
			answers.append(False)
			# If there's an image model it has positive value, otherwise -1
			# Without image model the probability just updates based on Pq and Pqd
			if Pi[0][question_id-1] == -1:
				for objectID in range(0,17):
					T = get_t(objectID+1, question_id, game.cursor)
					N = objects[objectID][question_id][0]
					D = objects[objectID][question_id][1]
					pO[objectID] = pO[objectID] * ((1 - probabilityD[T]) + (D - N + 1)/(D + 2.0)) / 2 #/((p_tags[question_id-1][1] + 1) / float(p_tags[question_id-1][0] + p_tags[question_id-1][0] + 2))
			else:
				for objectID in range(0,17):
					T = get_t(objectID+1, question_id, game.cursor)
					N = objects[objectID][question_id][0]
					D = objects[objectID][question_id][1]
					pO[objectID] = pO[objectID] * (((1 - probabilityD[T]) + (D - N + 1)/(D + 2.0) + 1 - Pi[objectID][question_id-1])) / 3 #/((p_tags[question_id-1][0] + 1) / float(p_tags[question_id-1][1] + p_tags[question_id-1][0] + 2))

	# Normalize the probabilities so that all object probabilities will sum to 1
	pO = pO / np.sum(pO)

	# Save the qustions to each answer and the updated probabilities
	with open("example.txt", "a") as myfile:
		myfile.write(question_tag + " -> " + answer+ " \n")
		myfile.write(str(pO) + "\n")

	return pO, answers

def ask_old(question_id, object, game, answer_data, answers, pO, Pi, p_tags, objects):
	# Takes best question and updates all object probabilies based on the answer

	probabilityD = get_tval(game.cursor)
	question_tag = _tags.all(game.cursor)[question_id-1]
	#answer = raw_input("Does it have " + tags[question_id-1] + "? (yes/no) ")
	#answer = answer.lower()
	answer = answer_data[object.id-1][question_id-1]
	#print game_folder, object.id,objectlist[object.id-1][0],'qt->'+question_tag+' ' ,'ans->'+answer

	if not (answer):
		# Not sure why this is here, it's old code, never seen it actually run
		#print game_folder, object.id,'qt->'+question_tag+' ' ,'sd'+answer+'<-', objectlist[object.id-1][0]

		sys.exit()

	if answer == 'yes' or answer is 'yes':
		answers.append(True)
		# If there's an image model it has positive value, otherwise -1
		# Without image model the probability just updates based on Pq and Pqd
		if Pi[0][question_id-1] == -1:
			for objectID in range(0,17):
				T = get_t(objectID+1, question_id, game.cursor)
				N = sum(objects[objectID+1][question_id])
				D = len(objects[objectID+1][question_id])
				pO[objectID] = pO[objectID] * (probabilityD[T] + (N + 1)/(D + 2.0)) / 2 #/((p_tags[question_id-1][1] + 1) / float(p_tags[question_id-1][1] + p_tags[question_id-1][0] + 2))
		else:
			for objectID in range(0,17):
				T = get_t(objectID+1, question_id, game.cursor)
				N = sum(objects[objectID+1][question_id])
				D = len(objects[objectID+1][question_id])
				pO[objectID] = pO[objectID] * ((probabilityD[T] + (N + 1)/(D + 2.0) + Pi[objectID][question_id-1])) / 3 #/((p_tags[question_id-1][1] + 1) / float(p_tags[question_id-1][1] + p_tags[question_id-1][0] + 2))

	else:
		if answer =='no' or answer is 'no':
			answers.append(False)
			# If there's an image model it has positive value, otherwise -1
			# Without image model the probability just updates based on Pq and Pqd
			if Pi[0][question_id-1] == -1:
				for objectID in range(0,17):
					T = get_t(objectID+1, question_id, game.cursor)
					N = sum(objects[objectID+1][question_id])
					D = len(objects[objectID+1][question_id])
					pO[objectID] = pO[objectID] * ((1 - probabilityD[T]) + (D - N + 1)/(D + 2.0)) / 2 #/((p_tags[question_id-1][1] + 1) / float(p_tags[question_id-1][0] + p_tags[question_id-1][0] + 2))
			else:
				for objectID in range(0,17):
					T = get_t(objectID+1, question_id, game.cursor)
					N = sum(objects[objectID+1][question_id])
					D = len(objects[objectID+1][question_id])
					pO[objectID] = pO[objectID] * (((1 - probabilityD[T]) + (D - N + 1)/(D + 2.0) + 1 - Pi[objectID][question_id-1])) / 3 #/((p_tags[question_id-1][0] + 1) / float(p_tags[question_id-1][1] + p_tags[question_id-1][0] + 2))

	# Normalize the probabilities so that all object probabilities will sum to 1
	pO = pO / np.sum(pO)

	# Save the qustions to each answer and the updated probabilities
	with open("example.txt", "a") as myfile:
		myfile.write(question_tag + " -> " + answer+ " \n")
		myfile.write(str(pO) + "\n")

	return pO, answers




# Old version takes ~75 seconds
# def get_p_tags_old(cursor):
# 	log.info('Getting p tags')
# 	start = time.time()
# 	# The P tag is the number of times a question has been answered true for a specific object
# 	# IE black and scissors has its own P tag
# 	p_tags = []

# 	# Get all (289, 1 per question?) tags from database
# 	tags = _tags.all(cursor)
# 	for tag in range(1,290):
# 		answers = {}
# 		cursor.execute("SELECT COUNT(*) FROM answers WHERE qid = %s and answer = TRUE", tag)
# 		answers[1] = cursor.fetchone()[0]
# 		cursor.execute("SELECT COUNT(*) FROM answers WHERE qid = %s and answer = FALSE", tag)
# 		answers[0] = cursor.fetchone()[0]
# 		p_tags.append(answers)
# 		#print tags[tag-1] + " prob yes: " + str(p_tags[tag-1][1]/ (float(p_tags[tag-1][0] + p_tags[tag-1][1]))) + " prob no: " +  str(p_tags[tag-1][0]/ (float(p_tags[tag-1][0] + p_tags[tag-1][1])))

# 		# p_tags is in the form of [{0: ###, 1: ###}], 1 item per questions. 0 = # of no, 1 = # of yes
# 		# this is indepdent of object because it gets total for every object?
# 	end = time.time()
# 	log.info('Done (%.2fs)', end - start)
# 	return p_tags

# New version takes ~0.25 seconds
def get_p_tags(cursor):
	log.info('Getting p tags')
	start = time.time()
	# The P tag is the number of times a question has been answered true for a specific object
	# IE black and scissors has its own P tag
	p_tags = []

	# Get all (289, 1 per question?) tags from database
	tags = _tags.all(cursor)
	cursor.execute('SELECT qid, answer, COUNT(*) FROM answers GROUP BY qid, answer')
	for row in cursor.fetchall():
		if len(p_tags) == row[0]-1:
			p_tags.append({0: 0, 1: 0})
		p_tags[row[0]-1][row[1]] = row[2]

		# p_tags is in the form of [{0: ###, 1: ###}], 1 item per questions. 0 = # of no, 1 = # of yes
		# this is indepdent of object because it gets total for every object?
	end = time.time()
	log.info('Done (%.2fs)', end - start)
	return p_tags

def get_best(game, objects, asked_questions, pO, Pi, p_tags, start):
	# Finds the question that best splits our current subset of objects
	tvals = get_tval(game.cursor)

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

				T = get_t(i, j, game.cursor)
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


def get_best_old(game, objects, asked_questions, pO, Pi, p_tags, start):
	# Finds the question that best splits our current subset of objects
	tvals = get_tval(game.cursor)

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

				T = get_t(i, j, game.cursor)
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


def get_tval(cursor):
	cursor.execute('SELECT yes_answers/total_answers FROM Pqd')

	result = cursor.fetchall()

	tvals = []
	for r in result:
		tvals.append(float(r[0]))

	# Basically a list of 14 proportions of yes answers. 1 entry per t_value
	return tvals

i = 0

_descriptions = []

def get_t(object_id, question_id, cursor):
	#TODO: make semi-permanent cache of description-tag relations so they don't have to be computed during simulation
	global _descriptions

	if not _descriptions:
		_descriptions = [{} for _ in range(17)]
		tags = _tags.all(cursor)
		cursor.execute('SELECT description, objectID, descNum FROM Descriptions')
		for row in cursor.fetchall():
			for tag in tags:
				if tag in row[0]:
					if not tag in _descriptions[row[1]-1]:
						_descriptions[row[1]-1][tag] = 1
					else:
						_descriptions[row[1]-1][tag] += 1

	tag = _tags.get(question_id, cursor)
	object_id = int(object_id)
	o = _descriptions[object_id-1]
	if not tag in o:
		return 0
	return o[tag]


def get_t_old(object_id, question_id, cursor):
	tag = _tags.get(question_id, cursor)

	cursor.execute('SELECT COUNT(*) \
					FROM Descriptions \
					WHERE description LIKE %s \
					AND objectID = %s', ('%{0}%'.format(tag), str(object_id)))


	return cursor.fetchone()[0]

