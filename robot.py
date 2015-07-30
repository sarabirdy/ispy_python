import time
import os

import numpy as np
import speech_recognition as sr
from naoqi import ALModule, ALProxy, ALBroker

count = 0
snd = None

def connect(address, port=9559, name="r", brokername="broker"):
	global broker
	broker = ALBroker("broker", "0.0.0.0", 0, "bobby.local", 9559)
	global r
	r = Robot(name, "bobby.local", 9559)

def robot():
	global r
	return r

def broker():
	global broker
	if not broker:
		broker = ALBroker("broker", "0.0.0.0", 0, "bobby.local", 9559)
	return broker

class Robot(ALModule):
	def __init__( self, strName, address = "bobby.local", port = 9559):
		ALModule.__init__( self, strName )
		self.outfile = None
		self.outfiles = [None]*(3)
		self.count = 99999999
		self.check = False

		self.yes_no_vocab = {
			"yes": ["yes", "ya", "sure", "definitely"],
			"no": ["no", "nope", "nah"]
		}

		# TODO: add unknown object names into this somehow
		# also add other names for objects dynamically??????
		self.object_vocab = {
			"digital_clock": ["digital clock", "blue clock", "black alarm clock"],
			"analog_clock": ["analog clock", "black clock", "black alarm clock"],
			"red_soccer_ball": ["red soccer ball", "red ball"],
			"basketball": ["basketball", "orange ball"],
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
			"polka_dot_box": ["polka dot box", "polka dotted box", "spotted box", "brown and white box"],
			"scissors": ["scissors"]
		}

		self.audio = ALProxy("ALAudioDevice", address, port)
		self.audio.setClientPreferences(self.getName(), 48000, [1,1,1,1], 0, 0)

		self.asr = ALProxy("ALSpeechRecognition", address, port)
		self.asr.setLanguage("English")
		self.asr.setVocabulary([j for i in self.yes_no_vocab.values() for j in i], False)

		self.tts = ALProxy("ALTextToSpeech", address, port)
		self.mem = ALProxy("ALMemory", address, port)


	def __del__(self):
		print "End Robot Class"

	def start(self):
		print "Starting Transcriber"
		self.audio.subscribe(self.getName())

	def stop(self):
		print "Stopping Transcriber"
		self.audio.unsubscribe(self.getName())
		if self.outfile != None:
			self.outfile.close()

	def processRemote(self, input_channels, input_samples, timestamp, input_buffer):
		print "listening"
		sound_data_interlaced = np.fromstring(str(input_buffer), dtype=np.int16)
		sound_data = np.reshape(sound_data_interlaced, (input_channels, input_samples), 'F')
		peak_value = np.max(sound_data)
		print "got peak value"
		if peak_value > 7500:
			print "Peak:", peak_value
			self.count = 30
		print "subtracting count"
		self.count -= 1
		if self.count == 0:
			print "STOP"*50
			self.check = True
		print "checked"
		if self.outfile == None:
			print "outfile was none"
			filename = "output.raw"
			self.outfile = open(filename, "wb")
		if self.outfile.closed:
			print "outfile was closed"
			filename = "output.raw"
			self.outfile = open(filename, "wb")
		print self.outfile
		sound_data[0].tofile(self.outfile)
		print "sent data to outfile"

	def say(self, text):
		"""
		Uses ALTextToSpeech to vocalize the given string
		"""

		self.tts.say(text)

	def ask(self, question):
		"""
		Has the robot ask a question and returns the answer
		"""
		# If you're just trying to test voice detection, you can uncomment
		# the following 5 lines. Bobby will guess "yellow flashlight" and will prompt
		# you to correct him by saying "blue flashlight"

		# fake_answers = ["no", "yes", "yes", "yes", "no", "yes", "yes"]
		# global count
		# count += 1
		# print question
		# return fake_answers[count]

		self.say(question)
		#starts listening for an answer
		self.asr.subscribe("TEST_ASR")
		data = (None, 0)
		while not data[0]:
			data = self.mem.getData("WordRecognized")
		#stops listening after he hears yes or no
		self.asr.unsubscribe("TEST_ASR")

		print data

		for word in self.yes_no_vocab:
			for syn in self.yes_no_vocab[word]:
				if data[0] == syn:
					return word

	def ask_object(self):
		self.start()
		print "asking object"
		while True:
			if self.check:
				break
			time.sleep(1)
		self.stop()
		#uses sox to convert raw files to wav files
		os.system("sox -r 48000 -e signed -b 16 -c 1 output.raw speech.wav")

		r = sr.Recognizer()
		with sr.WavFile("speech.wav") as source:
			speech = r.record(source)
		try:
			possibilities = r.recognize(speech, True)
			print possibilities
			for possibility in possibilities:
				for word in self.object_vocab:
					for syn in self.object_vocab[word]:
						if possibility["text"] == syn:
							# global broker
							# broker.shutdown()
							# exit(0)
							return possibility
			raise LookupError
		except LookupError:
			self.say("I couldn't understand what you said. Please go to the computer and type the name of your object.")
			print "Type the name of your object exactly as you see here."
			print self.object_vocab.keys()
			# global broker
			# broker.shutdown()
			# exit(0)
			return raw_input("What object were you thinking of?")


#------------------------Main------------------------#
if __name__ == "__main__":
	print "#----------Audio Script----------#"

	connect("bobby.local")
	obj_name = r.ask_object()
	print obj_name

	broker.shutdown()
	exit(0)
