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
from framework.media_rest import Media
import inspect
import time


print(CONFIG_FILE_PATH)
config = configparser.ConfigParser()
config.read(CONFIG_FILE_PATH)
logging.config.fileConfig(LOG_FILE_PATH)
logging.debug('Logging config file path is: {}'.format(CONFIG_FILE_PATH))
session = requests.Session()

# global list of headers from file
headers = []

# List of version numbers for API framework object types
api_version_category =config['api_info']['api_version_category']
api_version_workgroup = config['api_info']['api_version_workgroup']


# List of ID's of the configured categories and workgroups for these tests - set up in the setup_module() method
category_ids = []
workgroup_ids = []
media_upload_ids = []

# Individual global variables pointing to the ID's of the different types of metadata created by this test suite
# Note:  A list of ID's won't do for media metadata because each one is fundamentally different.  I have to handle
# Boolean metadata differently than integer or string metadata.  It's easier to give a variable name to the ID
# of each record.
boolean_any_metadata_id = 0
integer_any_metadata_id = 0
string_any_metadata_id = 0
int_picklist_metadata_id = 0
string_picklist_metadata_id = 0


def this_function_name():
    return inspect.stack()[1][3]

def add_object (session, data_class,data_type, data_attribute):
    '''
    Helper method for adding objects to test suite prior to execution of tests/suites
    Attirbutes follow the same format as the fill test:

    [{'name':'<top level>'},{'name':'<2nd level>'},{'name':'<3rd level>'},,{'description':"Category a for media test suite"}]

    Only the 'name' attribute is repeated - one for each level of the nested object.  See the fill_test for
    why this is.

    :param session:  Authenticated CM session object
    :param data_class: a framework class appropriate for the data object to be added
    :param data_type: constants.valid_api_names for this data type
    :param data_attribute: Attribute to be added - the object data
    :return: the ID of the object added to the database or None if the add fails
    '''
    logging.debug('Type of data sent to add_object = ' + str(type(data_class)))
    data_class.add_attribute(session = session, attribute = data_attribute)
    logging.info('Attempting ot add object of type {} with this JSON parameter: {}'.format(data_type.name,json.dumps(data_class.json_data)))
    apiurl = '/api/rest/' + data_type.name
    resp=rest_request(session,call_type.post, baseurl = config['login']['baseurl'],apiurl=apiurl,
                      payload_params = data_class.json_data, proxy = False)
    assert resp.status_code == 200, 'Failed to add object of type {} for this test suite '.format(data_type.name) + resp.text
    assert resp.json()['id'] is not None
    return resp.json()['id']


def delete_object(session, object_type, object_id):
    '''
    Deletes an object created for use in this test suite.  This is a generic delete method, as the parameters required for
    delete are very simple - just the ID in most cases.  The Ojbect Type must match the name of the object in the API delete
    command for that object.  For example:

    The workgroup delete api call is: DELETE /api/rest/workgroups/{id} thus the object_type must be 'workgroups'
    The category delete api call is:DELETE  /api/rest/categories/{id} thus the object_type mustbe 'categories'

    :param session: An authenticated session object
    :param object_type: The type of object to be deleted. Must match *exactly* the value in the URL of the DELETE api call
    :param object_id: The ID of the object to be deleted
    :return:
    '''
    apiurl = '/api/rest/' + object_type.name + '/' + str(object_id)
    resp = rest_request(session,call_type.delete, baseurl = config['login']['baseurl'],
                        apiurl=apiurl, proxy = False)
    if resp.status_code == 204:
        logging.info('Successfully deleted object of type {} with ID = {}'.format(object_type.name, object_id))
        return
    logging.error('Did not delete {} object with ID = {}'.format(object_type.name, object_id))
    assert resp.status_code == 204, 'Failed to delete object of type  {} for this test suite '.format(object_type.name) + resp.text

def media_upload(session, media_file_name, media_files_path):
    global config

    # Define the base data parameters for the test
    tcid = this_function_name()
    namespace = config['test']['namespace']
    baseurl = config['login']['baseurl']
    apiurl = '/api/rest/fileupload'
    media_file_name_path = media_files_path + media_file_name

    # Build Media file JSON attributes for import
    media_attribute = {'filename':media_file_name,'uploadType':'media_item'}

    # Begin Media upload using POST api/rest/fileupload/init call
    init_api_url = apiurl + '/init'
    resp = rest_request(session, call_type.post, baseurl=baseurl, apiurl=init_api_url,
                        query_params = None, payload_params=media_attribute,  proxy=False)
    logging.info('Response code from init call is: {}'.format(resp.status_code))
    assert resp.status_code == 200, 'Received incorrect response code after Media file upload init call.  Received {} expected 200'.format(resp.status_code)

    # Save off the json response to pluck the uuid out of it
    init_json_response = resp.json()
    uuid = init_json_response['uuid']
    logging.debug('UUID from Init call is: {}'.format(init_json_response['uuid']))
    logging.debug('filename from Init call is: {}'.format(init_json_response['filename']))

    # Prep the arguments for the put call
    file = open(media_file_name_path,'rb')
    put_apiurl = '/api/rest/fileupload/part/'+ uuid + '/0'

    #Send the put request to upload the file
    resp = rest_request(session,call_type.put,baseurl = baseurl, apiurl=put_apiurl, file_object = file)
        # Close the file before anything else can go wrong - leaving the file open
    file.close()
    logging.info('Response code from file put call is: {}'.format(resp.status_code))
    assert resp.status_code == 204, 'Received incorrect response code after file put call on media upload.  Received {} expected 204'.format(resp.status_code)

    # Commit the change
    commit_apiurl = apiurl + '/complete/' + uuid
    resp = rest_request(session,call_type.post, baseurl = baseurl, apiurl=commit_apiurl)
    logging.info('Response code from file complete call is: {}'.format(resp.status_code))
    assert resp.status_code == 204, 'Received incorrect response code after media upload complete call.  Received {} expected 204'.format(resp.status_code)

    # Get the id of the media object just created
    media_id_apiurl = '/api/rest/media'
    query_params = {'offset':0,'limit':10,'sort':'-lastModified','fields':'id,name'}
    resp = rest_request(session,call_type.get, baseurl = baseurl, apiurl = media_id_apiurl, query_params = query_params)
    logging.info('Response code from media get is {}'.format(resp.status_code))
    assert resp.status_code == 200, 'Received incorrect response code after media get to verify media upload.  Received {} expected 200.'.format(resp.status_code)
    uploaded_media_id = resp.json()['list'][0]['id']
    uploaded_media_name = resp.json()['list'][0]['name']
    assert uploaded_media_id is not None, 'Could not find media id in response'
    assert uploaded_media_name == media_file_name, 'Incorrect file name found in uploaded media object.  Expected {}, got {}'.format(media_file_name, uploaded_media_name)
    assert resp.json()
    logging.info('Media created with id = {}'.format(uploaded_media_id))
    return uploaded_media_id


