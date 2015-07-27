import time
import numpy
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
		self.motion = ALProxy("ALMotion", address, port)
		self.pose = ALProxy("ALRobotPosture", address, port)
		self.track = ALProxy("ALFaceTracker", address, port)
		self.gaze = ALProxy("ALGazeAnalysis", address, port)
		self.cam = ALProxy("ALVideoDevice", address, port)

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

	def stiffen(self, body_part = "Body"):
		"""
		Turns stiffnesses of specified robot body part all the way on over 1 second
		"""

		self.motion.stiffnessInterpolation(body_part, 1.0, 1.0)

	def rest(self):
		"""
		Goes to Crouch position and turns robot stiffnesses off

		"""
		self.motion.rest()

	def initCamera(self):
		"""
		Subscribes to robot cameras
		"""

		resolution = 2
		colorspace = 13
		fps = 10

		self.top_cam_client = camera.subscribeCamera("python_client", 0, resolution, colorspace, fps)
		self.bottom_cam_client = camera.subscribeCamera("python_client", 1, resolution, colorspace, fps)
	
	def getImage(self, camera):
		"""
		Returns image from either top or bottom camera on NAO robot converted to Numpy array.
		The "camera" parameter takes either "top" or "0" to use the top camera, and the bottom camera is the default.
		"""

		if camera == "top" or camera == 0:
			nao_image = self.cam.getImageRemote(self.top_cam_client)

		else:
			nao_image = self.cam.getImageRemote(self.bottom_cam_client)

		# convert to numpy array for OpenCV
		image = (numpy.reshape(numpy.frombuffer(nao_image[6], dtype = '%iuint8' % nao_image[2]), (nao_image[1], nao_image[0], nao_image[2])))

		return image