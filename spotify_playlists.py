import json
import re
import time
from SpotifyWrapper import SpotifyWrapper
import spotify

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

def get_all_playlists():
	"""Get the tracks from the starred playlist"""
	
	SW = SpotifyWrapper('1230966079')
	SW.login()

	session = SW.session

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
	SW.cleanup()

	return

if __name__ == '__main__':
	get_all_playlists()