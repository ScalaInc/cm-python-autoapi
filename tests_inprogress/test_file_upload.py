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
def test_endpoint_file_upload_file():
    '''
    Begin a media upload of a single file using POST /api/rest/fileupload/init
    Retain the UUID from the response.  Retain the media id from the response
    Put the file up on the server using PUT /api/rest/fileupload/part/{uuid}/0
    Commit the file upload using POST /api/rest/fileupload/complete/{uuid}
    Verify the media item 'landed' by pulling it back with GET /api/rest/media/{id}
    Delete the media item created in this test with DELETE /api/rest/media/{id}
    :return:
    '''

    global session, baseurl, config
    current_time_since_epoch = time.time()
    local_file_name = config['media_items']['mediafile_1']
    file_upload_path = config['path']['media']

    # Build JSON parameters for file upload in
    file_upload_parameter_list = {'filename':local_file_name,'filepath':file_upload_path,'uploadType':'media_item'}

    # Begin Media upload.   Start with Init call
    resp = rest_request(session, call_type.post, baseurl=config['login']['baseurl'], apiurl='/api/rest/fileupload/init',
                        query_params = None, payload_params= file_upload_parameter_list,  proxy=False)
    logging.info('Response from init call is: status_code =  {}, response = {}'.format(resp.status_code,resp.text))
    assert resp.status_code == 200, 'Received incorrect response code after Media file upload init call.'
    media_id = resp.json()['mediaId']

    # Save off the json response to pluck the uuid out of it
    json_init_response = resp.json()
    logging.debug('UUID from Init call is: {}'.format(json_init_response['uuid']))
    logging.debug('filename from Init call is: {}'.format(json_init_response['filename']))

    # Prep the arguments for the put call
    file = open(config['path']['media'] + local_file_name,'rb')
    file_upload_put_apiurl = '/api/rest/fileupload/part/'+json_init_response['uuid'] + '/0'

    #Send the put request to upload the file
    resp = rest_request(session,call_type.put,baseurl = config['login']['baseurl'], apiurl=file_upload_put_apiurl, file_object = file)
    logging.info('Response from file put call is: status_code =  {}, response = {}'.format(resp.status_code,resp.text))
    file.close()
    assert resp.status_code == 204, 'Received incorrect response code after file put call on media upload'

    # Commit the change
    commit_apiurl = '/api/rest/fileupload/complete/' + json_init_response['uuid']
    resp = rest_request(session,call_type.post, baseurl = config['login']['baseurl'], apiurl=commit_apiurl)
    logging.info('Response  from file complete call is: status_code =  {}, response = {}'.format(resp.status_code,resp.text))
    assert resp.status_code == 204, 'Received incorrect response code after media upload complete call.'

    # Get the Media back
    retrieve_media_apiurl = '/api/rest/media/' + str(media_id)
    resp = rest_request(session, type_of_call=call_type.get, baseurl=baseurl, apiurl=retrieve_media_apiurl)
    logging.info('Response  from media GET call is: status_code =  {}, response = {}'.format(resp.status_code, resp.text))
    assert resp.status_code == 200, 'Received incorrect response code after media get.  Expected 200, received {}'.format(resp.status_code)
    assert resp.json()['id'] == media_id, 'Incorrect media id retrieved by GET.  Expected {}, received {}'.format(media_id, resp.json()['id'])

    # Delete media item to clean up
    delete_apiurl = '/api/rest/media/' + str(media_id)
    resp = rest_request(session, type_of_call=call_type.delete, baseurl=baseurl, apiurl=delete_apiurl)
    logging.info('Response  from delete call is: is: status_code =  {}, response = {}'.format(resp.status_code,resp.text))
    assert resp.status_code == 204, 'Received incorrect response code during media delete call.'

@nottest
@with_setup(t_setup,t_teardown)
def test_endpoint_file_upload_single_file():
    '''
    Begin a media upload of a single file using POST /api/rest/fileupload/init
    Retain the UUID from the response.  Retain the media id from the response
    Put the file up on the server using POST /api/rest/fileupload/part/{uuid}/0
    No need to commit the file when using the POST api call
    Verify the media item 'landed' by pulling it back with GET /api/rest/media/{id}
    Delete the media item created in this test with DELETE /api/rest/media/{id}
    :return:
    '''

    global session, baseurl, config
    current_time_since_epoch = time.time()
    local_file_name = config['media_items']['mediafile_2']
    file_upload_path = config['path']['media']

    # Build JSON parameters for file upload in
    file_upload_parameter_list = {'filename': local_file_name, 'filepath': file_upload_path, 'uploadType': 'media_item'}

    # Begin Media upload.   Start with Init call
    resp = rest_request(session, call_type.post, baseurl=config['login']['baseurl'], apiurl='/api/rest/fileupload/init',
                        query_params = None, payload_params= file_upload_parameter_list,  proxy=False)
    logging.info('Response from init call is: status_code =  {}, response = {}'.format(resp.status_code,resp.text))
    assert resp.status_code == 200, 'Received incorrect response code after Media file upload init call.'
    media_id = resp.json()['mediaId']

    # Save off the json response to pluck the uuid out of it
    json_init_response = resp.json()
    logging.debug('UUID from Init call is: {}'.format(json_init_response['uuid']))
    logging.debug('filename from Init call is: {}'.format(json_init_response['filename']))

    # Prep the arguments for the put call
    file = open(config['path']['media'] + local_file_name, 'rb')
    file_upload_put_apiurl = '/api/rest/fileupload/part/'+json_init_response['uuid'] + '/0'


    #Send the put request to upload the file
    resp = rest_request(session, call_type.post, baseurl=config['login']['baseurl'], apiurl=file_upload_put_apiurl, file_object=file)
    logging.info('Response from file post call is: status_code =  {}, response = {}'.format(resp.status_code, resp.text))
    file.close()
    assert resp.status_code == 204, 'Received incorrect response code after file put call on media upload'

    # Get the Media back
    retrieve_media_apiurl = '/api/rest/media/' + str(media_id)
    resp = rest_request(session, type_of_call=call_type.get, baseurl=baseurl, apiurl=retrieve_media_apiurl)
    logging.info('Response  from media GET call is: is: status_code =  {}, response = {}'.format(resp.status_code,resp.text))
    assert resp.status_code == 200, 'Received incorrect response code after media get.  Expected 200, received {}'.format(resp.status_code)
    assert resp.json()['id'] == media_id, 'Incorrect media id retrieved by GET.  Expected {}, received {}'.format(media_id, resp.json()['id'])

    # Delete media item to clean up
    delete_apiurl = '/api/rest/media/' + str(media_id)
    resp = rest_request(session, type_of_call=call_type.delete, baseurl = baseurl, apiurl=delete_apiurl)
    logging.info('Response  from delete call is: is: status_code =  {}, response = {}'.format(resp.status_code,resp.text))
    assert resp.status_code == 204, 'Received incorrect response code during media delete call.'