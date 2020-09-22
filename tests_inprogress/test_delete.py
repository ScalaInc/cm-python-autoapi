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
from framework.media_rest import Media
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
api_version = config['api_info']['api_version']


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
def test_delete_1000_media():
    '''
    Delete 1000 media from the CM
    :return:
    '''

    global baseurl, session, api_version
    # Get a list of media items by ID
    media_object = Media(api_version)
    assert media_object.list_media(session, baseurl, limit=1000, fields='id')
    logging.info('Found {} media items'.format(len(media_object.last_response.json()['list'])))
    for id in media_object.last_response.json()['list']:
        current_id = id['id']
        assert media_object.delete_media_by_id(session, baseurl=baseurl, id=current_id)
