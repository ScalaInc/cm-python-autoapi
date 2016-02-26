import sys, json
from getpass import getpass
import requests
import logging
from time import sleep
import configparser
from framework.constants import *

logging.basicConfig(filename='logs/msg_test.log',level=logging.DEBUG,format='%(asctime)s %(message)s')

#baseurl = 'http://192.168.10.135:8080/ContentManager'
#baseurl = 'http://192.168.10.33:8081/CManager'

#prox = { 'http' : 'http://localhost:8888','https':'http://localhost:8888'}

config = configparser.ConfigParser()
config.read(CONFIG_FILE_PATH)

baseurl = config['login']['baseurl']


use_proxy = False

if '-d' in sys.argv:
	use_proxy = True
	
# get credentials
params = dict(
    networkId=0,
    username='sboh',
    password='sboh',
    rememberMe=True
    )

# start session for param reuse
session = requests.Session()
session.headers.update({'Content-type': 'application/json'})

def GET_rest_request(params={}, baseurl="", apiurl=""):
	global session, prox
#	print ('Message parameters are: '+ str(params))
	authurl = baseurl + apiurl
	print('url request is: ' + authurl)
#	resp = session.get(authurl,data=json.dumps(params),proxies= prox)
	resp = session.get(authurl,data=json.dumps(params),proxies = None)
	return resp
	
def PUT_rest_request(params={}, baseurl="", apiurl=""):
	global session, prox
#	print ('Message parameters are: '+ str(params))
	authurl = baseurl + apiurl
	print('url request is: ' + authurl)
#	resp = session.put(authurl,data = json.dumps(params),proxies= prox)
	resp = session.put(authurl,data = json.dumps(params),proxies = None)

def POST_rest_request(params={}, baseurl="", apiurl=""):
	global session, prox
#	print ('Message parameters are: '+ str(params))
	authurl = baseurl + apiurl
	print('url request is: ' + authurl)
#	resp = session.post(authurl,data=json.dumps(params),proxies= prox)
	resp = session.post(authurl,data=json.dumps(params),proxies = None)
	
	"""This method posts a change to the datum field of the message specified in the message with the specified message id"""
