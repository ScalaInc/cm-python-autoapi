__author__ = 'rkaye'
from nose import with_setup
from nose.tools import nottest
import logging
import logging.config
import configparser
from framework.fileupload_rest import File_upload
from framework.constants import CONFIG_FILE_PATH, LOG_FILE_PATH
from framework.authentication_rest import login, logout, get_auth_token
from framework.http_rest import *
import inspect
import time

print(CONFIG_FILE_PATH)
config = configparser.ConfigParser()
config.read(CONFIG_FILE_PATH)
baseurl = config['login']['baseurl']
logging.config.fileConfig(LOG_FILE_PATH)
logging.debug('Logging config file path is: {}'.format(CONFIG_FILE_PATH))
session = requests.Session()
category_id = 0
media_id_list = []
user_id_list = []
number_of_cases_run = 0
namespace = config['test']['namespace']


def this_function_name():
    return inspect.stack()[1][3]


def t_setup():
    '''
    In order to test this case, a new user must be created and the session must be logged in as this new user.
    That user must create a media and then approve it.
    '''

    # Begin by initiating a new login session for this test case.
    global config, session, media_id_list, user_id_list, baseurl, number_of_cases_run, namespace
    logging.info('Beginning test setup')
    baseurl = config['login']['baseurl']
    username = config['login']['username']
    password = config['login']['password']
    logging.debug('Read login info from config file and ready to begin.')
    logging.info('Initilizing session for next test case.')
    media_path = config['path']['media']
    # INITIALIZE SESSION OBJECT
    session = login(username, password, baseurl)
    assert session is not None
    media_id_list = []
    user_id_list = []


def t_teardown(upload_media=False):
    '''
    This method logs off from the CM.  It is intended to be run after each test case in this test suite.
    Decorate each test case with:  **@with_setup(setup, teardown)**

    if the upload_media flag is set to True, then the teardown module will attempt to delete the media objects created in
    setup_t
    '''
    global session
    logging.info('Beginning test teardown')
    response = logout(session, config['login']['baseurl'])
    assert response

@with_setup(t_setup,t_teardown)
def test_endpoint_list_frame_numbers():
    '''
    Call GET /api/rest/framesetTemplates/numberOfFrames
    validate response formatted coreectly
    :return:
    '''
    global session,baseurl

    get_frameset_summary_list_apiurl = '/api/rest/framesetTemplates/numberOfFrames'
    resp = rest_request(session, type_of_call=call_type.get,baseurl = baseurl, apiurl = get_frameset_summary_list_apiurl)
    logging.debug('Response from Get Frame List call is: status_code = {}, response = {}'.format(resp.status_code, resp.text))
    assert resp.status_code == 200,'Unexpected status code returned from get frame list request.  Expected 200, got {}'.format(resp.status_code)

@with_setup(t_setup, t_teardown)
def test_endpoint_list_framesets():
    '''
    Use GET /api/rest/framesetTemplates to pull down a list of all framesets
    :return:
    '''

    global session,baseurl

    get_frameset_list_apiurl = '/api/rest/framesetTemplates'
    resp = rest_request(session, type_of_call=call_type.get, baseurl = baseurl, apiurl = get_frameset_list_apiurl)
    logging.debug('Response from Get Frame List call is: status_code = {}, response = {}'.format(resp.status_code, resp.text))
    assert resp.status_code == 200,'Unexpected status code returned from get frame list request.  Expected 200, got {}'.format(resp.status_code)

