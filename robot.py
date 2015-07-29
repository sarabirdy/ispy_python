import time
import os

import numpy as np
import speech_recognition as sr
from naoqi import ALModule, ALProxy, ALBroker

count = 0
snd = None
#r = None
#broker = None

def connect(address="bobby.local", port=9559, name="r", brokername="broker"):
	global broker
	broker = ALBroker("broker", "0.0.0.0", 0, address, 9559)
	global r
	r = Robot(name, address, 9559)

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
			"polka_dot_box": ["polka dot box"],
			"scissors": ["scissors"]
		}

		self.audio = ALProxy("ALAudioDevice", address, port)
		self.audio.setClientPreferences(self.getName(), 48000, [1,1,1,1], 0, 0)

		self.asr = ALProxy("ALSpeechRecognition", address, port)
		self.asr.setLanguage("English")
		self.asr.setVocabulary([j for i in self.yes_no_vocab.values() for j in i], False)

		self.tts = ALProxy("ALTextToSpeech", address, port)
		self.mem = ALProxy("ALMemory", address, port)
		self.motion = ALProxy("ALMotion", address, port)
		self.pose = ALProxy("ALRobotPosture", address, port)
		self.track = ALProxy("ALFaceTracker", address, port)
		self.gaze = ALProxy("ALGazeAnalysis", address, port)
		self.cam = ALProxy("ALVideoDevice", address, port)

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

	def say(self, text, block = True):
		"""
		Uses ALTextToSpeech to vocalize the given string.
		If "block" argument is False, makes call asynchronous.
		"""

		if block:
			self.tts.say(text)

		else:
			self.tts.post.say(text)

	def ask(self, question):
		"""
		Has the robot ask a question and returns the answer
		"""
		global count
		print question
		count += 1
		if count == 1:
			return "no"
		elif count == 2:
			return "yes"
		elif count == 3:
			return "yes"
		elif count == 4:
			return "yes"
		elif count == 5:
			return "no"
		elif count == 6 or count == 7:
			return "yes"

		# self.say(question)
		# self.asr.subscribe("TEST_ASR")
		# data = (None, 0)
		# while not data[0]:
		# 	data = self.mem.getData("WordRecognized")
		# self.asr.unsubscribe("TEST_ASR")
		#
		# print data
		#
		# for word in self.yes_no_vocab:
		# 	for syn in self.yes_no_vocab[word]:
		# 		if data[0] == syn:
		# 			return word

	def ask_object(self):
		self.start()
		print "asking object"
		while True:
			if self.check:
				break
			time.sleep(1)
		self.stop()
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

	def stiffen(self, body_part = "Body"):
		"""
		Turns stiffnesses of specified robot body part completely on over 1 second
		"""

		self.motion.stiffnessInterpolation(body_part, 1.0, 1.0)

	def rest(self):
		"""
		Goes to Crouch position and turns robot stiffnesses off
		"""

		self.motion.rest()

	def turnHead(yaw = None, pitch = None, speed = 0.3):
		"""
		Turns robot head to the specified yaw and/or pitch in radians at the given speed.
		Yaw can range from 119.5 deg (left) to -119.5 deg (right) and pitch can range from 38.5 deg (up) to -29.5 deg (down).
		"""

		if not yaw is None:
       		self.motion.setAngles("HeadYaw", yaw, speed)
       	if not pitch is None:
       		self.motion.setAngles("HeadPitch", pitch, speed)

    def trackFace():
    	"""
    	Sets face tracker to just head and starts.
    	"""

		# start face tracker
		self.track.setWholeBodyOn(False)
		self.track.startTracker()

	def subscribeGaze():
		"""
		Subscribes to gaze analysis module so that robot starts writing gaze data to memory.
		Also sets the highest tolerance for determining if people are looking at the robot because those people's IDs are the only ones stored.
		"""

        self.gaze.subscribe("_")
        self.gaze.setTolerance(1)

    def getPeopleIDs():
    	"""
    	Retrieves people IDs from robot memory. If list of IDs was empty, return None.
    	"""

        people_ids = self.mem.getData("GazeAnalysis/PeopleLookingAtRobot")

        if len(people_ids) == 0:
        	return None

        return people_ids

    def getRawPersonGaze(person_id):
        """
        Returns person's gaze as a list of yaw (left -, right +) and pitch (up pi, down 0) in radians, respectively.
        Bases gaze on both eye and head angles. Does not compensate for variable robot head position.
        """

        try:
            # retrieve GazeDirection and HeadAngles values
            gaze_dir = self.mem.getData("PeoplePerception/Person/" + str(person_id) + "/GazeDirection")
            head_angles =  self.mem.getData("PeoplePerception/Person/" + str(person_id) + "/HeadAngles")
            
            # extract gaze direction and head angles data
            person_eye_yaw = gaze_dir[0]
            person_eye_pitch = gaze_dir[1]
            
            person_head_yaw = head_angles[0]
            person_head_pitch = head_angles[1]

        # RuntimeError: if gaze data can't be retrieved for that person ID anymore (e.g. if bot entirely loses track of person)
        # IndexError: if gaze direction or head angles are empty lists (e.g. if person's gaze is too steep)
        except (RuntimeError, IndexError):
            return None

        else:
            # combine eye and head gaze values
            person_gaze_yaw = -(person_eye_yaw + person_head_yaw) # person's left is (-), person's right is (+)
            person_gaze_pitch = person_eye_pitch + person_head_pitch + math.pi / 2 # all the way up is pi, all the way down is 0

            return [person_gaze_yaw, person_gaze_pitch]




#------------------------Main------------------------#
if __name__ == "__main__":
	print "#----------Audio Script----------#"

	connect("bobby.local")
	obj_name = r.ask_object()
	print obj_name

	broker.shutdown()
	exit(0)