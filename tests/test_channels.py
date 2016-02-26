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
frameset_id_list = []
namespace = config['test']['namespace']


def this_function_name():
    return inspect.stack()[1][3]

def create_channel(channel_name, channel_description, channel_type, frame_id, channel_playDedicated_audio):
    '''
    A utility function for rapidly creating channels
    :return: ID of created channel or None if channel create fails
    '''
    global session, namespace,baseurl, frameset_id_list

    channel_create_apiurl = '/api/rest/channels'
    channel_frameset = {'id':frame_id}

    channel_parameters = {'name':channel_name,'description':channel_description,'type':channel_type,'frameset':channel_frameset, 'playDedicatedAudioTrack':channel_playDedicated_audio}
    resp = rest_request(session, type_of_call=call_type.post, baseurl=baseurl, apiurl = channel_create_apiurl, payload_params= channel_parameters)
    logging.debug('Response from Create Channel call is: {}'.format(resp.text))
    logging.info('Response from Create channel call is {}, expected 200'.format(resp.status_code))
    try:
        channel_id = resp.json()['id']
    except KeyError:
        logging.error('Received no ID when attempting to create a channel')
        channel_id = None
    logging.info('Created Channel with ID = {}'.format(channel_id))
    return channel_id

def delete_channel(channel_id):
    # Delete the channel
    global session
    logging.debug('About to Delete channel wiiith id = {}'.format(channel_id))
    delete_apiurl = '/api/rest/channels/' + str(channel_id)
    resp = rest_request(session, type_of_call=call_type.delete, baseurl=baseurl,apiurl = delete_apiurl)
    logging.debug('Status code from Delete channel is {}, response is {}'.format(resp.status_code,resp.text))
    assert resp.status_code == 204, 'Unexpected status code during delete channel.  Expected 204, received {}'.format(resp.status_code)


def t_setup():
    '''
    Initialize the session object for the test case.
    '''

    # Begin by initiating a new login session for this test case.
    global config, session,frameset_id_list, user_id_list,baseurl
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

    #  Acquire a list of the id's of valid framesets on this system
    get_frameset_apiurl = '/api/rest/framesetTemplates'
    frameset_query_params = {'limit':1000, 'fields':'id'}
    resp = rest_request(session,type_of_call=call_type.get, baseurl=baseurl, apiurl = get_frameset_apiurl, query_params= frameset_query_params)
    logging.debug('GET all frameset IDs request response is: {}'.format(resp.text))
    frameset_list = resp.json()['list']
    assert len(resp.json()['list']) != 0, 'No framesets datafilled on system. Test case fails.'
    frameset_id_list = [item['id'] for item in frameset_list]

def t_teardown():
    global session,baseurl, media_id_list, user_id_list
    response = logout(session, config['login']['baseurl'])
    assert response

@with_setup(t_setup,t_teardown)
def test_endpoint_create_delete_channel():
    '''
    Basic Channel Creation with name and description
    :return:
    '''
    global session, namespace,baseurl, frameset_id_list

    channel_name = namespace  + '_' + this_function_name()
    channel_description = namespace + '_' + this_function_name() + ' Channel Description'
    channel_type = 'AUDIOVISUAL'
    channel_create_apiurl = '/api/rest/channels'
    channel_frameset = {'id':frameset_id_list[0]}
    channel_playDedicated_audio = False

    channel_parameters = {'name':channel_name,'description':channel_description,'type':channel_type,'frameset':channel_frameset, 'playDedicatedAudioTrack':channel_playDedicated_audio}
    resp = rest_request(session, type_of_call=call_type.post, baseurl=baseurl, apiurl = channel_create_apiurl, payload_params= channel_parameters)
    logging.debug('Response from Create Channel call is: {}'.format(resp.text))
    assert resp.status_code == 200, 'Response from Create channel call is {}, expected 200'.format(resp.status_code)
    channel_id = resp.json()['id']
    assert channel_id is not None
    logging.info('Created Channel with ID = {}'.format(channel_id))

    # Delete the channel
    delete_apiurl = '/api/rest/channels/' + str(channel_id)
    resp = rest_request(session, type_of_call=call_type.delete, baseurl=baseurl,apiurl = delete_apiurl)
    logging.debug('Status code from Delete channel is {}, response is {}'.format(resp.status_code,resp.text))
    assert resp.status_code == 204, 'Unexpected status code during delete channel.  Expected 204, received {}'.format(resp.status_code)

