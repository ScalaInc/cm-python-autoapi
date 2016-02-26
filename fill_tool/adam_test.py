__author__ = 'rkaye'
from nose import with_setup
import logging
import logging.config
import configparser
from framework.constants import *
from framework.authentication_rest import login, logout, get_auth_token
from framework.http_rest import *
from framework.users_rest import user_cm
from framework.workgroup_rest import Workgroup
from framework.media_metadata_rest import Media_metadata
from framework.category_rest import Category
from framework.fileupload_rest import File_upload

config = ""
session = requests.Session()

# global list of headers from file
headers = []
baseurl = ""

def setup_module():
    '''
    .. py:function:: setup_module()
    This module runs once at the beginning of this test suite.  Nose automatically executes
    the commands in this module once when this test suite starts
    '''
    global config
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE_PATH)
    logging.config.fileConfig(LOG_FILE_PATH)
    logging.debug('Config file path is: {}'.format(CONFIG_FILE_PATH))

def t_setup():
    '''
    Parameters read from config file:
    login.baseurl - the base url of the CM under test.
    login.username - the username used to log into the CM under test
    login.password - the password used by the scripts to log into the CM under test

    This method initializes the test session by logging into the CM under test and populating
    the session object used by this test suite.  The session object created by this method
    is authorized to send api commands to the CM under test.

    Setup is intended to be run before each test in this suite - ensuring that a new session
    is used for each test case (no side effects between test cases)

    Decorate each test case with: **@with_setup(t_setup, t_teardown)**
    '''
    global config, session, baseurl
    logging.info('Beginning test setup')
    baseurl = config['login']['baseurl']
    username = config['login']['username']
    password = config['login']['password']
    logging.debug('Read login info from config file and ready to begin.')
    logging.info('Initilizing session for next test case.')
    media_path = config['path']['media']
    # INITIALIZE SESSION OBJECT
    session = login(username, password, baseurl,networkID=0)
    assert session is not None


def t_teardown():
    '''
    This method logs off from the CM.  It is inteded to be run after each test case in this test suite.
    Decorate each test case with:  **@with_setup(setup, teardown)**
    '''
    global session, config
    logging.info('Beginning test teardown')
    response = logout(session, config['login']['baseurl'])
    assert response

@with_setup(t_setup, t_teardown)
def test_adam():
    '''
    This test is a quick and dirty test case that we used to duplicate CM-8718 (Wendys).  The test creates n players
    in the CM under test, and then modifes the metadata settings on eacy one.  Changing the value of n increases the
    number of players created.

    Each iteration through the main loop performs one POST request to add the player (/api/rest/players) and
    one PUT request to modify the metadata (/api/rest/players/{id})

    Each API call is loosly verified by checking the http response code (which should be 200).
    :return:
    '''
    global headers, session, config
    n = 1000
    param1 = {"type": "SCALA", "name": "player_1_kaye"}
    param_list = []
    for x in range(0,0+n):
        name = 'kaye_player_'+str(x)
        param_list.append({"type":"SCALA","name":name})
        logging.debug('adding next parameter to list of players: {}'.format(str(param_list[-1])))
    json_put = {'name': '<player name>', 'metadataValue': [{'playerMetadata': {'datatype': 'STRING', 'valueType': 'ANY', 'name': 'Player.StoreID', 'id': '20'},
                                                            'value': 'any value here'}, {'playerMetadata': {'datatype': 'BOOLEAN', 'valueType': 'ANY', 'name': 'Player.isExternal', 'id': '22'},
                                                            'value': 'TRUE'}],'playerDisplays': [{'channel': {'id': '49'}, 'screenCounter': 1}, {'channel': {'id': '168'}, 'screenCounter': 1}]}
    logging.debug('about to add this put record'+json.dumps(json_put,sort_keys=True, indent = 4, separators = (',',': ')))
    for item in param_list:
        json_put['name'] = item['name']
        resp = rest_request(session,call_type.post,baseurl = config['login']['baseurl'],apiurl="/api/rest/players",payload_params=item)
        logging.info('The status code for the add is: {} for entry {}'.format(resp.status_code, item['name']))
        assert resp.status_code == 200
#        logging.debug('The ID of the created record is: {}'.format(resp.json()['id']))
#        resp2 = rest_request(session,call_type.put,baseurl = config['login']['baseurl'],apiurl="/api/rest/players/"+str(resp.json()['id']),payload_params = json_put)
#        logging.info('The status code for the put on is: {} for entry {}'.format(resp2.status_code, item['name']))
#        assert resp2.status_code == 200
        pass

