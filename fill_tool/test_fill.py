from nose import with_setup
import logging
import logging.config
import configparser
import requests
from framework.constants import *
from framework.authentication_rest import login, logout, get_auth_token
from framework.http_rest import *
from framework.users_rest import user_cm
from framework.workgroup_rest import Workgroup
from framework.media_metadata_rest import Media_metadata
from framework.category_rest import Category
from framework.fileupload_rest import File_upload

# global list of headers from file
headers = []
session = requests.Session()

def setup_module():
    '''
    .. py:function:: setup_module()
    This module runs once at the beginning of this test suite.  Nose automatically executes
    the commands in this module once when this test suite starts
    '''
    global config,session
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE_PATH)
    logging.config.fileConfig(LOG_FILE_PATH)
    logging.debug('Config file path is: {}'.format(CONFIG_FILE_PATH))
    logging.info('Beginning test setup')
    baseurl = config['login']['baseurl']
    username = config['login']['username']
    password = config['login']['password']
    logging.debug('Read login info from config file and ready to begin.')
    logging.info('Initilizing session for next test case.')
    media_path = config['path']['media']
    # INITIALIZE SESSION OBJECT
    session = login(username, password, baseurl)


def t_setup():
    '''
    Parameters read from config file:
    login.baseurl - the base url of the CM under test]
    login.username - the username used to log into the CM under test
    login.password - the password used by the scripts to log into the CM under test

    This method initializes the test session by logging into the CM under test and populating
    the session object used by this test suite.  The session object created by this method
    is authorized to send api commands to the CM under test.

    Setup is intended to be run before each test in this suite - ensuring that a new session
    is used for each test case (no side effects between test cases)

    Decorate each test case with: **@with_setup(setup, teardown)**
    '''
    global config, session
    assert session is not None
def t_teardown():
    pass

def teardown_module():
    '''
    This method logs off from the CM.  It is inteded to be run after each test case in this test suite.
    Decorate each test case with:  **@with_setup(setup, teardown)**
    '''
    global session
    logging.info('Beginning test teardown')
    response = logout(session, config['login']['baseurl'])
    assert response


def print_one_line(line):
    print(line)
    print(str(line.strip().split(',')))


@with_setup(t_setup, t_teardown)
def fill_user(line):
    global headers, session, config
    logging.debug('first 8 bytes of line are: ' + line[0:8])
    if line[0:8] == 'username':
        logging.debug('Found header line in user name file.')
        headers = line.strip().split(',')
        logging.debug('headers found to be: ' + str(headers))
    else:
        values = line.strip().split(',')
        logging.debug('fill_user: Header length is: ' + str(len(headers)))
        logging.debug('fill_user: Header list is: ' + str(headers))
        logging.debug('fill_user: Attribute list is: ' + str(values))
        logging.debug('fill_user: Attribute length is: ' + str(len(values)))
        logging.debug('fill_user: Use these headers:' + str(headers[0:len(values)]))
        attribute = dict(zip(headers[0:len(values)], values))
        # logging.debug('attribute dictionary is: ' + str(attribute))
        user = user_cm()
        for count in range(len(headers)):
            logging.debug('fill_user: adding attribute with key = ' + str(headers[count]))
            logging.debug('fill_user: and value =                 ' + str(values[count]))
            logging.debug('fill_user: add this dict =             ' + json.dumps({headers[count]: values[count]}))
            if len(values[count]) > 0:
                user.add_attribute(session=session, attribute={headers[count]: values[count]})
        resp = rest_request(session, call_type.post, baseurl=config['login']['baseurl'], apiurl="/api/rest/users",
                            payload_params=user.user_data, proxy=False)