def setup_module():
    '''
    py:function:: setup_module()
    This module runs once at the beginning of this test suite.  Nose automatically executes
    the commands in this module once when this test suite starts

    In this specific test suite, the module config creates 4 media categories, 4 media workgroups and
    5 media metadata objects.  All of the objects created in this section are deleted in the teardown_module()
    function.

    The names of all objects created in setup will have the config['test']['namespace'] appended to it.  This prevents
    name conflicts if multiple instances of this script are run simultaneously.  This will hopefully become more
    important as time goes on and these suites are used in the performance tools.

    For example:

    if config['test']['namespace'] = 'test-01'

    Then the categories created by this function will be:
    a-test01
    b-test01
    c-test01
    d-test01

    If a second instance of this test suite is running in another process, changing the namespace variable will
    prevent the two instances from trying to add categories, workgroups or metadata with the same name.
    '''

    global category_ids, workgroup_ids, media_metadata_ids, boolean_any_metadata_id,integer_any_metadata_id,string_any_metadata_id,int_picklist_metadata_id, string_picklist_metadata_id, media_upload_ids, api_version_category

    # Log into session
    logging.info('Beginning test setup')
    baseurl = config['login']['baseurl']
    username = config['login']['username']
    password = config['login']['password']
    logging.debug('Read login info from config file and ready to begin.')
    logging.info('Initilizing session for next test case.')
    media_path = config['path']['media']
    namespace = config['test']['namespace']
    # INITIALIZE SESSION OBJECT
    session = login(username, password, baseurl)

    # Create media Metadata objects for use in this test suite
    media_metadata_ids=[]
    media_metadata_attributes_list = []
    mm = Media_metadata()
    ba = [{'name':namespace + 'boolean_any'},{'datatype':'BOOLEAN'},{'valueType':'ANY'}]
    ia = [{'name':namespace + 'integer_any'},{'datatype':'INTEGER'},{'valueType':'ANY'}]
    sa = [{'name':namespace + 'string_any'},{'datatype':'STRING'},{'valueType':'ANY'}]
    ip = [{'name':namespace + 'int_pickllist'},{'datatype':'INTEGER'},{'valueType':'PICKLIST'}]
    sp = [{'name':namespace + 'string_picklist'},{'datatype':'STRING'},{'valueType':'PICKLIST'}]

    boolean_any_metadata_id = add_object(session,data_class = mm, data_type = valid_api_names.metadata,data_attribute= ba )
    integer_any_metadata_id = add_object(session,data_class = mm, data_type = valid_api_names.metadata,data_attribute= ia )
    string_any_metadata_id = add_object(session,data_class = mm, data_type = valid_api_names.metadata,data_attribute= sa )
    int_picklist_metadata_id = add_object(session,data_class = mm, data_type = valid_api_names.metadata,data_attribute= ip )
    string_picklist_metadata_id = add_object(session,data_class = mm, data_type = valid_api_names.metadata,data_attribute= sp )

    logging.info('IDs of 5 media metadata objects added for this test suite.  They are: {}'.format(media_metadata_ids))

    # Create 4 media categories.  Use the namespace variable so that the names of this instance of the
    # suite do not conflict with other running instances
    category_ids = []
    category_attributes_list = []
    category_attributes_list.append([{'name':'a-' + namespace},{'description':"Category a for media test suite instance" + namespace}])
    category_attributes_list.append([{'name':'b-' + namespace},{'description':"Category b for media test suite instance" + namespace}])
    category_attributes_list.append([{'name':'c-' + namespace},{'description':"Category c for media test suite instance" + namespace}])
    category_attributes_list.append([{'name':'d-' + namespace},{'description':"Category d for media test suite instance" + namespace}])
    cat = Category(api_version_category)
    category_ids = [add_object(session,data_class = cat, data_type = valid_api_names.categories, data_attribute=item) for item in category_attributes_list]
    assert None not in category_ids

    logging.info('IDs of 4 media categories added for this test suite. They are: {}'.format(category_ids))


    # Create 4 workgroups.  Use the namespace variable so that the names used by this instance of the
    # test suite do not conflict with other running instances

    workgroup_ids = []
    workgroup_attributes_list = []
    workgroup_attributes_list.append([{'name':'a-' + namespace},{'description':'Workgroup a for media test suite instance ' + namespace}])
    workgroup_attributes_list.append([{'name':'b-' + namespace},{'description':'Workgroup b for media test suite instance ' + namespace}])
    workgroup_attributes_list.append([{'name':'c-' + namespace},{'description':'Workgroup c for media test suite instance ' + namespace}])
    workgroup_attributes_list.append([{'name':'d-' + namespace},{'description':'Workgroup d for media test suite instance ' + namespace}])
    wg = Workgroup(api_version_workgroup)
    workgroup_ids = [add_object(session,data_class = wg, data_type = valid_api_names.workgroups,data_attribute= item) for item in workgroup_attributes_list]
    assert None not in workgroup_ids

    logging.info('IDs of 4 workgroups added for this test suite. They are: {}'.format(workgroup_ids))
    logout(session,baseurl)




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

    # Create 3 media uploads based on files in the [media] section of testconfig if upload_media is set to True
    logging.debug('Upload Media is: {}'.format(upload_media))
    if upload_media:
        media_upload_ids = []
        media_upload_ids.append(media_upload(session = session, media_file_name = config['media_items']['mediafile_1'],media_files_path = config['path']['media']))
        media_upload_ids.append(media_upload(session = session, media_file_name = config['media_items']['mediafile_2'],media_files_path = config['path']['media']))
        media_upload_ids.append(media_upload(session = session, media_file_name = config['media_items']['mediafile_3'],media_files_path = config['path']['media']))
        logging.info ('Media uploaded by test case setup routine: {} media items with {} ids'.format(len(media_upload_ids), media_upload_ids))


def t_teardown(upload_media=False):
    '''
    This method logs off from the CM.  It is inteded to be run after each test case in this test suite.
    Decorate each test case with:  **@with_setup(setup, teardown)**

    if the upload_media flag is set to True, then the teardown module will attempt to delete the media objects created in
    setup_t
    '''
    global session

    if upload_media:
        for item in media_upload_ids:
            delete_object(session,valid_api_names.media,item)

    logging.info('Beginning test teardown')
    response = logout(session, config['login']['baseurl'])
    assert response

def teardown_module():
    '''
    This module runs once at the end of this test suite.  Nose automatically executes
    the commands in this module once when this test suite ends.

    This module creates a new login session to the CM and deletes the objects created at the
    beginning of this module in setup_module().
    '''
    global category_ids, workgroup_ids, boolean_any_metadata_id, integer_any_metadata_id, string_any_metadata_id, int_picklist_metadata_id, string_picklist_metadata_id
    logging.info('Beginning module teardown.')
    baseurl = config['login']['baseurl']
    username = config['login']['username']
    password = config['login']['password']
    logging.info('Preparing session for module teardown')
    # INITIALIZE SESSION OBJECT
    session = login(username, password, baseurl)

    for item in category_ids:
        delete_object(session,valid_api_names.categories,item)
    logging.info('Deleted {} categories used in this test suite.  Their IDs were: {}'.format(len(category_ids),category_ids))

    for item in workgroup_ids:
        delete_object(session,valid_api_names.workgroups,item)
    logging.info('Deleted {} workgroups used in this test suite.  Their IDs were: {}'.format(len(workgroup_ids),workgroup_ids))

    media_metadata_ids = [
    boolean_any_metadata_id,
    integer_any_metadata_id,
    string_any_metadata_id,
    int_picklist_metadata_id,
    string_picklist_metadata_id]
    for item in media_metadata_ids:
        delete_object(session,valid_api_names.metadata,item)
    logging.info('Deleted {} media metadata objects used in this test suite.  Their IDs were: {}'.format(len(media_metadata_ids),media_metadata_ids))

    logout(session,baseurl)
    logging.info('Module teardown complete.')

@with_setup(t_setup, t_teardown)
def test01():
    '''
    Create a Media object using POST /api/rest/media with all singleton data fields
    Validate the response from CM
    Pull the newly created media object back down from the CM using GET /api/rest/media/{ID}
    Validate that the fields match
    Delete the media object to clean up test case
    :return: Asserts true if fields match
    '''
    global headers, session, config
    namespace = config['test']['namespace']

    # Define the data parameters for the test
    media_uri = 'www.scala.' + namespace + '.com'
    baseurl = config['login']['baseurl']
    apiurl = '/api/rest/media'
    media_name = namespace + ' Auto Test Media01'

    # Build the media attribute to 'create' in this test
    media_item_attribute = {'name':media_name,'uri':media_uri,'mediaType':"HTML"}
    resp = rest_request(session,type_of_call=call_type.post,baseurl = baseurl,apiurl = apiurl ,payload_params=media_item_attribute)
    assert resp.status_code == 200, 'Status code of rest request to add media object is unexpectedly: {}'.format(resp.status_code)
    logging.debug('JSON response for media create is: {}'.format(resp.text))
    media_id = resp.json()['id']
    logging.info('Created media object with ID = {}'.format(media_id))

    # Retrieve the media object created above and verify that the attributes match
    apiurl = apiurl + '/' + str(media_id)
    resp = rest_request(session,type_of_call=call_type.get,baseurl = config['login']['baseurl'],apiurl = apiurl)
    logging.debug('JSON response for media get is: {}'.format(resp.text))

    # Compare basic data fields on returned record with expected values

    assert resp.json()['id'] == media_id, 'Incorrect media ID on returned media object.  Expected {} got {}'.format(media_id, resp.json()['id'])
    logging.debug('Validated that id of created object matches id of retrieved object {} == {}'.format(media_id, resp.json()['id']))
    assert resp.json()['name'] == media_name, 'Incorrect media Name on returned media object.  Expected {} got {}'.format(media_name, resp.json()['name'])
    logging.debug('Validated that name of created object matches id of retrieved object {} == {}'.format(media_name, resp.json()['name']))
    assert resp.json()['uri']  == media_uri, 'Incorrect uri on returned media object.  Expected {} got {}'.format(media_uri, resp.json()['uri'])
    logging.debug('Validated that uri of created object matches uri of retrieved object {} == {}'.format(media_uri, resp.json()['uri']))
    logging.info('Test case 01 complete. Cleaning up.')
    delete_object(session = session,object_type=valid_api_names.media,object_id = media_id)

