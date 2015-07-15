import math
import time
import logging as log
import sys
import config
import numpy as np
import tags
import database as db

_descriptions = []

def get_t_method1(object_id, question_id):
	"""
	Returns the number of descriptions that an object has that contains a specific tag
	"""

	tag = tags.get(question_id)

	db.cursor.execute('SELECT COUNT(*) FROM Descriptions WHERE description LIKE %s AND objectID = %s', ('%{0}%'.format(tag), str(object_id)))

	return db.cursor.fetchone()[0]

def get_t_method2(object_id, question_id):
	"""
	Returns the number of descriptions that an object has that contains a specific tag
	"""

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

db.init_driver()
db.connect(config.db['address'], config.db['username'], config.db['password'], config.db['database'], unix_socket=config.db['socket'])

for i in range(1,18):
	for q in range(1, 290):
		with open("test1.txt", "a") as myfile:
			myfile.write("object number: " + str(i) + " tag number: " + str(q) + "\n")
			myfile.write(str(get_t_method1(i,q)) + "\n")
		with open("test2.txt", "a") as myfile:
			myfile.write("object number: " + str(i) + " tag number: " + str(q) + "\n")
			myfile.write(str(get_t_method2(i,q)) + "\n")