def tn_change_request(message_name, message):
	print('sending thumbnailInMemory request')
	params = {"fields":[{"displayName":"datum","id":8,"name":"datum","required":False,"templateId":1,"type":"STRING","value":"13-6-2014 11:32:51"},{"displayName":"allinfo","id":12,"name":"allinfo","required":False,"templateId":2,"type":"STRING","value":"09:30-09:50\tGIC Oefenen vaardigheden sessie 2\n09:50-10:15\tGIC Oefenen vaardigheden sessie 3 en CLOSURE\n10:30-10:55\tGIC Oefenen scenario-onderwijs SET en sessie 1"},{"displayName":"naamles","id":11,"name":"naamles","required":False,"templateId":3,"type":"STRING","value":"GIC Oefenen vaardigheden SET en sessie 1"},{"displayName":"tijd","id":7,"name":"tijd","required":False,"templateId":4,"type":"STRING","value":"09:10-09:30"},{"displayName":"soortles","id":9,"name":"soortles","required":False,"templateId":5,"type":"STRING","value":"Generic Instructor Course"},{"displayName":"docent","id":10,"name":"docent","required":False,"templateId":6,"type":"STRING","value":""}],"name":1.1,"mediaType":"MESSAGE","pages":1,"template":{"approvalDetail":{"approvalStatus":"APPROVED","approvedBy":{"firstname":"sboh","id":4,"lastLogin":"2014-06-16 09:48:32","lastname":"sboh","username":"sboh"},"id":1,"lastModified":"2014-06-13 10:50:53","messageText":"Auto approved template","toApprove":{"firstname":"sboh","id":4,"lastLogin":"2014-06-16 09:48:32","lastname":"sboh","username":"sboh"},"user":{"firstname":"sboh","id":4,"lastLogin":"2014-06-16 09:48:32","lastname":"sboh","username":"sboh"}},"approvalStatus":"APPROVED","audioDucking":False,"createdDate":"2014-06-13 10:50:53","description":"","downloadPath":"/resources/content/Iadea Signboard_V3[45597185300].scb","generatingThumbnail":False,"height":480,"id":1,"lastModified":"2014-06-13 10:51:50","length":409075,"mediaItemFiles":[{"downloadPath":"%2Fresources%2Fcontent%2FIadea+Signboard_V3%5B45597185300%5D.scb","filename":"Iadea Signboard_V3[45597185300].scb","id":1,"md5":"f35cf884343548276df902fefbf7ad6e","originalFilename":"Iadea Signboard_V3.scb","prettifySize":"397.7 KB","size":407286,"status":"OK","thumbnailDownloadPaths":{"extraSmall":"/resources/thumbnails/1_medium.png","large":"/resources/thumbnails/1_extraLarge.png","medium":"/resources/thumbnails/1_large.png","mediumSmall":"/resources/thumbnails/1_playlist.png","small":"/resources/thumbnails/1_mediumLarge.png"},"uploadDate":"2014-06-13 10:50:53","uploadedBy":"sboh","version":1}],"mediaType":"TEMPLATE","messagesCount":0,"modifiedBy":{"firstname":"System Administrator","id":1,"lastLogin":"2014-06-13 13:36:45","username":"administrator"},"name":"Iadea Signboard_V3.scb","path":"/","playFullscreen":False,"playlistsCount":0,"prettifyDuration":"(?)","prettifyLength":"399.5 KB","prettifyType":"Scala Template","readOnly":False,"revision":1,"startValidDate":"2014-06-13","status":"OK","templatesCount":0,"thumbnailDownloadPaths":{"extraSmall":"/resources/thumbnails/1_medium.png","large":"/resources/thumbnails/1_extraLarge.png","medium":"/resources/thumbnails/1_large.png","mediumSmall":"/resources/thumbnails/1_playlist.png","small":"/resources/thumbnails/1_mediumLarge.png"},"uploadedBy":{"firstname":"sboh","id":4,"lastLogin":"2014-06-16 09:48:32","lastname":"sboh","username":"sboh"},"validDateStatus":"CURRENT_NO_EXPIRATION","webDavPath":"/data/autoTest/content/Iadea+Signboard_V3%5B45597185300%5D.scb","width":800,"workgroups":[{"id":2,"name":"sboh","owner":True}],"createdBy":{"firstname":"sboh","id":4,"lastLogin":"2014-06-16 09:48:32","lastname":"sboh","username":"sboh"},"mediaId":1,"numberOfFields":6,"numberOfFiles":0,"templateFields":[{"displayName":"datum","editable":True,"id":1,"maxCharacters":255,"maxLines":1,"name":"datum","order":1,"required":False,"type":"STRING","value":"10-12-2013","displayType":"String"},{"displayName":"allinfo","editable":True,"id":2,"maxCharacters":255,"maxLines":1,"name":"allinfo","order":2,"required":False,"type":"STRING","value":"10.00 - 12.00\tChronischeZorg\n13.00 - 14.00\tGevorderden","displayType":"String"},{"displayName":"naamles","editable":True,"id":3,"maxCharacters":255,"maxLines":1,"name":"naamles","order":3,"required":False,"type":"STRING","value":"CZ Basisopleiding","displayType":"String"},{"displayName":"tijd","editable":True,"id":4,"maxCharacters":255,"maxLines":1,"name":"tijd","order":4,"required":False,"type":"STRING","value":"09.00 - 11.00","displayType":"String"},{"displayName":"soortles","editable":True,"id":5,"maxCharacters":255,"maxLines":1,"name":"soortles","order":5,"required":False,"type":"STRING","value":"B48, D89, D98, I98, Y46, O66, E22, R44, H77, B48, D89, D98","displayType":"String"},{"displayName":"docent","editable":True,"id":6,"maxCharacters":255,"maxLines":1,"name":"docent","order":6,"required":False,"type":"STRING","value":"Dr. K. Wouters","displayType":"String"}]}}
	print ('old field value is: ' + params['fields'][0]['value'])
	params['fields'][0]['value'] = message
	print ('new field value is: ' + params['fields'][0]['value'])
	print ('old name is:' + str(params['name']))
	params['name'] = message_name
	print ('new name is:' + str(params['name']))
	PUT_rest_request(params, baseurl, '/api/rest/messages/thumbnailInMemory/')

	"""This method approves a change to the message indicated by the message_id parameter """