@with_setup(t_setup, t_teardown)
def test02():
    '''
    Create a media object, and then use the API to modify all of the simple attributes of that object
    using the PUT /api/rest/media/{ID} method.  Simple attributes are key-value pairs, as opposed
    to complex attributes which are json objects (approvals, workgroups etc)
    :return:
    '''
    global headers, session, config
    namespace = config['test']['namespace']

    # Define the base data parameters for the test
    media_uri = 'www.scala.' + namespace + '.com'
    baseurl = config['login']['baseurl']
    apiurl = '/api/rest/media'
    media_name = namespace + ' Auto Test Media02'

    # Define the parameters to be changed in this test
    description = 'Correct Description has been added to this media object'
    audioDucking = True
    playFullscreen = True
    startValidDate = '2005-02-01'
    endValidDate = '2020-03-01'
#    validDateStatus = 'Future'

    # Build the media attribute to 'create' in this test
    media_item_attribute = {'name':media_name,'uri':media_uri,'mediaType':"HTML"}
    resp = rest_request(session,type_of_call=call_type.post,baseurl = baseurl,apiurl = apiurl ,payload_params=media_item_attribute)
    logging.debug('JSON response for media create is: {}'.format(resp.text))
    assert resp.status_code == 200, 'Status code of rest request to add media object is unexpectedly: {}'.format(resp.status_code)
    media_id = resp.json()['id']
    logging.info('Created media object with ID = {}'.format(media_id))

    # Modify the media that was created above by changing the listed parameters
    apiurl = apiurl + '/' + str(media_id)
    parameters = {'description':description,
                  'audioDucking':audioDucking,
                  'playFullscreen':playFullscreen,
                  'startValidDate':startValidDate,
                  'endValidDate':endValidDate,
#                  'validDateStatus':validDateStatus  <---Note:  System Status field set by system not by API
    }

    resp = rest_request(session,type_of_call=call_type.put,baseurl = baseurl, apiurl = apiurl,payload_params = parameters)
    assert resp.status_code == 200, 'Status code of put request to modify medio object is unexpectedly: {}'.format(resp.status_code)
    logging.debug('JSON response for media modify is {}'.format(resp.text))

    # Retrieve the media object created above and verify that the attributes match
    resp = rest_request(session,type_of_call=call_type.get,baseurl = config['login']['baseurl'],apiurl = apiurl)
    logging.debug('JSON response for media get is: {}'.format(resp.text))
    assert resp.json()['description']  == description, 'Incorrect data in returned media object.  Expected {} got {}'.format(description, resp.json()['description'])
    assert resp.json()['audioDucking'] == audioDucking,  'Incorrect data in returned media object.  Expected {} got {}'.format(audioDucking, resp.json()['audioDucking'])
    assert resp.json()['playFullscreen'] == playFullscreen,  'Incorrect data in returned media object.  Expected {} got {}'.format(playFullscreen, resp.json()['playFullscreen'])
    assert resp.json()['startValidDate'] == startValidDate,  'Incorrect data in returned media object.  Expected {} got {}'.format(startValidDate, resp.json()['startValidDate'])
    assert resp.json()['endValidDate'] == endValidDate,  'Incorrect data in returned media object.  Expected {} got {}'.format(endValidDate, resp.json()['endValidDate'])

    logging.info('Test case 02 complete.  Cleaning up.')
    delete_object(session = session,object_type=valid_api_names.media,object_id = media_id)


@with_setup(t_setup, t_teardown)
def test03():
    global headers, session, config, category_ids
    namespace = config['test']['namespace']

    # Define the base data parameters for the test
    media_uri = 'www.scala.' + namespace + '.com'
    baseurl = config['login']['baseurl']
    apiurl = '/api/rest/media'
    media_name = namespace + ' Auto Test Media03'

    # Build the media attribute to 'create' in this test
    media_item_attribute = {'name':media_name,'uri':media_uri,'mediaType':"HTML"}
    resp = rest_request(session,type_of_call=call_type.post,baseurl = baseurl,apiurl = apiurl ,payload_params=media_item_attribute)
    logging.debug('JSON response for media create is: {}'.format(resp.text))
    assert resp.status_code == 200, 'Status code of rest request to add media object is unexpectedly: {}'.format(resp.status_code)
    media_id = resp.json()['id']
    logging.info('Created media object with ID = {}'.format(media_id))

   # Define the parameters to be changed in this test
    cat_list = [{'id':x} for x in category_ids]
    parameters = {'categories':cat_list}
    put_apiurl = apiurl +'/' + str(resp.json()['id'])

    #Make the change to the media record for this test case
    resp = rest_request(session, type_of_call = call_type.put, baseurl = baseurl, apiurl = put_apiurl, payload_params = parameters)
    assert resp.status_code == 200, 'Status code of rest request to modify media object was unexpectedly: {}'.format(resp.status_code)
    logging.info('modified media record so it contains {} categories'.format(len(cat_list)))

    #Pull the media object back down and verify that the categories were correctly added
    resp = rest_request(session, type_of_call=call_type.get,baseurl = baseurl, apiurl = put_apiurl)
    assert resp.status_code == 200, 'Status code of rest request to get media object after change was unexpectedly: {}'.format(resp.status_code)
    logging.info('modified media record so it contains {} categories'.format(len(cat_list)))

    updated_category_list = [item['id'] for item in resp.json()['categories']]
    logging.info('category list returned from cm is: {}'.format(updated_category_list))
    logging.info('complete category list is:         {}'.format(category_ids))

    assert set(category_ids) == set(updated_category_list), 'Incorrect category assignment.'

    # Clean up test case by deleting the media object created for this test case
    logging.info('Test case 03 complete.  Cleaning up.')
    delete_object(session = session,object_type=valid_api_names.media,object_id = media_id)


@with_setup(t_setup, t_teardown)
def test05():
    global headers, session, config, category_ids,workgroup_ids
    namespace = config['test']['namespace']

    # Define the base data parameters for the test
    media_uri = 'www.scala.' + namespace + '.com'
    baseurl = config['login']['baseurl']
    apiurl = '/api/rest/media'
    media_name = namespace + ' Auto Test Media05'

    # Build the media attribute to 'create' in this test
    media_item_attribute = {'name':media_name,'uri':media_uri,'mediaType':"HTML"}
    resp = rest_request(session,type_of_call=call_type.post,baseurl = baseurl,apiurl = apiurl ,payload_params=media_item_attribute)
    logging.debug('JSON response for media create is: {}'.format(resp.text))
    assert resp.status_code == 200, 'Status code of rest request to add media object is unexpectedly: {}'.format(resp.status_code)
    media_id = resp.json()['id']
    logging.info('Created media object with ID = {}'.format(media_id))

   # Define the parameters to be changed in this test
    wg_list = [{'id':x,'owner':False} for x in workgroup_ids]
    wg_list[0]['owner']= True
    parameters = {'workgroups':wg_list}
    put_apiurl = apiurl +'/' + str(resp.json()['id'])

    #Make the change to the media record for this test case
    resp = rest_request(session, type_of_call = call_type.put, baseurl = baseurl, apiurl = put_apiurl, payload_params = parameters)
    assert resp.status_code == 200, 'Status code of rest request to modify media object was unexpectedly: {}'.format(resp.status_code)
    logging.debug('Response from PUT request {}'.format(resp.text))
    logging.info('modified media record so it contains {} workgroups'.format(len(wg_list)))

    #Pull the media object back down and verify that the categories were correctly added
    resp = rest_request(session, type_of_call=call_type.get,baseurl = baseurl, apiurl = put_apiurl)
    assert resp.status_code == 200, 'Status code of rest request to get media object after change was unexpectedly: {}'.format(resp.status_code)
    logging.info('modified media record so it contains {} workgroups'.format(len(wg_list)))

    updated_workgroup_list = [item['id'] for item in resp.json()['workgroups']]
    logging.info('workgroup list returned from cm is: {}'.format(updated_workgroup_list))
    logging.info('complete category list is:         {}'.format(workgroup_ids))

    assert set(workgroup_ids) == set(updated_workgroup_list), 'Incorrect workgroup assignment.'

    # Clean up test case by deleting the media object created for this test case
    logging.info('Test case 05 complete.  Cleaning up.')
    delete_object(session = session,object_type=valid_api_names.media,object_id = media_id)

