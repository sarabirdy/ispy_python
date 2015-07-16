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

		self.vocab = {
			"yes": ["yes", "ya", "yep", "yup", "sure", "definitely"],
			"no": ["no", "nope"]
		}
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
		data = (None, None)
		while not data[0]:
			data = self.mem.getData("WordRecognized")
		self.asr.unsubscribe("TEST_ASR")

		for word in self.vocab:
			for syn in self.vocab[word]:
				if data[0] == syn:
					return word

	def askObject(self):
		self.say("Please go to the computer and type in the name of the object that you were thinking of.")
