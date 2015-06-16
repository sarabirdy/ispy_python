_tags = []

def get(question_id, cursor):
	#cursor.execute('SELECT tag from Tags where id = %s', (question_id))
	return all(cursor)[question_id-1]

	#return cursor.fetchone()[0]

def all(cursor):
	"""
	Get list of all tags
	Returns list in the form of [tag]
	"""

	global _tags
	if not _tags:
		cursor.execute('SELECT tag FROM Tags')
		result = cursor.fetchall()
		for tag in result:
			_tags.append(tag[0])
	return _tags
			