@with_setup(t_setup, t_teardown)
def test07():
    '''
    Add a media item.  Use POST /api/rest/media/{id} to add both workgroups and category assignments to the
    newly created record
    :return:
    '''
    global headers, session, config, category_ids,workgroup_ids
    namespace = config['test']['namespace']

    # Define the base data parameters for the test
    media_uri = 'www.scala.' + namespace + '.com'
    baseurl = config['login']['baseurl']
    apiurl = '/api/rest/media'
    media_name = namespace + ' Auto Test Media07'

    # Build the media attribute to 'create' in this test
    media_item_attribute = {'name':media_name,'uri':media_uri,'mediaType':"HTML"}
    resp = rest_request(session,type_of_call=call_type.post,baseurl = baseurl,apiurl = apiurl ,payload_params=media_item_attribute)
    logging.debug('JSON response for media create is: {}'.format(resp.text))
    assert resp.status_code == 200, 'Status code of rest request to add media object is unexpectedly: {}'.format(resp.status_code)
    media_id = resp.json()['id']
    logging.info('Created media object with ID = {}'.format(media_id))

   # Define the parameters to be changed in this test
    wg_list = [{'id':x,'owner':False} for x in workgroup_ids]
    wg_list[0]['owner']= True
    cat_list = [{'id':x} for x in category_ids]
    parameters = {'workgroups':wg_list,'categories':cat_list}
    put_apiurl = apiurl +'/' + str(resp.json()['id'])

    #Make the change to the media record for this test case
    resp = rest_request(session, type_of_call = call_type.put, baseurl = baseurl, apiurl = put_apiurl, payload_params = parameters)
    assert resp.status_code == 200, 'Status code of rest request to modify media object was unexpectedly: {}'.format(resp.status_code)
    logging.debug('Response from PUT request {}'.format(resp.text))
    logging.info('modified media record so it contains {} workgroups'.format(len(wg_list)))

    #Pull the media object back down and verify that the categories were correctly added
    resp = rest_request(session, type_of_call=call_type.get,baseurl = baseurl, apiurl = put_apiurl)
    assert resp.status_code == 200, 'Status code of rest request to get media object after change was unexpectedly: {}'.format(resp.status_code)
    logging.info('modified media record so it contains {} workgroups'.format(len(wg_list)))

    updated_workgroup_list = [item['id'] for item in resp.json()['workgroups']]
    logging.info('workgroup list returned from cm is: {}'.format(updated_workgroup_list))
    logging.info('complete workgroup list is:         {}'.format(workgroup_ids))

    assert set(workgroup_ids) == set(updated_workgroup_list), 'Incorrect workgroup assignment.'

    updated_category_list = [item['id'] for item in resp.json()['categories']]
    logging.info('category list returned from cm is: {}'.format(updated_category_list))
    logging.info('complete category list is:         {}'.format(category_ids))

    assert set(category_ids)  == set(updated_category_list), 'Incorrect category assignment.'

    # Clean up test case by deleting the media object created for this test case
    logging.info('Test case 05 complete.  Cleaning up.')
    delete_object(session = session,object_type=valid_api_names.media,object_id = media_id)


@with_setup(t_setup, t_teardown)
def test10():
    '''
    Add a media item.  Use PUT /api/rest/media/{id} to modify metadata content - Boolean metadata to be specific
    Validate that the boolean metadata record gets correctly updated.  This test changes the metadataValue
    on the test media object from false, to true and back to false.  For each change, the media object is analyzed
    and checked for the expected metadataValue
    :return:
    '''
    tcid = 10
    global headers, session, config, category_ids,workgroup_ids,boolean_any_metadata_id
    namespace = config['test']['namespace']

    # Define the base data parameters for the test
    media_uri = 'www.scala.' + namespace + '.com'
    baseurl = config['login']['baseurl']
    apiurl = '/api/rest/media'
    media_name = namespace + ' Auto Test Media' + str(tcid)

    # Build the media attribute to 'create' in this test
    media_item_attribute = {'name':media_name,'uri':media_uri,'mediaType':"HTML"}
    resp = rest_request(session,type_of_call=call_type.post,baseurl = baseurl,apiurl = apiurl ,payload_params=media_item_attribute)
    logging.debug('JSON response for media create is: {}'.format(resp.text))
    assert resp.status_code == 200, 'Status code of rest request to add media object is unexpectedly: {}'.format(resp.status_code)
    media_id = resp.json()['id']
    logging.info('Created media object with ID = {}'.format(media_id))

   # Define the parameters to be changed in this test
    put_apiurl = apiurl +'/' + str(resp.json()['id'])
    #Change value of metadata to 'False
    parameters = {'metadataValue': [{'value': 'true', 'metadata': {'datatype': 'BOOLEAN', 'id': boolean_any_metadata_id, 'valueType': 'ANY'}}]}

    #Make the change to the media record for this test case.  Setting boolean metadata to 'true'
    resp = rest_request(session, type_of_call = call_type.put, baseurl = baseurl, apiurl = put_apiurl, payload_params = parameters)
    assert resp.status_code == 200, 'Status code of rest request to modify media object was unexpectedly: {}'.format(resp.status_code)
    logging.debug('Response from PUT request {}'.format(resp.text))

    #Pull back the media item to check if the value of the metadata has changed to 'true'
    get_apiurl = apiurl + '/' + str(media_id)
    resp = rest_request(session, type_of_call=call_type.get, baseurl = baseurl, apiurl = get_apiurl)
    found_modified_metadata = False
    logging.info('Get response on media object = {}'.format(resp.text))
    for item in resp.json()['metadataValue']:
        if item['metadata']['id'] == boolean_any_metadata_id and item['value']=='true':
            logging.info('Found metadata ID = {} in JSON response after PUT to change metadata.'.format(boolean_any_metadata_id))
            found_modified_metadata = True
    assert found_modified_metadata == True

    parameters = {'metadataValue': [{'value': 'false', 'metadata': {'datatype': 'BOOLEAN', 'id': boolean_any_metadata_id, 'valueType': 'ANY'}}]}
    #Make the change to the media record for this test case.  Setting boolean metadata to 'false'
    resp = rest_request(session, type_of_call = call_type.put, baseurl = baseurl, apiurl = put_apiurl, payload_params = parameters)
    assert resp.status_code == 200, 'Status code of rest request to modify media object was unexpectedly: {}'.format(resp.status_code)
    logging.debug('Response from PUT request {}'.format(resp.text))

    #Pull back the media item to check if the value of the metadata has changed to 'false'
    get_apiurl = apiurl + '/' + str(media_id)
    resp = rest_request(session, type_of_call=call_type.get, baseurl = baseurl, apiurl = get_apiurl)
    found_modified_metadata = False
    logging.info('Get response on media object = {}'.format(json.dumps(resp.json())))
    assert 'metadataValue' not in resp.json()

    # Clean up test case by deleting the media object created for this test case
    logging.info('Test case {} complete.  Cleaning up.'.format(tcid))
    delete_object(session = session,object_type=valid_api_names.media,object_id = media_id)