def tn_auth_request(message_id, message_name, message):
	print('sending commit command')
	#http://192.168.10.135:8080/ContentManager/api/rest/messages/5
	params = {"id":5,"approvalDetail":{"approvalStatus":"APPROVED","approvedBy":{"firstname":"sboh","id":4,"lastLogin":"2014-06-16 10:19:12","lastname":"sboh","username":"sboh"},"id":5,"lastModified":"2014-06-16 10:32:36","messageText":"Auto approved by user privilege.","toApprove":{"firstname":"sboh","id":4,"lastLogin":"2014-06-16 10:19:12","lastname":"sboh","username":"sboh"},"user":{"firstname":"sboh","id":4,"lastLogin":"2014-06-16 10:19:12","lastname":"sboh","username":"sboh"}},"approvalStatus":"APPROVED","audioDucking":False,"createdDate":"2014-06-13 10:55:22","generatingThumbnail":False,"height":480,"lastModified":"2014-06-16 10:32:36","mediaType":"MESSAGE","messagesCount":0,"modifiedBy":{"firstname":"sboh","id":4,"lastLogin":"2014-06-16 10:19:12","lastname":"sboh","username":"sboh"},"name":1.1,"playFullscreen":False,"playlistsCount":0,"prettifyDuration":"(0)","prettifyType":"message","readOnly":False,"startValidDate":"2014-06-13","templatesCount":0,"thumbnailDownloadPaths":{"extraSmall":"/resources/thumbnails/MSG_5_medium1.png","large":"/resources/thumbnails/MSG_5_extraLarge1.png","medium":"/resources/thumbnails/MSG_5_large1.png","mediumSmall":"/resources/thumbnails/MSG_5_playlist1.png","small":"/resources/thumbnails/MSG_5_mediumLarge1.png"},"uploadedBy":{"firstname":"sboh","id":4,"lastLogin":"2014-06-16 10:19:12","lastname":"sboh","username":"sboh"},"validDateStatus":"CURRENT_NO_EXPIRATION","width":800,"createdBy":{"firstname":"sboh","id":4,"lastLogin":"2014-06-16 10:19:12","lastname":"sboh","username":"sboh"},"fields":[{"displayName":"datum","id":8,"name":"datum","required":False,"templateId":1,"type":"STRING","value":"13-6-2014 11:32:51 asdfg"},{"displayName":"allinfo","id":12,"name":"allinfo","required":False,"templateId":2,"type":"STRING","value":"09:30-09:50\tGIC Oefenen vaardigheden sessie 2\n09:50-10:15\tGIC Oefenen vaardigheden sessie 3 en CLOSURE\n10:30-10:55\tGIC Oefenen scenario-onderwijs SET en sessie 1"},{"displayName":"naamles","id":11,"name":"naamles","required":False,"templateId":3,"type":"STRING","value":"GIC Oefenen vaardigheden SET en sessie 1"},{"displayName":"tijd","id":7,"name":"tijd","required":False,"templateId":4,"type":"STRING","value":"09:10-09:30"},{"displayName":"soortles","id":9,"name":"soortles","required":False,"templateId":5,"type":"STRING","value":"Generic Instructor Course"},{"displayName":"docent","id":10,"name":"docent","required":False,"templateId":6,"type":"STRING","value":""}],"hasSnapshot":True,"hasUnapprovedElements":False,"pages":1,"template":{"approvalDetail":{"approvalStatus":"APPROVED","approvedBy":{"firstname":"sboh","id":4,"lastLogin":"2014-06-16 10:19:12","lastname":"sboh","username":"sboh"},"id":1,"lastModified":"2014-06-13 10:50:53","messageText":"Auto approved template","toApprove":{"firstname":"sboh","id":4,"lastLogin":"2014-06-16 10:19:12","lastname":"sboh","username":"sboh"},"user":{"firstname":"sboh","id":4,"lastLogin":"2014-06-16 10:19:12","lastname":"sboh","username":"sboh"}},"approvalStatus":"APPROVED","audioDucking":False,"createdDate":"2014-06-13 10:50:53","description":"","downloadPath":"/resources/content/Iadea Signboard_V3[45597185300].scb","generatingThumbnail":False,"height":480,"id":1,"lastModified":"2014-06-13 10:51:50","length":409075,"mediaItemFiles":[{"downloadPath":"%2Fresources%2Fcontent%2FIadea+Signboard_V3%5B45597185300%5D.scb","filename":"Iadea Signboard_V3[45597185300].scb","id":1,"md5":"f35cf884343548276df902fefbf7ad6e","originalFilename":"Iadea Signboard_V3.scb","prettifySize":"397.7 KB","size":407286,"status":"OK","thumbnailDownloadPaths":{"extraSmall":"/resources/thumbnails/1_medium.png","large":"/resources/thumbnails/1_extraLarge.png","medium":"/resources/thumbnails/1_large.png","mediumSmall":"/resources/thumbnails/1_playlist.png","small":"/resources/thumbnails/1_mediumLarge.png"},"uploadDate":"2014-06-13 10:50:53","uploadedBy":"sboh","version":1}],"mediaType":"TEMPLATE","messagesCount":0,"modifiedBy":{"firstname":"System Administrator","id":1,"lastLogin":"2014-06-13 13:36:45","username":"administrator"},"name":"Iadea Signboard_V3.scb","path":"/","playFullscreen":False,"playlistsCount":0,"prettifyDuration":"(?)","prettifyLength":"399.5 KB","prettifyType":"Scala Template","readOnly":False,"revision":1,"startValidDate":"2014-06-13","status":"OK","templatesCount":0,"thumbnailDownloadPaths":{"extraSmall":"/resources/thumbnails/1_medium.png","large":"/resources/thumbnails/1_extraLarge.png","medium":"/resources/thumbnails/1_large.png","mediumSmall":"/resources/thumbnails/1_playlist.png","small":"/resources/thumbnails/1_mediumLarge.png"},"uploadedBy":{"firstname":"sboh","id":4,"lastLogin":"2014-06-16 10:19:12","lastname":"sboh","username":"sboh"},"validDateStatus":"CURRENT_NO_EXPIRATION","webDavPath":"/data/autoTest/content/Iadea+Signboard_V3%5B45597185300%5D.scb","width":800,"workgroups":[{"id":2,"name":"sboh","owner":True}],"createdBy":{"firstname":"sboh","id":4,"lastLogin":"2014-06-16 10:19:12","lastname":"sboh","username":"sboh"},"mediaId":1,"numberOfFields":6,"numberOfFiles":0,"templateFields":[{"displayName":"datum","editable":True,"id":1,"maxCharacters":255,"maxLines":1,"name":"datum","order":1,"required":False,"type":"STRING","value":"10-12-2013","displayType":"String"},{"displayName":"allinfo","editable":True,"id":2,"maxCharacters":255,"maxLines":1,"name":"allinfo","order":2,"required":False,"type":"STRING","value":"10.00 - 12.00\tChronischeZorg\n13.00 - 14.00\tGevorderden","displayType":"String"},{"displayName":"naamles","editable":True,"id":3,"maxCharacters":255,"maxLines":1,"name":"naamles","order":3,"required":False,"type":"STRING","value":"CZ Basisopleiding","displayType":"String"},{"displayName":"tijd","editable":True,"id":4,"maxCharacters":255,"maxLines":1,"name":"tijd","order":4,"required":False,"type":"STRING","value":"09.00 - 11.00","displayType":"String"},{"displayName":"soortles","editable":True,"id":5,"maxCharacters":255,"maxLines":1,"name":"soortles","order":5,"required":False,"type":"STRING","value":"B48, D89, D98, I98, Y46, O66, E22, R44, H77, B48, D89, D98","displayType":"String"},{"displayName":"docent","editable":True,"id":6,"maxCharacters":255,"maxLines":1,"name":"docent","order":6,"required":False,"type":"STRING","value":"Dr. K. Wouters","displayType":"String"}]}}
	print (params['fields'][0]['value'])
	params['fields'][0]['value'] = message
	print (params['fields'][0]['value'])
	params['name']= str(message_name)
	PUT_rest_request(params, baseurl, '/api/rest/messages/'+ str(message_id))
	