@with_setup(t_setup, t_teardown)
def test_endpoint_compare_frameset_list_results():
    '''
    use GET /api/rest/framesetTemplates/numberOfFrames to pull down the frameset summary
    use GET /api/rest/framesetTemplates to pull down the actual framesets
    Compare the total number of framesets in both lists - they should be the same
    Note:  Max of 1000 framesets can be supported in this test
    :return:
    '''

    global session,baseurl
    get_frameset_summary_list_apiurl = '/api/rest/framesetTemplates/numberOfFrames'
    resp_summary = rest_request(session, type_of_call=call_type.get,baseurl = baseurl, apiurl = get_frameset_summary_list_apiurl)
    logging.debug('Response from Get Frame List call is: status_code = {}, response = {}'.format(resp_summary.status_code, resp_summary.text))
    assert resp_summary.status_code == 200,'Unexpected status code returned from get frame list request.  Expected 200, got {}'.format(resp_summary.status_code)

    get_frameset_list_apiurl = '/api/rest/framesetTemplates'
    resp_actual = rest_request(session, type_of_call=call_type.get, baseurl = baseurl, apiurl = get_frameset_list_apiurl, query_params={'limit':1000})
    logging.debug('Response from Get Frame List call is: status_code = {}, response = {}'.format(resp_actual.status_code, resp_actual.text))
    assert resp_actual.status_code == 200,'Unexpected status code returned from get frame list request.  Expected 200, got {}'.format(resp_actual.status_code)

    # Now collect the total number of framesets returned by both API calls
    list_of_frameset_summary_counts = [item['numberOfFramesets']for item in resp_summary.json()['frameNumbers']]
    frameset_summary_total = sum(list_of_frameset_summary_counts)
    frameset_list_total = resp_actual.json()['count']

    logging.info('Summary API call returned {} framesets, list API call returned {} framesets'.format(frameset_summary_total,frameset_list_total))
    assert frameset_summary_total == frameset_list_total

@with_setup(t_setup,t_teardown)
def test_endpoint_find_frameset_by_id():
    '''
    use Get /api/rest/framesetTemplates to pull down a list of all framesets
    use GET /api/rest/framesetTemplate/{id} to pull down each template by ID
    Verify that all of the framesets pull down by ID
    NOTE: Max of 1000 framesets on system for this test
    :return:
    '''
    global session, baseurl

    # GET list of framesets on the system
    get_frameset_list_apiurl = '/api/rest/framesetTemplates'
    get_frameset_query_params = {'limit':1000, 'fields':'id'}

    resp = rest_request(session, type_of_call=call_type.get, baseurl=baseurl, apiurl = get_frameset_list_apiurl, query_params=get_frameset_query_params)
    logging.debug('Response from GET frameset list request is: status_code = {}, response = {}'.format(resp.status_code, resp.text))

    list_of_frameset_ids = [item['id'] for item in resp.json()['list']]

    # Now pull down each frame_id in the list one at a time and confirm that the ID's match
    for frame_id in list_of_frameset_ids:
        get_one_frameset_apiurl = get_frameset_list_apiurl + '/' + str(frame_id)
        resp = rest_request(session, type_of_call=call_type.get, baseurl = baseurl, apiurl=get_one_frameset_apiurl)
        logging.debug('Response code from GET Frameset by ID call is: {}'.format(resp.status_code))
        assert resp.status_code == 200, 'Incorrect status code for GET response.  Expected 200, got {}'.format(resp.status_code)
        assert resp.json()['id'] == frame_id,'Incorrect ID in GET response.  Expected {}, got {}'.format(frame_id, resp.json()['id'])
        logging.info('Matched IDs of Framesets. {} == {}'.format(frame_id, resp.json()['id']))