@nottest
@with_setup(t_setup, t_teardown)
def test11():
    '''
    Add a media item.  Use PUT /api/rest/media/{id} to modify metadata content - String metadata to be specific
    Validate that the string metadata record gets correctly updated.  This test changes the metadataValue
    on the test media object from initial_metadata_value, to metadata_value_after_change and back to initial)metadata_value.
    For each change, the media object is analyzed and checked for the expected metadataValue
    :return:
    '''
    tcid = 11
    global headers, session, config, category_ids,workgroup_ids,string_any_metadata_id
    namespace = config['test']['namespace']
    initial_metadata_value = 'blah blah blahdy blah scala blah'
    metadata_value_after_change = 'booga fooga mooga scala hooga'

    # Define the base data parameters for the test
    media_uri = 'www.scala.' + namespace + str(tcid) + '.com'
    baseurl = config['login']['baseurl']
    apiurl = '/api/rest/media'
    media_name = namespace + ' Auto Test Media' + str(tcid)

    # Build the media attribute and 'create' it
    media_item_attribute = {'name':media_name,'uri':media_uri,'mediaType':"HTML",
                            'metadataValue': [{'value': initial_metadata_value,
                                               'metadata': {'datatype': 'STRING', 'id': string_any_metadata_id, 'valueType': 'ANY'}}]}
    resp = rest_request(session,type_of_call=call_type.post,baseurl = baseurl,apiurl = apiurl ,payload_params=media_item_attribute)
    logging.debug('Status code for response for media create is: {}, and message is {}'.format(resp.status_code,resp.text))
    assert resp.status_code == 200, 'Status code of rest request to add media object is unexpectedly: {}'.format(resp.status_code)
    media_id = resp.json()['id']
    logging.info('Created media object with ID = {}'.format(media_id))

    #Pull back the media item to check if the value of the metadata value is initial_metadata_value
    get_apiurl = apiurl + '/' + str(media_id)
    resp = rest_request(session, type_of_call=call_type.get, baseurl = baseurl, apiurl = get_apiurl)
    found_modified_metadata = False
    logging.info('Get response on media object = {}'.format(resp.text))
    for item in resp.json()['metadataValue']:
        if item['metadata']['id'] == string_any_metadata_id and item['value']==initial_metadata_value:
            logging.info('Found metadata ID = {} in JSON response after PUT to change metadata.'.format(boolean_any_metadata_id))
            found_modified_metadata = True
    assert found_modified_metadata == True,'Did not find appropriate metadata in the media object created by this test'

   # Define the parameters to be changed in this test
    put_apiurl = apiurl +'/' + str(resp.json()['id'])
    media_item_change_attribute = {'name':media_name,'uri':media_uri,'mediaType':"HTML",
                            'metadataValue': [{'value': metadata_value_after_change,
                                               'metadata': {'datatype': 'STRING', 'id': string_any_metadata_id, 'valueType': 'ANY'}}]}

    #Make the change to the media record for this test case.  Setting string metadata to  medatadata_value_after_change
    resp = rest_request(session, type_of_call = call_type.put, baseurl = baseurl, apiurl = put_apiurl, payload_params = media_item_change_attribute)
    assert resp.status_code == 200, 'Status code of rest request to modify media object was unexpectedly: {}'.format(resp.status_code)
    logging.debug('Response from PUT request {}'.format(resp.text))

    #Pull back the media item to check if the value of the metadata has changed to media_item_change_attribute
    get_apiurl = apiurl + '/' + str(media_id)
    resp = rest_request(session, type_of_call=call_type.get, baseurl = baseurl, apiurl = get_apiurl)
    found_modified_metadata = False
    logging.info('Get response on media object = {}'.format(resp.text))
    for item in resp.json()['metadataValue']:
        if item['metadata']['id'] == string_any_metadata_id and item['value']==metadata_value_after_change:
            logging.info('Found metadata ID = {} in JSON response after PUT to change metadata.'.format(boolean_any_metadata_id))
            found_modified_metadata = True
    assert found_modified_metadata == True

    # Clean up test case by deleting the media object created for this test case
    logging.info('Test case {} complete.  Cleaning up.'.format(tcid))
    delete_object(session = session,object_type=valid_api_names.media,object_id = media_id)

@nottest
@with_setup(t_setup, t_teardown)
def test12():
    '''
    Add a media item.  Use PUT /api/rest/media/{id} to modify metadata content - Integer metadata to be specific
    Validate that the integer metadata record gets correctly updated.  This test changes the metadataValue
    on the test media object from initial_metadata_value, to metadata_value_after_change and back to initial_metadata_value.
    For each change, the media object is analyzed and checked for the expected metadataValue
    :return:
    '''
    tcid = 12
    global headers, session, config, category_ids,workgroup_ids,integer_any_metadata_id
    namespace = config['test']['namespace']
    initial_metadata_value = 4
    metadata_value_after_change = 99

    # Define the base data parameters for the test
    media_uri = 'www.scala.' + namespace + str(tcid) + '.com'
    baseurl = config['login']['baseurl']
    apiurl = '/api/rest/media'
    media_name = namespace + ' Auto Test Media_' + str(tcid)

    # Build the media attribute and 'create' it
    media_item_attribute = {'name':media_name,'uri':media_uri,'mediaType':"HTML",
                            'metadataValue': [{'value': initial_metadata_value,
                                               'metadata': {'datatype': 'STRING', 'id': integer_any_metadata_id, 'valueType': 'ANY'}}]}
    resp = rest_request(session,type_of_call=call_type.post,baseurl = baseurl,apiurl = apiurl ,payload_params=media_item_attribute)
    logging.debug('Status code for response for media create is: {}, and message is {}'.format(resp.status_code,resp.text))
    assert resp.status_code == 200, 'Status code of rest request to add media object is unexpectedly: {}'.format(resp.status_code)
    media_id = resp.json()['id']
    logging.info('Created media object with ID = {}'.format(media_id))

    #Pull back the media item to check if the value of the metadata value is initial_metadata_value
    get_apiurl = apiurl + '/' + str(media_id)
    resp = rest_request(session, type_of_call=call_type.get, baseurl = baseurl, apiurl = get_apiurl)
    found_modified_metadata = False
    logging.info('Get response on media object = {}'.format(resp.text))
    for item in resp.json()['metadataValue']:
        if item['metadata']['id'] == string_any_metadata_id and item['value']==initial_metadata_value:
            logging.info('Found metadata ID = {} in JSON response after PUT to change metadata.'.format(boolean_any_metadata_id))
            found_modified_metadata = True
    assert found_modified_metadata == True,'Did not find appropriate metadata in the media object created by this test'

   # Define the parameters to be changed in this test
    put_apiurl = apiurl +'/' + str(resp.json()['id'])
    media_item_change_attribute = {'name':media_name,'uri':media_uri,'mediaType':"HTML",
                            'metadataValue': [{'value': metadata_value_after_change,
                                               'metadata': {'datatype': 'STRING', 'id': string_any_metadata_id, 'valueType': 'ANY'}}]}

    #Make the change to the media record for this test case.  Setting string metadata to  medatadata_value_after_change
    resp = rest_request(session, type_of_call = call_type.put, baseurl = baseurl, apiurl = put_apiurl, payload_params = media_item_change_attribute)
    assert resp.status_code == 200, 'Status code of rest request to modify media object was unexpectedly: {}'.format(resp.status_code)
    logging.debug('Response from PUT request {}'.format(resp.text))

    #Pull back the media item to check if the value of the metadata has changed to media_item_change_attribute
    get_apiurl = apiurl + '/' + str(media_id)
    resp = rest_request(session, type_of_call=call_type.get, baseurl = baseurl, apiurl = get_apiurl)
    found_modified_metadata = False
    logging.info('Get response on media object = {}'.format(resp.text))
    for item in resp.json()['metadataValue']:
        if item['metadata']['id'] == string_any_metadata_id and item['value']==metadata_value_after_change:
            logging.info('Found metadata ID = {} in JSON response after PUT to change metadata.'.format(boolean_any_metadata_id))
            found_modiffied_metadata = True
    assert found_modified_metadata == True

    # Clean up test case by deleting the media object created for this test case
    logging.info('Test case {} complete.  Cleaning up.'.format(tcid))
    delete_object(session = session,object_type=valid_api_names.media,object_id = media_id)