@with_setup(t_setup, t_teardown)
def test_CM_8689():
    '''
    Test to validate CM 8689.  A quick and dirty test relying on manual setup of the CM to run one or two scenarios
    using Media metadata.  The Metadata ID = metadata_id, and the media id = media_id.  Both of these are manually set up
    at the beginning of the test case.
    :return:
    '''
    global session

    # Settings for marabuntu
    metadata_id = 6
    media_id = 34
    baseurl = 'http://107.1.98.148:8080/ContentManager'

    # Settngs for local Content Manager
    # metadata_id = 2
    # media_id = 9
    # baseurl = 'http://192.168.200.129:8080/ContentManager'

    apiurl = '/api/rest/media/' + str(media_id)
    resp = rest_request(session,type_of_call=call_type.get,baseurl=baseurl, apiurl = apiurl)
    logging.info('Response of media get is: status_code = {}, response = {}'.format(resp.status_code, resp.text))

    values_to_test = [1,2,True, False, None, 'blueberry pie', 5, -233]

    for value in values_to_test:
        logging.info('About to test the PUT call with value = {}'.format(value))
        data_param = {"metadataValue": [
                    {
                    "id": 3,
                    "value": value,
                    "metadata": {
                    "id": metadata_id,
                    "datatype": "STRING",
                    "valueType": "PICKLIST",
                    "predefinedValues": [
                        {
                        "id": 1,
                        "value": "a",
                        "sortOrder": 1
                        },
                        {
                        "id": 2,
                        "value": "b",
                        "sortOrder": 2
                        }
                    ]
                    }
                    }
                ]}



        #data_param =  {"id":34,"name":"RobotWorm.jpg","downloadPath":"/resources/content/test2/RobotWorm[46358636600].jpg","webDavPath":"/data/scala/content/test2/RobotWorm%5B46358636600%5D.jpg","path":"/content/test2","audioDucking":false,"playFullscreen":false,"approvalStatus":"APPROVED","approvalDetail":{"id":34,"approvalStatus":"APPROVED","user":{"id":1,"username":"administrator","firstname":"System Administrator","lastname":"Administrator","lastLogin":"2014-09-09 15:06:31"},"toApprove":{"id":1,"username":"administrator","firstname":"System Administrator","lastname":"Administrator","lastLogin":"2014-09-09 15:06:31"},"approvedBy":{"id":1,"username":"administrator","firstname":"System Administrator","lastname":"Administrator","lastLogin":"2014-09-09 15:06:31"},"messageText":"Auto approved by user privilege.","lastModified":"2014-09-09 15:10:14"},"createdDate":"2014-09-09 13:59:26","mediaType":"IMAGE","startValidDate":"2014-09-09","length":23180,"prettifyLength":"22.6 KB","revision":1,"uploadedBy":{"id":1,"username":"administrator","firstname":"System Administrator","lastname":"Administrator","lastLogin":"2014-09-09 15:06:31"},"modifiedBy":{"id":1,"username":"administrator","firstname":"System Administrator","lastname":"Administrator","lastLogin":"2014-09-09 15:06:31"},"messagesCount":0,"playlistsCount":1,"templatesCount":0,"validDateStatus":"CURRENT_NO_EXPIRATION","mediaItemFiles":[{"id":32,"filename":"RobotWorm[46358636600].jpg","size":23180,"prettifySize":"22.6 KB","uploadDate":"2014-09-09 13:59:26","version":1,"downloadPath":"/resources/content/test2/RobotWorm[46358636600].jpg","originalFilename":"RobotWorm.jpg","status":"OK","uploadedBy":"administrator","md5":"a1a56e2044ac3ab9a42bb3bc67e7fbd3","mediaType":"IMAGE"}],"metadataValue":[{"id":3,"value":"2","metadata":{"id":6,"name":"MediaItem.blah blah blah","datatype":"STRING","valueType":"PICKLIST","order":1,"predefinedValues":[{"id":1,"value":"a","sortOrder":1},{"id":2,"value":"b","sortOrder":2}]}}],"prettifyType":"Image","status":"OK","generatingThumbnail":true,"readOnly":false,"uploadType":"MEDIA"}



        resp = rest_request(session, type_of_call=call_type.put, baseurl = baseurl, apiurl = apiurl, payload_params=data_param)
        logging.info('Response from PUT to change value to {} is: status_code= {}, response = {}'.format(value,resp.status_code, resp.text))

        resp = rest_request(session, type_of_call = call_type.get, baseurl = baseurl, apiurl = '/api/rest/media/34')
        logging.info('Media items found in response are: {}'.format(resp.text))