print ('logging in and requesting auth token')
authurl = baseurl + '/api/rest/auth/login'
print('url request is: ', authurl)
#resp = session.post(authurl, data=json.dumps(params),proxies=prox)
resp = session.post(authurl, data=json.dumps(params),proxies = None)
print ('sent out request')
#resp = session.post(authurl,data = json.dumps(params))
auth_token = resp.json().get('apiToken')
print ('Auth Token is: ' + auth_token)
# add authorization token to the session
session.headers.update({'apiToken': auth_token})


print('retrieving message list by id')
params = {'offset':0,'limit':15,'sort':'name','fields':'id'}
resp = GET_rest_request(params, baseurl,'/api/rest/media/')

#with open('response.text','w') as f:
#	f.writelines(resp.text)
resp_object = json.loads(resp.text)
#print ('length of list= '+ str(len(resp_object['list'])))


#x = [resp_object['list'][y]['id'] for y in len(resp_object['list'])]
#print (str(x))
#print ('manual count')
#print (resp_object['list'][0]['id'])
#print (resp_object['list'][2]['id'])
#print (resp_object['list'][3]['id'])
#print (resp_object['list'][4]['id'])
#print (resp_object['list'])

'''
message_id_list = [912,911,910,909,908,907,873,1997,862,2004]
message_name_list = ['10.7','10.6','10.5','10.4','10.3','10.2','10.1','10.8','sssss','10.9']
dict_id_name = {}
'''

message_id_list = []
message_name_list = []
dict_id_name = {}

for x in range(len(resp_object['list'])):
	print (x)
	print ('id = ', resp_object['list'][x]['id'])
	print ('name = ', resp_object['list'][x]['name'])
	message_id_list.append(resp_object['list'][x]['id'])
	message_name_list.append(resp_object['list'][x]['name'])
	dict_id_name[resp_object['list'][x]['id']] = str(resp_object['list'][x]['name'])

print (str(message_name_list))
print (str(message_id_list))
print (str(dict_id_name))

while(True):
	for y in range(len(message_id_list)):
		print('about to change text to RIW')
		tn_change_request(message_name_list[y], 'Rich it really worked')
		tn_auth_request(str(message_id_list[y]),str(message_name_list[y]), 'Rich it worked')

	for y in range(len(message_id_list)):
		print('about to change text to BBB')
		tn_change_request(message_name_list[y], 'Blarg Blarg Blarg')
		tn_auth_request(str(message_id_list[y]),str(message_name_list[y]), 'Blarg Blarg Blarg')	
		sleep(3)


'''
print ('**********************************************************1')
tn_change_request('10.1','Rich it worked')
print ('**********************************************************2')
tn_auth_request(873,'10.1','Rich it worked')
'''