@nottest
@with_setup(t_setup,t_teardown)
def test13():
    '''
    Add three media items.  Store the ID's of the media objects created.  Then delete using an 'in'
    filter - two of the three media objects.  So, if the id's of the media objects created are:
    4,5,9

    delete 4 and 5 using an 'in' filter and the DELETE api/rest/media API call


    :return:
    '''
    tcid = 13
    global headers, session, config
    namespace = config['test']['namespace']
    assert True

    # Define the base data parameters for the test
    baseurl = config['login']['baseurl']
    apiurl = '/api/rest/media'
    media_id_list = []

    # Build the media attributes and 'create' rhe media objects
    for media_item in range(5):
        media_name = "test media object " + namespace + '_' + str(media_item)
        media_uri = 'www.scala.' + namespace + str(tcid) + '_' + str(media_item) +'.com'
        media_item_attribute = {'name':media_name,'uri':media_uri,'mediaType':"HTML"}
        logging.debug('Adding media web page with attribute = {}'.format(media_item_attribute))
        resp = rest_request(session,type_of_call = call_type.post, baseurl = baseurl, apiurl = apiurl, payload_params=media_item_attribute)
        assert resp.status_code == 200,"Invalid response received when creating media object code = {}, text = {}".format(resp.status_code, resp.text)
        logging.debug('Response from POST to create media is: {}'.format(json.dumps(resp.json())))
        media_id_list.append(resp.json()['id'])
    logging.info('Created {} media objects with IDs: {}'.format(len(media_id_list),media_id_list))

    # Delete the media items I created using a filter.  Only delete the middle slice
    # media_item_list[2:4]
    filter ={'filters': "{'id' : {'values':" +str(media_id_list[2:4])+", 'comparator' : 'in'}}"}
    logging.debug('Filter for delete is: {}'.format(json.dumps(filter)))
    resp = rest_request(session, type_of_call = call_type.delete, baseurl = baseurl, apiurl = apiurl, query_params=filter)
    logging.info('Status Code from delete is: {}'.format(resp.status_code))
    logging.debug('Response from Delete call is: {}'.format(json.dumps(resp.json())))

    # Verify that the DELETE call was honored.
    for media_id_index in range(len(media_id_list)):
        get_api_url = apiurl+'/'+str(media_id_list[media_id_index])
        resp = rest_request(session, type_of_call = call_type.get, baseurl = baseurl, apiurl = get_api_url)
        logging.info('About to check for media items that should have been deleted by the delete filter.')
        if media_id_index == 0 or media_id_index == 1 or media_id_index == 4:
            logging.info('Checking if media item with ID={} should was deleted.  It should still exist'.format(media_id_list[media_id_index]))
            assert resp.status_code == 200, 'After deleting with filter, did not find media object with ID = {} that should not have matched the delete filter.  Status code = {} expecting 200'.format(media_id_list[media_id_index], resp.status_code)
        else:
            logging.info('Checking if media item with ID={} should was deleted.  It should have been deleted.'.format(media_id_list[media_id_index]))
            assert resp.status_code == 400, 'After deleting with filter, found media object with ID = {} that should have matched the delete filter.    Status code = {} expecting 400'.format(media_id_list[media_id_index], resp.status_code)

    # Clean up the media objects created in this test
    for media_id_index in range(len(media_id_list)):
        cleanup_apiurl = apiurl + '/' + str(media_id_list[media_id_index])
        resp = rest_request(session = session, type_of_call = call_type.delete, baseurl = baseurl, apiurl = cleanup_apiurl)
        logging.info('During cleanup received status code of {} when deleting media object with id of {}'.format(resp.status_code, media_id_list[media_id_index]))

@nottest
@with_setup(t_setup,t_teardown)
def test23():
    '''
    Create a media object with workgroup, category, and metadata using POST /api/rest/media.
    Also set the following fields in the post message:
    description
    uri
    audioDucking
    playFullScreen
    volume
    startValidDate
    endValidDate
    validDateStatus

    Unlike test case 2, this test sets all of the default values in the create (POST) message.  Test02
    uses the PUT /api/rest/media inteface to change these values AFTER the media is created.  This test
    uses the POST API call to set these variables directly.

    '''

    global headers, session, config,integer_any_metadata_id,string_any_metadata_id,boolean_any_metadata_id
    namespace = config['test']['namespace']
    tcid = 23

    # Define the base data parameters for the test
    media_uri = 'www.scala.' + namespace + '.com'
    baseurl = config['login']['baseurl']
    apiurl = '/api/rest/media'
    media_name = namespace + ' Auto Test Media_' + str(tcid)

    # Define the parameters to be changed in this test
    description = 'Correct Description has been added to this media object'
    audioDucking = True
    playFullscreen = True
    startValidDate = '2005-02-01'
    endValidDate = '2020-03-01'
    initial_integer_metadata_value = 5
    initial_boolean_metadata_value = True
    initial_string_metadata_value = 'foo'
#    validDateStatus = 'Future'

    # Build the media attribute to 'create' in this test
    media_item_attribute = {'name':media_name,
                            'uri':media_uri,
                            'mediaType':"HTML",
                            'description':description,
                            'audioDucking':audioDucking,
                            'playFullscreen':playFullscreen,
                            'startValidDate':startValidDate,
                            'endValidDate':endValidDate#,
                            # 'metadataValue': [{'value': initial_integer_metadata_value,'metadata': {'datatype': 'INTEGER', 'id': integer_any_metadata_id, 'valueType': 'ANY'}},
                            #                   {'value': initial_boolean_metadata_value,'metadata': {'datatype': 'STRING', 'id': string_any_metadata_id, 'valueType': 'ANY'}},
                            #                   {'value': initial_string_metadata_value,'metadata': {'datatype': 'BOOLEAN', 'id': boolean_any_metadata_id, 'valueType': 'ANY'}}
                            #                   ]
                           }
    resp = rest_request(session,type_of_call=call_type.post,baseurl = baseurl,apiurl = apiurl ,payload_params=media_item_attribute)
    logging.debug('JSON response for media create is: {}'.format(resp.text))
    assert resp.status_code == 200, 'Status code of rest request to add media object is unexpectedly: {}'.format(resp.status_code)
    media_id = resp.json()['id']
    logging.info('Created media object with ID = {}'.format(media_id))

    # Retrieve the media object created above and verify that the attributes match
    get_apiurl = apiurl + '/' + str(media_id)
    resp = rest_request(session,type_of_call=call_type.get,baseurl = config['login']['baseurl'],apiurl = get_apiurl)
    logging.debug('JSON response for media get is: {}'.format(resp.text))
    assert resp.json()['description']  == description, 'Incorrect data in returned media object.  Expected {} got {}'.format(description, resp.json()['description'])
    assert resp.json()['audioDucking'] == audioDucking,  'Incorrect data in returned media object.  Expected {} got {}'.format(audioDucking, resp.json()['audioDucking'])
    assert resp.json()['playFullscreen'] == playFullscreen,  'Incorrect data in returned media object.  Expected {} got {}'.format(playFullscreen, resp.json()['playFullscreen'])
    assert resp.json()['startValidDate'] == startValidDate,  'Incorrect data in returned media object.  Expected {} got {}'.format(startValidDate, resp.json()['startValidDate'])
    assert resp.json()['endValidDate'] == endValidDate,  'Incorrect data in returned media object.  Expected {} got {}'.format(endValidDate, resp.json()['endValidDate'])
            

    logging.info('Test case 23 complete.  Cleaning up.')
    delete_object(session = session,object_type=valid_api_names.media,object_id = media_id)