@with_setup(t_setup, t_teardown)
def fill_workgroup(line, first_line):
    global headers, session, config
    wg = Workgroup()
    if first_line:
        logging.debug('fill_workgroup: Found header line in workgroups file.')
        headers = line.strip().split(',')
        logging.debug('fill_workgroup: headers found to be: {}'.format(str(headers)))
        logging.debug('First line? {}'.format(first_line))
        assert True
        return
    else:
        logging.debug('****************************************************')
        values = line.strip().split(',')
        logging.debug('Header Length is: {}'.format(str(len(headers))))
        logging.debug('Header list is: {}'.format(str(headers)))
        logging.debug('Attribute list is: ' + str(values))
        logging.debug('Attribute length is: ' + str(len(values)))
        logging.debug('Use these headers:' + str(headers[0:len(values)]))
        logging.debug('the type of wg is: {}'.format(type(wg)))
        attribute = [{headers[x]: values[x]} for x in range(len(values)) if values[x] is not ""]
        logging.debug('The FINAL attribute list of dicts is: {}'.format(json.dumps(attribute)))
        result = wg.add_attribute(session, attribute)
        logging.debug('The result from add_attribute is: {}'.format(result))
    logging.debug('FINAL user data before making rest request: {}'.format(wg.json_data))
    resp = rest_request(session, call_type.post, baseurl=config['login']['baseurl'], apiurl="/api/rest/workgroups",
                        payload_params=wg.json_data, proxy=False)
    logging.info('Adding workgroup returned status_code: {}'.format(resp.status_code))
    assert resp.status_code == 200


@with_setup(t_setup, t_teardown)
def fill_media_metadata(line, first_line):
    global headers, session, config
    mmd = Media_metadata()
    if first_line:
        logging.debug('Found header line in workgroups file.')
        headers = line.strip().split(',')
        logging.debug('headers found to be: {}'.format(str(headers)))
        logging.debug('First line? {}'.format(first_line))
        assert True
        return
    else:
        logging.debug('****************************************************')
        values = line.strip().split(',')
        logging.debug('Header Length is: {}'.format(str(len(headers))))
        logging.debug('Header list is: {}'.format(str(headers)))
        logging.debug('Attribute list is: ' + str(values))
        logging.debug('Attribute length is: ' + str(len(values)))
        logging.debug('Use these headers:' + str(headers[0:len(values)]))
        attribute = [{headers[x]: values[x]} for x in range(len(values)) if values[x] is not ""]
        result = mmd.add_attribute(session, attribute)
        assert result
    logging.debug('The FINAL attribute list of dicts is: {}'.format(json.dumps(attribute)))
    resp = rest_request(session, call_type.post, baseurl=config['login']['baseurl'], apiurl="/api/rest/metadata",
                        payload_params=mmd.json_data, proxy=False)
    logging.info('Adding media metadata returned status_code: {}'.format(resp.status_code))
    assert resp.status_code == 200

@with_setup(t_setup, t_teardown)
def fill_categories(line, first_line):
    global headers, session, config
    mc = Category()
    if first_line:
        logging.debug('Found header line in categories file.')
        headers = line.strip().split(',')
        logging.debug('headers found to be: {}'.format(str(headers)))
        logging.debug('First line? {}'.format(first_line))
        assert True
        return
    else:
        logging.debug('****************************************************')
        values = line.strip().split(',')
        logging.debug('Header Length is: {}'.format(str(len(headers))))
        logging.debug('Header list is: {}'.format(str(headers)))
        logging.debug('Attribute list is: ' + str(values))
        logging.debug('Attribute length is: ' + str(len(values)))
        logging.debug('Use these headers:' + str(headers[0:len(values)]))
        attribute = [{headers[x]: values[x]} for x in range(len(values)) if values[x] is not ""]
        result = mc.add_attribute(session, attribute)
        assert result, 'Failed to add all attributes to the category'
    logging.debug('The FINAL attribute list of dicts is: {}'.format(json.dumps(attribute)))
    resp = rest_request(session, call_type.post, baseurl=config['login']['baseurl'], apiurl="/api/rest/categories",
                        payload_params=mc.json_data, proxy=False)
    logging.info('Adding media metadata returned status_code: {}'.format(resp.status_code))
    assert resp.status_code == 200, 'Status code for catagory fill was not 200'
#    pass  - notsure why this line never got deleted - did I make a mistake?  I'll comment it for now.

