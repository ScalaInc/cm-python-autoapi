import sys, json
from getpass import getpass
import requests
import logging

logging.basicConfig(filename='logs/script.log',level=logging.DEBUG,format='%(asctime)s %(message)s')

baseurl = sys.argv[1]

# get credentials
params = dict(
    username='administrator',
    password='scala',
)
# debug mode
if '-V' in sys.argv:
    import httplib
    httplib.HTTPConnection.debuglevel = 1

# start session for param reuse
session = requests.Session()
session.headers.update({'Content-type': 'application/json'})

print ('Requesting auth-token...')
authurl = baseurl + '/api/rest/auth/login'
print('url request is: ', authurl)
resp = session.post(authurl, data=json.dumps(params))
#print (resp.text)
auth_token = resp.json().get('apiToken')

# add token to the session
session.headers.update({'apiToken': auth_token})
print  ('    Token:', auth_token)

print ('\nCreating playlist...')
url = baseurl + '/api/rest/playlists/'
plto = dict(name='tutorial playlist', playlistType='MEDIA_PLAYLIST')
"""resp = session.post(url, data=json.dumps(plto))"""
resp.raise_for_status()
plto = resp.json()
print (plto)

print ('\nListing playlists...')
url = baseurl + '/api/rest/playlists/all'
resp = session.get(url)
playlists = resp.json().get('list', [])
for playlist in playlists:
    print ('  *', playlist['name'], playlist['id'])