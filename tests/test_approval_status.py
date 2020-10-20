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
    message_id_list = []

    approval_status_username = namespace + '_approvalStatus_' + str(number_of_cases_run)
    approval_status_password = 'approvalStatusPassword'

    # Determine ID of Administrator role
    list_role_apiurl = '/api/rest/roles'
    admin_role_id = None
    resp = rest_request(session, type_of_call=call_type.get, baseurl=baseurl, apiurl=list_role_apiurl,
                        query_params={'fields': 'name,id', 'limit': '1000'})
    logging.debug("Response from list roles is: {}".format(resp.text))
    for item in resp.json()['list']:
        if item['name'] == 'Administrator':
            admin_role_id = item['id']

    # Only users of with the correct role can see media objects I need to see in this test.  Looking for the
    # Administrator role so I can add it to my new user
    assert admin_role_id is not None, 'Could not identify the Administrator Role for this system.  Aborting test'

    # Create user for use in approval status api testing
    user_parameters = {
        'dateFormat': 'MM-dd-yyyy',
        'emailaddress': 'approval_status@scala.com',
        'enabled': True,
        'firstname': 'Approval',
        'isAsiaSpeakingLanguage': True,
        'isSuperAdministrator': True,
        'isWebserviceUser': True,
        'language': 'English',
        'languageCode': 'en',
        'lastname': 'Status',
        'password': approval_status_password,
        'name': 'user first name and last name',
        'receiveApprovalEmails': 'false',
        'receiveEmailAlerts': 'false',
        'timeFormat': '12h',
        'roles': [{'id': admin_role_id}],
        'username': approval_status_username
    }
    new_user_apiurl = '/api/rest/users'
    resp = rest_request(session, type_of_call=call_type.post, baseurl=baseurl, apiurl=new_user_apiurl,
                        payload_params=user_parameters)
    logging.debug('Create User status code = {}'.format(resp.status_code))
    logging.debug('Response from Create User is: {}'.format(resp.text))
    user_id_list.append(resp.json()['id'])

    # Login as new user
    session_not_admin = login(approval_status_username, approval_status_password, baseurl)
    assert session_not_admin is not None
    session = session_not_admin

    # Create Media for use in Approval Status API testing
    resp = rest_request(session, type_of_call=call_type.get, baseurl=baseurl, apiurl='/api/rest/media',
                        query_params={'fields': 'id'})
    # time.sleep(10)
    logging.debug('list of media on the system before we add new media = {}'.format(resp.text))
    media_name = namespace + '_approval_status_' + str(number_of_cases_run)
    media_params = {'name': media_name, 'uri': 'http://www.approval_status.com', 'mediaType': 'HTML'}
    resp = rest_request(session_not_admin, type_of_call=call_type.post, baseurl=baseurl, apiurl='/api/rest/media',
                        payload_params=media_params)
    logging.debug('Create Media response is: {}'.format(resp.text))
    media_id_list.append(resp.json()['id'])
    logging.debug('Media for tests has been created id = {}'.format(media_id_list))

    #Create Approval record for the media object using the new user as login
    #New user is used b/c administrator leaves no traces when he approves a media object :(
    approval_parameters = {'approval': {'action': 'APPROVE'}}
    approve_media_apiurl = '/api/rest/media/' + str(media_id_list[0])
    resp = rest_request(session_not_admin, type_of_call=call_type.put, baseurl=baseurl, apiurl=approve_media_apiurl,
                        payload_params=approval_parameters)
    # Upload a template
    # TODO: need to write the routine to upload a template and get the template id

    # Upload a message to the template
    # TODO: need to write the routine to upload a message and assign it to a template
    # TODO: and get the message id and add it to the message_id_list


    number_of_cases_run += 1


def t_teardown():
    global session, baseurl, media_id_list, user_id_list

    # first login as administrator
    resp = logout(session, config['login']['baseurl'])
    username = config['login']['username']
    password = config['login']['password']
    session = login(username, password, baseurl)
    assert session is not None

    # Delete User Profile created for this test -
    delete_user_apiurl = '/api/rest/users/' + str(user_id_list[0])
    logging.debug('URL for delete user call is: {}'.format(delete_user_apiurl))
    logging.debug('ID of user to delete is foo: {}'.format(user_id_list))
    resp = rest_request(session, type_of_call=call_type.delete, baseurl=baseurl, apiurl=delete_user_apiurl)
    logging.debug('Response code of delete user is foo: {}'.format(resp.status_code))
    logging.debug('Calling delete user to clean up after test case: {}'.format(resp.text))
    if resp.status_code == 500:
        logging.debug('foo: Status code 500 detected.  Response is: {}'.format(resp.text))

    # Delete Media object created for this test
    logging.debug('Deleting Media for this test suite id = {}'.format(media_id_list))
    baseurl = config['login']['baseurl']
    media_delete_apiurl = '/api/rest/media/' + str(media_id_list[0])
    logging.debug('Calling Delete Media for apiurl foo = {}'.format(media_delete_apiurl))
    resp = rest_request(session, type_of_call=call_type.delete, baseurl=baseurl, apiurl=media_delete_apiurl)
    logging.debug('Response from delete Media call is foo: {}'.format(resp.status_code))
    logging.debug('Status code from delete Media call is foo: {}'.format(resp.status_code))
    if resp.status_code != 204:
        logging.debug("Media may have not been deleted at end of this test case.")

    # Delete the template created for this test
    # TODO: write the routine to delete the template created for this test

    # Delete the message created for this test
    # TODO: write the routine to delete the message created for this test
    
    response = logout(session, config['login']['baseurl'])


@with_setup(t_setup, t_teardown)
def test_endpoint_list_approver_media():
    global session, media_id_list, baseurl
    logging.debug('Media for this test is: {}'.format(media_id_list))
    apiurl = '/api/rest/approvalStatus/' + str(media_id_list[0]) + '/mediaApprovers'
    resp = rest_request(session, type_of_call=call_type.get, baseurl=baseurl, apiurl=apiurl)
    logging.debug(resp.text)
    assert resp.status_code == 200

# need to complete the TODOs above before enabling this test
@nottest
# @with_setup(t_setup, t_teardown)
def test_endpoint_list_approver_message():
    global session, media_id_list, baseurl
    logging.debug('Media for this test is: {}'.format(media_id_list))
    apiurl = '/api/rest/approvalstatus' + str(message_id_list[0]) + '/messageApprovers'
    resp = rest_request(session, type_of_call=call_type.get, baseurl=baseurl, apiurl=apiurl)
    pass


@with_setup(t_setup, t_teardown)
def test_endpoint_list_possible_approval_states():
    global session, baseurl
    apiurl = '/api/rest/approvalStatus'
    resp = rest_request(session, type_of_call=call_type.get, baseurl=baseurl, apiurl=apiurl)
    logging.debug('List Possible States request returned: {}'.format(resp.text))
    assert resp.status_code == 200, 'List Possible States message failed with this response: {}'.format(resp.text)


@with_setup(t_setup, t_teardown)
def test_endpoint_current_approval_state():
    global session, baseurl
    apiurl = '/api/rest/approvalStatus/' + str(media_id_list[0]) + '/state'
    resp = rest_request(session, type_of_call=call_type.get, baseurl=baseurl, apiurl=apiurl)
    logging.debug('List current state request returned: {}'.format(resp.text))
    assert resp.status_code == 200, 'List current States message failed with this response: {}'.format(resp.text)

