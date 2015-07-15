def robotAsk(question):
	"""
	Has the robot ask a question and returns the answer
	"""
	tts.say(question)
	asr.subscribe()
	data = mem.getData("WordRecognized")
	ans = data[0]
	asr.unsubscribe()
	return ans
