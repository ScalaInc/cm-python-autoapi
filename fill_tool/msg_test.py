import sys, json
from getpass import getpass
import requests
import logging

logging.basicConfig(filename='logs/msg_test.log',level=logging.DEBUG,format='%(asctime)s %(message)s')

baseurl = 'http://192.168.10.135:8080/ContentManager'

prox = { 'http' : 'http://localhost:8888','https':'http://localhost:8888'}

use_proxy = False

if '-d' in sys.argv:
	use_proxy = True
	
# get credentials
params = dict(
    username='sboh',
    password='sboh',
    )

# start session for param reuse
session = requests.Session()
session.headers.update({'Content-type': 'application/json'})

def GET_rest_request(params={}, baseurl="", apiurl=""):
	global session, prox
	print ('Message parameters are: '+ str(params))
	authurl = baseurl + apiurl
	print('url request is: ' + authurl)
	resp = session.get(authurl,data=json.dumps(params),proxies= prox)
	
def PUT_rest_request(params={}, baseurl="", apiurl=""):
	global session, prox
	print ('Message parameters are: '+ str(params))
	authurl = baseurl + apiurl
	print('url request is: ' + authurl)
	resp = session.put(authurl,data=json.dumps(params),proxies= prox)
	
def POST_rest_request(params={}, baseurl="", apiurl=""):
	global session, prox
	print ('Message parameters are: '+ str(params))
	authurl = baseurl + apiurl
	print('url request is: ' + authurl)
	resp = session.post(authurl,data=json.dumps(params),proxies= prox)
	
print ('logging in and requesting auth token')
authurl = baseurl + '/api/rest/auth/login'
print('url request is: ', authurl)
resp = session.post(authurl, data=json.dumps(params),proxies=prox)
auth_token = resp.json().get('apiToken')
print ('Auth Token is: ' + auth_token)
# add authorization token to the session
session.headers.update({'apiToken': auth_token})

print('sending first media list command')
#http://192.168.10.135:8080/ContentManager/api/rest/media?limit=100&offset=0&sort=name&filters=%7B'workgroups':%7B'values':['2']%7D%7D
params = {'limit':'100','offset':'0','sort':'name','filters':"{'workgroups':{'values':['2']}}",}
GET_rest_request(params,baseurl, '/api/rest/media')

print('sending template list command')
#http://192.168.10.135:8080/ContentManager/api/rest/templates?limit=100&offset=0&filters=%7B'name':%7B'values':['Iadea%20Signboard_V3.scb']%7D%7D
params = {'limit':'100','offset':'0','sort':'name',}
GET_rest_request(params, baseurl, '/api/rest/templates')

print('sending second media list command')
#http://192.168.10.135:8080/ContentManager/api/rest/media?limit=100&offset=0&sort=name&filters=%7B'name':%7B'values':['%22Foyer%201e%20verdieping%22']%7D%7D
params = {'limit':'100','offset':'0','sort':'name',}
GET_rest_request(params,baseurl, '/api/rest/media')

print('sending looped get request')
#http://192.168.10.135:8080/ContentManager/api/rest/media?limit=100&offset=0&sort=name&filters=%7B'name':%7B'values':['1.1']%7D%7D

print('sending my very own get on the media id')
params = {}
GET_rest_request(params, baseurl, '/api/rest/media/5/usingMessages')

print('sending looped put')
#http://192.168.10.135:8080/ContentManager/api/rest/messages/5
params = {'name':'1.1'}
PUT_rest_request(params, baseurl, '/api/rest/messages/5')

print('sending thumbnail update request')
params = {}
POST_rest_request(params, baseurl, '/api/rest/messages/5/thumbnail')

print('Sending find message by id')
params = {}
GET_rest_request(params, baseurl, '/api/rest/messages/5')