@with_setup(t_setup,t_teardown)
def test_endpoint_duplicate_channel():
    '''
    Create Channel.  Duplicate channel.  Validate duplication.  Clean up.
    :return:
    '''

    global session, namespace,baseurl, frameset_id_list
    # Create a channel to be duplicated

    channel_name = namespace  + '_' + this_function_name()
    channel_description = namespace + '_' + this_function_name() + ' Channel Description'
    channel_type = 'AUDIOVISUAL'
    channel_create_apiurl = '/api/rest/channels'
    channel_frameset = {'id':frameset_id_list[0]}
    channel_playDedicated_audio = False

    channel_parameters = {'name':channel_name,'description':channel_description,'type':channel_type,'frameset':channel_frameset, 'playDedicatedAudioTrack':channel_playDedicated_audio}
    resp = rest_request(session, type_of_call=call_type.post, baseurl=baseurl, apiurl = channel_create_apiurl, payload_params= channel_parameters)
    logging.debug('Response from Create Channel call is: {}'.format(resp.text))
    assert resp.status_code == 200, 'Response from Create channel call is {}, expected 200'.format(resp.status_code)
    channel_id = resp.json()['id']
    assert channel_id is not None
    logging.info('Created Channel with ID = {}'.format(channel_id))

    # Duplicate the Channel using /api/rest/channels/{id}/duplicate
    duplicate_channel_api = '/api/rest/channels/' + str(channel_id) + '/duplicate'
    duplicate_channel_name = channel_name + 'dup'
    duplicate_channel_parameters = {'name':duplicate_channel_name}
    dup_resp = rest_request(session, type_of_call = call_type.post, baseurl=baseurl, apiurl = duplicate_channel_api,payload_params=duplicate_channel_parameters)
    logging.debug('Status code from duplicate message: {}, actual response is: {}'.format(dup_resp.status_code, dup_resp.text))
    assert dup_resp.status_code == 200, 'Could not validate duplication of channel element.'
    assert dup_resp.json()['id'] is not None
    dup_channel_id = dup_resp.json()['id']
    assert channel_id != dup_channel_id

    # Ok.  Validate that the duplicate record matches the original
    assert resp.json()['name'] != dup_resp.json()['name'],'Name of duplicate matches name of original'
#    assert resp.json()['description'] == dup_resp.json()['description'], 'Description of duplicate does not match original.  Orig = {}, dup = {}'.format(resp.json()['description'],dup_resp.json()['description'])
    assert resp.json()['type'] == dup_resp.json()['type'], 'Type of duplicate does not match original'
    assert resp.json()['playDedicatedAudioTrack'] == dup_resp.json()['playDedicatedAudioTrack'], 'playDedicatedAudioTrack of duplicate does not match original'
#    logging.debug('Original frameset is {}'.format(resp.json()['frameset']))
#    logging.debug('Duplicate frameset is {}'.format(dup_resp.json()['frameset']))
#    assert resp.json()['framesCounter'] == dup_resp.json()['framesCounter'],'duplicate has different number of frames than original.  Orig {} Dup {}'.format(resp.json()['framesCounter'],dup_resp.json()['framesCounter'])

    # Clean up by deleting the two two records created during testing
    delete_apiurl = '/api/rest/channels/' + str(channel_id)
    delete_dup_apiurl = '/api/rest/channels/' +str(dup_channel_id)

    logging.debug('Delete original apiurl = ' + delete_apiurl)
    logging.debug('Delete duplicate apiurl = ' + delete_dup_apiurl)

    resp = rest_request(session, type_of_call=call_type.delete, baseurl=baseurl,apiurl = delete_apiurl)
    dup_resp =  rest_request(session, type_of_call=call_type.delete, baseurl=baseurl,apiurl = delete_dup_apiurl)
    assert resp.status_code == dup_resp.status_code == 204, 'Could not validate that test channels were '

@with_setup(t_setup,t_teardown)
def test_endpoint_find_channel():
    '''
    Create a channel using POST /api/rest/channels
    Find that channel by ID using GET /api/rest/channels/{id} < -- This is the API to check
    Delete channel created in this test by using DELETE /api/rest/channels/
    :return:
    '''
    global session, namespace,baseurl, frameset_id_list

    channel_name = namespace  + '_' + this_function_name()
    channel_description = namespace + '_' + this_function_name() + ' Channel Description'
    channel_type = 'AUDIOVISUAL'
    channel_create_apiurl = '/api/rest/channels'
    channel_frameset = {'id':frameset_id_list[0]}
    channel_playDedicated_audio = False

    channel_parameters = {'name':channel_name,'description':channel_description,'type':channel_type,'frameset':channel_frameset, 'playDedicatedAudioTrack':channel_playDedicated_audio}
    resp = rest_request(session, type_of_call=call_type.post, baseurl=baseurl, apiurl = channel_create_apiurl, payload_params= channel_parameters)
    logging.debug('Response from Create Channel call is: {}'.format(resp.text))
    assert resp.status_code == 200, 'Response from Create channel call is {}, expected 200'.format(resp.status_code)
    channel_id = resp.json()['id']
    assert channel_id is not None
    logging.info('Created Channel with ID = {}'.format(channel_id))

    #  Find the channel using the GET /api/rest/channels/{id}
    find_apiurl = '/api/rest/channels/' + str(channel_id)
    resp = rest_request(session, type_of_call = call_type.get, baseurl = baseurl, apiurl = find_apiurl)
    logging.debug('Status code from find channel call is: {}'.format(resp.status_code))
    logging.debug('Response object from find channel call is: {}'.format(resp.text))
    assert channel_id == resp.json()['id'], 'Object returned by find channel API did not have the same ID as the object created earlier in this test.'


    # Delete the channel
    delete_apiurl = '/api/rest/channels/' + str(channel_id)
    resp = rest_request(session, type_of_call=call_type.delete, baseurl=baseurl,apiurl = delete_apiurl)
    logging.debug('Status code from Delete channel is {}, response is {}'.format(resp.status_code,resp.text))
    assert resp.status_code == 204, 'Unexpected status code during delete channel.  Expected 204, received {}'.format(resp.status_code)

