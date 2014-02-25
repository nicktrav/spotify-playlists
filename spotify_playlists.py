import spotify
import threading
import os, sys
import getpass
import json
import re
import time
import shutil

# The listening event for the session login
logged_in_event = threading.Event()
def logged_in_listener(session, error_type):
	logged_in_event.set()

def save_session_blob(session, bytestring):
	"""Get the blob of the current session and save it to
		file for quick loading next time.

		Callback for spotify.SessionEvent.CREDENTIALS_BLOB_UPDATED"""
	
	print 'Saving session bytestring ... '
	
	# Open file, write, then close
	f = open('.session_blob', 'w')
	f.write(bytestring)
	f.close()
	
	return

def get_session_blob():
	"""Load the session blob, if it exists"""
	# Check to see if file exists
	if os.path.exists('.session_blob'):
		# If so, read the data from the file and return
		f = open('.session_blob', 'r')
		res = f.read()
		f.close()
		
		return res
	else:
		return None

def spotify_login(user):
	print 'Logging in with user: %s' % user

	# set up config
	config = spotify.Config()
	config.user_agent = 'Test'
	
	# set up the session
	session = spotify.Session(config=config)

	# register callbacks for the session events
	session.on(spotify.SessionEvent.LOGGED_IN, logged_in_listener)

	# look for a session blob
	blob = get_session_blob()

	# handle the case where there is no blob yet
	if blob == None:
		print 'No blob exists yet'
		pwd = getpass.getpass('Enter device password: ')

	# logging in with password or session blob?
	# sometimes there is a timeout. If so, end.
	try:
		# log in with blob
		if blob != None:
			session.login(user, None, False, blob)
		# log in with password
		else:
			session.on(spotify.SessionEvent.CREDENTIALS_BLOB_UPDATED, save_session_blob)
			session.login(user, pwd, False)

	except spotify.error.Timeout, e:
		print e.strerror
		print 'Exiting ...'
		sys.exit(1)

	while not logged_in_event.wait(0.1):
		session.process_events()

	return session

def get_playlist_tracks(playlist):
	"""Return a list list of track objects for the specified playlist"""
	pl = {}
	# load the playlist
	playlist.load(20) # add a timeout of 20 seconds
	print '\nProcessing playlist %s' % playlist.name.encode('utf-8')
	pl['link'] = playlist.link.uri
	pl['name'] = playlist.name.encode('utf-8')

	# list to hold all of the processed tracks
	tracks = []

	# Get the tracks from the starred playlist
	print '\tGot %d tracks' % len(playlist.tracks_with_metadata)
	for plt in playlist.tracks_with_metadata:
		track_info = {}
		track_info['create_time'] = plt.create_time
		# track_info['creator'] = plt.creator.link.uri
		
		# the actual track
		t = plt.track
		t.load(20) # add a timeout of 20 seconds
		
		track_info['track'] = t.link.uri
		track_info['artists'] = [a.link.uri for a in t.artists]
		track_info['album'] = t.album.link.uri
		track_info['track_name'] = t.name
		track_info['duration'] = t.duration
		track_info['popularity'] = t.popularity
		track_info['starred'] = t.starred
		track_info['disc'] = t.disc
		track_info['index'] = t.index

		tracks.append(track_info)

		print '\tProcessed track %s' % track_info['track']

	pl['tracks'] = tracks

	return pl

def cleanup():
	"""Temporary files are left behind in /tmp. Remove them."""
	print '\nRemoving tmp/ ...'

	try:
		shutil.rmtree('tmp/')
	except:
		print 'Could not remove tmp/ directory.'

	return

def get_all_playlists():
	"""Get the tracks from the starred playlist"""
	
	session = spotify_login('1230966079')

	# load information for the user
	user = session.user.load(20)
	
	# set up the dictionary object with the relevant information
	u_dict = {}
	u_dict['spotify_id'] = user.link.uri
	u_dict['playlists'] = []

	# get the playlists for the logged in user
	pls = session.playlist_container
	pls.load(20)
	
	for pl in pls:
		# don't dive into playlist containers
		if type(pl) != spotify.playlist.Playlist:
			continue

		# load the playlist
		pl.load()

		# get the playlist
		pl_dict = get_playlist_tracks(pl)

		# place the playlist object in the user dictionary
		u_dict['playlists'].append(pl_dict)

	
	# set up the filename
	user_id = re.sub(':', '-', u_dict['spotify_id'])
	timestamp = re.sub('\.', '-', str(time.time()))
	filename = timestamp + '-' + user_id + '.json'
	
	# write to file
	f = open('output/'+filename, 'w')

	f.write(json.dumps(u_dict, indent=4, sort_keys=True))

	f.close()

	# cleanup the tmp directory left behind
	time.sleep(1)
	cleanup()

	return

if __name__ == '__main__':
	get_all_playlists()