@with_setup(t_setup,t_teardown)
def test35():
    '''
    Create a media object using POST /api/rest/media
    Use PUT /api/rest/media/{id} to add workgroup assignments
    Use GET /api/rest/media/{id}/workgroups to validate that the workgroups were added
    :return:
    '''
    global headers, session, config,workgroup_ids

    # Define the base data parameters for the test
    tcid = 35
    namespace = config['test']['namespace']
    media_uri = 'www.scala.' + namespace + '.com'
    baseurl = config['login']['baseurl']
    apiurl = '/api/rest/media'
    media_name = namespace + ' Auto Test Media_' + str(tcid)

    # Build the media attribute to 'create' in this test
    media_item_attribute = {'name':media_name,
                            'uri':media_uri,
                            'mediaType':"HTML"}
    resp = rest_request(session,type_of_call=call_type.post,baseurl = baseurl,apiurl = apiurl ,payload_params=media_item_attribute)
    logging.debug('JSON response for media create is: {}'.format(resp.text))
    assert resp.status_code == 200, 'Status code of rest request to add media object is unexpectedly: {}'.format(resp.status_code)
    logging.info('Created media object under test')
    media_id = resp.json()['id']
    logging.info('Created media object with ID = {}'.format(media_id))

    # Send PUT request to add workgroup information to the media object created above
    media_workgroup_list = [{'id':wg_id,'owner':False} for wg_id in workgroup_ids]
    media_workgroup_list[0]['owner'] = True
    media_workgroups_added_attribute = {'workgroups':media_workgroup_list}
    put_apiurl = apiurl + '/' + str(media_id)
    resp = rest_request(session, type_of_call = call_type.put,baseurl = baseurl, apiurl = put_apiurl, payload_params = media_workgroups_added_attribute)
    assert resp.status_code == 200,'Incorrect status code received when adding workgroups to media object expected 200 recieved {}'.format(str(resp.status_code))
    logging.info('Changed media object under test so that it has workgroup assignments')
    logging.debug(resp.text)

    # GET /api/rest/media/{id}/workgroups to retrieve object and validate workgroups
    get_workgroups_apiurl = apiurl + '/' + str(media_id) + '/workgroups'
    resp = rest_request(session, type_of_call = call_type.get, baseurl = baseurl, apiurl = get_workgroups_apiurl)
    assert resp.status_code == 200, 'Incorrect status code received when requesting workgroup info for media with GET /api/rest/media/{id}/workgroups.  Expected 200, received {}'.format(resp.status_code)
    assert resp.json()['mediaWorkgroups'][0]['id'] == media_id, 'Incorrect media object returned from GET /api/rest/media/{id}/workgroups.  Expected ID = {}, received ID = {}'.format(str(media_id), str(resp.json()['mediaWorkgroups'][0]['id']))
    list_of_returned_workgroups = [x['id'] for x in resp.json()['mediaWorkgroups'][0]['list']]
    assert set(list_of_returned_workgroups) == set(workgroup_ids),'Workgroup IDs in media did not match suite workgroup IDs. Found {}, expected {}'.format(str(list_of_returned_workgroups),str(workgroup_ids))

    logging.info('Test case 35 complete.  Cleaning up.')
    delete_object(session = session,object_type=valid_api_names.media,object_id = media_id)

@with_setup(t_setup,t_teardown)
def test38():
    '''
    Create a media object using POST /api/rest/media
    Use PUT /api/rest/media/{id} to add category assignment
    Use GET /api/rest/media{id}/categories to validate that the categories were added
    :return:
    '''
    global headers, session, config,category_ids

    # Define the base data parameters for the test
    tcid = this_function_name()
    namespace = config['test']['namespace']
    media_uri = 'www.scala.' + namespace + '.com'
    baseurl = config['login']['baseurl']
    apiurl = '/api/rest/media'
    media_name = namespace + ' Auto Test Media_' + str(tcid)

    # Build the media attribute to 'create' in this test
    media_item_attribute = {'name':media_name,
                            'uri':media_uri,
                            'mediaType':"HTML"}
    resp = rest_request(session,type_of_call=call_type.post,baseurl = baseurl,apiurl = apiurl ,payload_params=media_item_attribute)
    logging.debug('JSON response for media create is: {}'.format(resp.text))
    assert resp.status_code == 200, 'Status code of rest request to add media object is unexpectedly: {}'.format(resp.status_code)
    logging.info('Created media object under test')
    media_id = resp.json()['id']
    logging.info('Created media object with ID = {}'.format(media_id))

    # Send PUT request to add workgroup information to the media object created above
    media_category_list = [{'id':ct_id} for ct_id in category_ids]
    media_category_added_attribute = {'categories':media_category_list}
    put_apiurl = apiurl + '/' + str(media_id)
    resp = rest_request(session, type_of_call = call_type.put,baseurl = baseurl, apiurl = put_apiurl, payload_params = media_category_added_attribute)
    assert resp.status_code == 200,'Incorrect status code received when adding category to media object expected 200 received {}'.format(str(resp.status_code))
    logging.info('Changed media object under test so that it has category assignments')
    logging.debug(resp.text)

    # GET /api/rest/media/{id}/workgroups to retrieve object and validate workgroups
    get_categories_apiurl = apiurl + '/' + str(media_id) + '/categories'
    resp = rest_request(session, type_of_call = call_type.get, baseurl = baseurl, apiurl = get_categories_apiurl)
    assert resp.status_code == 200, 'Incorrect status code received when requesting categories info for media with GET /api/rest/media/{id}/categories.  Expected 200, received {}'.format(resp.status_code)
    logging.debug('Category list after put has added categories is: {}'.format(resp.text))
    assert 'mediaCategories' in resp.json(), 'No categories found in media object after put. {}'.format(resp.text)
    list_of_returned_categories = [x['id'] for x in resp.json()['mediaCategories'][0]['list']]
    assert set(list_of_returned_categories) == set(category_ids),'Category IDs in media did not match suite workgroup IDs. Found {}, expected {}'.format(str(list_of_returned_categories),str(category_ids))

    logging.info('Test case 38 complete.  Cleaning up.')
    delete_object(session = session,object_type=valid_api_names.media,object_id = media_id)


@nottest
#@with_setup(t_setup(upload_media = True),t_teardown(upload_media = False))
def test40():
    '''
    Test the Generate Thumbnail api /api/rest/media
    :return:
    '''
    global headers, session, config, media_upload_ids

    # Define the base data parameters for the test
    tcid = this_function_name()
    namespace = config['test']['namespace']
    baseurl = config['login']['baseurl']

    logging.info('Media created by setup with ids = {}'.format(media_upload_ids))
    uuid_list = []
    time.sleep(10)
    # Loop through all the media items set up in the t_setup method
    for media_id in media_upload_ids:
        # Check for the thumbnail status - should start at 'Done' GET /api/rest/media/thumbnailStatus/{media ID}
        get_thumbnail_status_by_media_apiurl = '/api/rest/media/thumbnailStatus/' + str(media_id)
        resp = rest_request(session,type_of_call = call_type.get, baseurl = baseurl, apiurl = get_thumbnail_status_by_media_apiurl)
        initial_thumbnail_status= resp.json()['value']
        logging.debug('Thumbnail status for media with ID = {} is {}'.format(media_id, resp.json()['value']))
        assert initial_thumbnail_status == 'Done', 'Thumbnail status for media item with id = {} is not Done before starting test.  Actual thumbnail status is: {}'.format(media_id,initial_thumbnail_status)

        # Send a request to regenerate thumbnail for current media item:  POST /api/rest/media/{mediaId}/thumbnail
        rest_thumbnail_apiurl = '/api/rest/media/' + str(media_id) + '/thumbnail'
        time.sleep(10)
        resp = rest_request(session, type_of_call=call_type.post, baseurl = baseurl, apiurl = rest_thumbnail_apiurl)
        logging.debug('Status code of generate media request is: {}.  Message is: {}'.format(resp.status_code, resp.text))
        uuid_list.append(resp.json()['uuid'])
        assert resp.json()['uuid'] is not None, 'Did not receive UUID on thumbnail generation.  Response for thumbnail generation API call is: {}'.format(resp.text)

    # Poll 3 minutes for the thumbnail to transition to 'Done' for all three media objects

    uuid_is_Done = [False] * len(uuid_list)
    minutes_to_wait = int(config['timer']['uuid_minutes_to_wait'])

    for x in range(minutes_to_wait):
        for uuid_index in range(len(uuid_list)):
            # Send GET
            get_thumbnail_status_by_uuid_apiurl = '/api/rest/media/' + uuid_list[uuid_index] + '/thumbnailStatus'
            resp = rest_request(session,type_of_call= call_type.get, baseurl = baseurl, apiurl = get_thumbnail_status_by_uuid_apiurl)
            assert resp.status_code == 200, "Failed to retrieve status of thumbnail based on UUID for UUID {}, media object {}".format(uuid_list[uuid_index], media_upload_ids[uuid_index])
            logging.debug('Retrieved status of thumbnail UUID = {}, state is: {}'.format(resp.json()['uuid'],resp.json()['value']))
            if resp.json()['value'] == 'Done':
                uuid_is_Done[uuid_index] = True
        time.sleep(10)

    assert False not in uuid_is_Done, "Was not able to validate UUID was done after {} minutes for all media IDs: {}, Done:{}".format(minutes_to_wait, media_upload_ids, uuid_is_Done)