@with_setup(t_setup,t_teardown)
def test_endpoint_list_channels():
    '''
    Create multiple channels using POST /aip/rest/channels
    List those channels using GET /api/rest/channels
    Delete said channels
    :return:
    '''
    global session, namespace,baseurl, frameset_id_list

    channel_name_master = namespace + '_' + this_function_name()
    channel_description = 'namespace' +'_' + this_function_name() + ' Channel Description'
    channel_type = 'AUDIOVISUAL'
    channel_playDedicated_audio = False
    logging.info('Frameset IDs for this test: {}'.format(frameset_id_list))

    channel_id_list = []
    for frame_id in frameset_id_list:
        channel_name = channel_name_master + '_' + str(frame_id)
        channel_id_list.append(create_channel(channel_name = channel_name,
                       channel_description = channel_description,
                       channel_type= channel_type,
                       frame_id = frame_id,
                       channel_playDedicated_audio=channel_playDedicated_audio))
    logging.debug('List of channel ids created for this test is: {}'.format(channel_id_list))
    assert None not in channel_id_list, ('At least on channel was not created in channel create loop')

    #List the channels created above.  Verify that all of the channels created in this test case also appear in the list results
    get_query_parameters = {'limit':900,'fields':'id'}
    get_apiurl = '/api/rest/channels'

    resp = rest_request(session, type_of_call=call_type.get, baseurl = baseurl, apiurl = get_apiurl, query_params=get_query_parameters)
    logging.debug('Status code from list Channels is: {}'.format(resp.status_code))
    logging.debug('Response from get Channels list is: {}'.format(resp.text))

    assert resp.status_code == 200, 'Incorrect status code received from get channels call. Expected 200 got {}'.format(resp.status_code)

    # Compare list of returned id's to the list of created id's
    returned_channel_id_list = [item['id'] for item in resp.json()['list']]
    logging.debug('List of channels created by this test case: {}'.format(channel_id_list))
    logging.debug('List of channels returned from list channel API call is: {}'.format(returned_channel_id_list))
    found_all_created_channels = True
    for channel_id in channel_id_list:
        if channel_id not in returned_channel_id_list:
            logging.debug('Channel with ID = {} found in channel ID list but not in returned channel list.'.format(channel_id))
            found_all_created_channels = False
    logging.debug('About to assert that I found all the channels I expected is true with actual value = {}'.format(found_all_created_channels))
    assert found_all_created_channels, 'List of channels returned from list did not match list of created channels.'
    logging.debug('List of channels returned from list channel API call and those created from this test case')


    # Delete all channels created in this test - Cleanup
    logging.debug('Delete these channels: {}'.format(channel_id_list))
    for deleted_channel_id in channel_id_list:
        delete_channel(deleted_channel_id)

