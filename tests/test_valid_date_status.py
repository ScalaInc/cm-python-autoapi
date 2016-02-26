__author__ = 'rkaye'
from nose import with_setup
from nose.tools import nottest
import logging
import logging.config
import configparser
from framework.constants import CONFIG_FILE_PATH, LOG_FILE_PATH
from framework.authentication_rest import login, logout, get_auth_token
from framework.http_rest import *
import inspect

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
    This method logs off from the CM.  It is inteded to be run after each test case in this test suite.
    Decorate each test case with:  **@with_setup(setup, teardown)**

    if the upload_media flag is set to True, then the teardown module will attempt to delete the media objects created in
    setup_t
    '''
    global session
    logging.info('Beginning test teardown')
    response = logout(session, config['login']['baseurl'])
    assert response


@with_setup(t_setup, t_teardown)
def test_endpoint_valid_date_status():
    global session, baseurl

    valid_date_apiurl = '/api/rest/validDateStatus'

    resp = rest_request(session, type_of_call=call_type.get, baseurl= baseurl, apiurl = valid_date_apiurl)
    logging.debug('Response from Get Valid Date Status call is: status code = {}, response = {}'.format(resp.status_code, resp.text))
    assert resp.status_code == 200, 'Status code from Valid Date Status call was not correct.  Expected 200 received {}'.format(resp.status_code)
    status_values = resp.json()['statusValues']
    assert len(status_values) == 4
