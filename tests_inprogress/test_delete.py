__author__ = 'rkaye'

import datetime

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
from framework.users_rest import Users
from framework.roles_rest import Roles

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
api_version_users = config['api_info']['api_version_users']
api_version_roles = config['api_info']['api_version_roles']

def this_function_name():
    return inspect.stack()[1][3]


def t_setup():
    '''
    In order to test this case, a new user must be created and the session must be logged in as this new user.
    That user must create a media and then approve it.
    '''

    # Begin by initiating a new login session for this test case.
    global config, session, media_id_list, user_id_list, baseurl, number_of_cases_run, namespace, unique_name, \
        user_object, api_version_users, api_version_roles
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
    # create a data structure with all the role ID and Name information for use by test cases
    role_object = Roles(api_version_roles)
    role_object.list_roles(session=session,
                           baseurl=baseurl,
                           limit=100,
                           fields='name,id')
    role_list_response = role_object.get_response_key('list')

    logging.debug("role_list_responses {}".format(str(role_list_response)))

    # set up a unique string associated with this test for naming objects
    now = datetime.datetime.now()
    unique_name = namespace + "_" + now.strftime("%Y_%m_%d_%H%S.%f")
    user_object = Users(api_version_users)

    assert user_object.create_user(session=session,
                                   baseurl=baseurl,
                                   emailAddress=unique_name + str(1) + 'setup@' + 'blah.com',
                                   username=unique_name + "_setup_setup_" + str(1),
                                   firstname=unique_name + "_setup" + str(1),
                                   lastname=unique_name + "_setup" + str(1),
                                   password="12345678",
                                   name="setup_setup" + str(1),
                                   role_list=[role_list_response[0]]
                                   ), 'create user failed in setup for tests_delete.py'

    user_id_list.append(user_object.get_response_key('id'))
    logging.debug("Appended user_id {} to user_id_list".format(user_object.get_response_key('id')))

def t_teardown(upload_media=False):
    '''
    This method logs off from the CM.  It is intended to be run after each test case in this test suite.
    Decorate each test case with:  **@with_setup(setup, teardown)**

    if the upload_media flag is set to True, then the teardown module will attempt to delete the media objects created in
    setup_t
    '''
    global session
    # TODO: Need to delete users that begin with unique_name[:4] or starts with unique_name
    logging.info('Beginning test teardown')
    response = logout(session, config['login']['baseurl'])
    assert response

@with_setup(setup=t_setup)
def test_login_new_user():
    global session, user_id_list, user_name, user_password, baseurl, unique_name
    user_name = unique_name + "_setup_setup" + str(1)
    user_password = "12345678"
    logging.info("Logging in with new user {} and password {}".format(user_name, user_password))
    session = login(user_name, user_password, baseurl)

    assert session is not None, "unable to login with user_name {}".format(user_name)

    logging.info("Successfully logged in with user_name {}".format(user_name))

# @with_setup(t_setup, t_teardown)
def test_upload_1000_media():
    global session, user_id_list, user_name, user_password, baseurl, unique_name
    # need to create a list of media objects to load
    # need to upload the objects
    pass

@nottest
@with_setup(teardown=t_teardown)
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
