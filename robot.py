import time
from naoqi import ALProxy

r = None

def connect(address, port=9559):
	global r
	r = Robot(address, port)

def robot():
	global r
	return r

class Robot():

	def __init__(self, address, port=9559):
		self.asr = ALProxy("ALSpeechRecognition", address, port)
		self.tts = ALProxy("ALTextToSpeech", address, port)
		self.mem = ALProxy("ALMemory", address, port)

		self.asr.setLanguage("English")

		self.yes_no_vocab = {
			"yes": ["yes", "ya", "yep", "yup", "sure"],
			"no": ["no", "nope", "nah"]
			
		self.vocab = {
			"yes": ["yes", "ya", "yep", "yup", "sure", "definitely"],
			"no": ["no", "nope"]

		self.vocab = self.yes_no_vocab
		self.asr.setVocabulary([j for i in self.vocab.values() for j in i], False)

	def say(self, text):
		"""
		Uses ALTextToSpeech to vocalize the given string
		"""

		self.tts.say(text)

	def ask(self, question):
		"""
		Has the robot ask a question and returns the answer
		"""

		self.say(question)
		self.asr.subscribe("TEST_ASR")
		data = (None, 0)
		while not data[0]:
			data = self.mem.getData("WordRecognized")
		self.asr.unsubscribe("TEST_ASR")

		print data

		for word in self.vocab:
			for syn in self.vocab[word]:
				if data[0] == syn:
					return word

	def askObject(self):

		object_vocab = {
		"digital_clock": ["digital clock", "blue clock", "black alarm clock"],
		"analog_clock": ["analog clock", "black clock", "black alarm clock"],
		"red_soccer_ball": ["red soccer ball"],
		"basketball": ["basketball"],
		"football": ["football"],
		"yellow_book": ["yellow book"],
		"yellow_flashlight": ["yellow flashlight"],
		"blue_soccer_ball": ["blue soccer ball", "blue ball"],
		"apple": ["apple"],
		"black_mug": ["black mug"],
		"blue_book": ["blue book"],
		"blue_flashlight": ["blue flashlight"],
		"cardboard_box": ["cardboard box"],
		"pepper": ["pepper", "jalapeno"],
		"green_mug": ["green mug"],
		"polka_dot_box": ["polka dot box"],
		"scissors": ["scissors"]
		}

		self.vocab = object_vocab
		self.asr.setVocabulary([j for i in object_vocab.values() for j in i], False)

		obj_name = self.ask("What object were you thinking of?")

		self.vocab = self.yes_no_vocab
		self.asr.setVocabulary([j for i in self.vocab.values() for j in i], False)

		y = self.ask("I heard you say %s. Is this correct?" % obj_name)

		if y == "no":
			self.say("Please type the correct object name on the computer.")

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

		return obj_name
