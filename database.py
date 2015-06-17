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

		self.connection = self.driver.connect(address, username, password, database, unix_socket='/Applications/MAMP/tmp/mysql/mysql.sock')
		with self.connection:
			self.cursor = self.connection.cursor()
			log.info('Connected to database')

	def _init_driver(self):
		"""
		Use native MySQLdb driver,
		or fall back on pymysql
		"""

		try:
			import MySQLdb
			self.driver = MySQLdb
			log.info('Using MySQLdb')
		except ImportError:
			log.info('MySQLdb not found')
			
			try:
				import pymysql
				self.driver = pymysql
				log.info('Using pymysql')
			except ImportError:
				raise Exception('No database driver found')