@with_setup(t_setup, t_teardown)
def test_endpoint_create_frameset():
    '''
    Use POST /ContentManager/api/rest/framesetTemplates to create a frameset
    Validate that the field of the object in the response match those in the request(names only for this test case)
    Delete the newly created frameset.
    :return:
    '''
    global session, baseurl, namespace
    frameset_name = namespace + '_' + this_function_name()

    add_frameset_apiurl = '/api/rest/framesetTemplates'
    add_frameset_parameter = {"name": frameset_name}
    #
    # add_frameset_parameter = {	"name": frameset_name,
    #                                     "frames": [
    #                                         {
    #                                             # "id": 17,
    #                                             "name": "Main",
    #                                             "color": "#ccccff",
    #                                             "left": 214,
    #                                             "top": 0,
    #                                             "width": 1066,
    #                                             "height": 640,
    #                                             "zOrder": 0,
    #                                             "autoscale": "FILL_EXACTLY",
    #                                             "hidden": False
    #                                         },
    #                                         {
    #                                             # "id": 98,
    #                                             "name": "Left",
    #                                             "color": "#99ccff",
    #                                             "left": 0,
    #                                             "top": 0,
    #                                             "width": 214,
    #                                             "height": 640,
    #                                             "zOrder": 1,
    #                                             "autoscale": "FILL_EXACTLY",
    #                                             "hidden": False
    #                                         },
    #                                         {
    #                                             # "id": 19,
    #                                             "name": "Bottom Crawl",
    #                                             "color": "#9999cc",
    #                                             "left": 0,
    #                                             "top": 640,
    #                                             "width": 1280,
    #                                             "height": 128,
    #                                             "zOrder": 2,
    #                                             "autoscale": "FILL_EXACTLY",
    #                                             "hidden": False
    #                                         }
    #                                     ],
    #                                     "defaultSet": True,
    #                                     "width": 1280,
    #                                     "height": 768}
    #

    resp = rest_request(session, type_of_call=call_type.post, baseurl = baseurl, apiurl = add_frameset_apiurl, payload_params= add_frameset_parameter)
    logging.debug('Response from add frameset request is: status_code = {}, response = {}'.format(resp.status_code, resp.text))
    assert resp.status_code == 200, 'Unexpected status code received on add frameSet request.  Expected 200, got {}'.format(resp.status_code)
    assert 'id' in resp.json().keys(), 'Did not find ID in the object created by add frameset API call'
    assert resp.json()['name'] == frameset_name, 'Name of object created by this test is not correct.  Expected {}, found {}'.format(frameset_name, resp.json()['name'])
    #Clean up
    delete_apiurl = add_frameset_apiurl +'/' + str(resp.json()['id'])
    resp = rest_request(session, type_of_call=call_type.delete, baseurl = baseurl, apiurl = delete_apiurl)
    assert resp.status_code == 204, 'Incorrect status code returned on delete frameset request.  Expected 204, got {}'.format(resp.status_code)

