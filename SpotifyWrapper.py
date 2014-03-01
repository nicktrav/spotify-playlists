import spotify 
import os
import threading
from getpass import getpass
import shutil

class SpotifyWrapper:
	def __init__(self, username):
		self.username = username
		self.config = spotify.Config()
		self.session_blob = None
		self.session = None
		self.logged_in_event = threading.Event()

	def load_session_blob(self):
		
		# check file exists
		if os.path.exists('.session_blob') == False:
			print 'No .session_blob file exists yet'
			return None

		# open the .session_blob file
		with open('.session_blob', 'r') as f:
			self.session_blob = f.read().split('\n')[0]
			f.close()

		return self.session_blob

	def save_session_blob(self, session, bytestring):
		
		self.session_blob = bytestring
		
		with open('.session_blob', 'w') as f:
			f.write(self.session_blob)
			f.close()

		print 'Saved session blob.'

	def logged_in_listener(self, session, error_type):
		
		print 'Logged in!'
		self.logged_in_event.set()

	def login(self, password=None):
		
		# set up the config
		self.config.user_agent = 'test'

		# set up the session
		self.session = spotify.Session(config=self.config)

		# register callbacks for session events
		self.session.on(spotify.SessionEvent.LOGGED_IN, self.logged_in_listener)
		self.session.on(spotify.SessionEvent.CREDENTIALS_BLOB_UPDATED, self.save_session_blob)

		# if the user has entered a password, use that
		if password != None:
			self.session.login(self.username, password)
			return self.session

		# load the session blob
		self.load_session_blob()

		# where there is currently no session blob
		if self.session_blob == None:

			# ask for a password
			pwd = getpass('Enter device password: ')
			
			# login with a password
			self.session.login(self.username, pwd, False)
		else:
			
			# login with the session_blob
			self.session.login(self.username, None, False, self.session_blob)

		# wait for login
		while not self.logged_in_event.wait(0.1):
			self.session.process_events()

		# return the session
		return self.session

	def cleanup(self):
		"""Temporary files are left behind in /tmp. Remove them."""
		print 'Removing tmp/ ...'

		try:
			shutil.rmtree('tmp/')
		except:
			print 'Could not remove tmp/ directory.'

		return
