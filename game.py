import time
import logging as log

import objects
import models
import database as db

global _objects

class Game:
	"""
	Main class that handles game logic
	"""

	def playGame(self, number_of_objects, sim, use_image_models):
		"""
		Play the game
		"""

		log.info('Playing game %d', self.id)

		start = time.time()

		# Generate all image probabilities at once since this takes a little while
		if use_image_models:
			Pi = models.gen_image_probabilities(self, number_of_objects)
		else:
			Pi = [[-1] * 289] * 17
		# Initialize game stats to empty
		NoOfQuestions = 0
		round_wins = 0
		round_losses = 0
		avg_win = 0
		avg_lose = 0
		question_answers = {}
		questions_asked = {}
		objlist = objects.get_all()
		# For each object in the set
		count = 0

		for i in objlist:
			if sim:
				print "\nPlease choose an object. Your choices are:\n"
				for j in range(len(objlist)):
					print objlist[j].name
				chosen = raw_input("\nAre you ready to play now? (yes/no) ")
				while chosen.lower() != "yes":
					chosen = raw_input("Now are you ready? (yes/no) ")
			result, number_of_questions, answers, askedQuestions = i.playObject(self, Pi, number_of_objects, sim)
			log.info("Game %d, object %d complete, updating stats", self.id, i.id)
			if result == 0: # Loss
				round_losses += 1
				avg_lose += number_of_questions
			else: # Win
				round_wins += 1
				avg_win += number_of_questions
			NoOfQuestions += number_of_questions

			# Save questions and answers for later
			questions_asked[i.id] = askedQuestions
			question_answers[i.id] = answers

			count += 1

			if sim == True and count != 0:
				quit = None
				while quit != "yes" and quit != "no":
					quit = raw_input("Would you like to quit this game early? (yes/no) \nThere are %d rounds left. " % (17 - count))
					quit = quit.lower()
				if quit == "yes":
					break
		# Save results
		self._record(round_wins, round_losses, NoOfQuestions, count)

		end = time.time()
		log.info("Game %d complete (Took %ds)", self.id, int(end - start))

		return round_wins, round_losses, NoOfQuestions, avg_win, avg_lose, question_answers, questions_asked

	def _record(self, wins, losses, num_questions, number_of_objects_played):
		"""
		Record game data
		"""

		with open("game.txt", "a") as myfile:
			myfile.write("Round " + str(self.id) + ": ")
			myfile.write("Wins=" + str(wins) + ', Losses='+str(losses))
			myfile.write(" Accuracy: " + str(wins/float(number_of_objects_played)) + "\n")
			myfile.write("Average number of questions: " + str(num_questions/float(number_of_objects_played)) + "\n")


	def __init__(self, id):
		self.id = id