@with_setup(t_setup, t_teardown)
def test_endpoint_modify_frameset():
    '''
    Use POST /ContentManager/api/rest/framesetTemplates to create a frameset
    Validate that the field of the object in the response match those in the request(names only for this test case)
    Delete the newly created frameset.
    :return:
    '''
    global session, baseurl, namespace, frameset_id
    frameset_name = namespace + '_' + this_function_name()
    add_frameset_apiurl = '/api/rest/framesetTemplates'

    add_frameset_parameter = {"name": frameset_name}
    # add_frameset_parameter = {	"name": frameset_name,
    #                                     "frames": [
    #                                         {
    #                                             "id": 17,
    #                                             "name": "Main",
    #                                             "color": "#ccccff",
    #                                             "left": 214,
    #                                             "top": 0,
    #                                             "width": 1066,
    #                                             "height": 640,
    #                                             "zOrder": 0,
    #                                             "autoscale": "FILL_EXACTLY",
    #                                             "hidden": False
    #                                         },
    #                                         {
    #                                             "id": 98,
    #                                             "name": "Left",
    #                                             "color": "#99ccff",
    #                                             "left": 0,
    #                                             "top": 0,
    #                                             "width": 214,
    #                                             "height": 640,
    #                                             "zOrder": 1,
    #                                             "autoscale": "FILL_EXACTLY",
    #                                             "hidden": False
    #                                         },
    #                                         {
    #                                             "id": 19,
    #                                             "name": "Bottom Crawl",
    #                                             "color": "#9999cc",
    #                                             "left": 0,
    #                                             "top": 640,
    #                                             "width": 1280,
    #                                             "height": 128,
    #                                             "zOrder": 2,
    #                                             "autoscale": "FILL_EXACTLY",
    #                                             "hidden": False
    #                                         }
    #                                     ],
    #                                     "defaultSet": False,
    #                                     "width": 1280,
    #                                     "height": 768}


    resp = rest_request(session, type_of_call=call_type.post, baseurl = baseurl, apiurl = add_frameset_apiurl, payload_params= add_frameset_parameter)
    logging.debug('Response from add frameset request is: status_code = {}, response = {}'.format(resp.status_code, resp.text))
    assert resp.status_code == 200, 'Unexpected status code received on add frameSet request.  Expected 200, got {}'.format(resp.status_code)
    assert 'id' in resp.json().keys(), 'Did not find ID in the object created by add frameset API call'
    assert resp.json()['name'] == frameset_name, 'Name of object created by this test is not correct.  Expected {}, found {}'.format(frameset_name, resp.json()['name'])

    frameset_id = resp.json()['id']
    modify_frameset_apiurl = '/api/rest/framesetTemplates/' + str(frameset_id)
    new_frame_name = 'new new new new'
    modify_frameset_parameter = {
        "id": frameset_id,
        "name": "rst01_blahdi-blu",
        "frames": [
            {
                "id": 78,
                "name": "Main",
                "color": "#ccccff",
                "left": 214,
                "top": 0,
                "width": 1066,
                "height": 640,
                "zOrder": 0,
                "autoscale": "FILL_EXACTLY",
                "hidden": False
            },
            {
                "id": 79,
                "name": "Left",
                "color": "#99ccff",
                "left": 0,
                "top": 0,
                "width": 214,
                "height": 640,
                "zOrder": 1,
                "autoscale": "FILL_EXACTLY",
                "hidden": False
            },
            {
                "id": 80,
                "name": "Bottom Crawl",
                "color": "#9999cc",
                "left": 0,
                "top": 640,
                "width": 1280,
                "height": 128,
                "zOrder": 2,
                "autoscale": "FILL_EXACTLY",
                "hidden": False
            },
            {
                "id": 81,
                "name": new_frame_name,
                "color": "#9999cc",
                "left": 0,
                "top": 640,
                "width": 1280,
                "height": 128,
                "zOrder": 3,
                "autoscale": "FILL_EXACTLY",
                "hidden": False
            }
        ],
        "defaultSet": False,
        "width": 1280,
        "height": 768
}

    resp = rest_request(session, type_of_call=call_type.put, baseurl = baseurl, apiurl = modify_frameset_apiurl, payload_params=modify_frameset_parameter)
    logging.debug('Response from put frameset is: status_code = {}, response = {}'.format(resp.status_code, resp.text))
    assert resp.status_code == 200, 'Received unexpected response code when calling PUT /api/rest/framesetTemplates, expected 200, got {}'.format(resp.status_code)

    # Now pull back the frameset and see if the change took effect
    resp = rest_request(session,type_of_call=call_type.get, baseurl = baseurl, apiurl = modify_frameset_apiurl)
    logging.debug('Response from get frameset is: status_code = {}, response = {}'.format(resp.status_code, resp.text))
    assert resp.status_code == 200, 'Received unexpected response code when calling GET /api/rest/frameesetTemplates, expected 200, got {}'.format(resp.status_code)

    # Verify that the new frame was added to the frameset
    assert len(resp.json()['frames']) == 4, 'Expected 4 frames in frameset, found {}'.format(len(resp.json()['frames']))

    # Delete the object created in this test
    delete_apiurl = '/api/rest/framesetTemplates/' + str(frameset_id)
    resp = rest_request(session, type_of_call=call_type.delete, baseurl = baseurl, apiurl = delete_apiurl)
    assert resp.status_code == 204, 'Received unexpected response from DELETE /api/rest/framesetTemplates: status code = {}, response = {}'.format(resp.status_code,resp.text)
