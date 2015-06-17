import database as db

_tags = []

def get(question_id):
	return get_all()[question_id-1]


def get_all():
	"""
	Get list of all tags
	Returns list in the form of [tag]
	"""

	global _tags
	if not _tags:
		db.cursor.execute('SELECT tag FROM Tags')
		result = db.cursor.fetchall()
		for tag in result:
			_tags.append(tag[0])
	return _tags
			