@with_setup(t_setup, t_teardown)
def fill_uploads(line, first_line, api_version):
    global headers, session, config
    fup = File_upload(api_version)
    if first_line:
        logging.debug('Found header line in categories file.')
        headers = line.strip().split(',')
        logging.debug('headers found to be: {}'.format(str(headers)))
        logging.debug('First line? {}'.format(first_line))
        assert True
        return
    else:
        logging.debug('****************************************************')
        values = line.strip().split(',')
        logging.debug('Header Length is: {}'.format(str(len(headers))))
        logging.debug('Header list is: {}'.format(str(headers)))
        logging.debug('Attribute list is: ' + str(values))
        logging.debug('Attribute length is: ' + str(len(values)))
        logging.debug('Use these headers:' + str(headers[0:len(values)]))
        attribute = [{headers[x]: values[x]} for x in range(len(values)) if values[x] is not ""]

        # Save off the key value pair containing the server side filename
        logging.debug('The list of key value pairs extracted from the file is: {}'.format(attribute))
        filename_key_pair = attribute.pop(0)

        # Place the attributes into the correct format to use as parameters in restful call
        result = fup.add_attribute(session, attribute)
        assert result, 'Failed to add all attributes to the category'
        logging.debug('The FINAL attribute list of dicts is: {}'.format(json.dumps(attribute)))

        # Begin Media upload.   Start with Init call
        resp = rest_request(session, call_type.post, baseurl=config['login']['baseurl'], apiurl='/api/rest/fileupload/init',
                            query_params = None, payload_params=fup.json_data,  proxy=False)
        logging.info('Response code from init call is: {}'.format(resp.status_code))
        assert resp.status_code == 200, 'Received incorrect response code after Media file upload init call.'

        # Save off the json response to pluck the uuid out of it
        json_response = json.loads(resp.text)
        logging.debug('UUID from Init call is: {}'.format(json_response['uuid']))
        logging.debug('filename from Init call is: {}'.format(json_response['filename']))

        # Prep the arguments for the put call
        file = open(config['path']['media'] + filename_key_pair['image_name'],'rb')
        apiurl = '/api/rest/fileupload/part/'+json_response['uuid'] + '/0'

        #Send the put request to upload the file
        resp = rest_request(session,call_type.put,baseurl = config['login']['baseurl'], apiurl=apiurl, file_object = file)
        logging.info('Response code from file put call is: {}'.format(resp.status_code))
        file.close()
        assert resp.status_code == 204, 'Received incorrect response code after file put call on media upload'

        # Commit the change
        apiurl = '/api/rest/fileupload/complete/' + json_response['uuid']
        resp = rest_request(session,call_type.post, baseurl = config['login']['baseurl'], apiurl=apiurl)
        logging.info('Response code from file complete call is: {}'.format(resp.status_code))
        assert resp.status_code == 204, 'Received incorrect response code after media upload complete call.'



    # logging.info('Adding media metadata returned status_code: {}'.format(resp.status_code))
    # assert resp.status_code == 200, 'Status code for catagory fill was not 200'

# def test_create_users():
#     '''
#     This test loads the CM under test with user data
#     :return:Pass or Fail
#     '''
#     with open('config/users.csv', 'r') as f:
#         for line in f:
#             # yield print_one_line, line
#             yield fill_user, line
#
#
# def test_create_workgroups():
#     '''
#     This test loads the CM under test with workgroup data
#     :return: Pass or Fail
#     '''
#     first_line = True
#     with open('config/workgroups.csv', 'r') as f:
#         for line in f:
#             # yield print_one_line, line
#             yield fill_workgroup, line, first_line
#             first_line = False
#
#
# def test_create_media_metadata():
#     '''
#     This test loads the CM under test with media metadata
#     :return: Pass or Fail
#     '''
#     first_line = True
#     with open('config/media_metadata.csv', 'r') as f:
#         for line in f:
#             # yield print_one_line, line
#             yield fill_media_metadata, line, first_line
#             first_line = False
#
# def test_create_categories():
#     '''
#     This test loads the CM under test with media categories
#     :return: Pass or Fail
#     '''
#     first_line = True
#     with open('config/categories.csv','r') as f:
#         for line in f:
#             yield fill_categories, line, first_line
#             first_line = False

def test_create_media_file_uploads():
    '''
    This test loads the CM under test with media files
    :return: Pass or Fail
    '''
    first_line = True
    with open('config/mediafiles_million.csv','r') as f:
        for line in f:
            yield fill_uploads, line, first_line, 1.0
            first_line = False