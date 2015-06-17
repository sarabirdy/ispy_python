import time
import logging as log

import objects
import models
import database as db

class Game:
	"""
	Main class that handles game logic
	"""

	def play(self):
		"""
		Play the game
		"""

		log.info('Playing game %d', self.id)

		start = time.time()

		# Generate all image probabilities at once since this takes a little while
		Pi = models.gen_image_probabilities(self)

		# Initialize game stats to empty
		NoOfQuestions = 0
		round_wins = 0
		round_losses = 0
		avg_win = 0
		avg_lose = 0
		question_answers = {}
		questions_asked = {}

		# For each object in the set
		for obj in objects.get_all():
			# Record individual object stats
			result, number_of_questions, answers, askedQuestions = obj.play(self, Pi)
			log.info("Game %d, object %d complete, updating stats", self.id, obj.id)
			if result == 0: # Loss
				round_losses = round_losses + 1
				avg_lose = avg_lose + number_of_questions
			else: # Win
				round_wins = round_wins + 1
				avg_win = avg_win + number_of_questions
			NoOfQuestions = number_of_questions + NoOfQuestions

			# Save questions and answers for later
			questions_asked[obj.id] = askedQuestions
			question_answers[obj.id] = answers

		# Save results
		self._record(round_wins, round_losses, NoOfQuestions)

		end = time.time()
		log.info("Game %d complete (Took %ds)", self.id, int(end - start))

		return round_wins, round_losses, NoOfQuestions, avg_win, avg_lose, question_answers, questions_asked

	def _record(self, wins, losses, num_questions):
		with open("game.txt", "a") as myfile:
			myfile.write("Round " + str(self.id) + ": ")
			myfile.write("Wins=" + str(wins) + ', Losses='+str(losses))
			myfile.write(" Accuracy: " + str(wins/float(17)) + "\n")
			myfile.write("Average number of questions: " + str(num_questions/float(17)) + "\n")


	def __init__(self, id):
		self.id = id
