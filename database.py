import logging as log

class Database:
	"""
	Handles database drivers
	"""

	def __init__(self, address, username, password, database):
		"""
		Initialize the database connection with credentials
		"""

		self._init_driver()

		connection = self.driver.connect(address, username, password, database)
		with connection:
			self.cursor = connection.cursor()
			log.info('Connected to database')

	def _init_driver(self):
		"""
		Use native mysqldb driver,
		or fall back on pymsql
		"""

		try:
			import mysqldb
			self.driver = mysqldb
			log.info('Using mysqldb')
		except ImportError:
			log.info('Mysqldb not found')
			
			try:
				import pymysql
				self.driver = pymysql
				log.info('Using pymysql')
			except ImportError:
				raise Exception('No database driver found')