@nottest
@with_setup(t_setup(upload_media=False),t_teardown(upload_media=False))
def test45():
    '''
    List media by filter - on workgrouop
    Create 40 media objects PUT /api/rest/media
    Use PUT /api/rest/media to give 20 of them all workgroup assignments
    use GET /api/rest/media with filter on workgroup
    validate that the correct 20 media objects came back
    delete all objects created in this test
    :return:
    '''

    global headers, session, config, workgroup_ids

    # Define the base data parameters for the test
    tcid = this_function_name()
    namespace = config['test']['namespace']
    baseurl = config['login']['baseurl']
    apiurl = '/api/rest/media'
    n = 40 # Number of media objects created for this test

    # Create 40 media objects for use in this test case
    media_put_apiurl = '/api/rest/media'
    media_id_list = []
    for count_40 in range(n):
        name = 'media_name_{}_{}_{}'.format(namespace,tcid,count_40)
        uri = 'uri.{}.{}.{}'.format(namespace, tcid, str(count_40))
        description = 'Description of media for test case: {}, namespace: {}, count: {}'.format(namespace, tcid, str(count_40))
        media_type = 'HTML'
        attribute = {'name':name,'uri':uri,'description':description,'mediaType':media_type}
        logging.debug('Media attribute is: {}'.format(attribute))
        resp = rest_request(session, type_of_call=call_type.post, baseurl = baseurl, apiurl = media_put_apiurl, payload_params= attribute)
        assert resp.status_code == 200, 'foo Failed to add web media object during setup of test case {}.  Status code = {}, object = {}'.format(tcid, resp.status_code, resp.text)
        logging.debug('Added new media object with id = {}'.format(resp.json()['id']))
        media_id_list.append(resp.json()['id'])
    logging.info('Added 40 media objects.  IDs ='.format(media_id_list))

    # Use PUT /api/rest/media to add half of the media objects created to a workgroup
    for media_id in media_id_list[0:(n//2)]:
        media_workgroup_list = [{'id':wg_id,'owner':False} for wg_id in workgroup_ids]
        media_workgroup_list[0]['owner'] = True
        media_workgroups_added_attribute = {'workgroups':media_workgroup_list}
        put_apiurl = apiurl + '/' + str(media_id)
        resp = rest_request(session,type_of_call=call_type.put,baseurl=baseurl,apiurl=put_apiurl,payload_params=media_workgroups_added_attribute)
        assert resp.status_code==200, 'Did not get expected response when assigning workgroup to media expected 200, got {}. Response: {}'.format(resp.status_code,resp.text)
        logging.debug('Added workgroup assignments {} to media with id  = {}'.format(media_workgroup_list, media_id))

    logging.info('Modified 20 records so their workgroup settings IDs are: {}'.format(media_id_list[0:n//2]))

    # Use GET /api/rest/media to retrieve workgroups based on filter.  Only members of the first
    # workgroup in workgroup_ids will be retrieved

    get_query_params = {'filters':"{workgroups : {values : ['anyAssigned']}}",'fields':'id','limit':n}
    resp = rest_request(session,type_of_call=call_type.get, baseurl=baseurl, apiurl=apiurl,query_params=get_query_params)
    assert resp.status_code == 200, "Filtered GET to /api/rest/media failed.  Expected response status code 200, got {}".format(resp.status_code)
    logging.debug('Filtered GET response is: {}'.format(resp.text))
    assert resp.json()['count'] == n//2, "Incorrect count of ID's in return object from filtered GET.  Expected {}, got {}".format(n//2, resp.json()['count'])
    response_id_list = [int(item['id']) for item in resp.json()['list']]
    logging.debug('Found the following IDs of media objects with workgroup assignments {}'.format(response_id_list))
    logging.debug('The following IDs should have been found in the response: {}'.format(media_id_list[0:n//2]))
    assert set(response_id_list) == set(media_id_list[0:n//2]), "Set of returned ids does not match set where workgroups added. Returned {} expected {}".format(response_id_list,media_id_list[0:n//2])


    logging.info('Test case complete.  Cleaning up.')
    for media_id in media_id_list:
        delete_object(session = session,object_type=valid_api_names.media,object_id = media_id)

@nottest
@with_setup(t_setup(upload_media=False),t_teardown(upload_media=False))
def test50():
    '''
    List media by filter - on category
    Create 40 media objects PUT /api/rest/media
    Use PUT /api/rest/media to give 20 of them a catagory assignment
    use GET /api/rest/media with filter on catagory
    validate that the correct 20 media objects came back
    delete all objects created in this test
    :return:
    '''

    global headers, session, config, workgroup_ids

    # Define the base data parameters for the test
    tcid = this_function_name()
    namespace = config['test']['namespace']
    baseurl = config['login']['baseurl']
    apiurl = '/api/rest/media'
    n = 40 # Number of media objects created for this test

    # Create 40 media objects for use in this test case
    media_put_apiurl = '/api/rest/media'
    media_id_list = []
    for count_40 in range(n):
        name = 'media_name_{}_{}_{}'.format(namespace,tcid,count_40)
        uri = 'uri.{}.{}.{}'.format(namespace, tcid, str(count_40))
        description = 'Description of media for test case: {}, namespace: {}, count: {}'.format(namespace, tcid, str(count_40))
        media_type = 'HTML'
        attribute = {'name':name,'uri':uri,'description':description,'mediaType':media_type}
        logging.debug('Media attribute is: {}'.format(attribute))
        resp = rest_request(session, type_of_call=call_type.post, baseurl = baseurl, apiurl = media_put_apiurl, payload_params= attribute)
        assert resp.status_code == 200, 'foo Failed to add web media object during setup of test case {}.  Status code = {}, object = {}'.format(tcid, resp.status_code, resp.text)
        logging.debug('Added new media object with id = {}'.format(resp.json()['id']))
        media_id_list.append(resp.json()['id'])
    logging.info('Added 40 media objects.  IDs ='.format(media_id_list))

    # Use PUT /api/rest/media to add half of the media objects created to a workgroup
    for media_id in media_id_list[0:(n//2)]:
        media_workgroup_list = [{'id':wg_id,'owner':False} for wg_id in workgroup_ids]
        media_workgroup_list[0]['owner'] = True
        media_workgroups_added_attribute = {'workgroups':media_workgroup_list}
        put_apiurl = apiurl + '/' + str(media_id)
        resp = rest_request(session,type_of_call=call_type.put,baseurl=baseurl,apiurl=put_apiurl,payload_params=media_workgroups_added_attribute)
        assert resp.status_code==200, 'Did not get expected response when assigning workgroup to media expected 200, got {}. Response: {}'.format(resp.status_code,resp.text)
        logging.debug('Added workgroup assignments {} to media with id  = {}'.format(media_workgroup_list, media_id))

    logging.info('Modified 20 records so their workgroup settings IDs are: {}'.format(media_id_list[0:n//2]))

    # Use GET /api/rest/media to retrieve workgroups based on filter.  Only members of the first
    # workgroup in workgroup_ids will be retrieved

    get_query_params = {'filters':"{workgroups : {values : ['anyAssigned']}}",'fields':'id','limit':n}
    resp = rest_request(session,type_of_call=call_type.get, baseurl=baseurl, apiurl=apiurl,query_params=get_query_params)
    assert resp.status_code == 200, "Filtered GET to /api/rest/media failed.  Expected response status code 200, got {}".format(resp.status_code)
    logging.debug('Filtered GET response is: {}'.format(resp.text))
    assert resp.json()['count'] == n//2, "Incorrect count of ID's in return object from filtered GET.  Expected {}, got {}".format(n//2, resp.json()['count'])
    response_id_list = [int(item['id']) for item in resp.json()['list']]
    logging.debug('Found the following IDs of media objects with workgroup assignments {}'.format(response_id_list))
    logging.debug('The following IDs should have been found in the response: {}'.format(media_id_list[0:n//2]))
    assert set(response_id_list) == set(media_id_list[0:n//2]), "Set of returned ids does not match set where workgroups added. Returned {} expected {}".format(response_id_list,media_id_list[0:n//2])


    logging.info('Test case 50 complete.  Cleaning up.')
    for media_id in media_id_list:
        delete_object(session = session,object_type=valid_api_names.media,object_id = media_id)