@with_setup(t_setup,t_teardown)
def test_endpoint_multi_update_channel():
    '''
    Create  channel objects using POST /api/rest/channels
    Send the ID's into storagge using POST /api/rest/storage and retain the UUID from the response
    Using the UUID, use PUT /api/rest/channels/multi to change the description of the three channel objects
    Use get /api/rest/channels to pull down the three channels and verify that the change took effect.
    Delete the three media objects created in this test case
    :return:
    '''
    global session, namespace, baseurl, frameset_id_list

    channel_name_master = namespace + '_' + this_function_name()
    channel_description = 'namespace' +'_' + this_function_name() + ' Initial Channel Description'
    channel_type = 'AUDIOVISUAL'
    channel_playDedicated_audio = False
    logging.info('Frameset IDs for this test: {}'.format(frameset_id_list))
    changed_channel_description = this_function_name() + ' Changed Test Description Text'

    channel_id_list = []
    for frame_id in frameset_id_list:
        channel_name = channel_name_master + '_' + str(frame_id)
        channel_id_list.append(create_channel(channel_name = channel_name,
                       channel_description = channel_description,
                       channel_type= channel_type,
                       frame_id = frame_id,
                       channel_playDedicated_audio=channel_playDedicated_audio))
    logging.debug('List of channel ids created for this test is: {}'.format(channel_id_list))
    assert None not in channel_id_list, ('At least on channel was not created in channel create loop')

    # Send the ID's into storage
    storage_parameters = {'ids':channel_id_list}
    logging.debug('Storage request pending using : {}'.format(json.dumps(storage_parameters)))
    storage_apiurl = '/api/rest/storage'
    resp = rest_request(session, type_of_call=call_type.post, baseurl = baseurl, apiurl = storage_apiurl, payload_params=storage_parameters)
    logging.debug('Response code for storage request is: {}, response is: {}'.format(resp.status_code, resp.text))
    assert resp.status_code == 200, 'Incorrect status code when pushing channel IDs into storage.'
    assert resp.json()['value'] is not None
    storage_uuid = resp.json()['value']

    # Send the multi request to modify the description field on all of the channels created above
    multi_change_apiurl = '/api/rest/channels/multi/' + storage_uuid
    multi_change_parameter = {'id':storage_uuid, 'uuid':storage_uuid, 'item':{'description':changed_channel_description}}
    resp = rest_request(session,type_of_call=call_type.put, baseurl = baseurl, apiurl = multi_change_apiurl, payload_params= multi_change_parameter)
    logging.debug('Status code of multi request is: {}, response is: {}'.format(resp.status_code, resp.text))

    # Pull the channels back and verify that their descriptions have changed:
    channel_check_apiurl = '/api/rest/channels'
    channel_check_parameters = {'fields':'id,description'}
    for channel_id in channel_id_list:
        current_channel_check_apiurl = channel_check_apiurl +'/' + str(channel_id)
        logging.debug('Checking for correct description on channel ID = {}'.format(channel_id))
        resp = rest_request(session, type_of_call=call_type.get, baseurl = baseurl, apiurl = current_channel_check_apiurl, query_params= channel_check_parameters)
        logging.debug('Response from get channel request is status_code = {}, response = {}'.format(resp.status_code, resp.text))
        assert resp.json()['description']==changed_channel_description, 'Found incorrect description after put request'

    # Delete all channels created in this test - Cleanup
    logging.debug('Delete theseee channels: {}'.format(channel_id_list))
    for deleted_channel_id in channel_id_list:
        delete_channel(deleted_channel_id)

@with_setup(t_setup,t_teardown)
def test_endpoint_update_channel():
    '''
    Create a single channel POST /api/rest/chanels
    Use PUT /api/rest/channels/{id} to modify it's description
    Use GET /api/rest/channels/{id} to pull back the channel modified above
    Assert that the PUT command modified the description of the channel object
    Delete the channel object (cleanup)
    '''


    global session, namespace, baseurl, frameset_id_list

    channel_name_master = namespace + '_' + this_function_name()
    channel_description = 'namespace' +'_' + this_function_name() + ' Initial Channel Description'
    channel_type = 'AUDIOVISUAL'
    channel_playDedicated_audio = False
    logging.info('Frameset IDs for this test: {}'.format(frameset_id_list))
    changed_channel_description = this_function_name() + ' Changed Test Description Text'

    channel_name = channel_name_master + '_' + str(frameset_id_list[0])
    channel_id = (create_channel(channel_name = channel_name,
                       channel_description = channel_description,
                       channel_type= channel_type,
                       frame_id = frameset_id_list[0],
                       channel_playDedicated_audio=channel_playDedicated_audio))
    logging.debug('Channel Created for this test case: {}'.format(channel_id))

    # Send PUT request to /api/rest/channels to update the single media
    put_apiurl = '/api/rest/channels/' + str(channel_id)
    put_parameter = {'description':changed_channel_description,'type':channel_type}
    resp = rest_request(session, type_of_call=call_type.put,baseurl=baseurl,apiurl=put_apiurl,payload_params=put_parameter)
    logging.debug('Response from put request to modify channel description: status code = {}, response = {}'.format(resp.status_code,resp.text))
    assert resp.status_code == 200, 'Invalid status code when issuing put call to modify channel description.  Expected 200 got {}'.format(resp.status_code)

    # GET the channel back and make sure the description was changed by the put request
    get_apiurl = '/api/rest/channels/'+str(channel_id)
    resp = rest_request(session, type_of_call=call_type.get,baseurl=baseurl,apiurl=get_apiurl)
    logging.debug('Response from get request after put is: status_code = {},response = {}'.format(resp.status_code, resp.text) )
    assert resp.status_code == 200, 'Failed to recall channel object after put request {}'.format(resp.text)
    assert resp.json()['description']==changed_channel_description

    # Delete the channel used in this test
    delete_channel(channel_id)

