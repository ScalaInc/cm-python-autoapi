__author__ = 'rkaye'

from nose import with_setup
from nose.tools import nottest
import logging
import logging.config
import configparser
from framework.constants import CONFIG_FILE_PATH, LOG_FILE_PATH
from framework.authentication_rest import login, logout, get_auth_token
from framework.http_rest import *
from framework.workgroup_rest import Workgroup
from framework.media_metadata_rest import Media_metadata
from framework.category_rest import Category
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
namespace = config['test']['namespace']


def t_setup(upload_media = False):
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

    If the upload_media flag is set to 'true' then media uploads will be generated as part of the setup
    for this test case.  Since media file uploads are costly (in time) it makes sense to only
    upload them for test cases which require them.

    Note:  This test case has flags that set up certain environmental components on a
    test case by test case basis.  If the flag is set to true, then the components are added
    A matching flag in t_teardown should be set to true to make sure that the elements created
    here are automatically cleaned up when the test case exits

    upload_meda = upload 3 media items (jpegs) as defined in the config file
    '''

    # Begin by initiating a new login session for this test case.
    global config, session, media_upload_ids
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

def t_teardown(upload_media=False):
    '''
    This method logs off from the CM.  It is inteded to be run after each test case in this test suite.
    Decorate each test case with:  **@with_setup(setup, teardown)**

    if the upload_media flag is set to True, then the teardown module will attempt to delete the media objects created in
    setup_t
    '''
    global session
    logging.info('Beginning test teardown')
    response = logout(session, config['login']['baseurl'])
    assert response

'''
Categories Tests
'''

@with_setup(t_setup,t_teardown)
def test_endpoint_category_add():
    global session,config,category_id
    baseurl = config['login']['baseurl']
    resp = rest_request(session, type_of_call=call_type.post,baseurl = baseurl, apiurl='/api/rest/categories',payload_params={'name':namespace+"_red",'description':'blue'})
    logging.info('status_code = {}'.format(resp.status_code))
    logging.info('response = {}'.format(resp.text))
    category_id = resp.json()['id']
    assert resp.status_code == 200

@with_setup(t_setup,t_teardown)
def test_endpoint_category_usage():
    global session,config,category_id
    baseurl = config['login']['baseurl']
    resp = rest_request(session, type_of_call=call_type.get,baseurl = baseurl, apiurl='/api/rest/categories/usage',query_params={'ids':category_id})
    logging.info('status_code = {}'.format(resp.status_code))
    logging.info('response = {}'.format(resp.text))
    assert resp.status_code == 200

@with_setup(t_setup,t_teardown)
def test_endpoint_category_list():
    global session,config,category_id
    baseurl = config['login']['baseurl']
    resp = rest_request(session, type_of_call=call_type.get,baseurl = baseurl, apiurl='/api/rest/categories')
    logging.info('status_code = {}'.format(resp.status_code))
    logging.info('response = {}'.format(resp.text))
    assert resp.status_code == 200

@with_setup(t_setup,t_teardown)
def test_endpoint_category_find():
    global session,config,category_id
    baseurl = config['login']['baseurl']
    resp = rest_request(session, type_of_call=call_type.get,baseurl = baseurl, apiurl='/api/rest/categories/' + str(category_id))
    logging.info('status_code = {}'.format(resp.status_code))
    logging.info('response = {}'.format(resp.text))
    assert resp.status_code == 200

@with_setup(t_setup,t_teardown)
def test_endpoint_category_update_single():
    global session,config,category_id
    baseurl = config['login']['baseurl']
    resp = rest_request(session, type_of_call=call_type.put,baseurl = baseurl, apiurl='/api/rest/categories/' + str(category_id),payload_params={'name':namespace+'_red','description':'booga'})
    logging.info('status_code = {}'.format(resp.status_code))
    logging.info('response = {}'.format(resp.text))
    assert resp.status_code == 200


@with_setup(t_setup,t_teardown)
def test_endpoint_category_delete():
    global session,config,category_id
    baseurl = config['login']['baseurl']
    resp = rest_request(session, type_of_call=call_type.delete,baseurl = baseurl, apiurl='/api/rest/categories/' + str(category_id))
    logging.info('status_code = {}'.format(resp.status_code))
    logging.info('response = {}'.format(resp.text))
    assert resp.status_code == 204
