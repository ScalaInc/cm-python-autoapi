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
def test_endpoint_get_db_config():
    '''
    Use GET /api/rest/dbConfig to retrieve database configuration
    Validate that all fields are present and log the response
    :return:
    '''
    global session, baseurl
    get_db_config_apiurl = '/api/rest/dbConfig'
    # This information should never change unless something breaks.

    resp = rest_request(session, type_of_call=call_type.get, baseurl=baseurl, apiurl=get_db_config_apiurl)
    logging.debug(
        'Request for database configuration sent: status code = {}, response = {} '.format(resp.status_code, resp.text))
    assert resp.status_code == 200, 'Incorrect status code received from GET database config request.  Expected 200, got {}'.format(
        resp.status_code)

    assert 'type' in resp.json(), 'Field "type" not found in database get config request.'
    assert 'hostName' in resp.json(), 'Field "hostName" not found in database get config request.'
    assert 'port' in resp.json(), 'Field "port" not found in database get config request.'
    assert 'schema' in resp.json(), 'Field "schema" not found in database get config request.'
    assert 'username' in resp.json(), 'Field "username" not found in database get config request.'
    #assert 'connectionOptions' in resp.json(), 'Field "connectionOptions" not found in database get config request.'


@with_setup(t_setup, t_teardown)
def test_endpoint_retrieve_pool_statistics():
    '''
    Use GET /api/rest/dbConfig/dbpoolstats to retrieve database pooling statistics.
    Just check that the status code on the response is 200.  The pooling
    has been written out of Indy, and the response to this API is not yet defined
    :return:
    '''
    global session, baseurl
    get_pool_statistics_apiurl = '/api/rest/dbConfig/dbpoolstats'

    resp = rest_request(session, type_of_call=call_type.get, baseurl=baseurl, apiurl=get_pool_statistics_apiurl)
    # Note:  This API call will change substantially in Indy.  The database pooling feature introduced
    #In 10.3 has been completely rewritten.  The new format for database statistics is TBD.
    # So... only testing the status code of this response for now

    assert resp.status_code == 200, 'Incorrect status returned from retrieve db pool statistics request.  Expected 200, received {}'.format(
        resp.status_code)


@with_setup(t_setup, t_teardown)
def test_endpoint_verify_database_connection():
    '''
    Use GET /api/rest/dbConfig to pull down the database configuration
    Parse the information returned in that call and construct a new API call to /api/rest/dbConfig/test
    validate the response has the correct status code
    validate that the response has the correct value: SUCCESS
    :return:
    '''
    global session, config, baseurl
    get_db_config_apiurl = '/api/rest/dbConfig'
    test_db_config_apiurl = '/api/rest/dbConfig/test'

    resp = rest_request(session, type_of_call=call_type.get, baseurl=baseurl, apiurl=get_db_config_apiurl)
    logging.debug(
        'Request for database configuration sent: status code = {}, response = {} '.format(resp.status_code, resp.text))
    assert resp.status_code == 200, 'Incorrect status code received from GET database config request.  Expected 200, got {}'.format(
        resp.status_code)

    # Use response of GET database config request to construct the test database config request
    type = resp.json()['type']
    hostName = resp.json()['hostName']
    port = resp.json()['port']
    schema = resp.json()['schema']
    username = resp.json()['username']
    #connectionOptions = resp.json()['connectionOptions']
    password = config['database']['password']

    database_test_parameters = {'type': type, 'hostName': hostName, 'port': port, 'schema': schema,
                                'username': username,  'password': password}

    # Now issue the test database request
    resp = rest_request(session, type_of_call=call_type.get, baseurl=baseurl, apiurl=test_db_config_apiurl,
                        query_params=database_test_parameters)
    logging.debug('Database test API call sent: status code = {}, response = {}'.format(resp.status_code, resp.text))
    assert resp.status_code == 200, 'Unexpected response status code on test database connection call.  Expected 200, received {}'.format(
        resp.status_code)
    assert 'status' in resp.json(), 'Could not parse "type" in database status response'


