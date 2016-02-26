__author__ = 'rkaye'

from nose import with_setup
from nose.tools import nottest
import logging
import logging.config
import configparser
from framework.constants import CONFIG_FILE_PATH, LOG_FILE_PATH
from framework.authentication_rest import login, logout, get_auth_token
from framework.http_rest import *
from framework.fileupload_rest import File_upload
from framework.templates_rest import Templates
from framework.media_rest import Media
from framework.channel_rest import Channels
from framework.frameset_template_rest import Frameset_template
from framework.player_rest import Player
from framework.message_rest import Message
import inspect
import time

config = configparser.ConfigParser()
config.read(CONFIG_FILE_PATH)
baseurl = config['login']['baseurl']
logging.config.fileConfig(LOG_FILE_PATH)
logging.debug('Logging config file path is: {}'.format(CONFIG_FILE_PATH))
session = requests.Session()
namespace = config['test']['namespace']
api_version = config['api_info']['api_version']
api_version_templates = config['api_info']['api_version_templates']
api_version_fileupload = config['api_info']['api_version_fileupload']
api_version_media = config['api_info']['api_version_media']
api_version_messages = config['api_info']['api_version_messages']
api_version_channels = config['api_info']['api_version_channels']
api_version_framesets = config['api_info']['api_version_framesets']
api_version_player = config['api_info']['api_version_player']
template_id = 0
frameset_id = 0
channel_id = 0
player_id = 0
player_name = ""
player_description = ""
channel_name = ""
media_id = 0


def this_function_name():
    return inspect.stack()[1][3]


def setup():
    global config, baseurl, media_id, template_id, frameset_id, channel_id, channel_name, namespace, api_version_media, player_id, player_name, player_description

    # Begin by initiating a new login session for this test case.
    logging.info('Beginning test setup')
    baseurl = config['login']['baseurl']
    username = config['login']['username']
    password = config['login']['password']
    logging.debug('Read login info from config file and ready to begin.')
    logging.info('Initializing session for test module setup.')

    # INITIALIZE SESSION OBJECT
    setup_session = login(username, password, baseurl)
    assert setup_session is not None

    # Create a media item for use in this test suite
    file_up = File_upload(api_version_fileupload)

    # Initiate Upload of media item
    file_up.initiate_upload(setup_session, baseurl=baseurl, local_file_name=config['media_items']['mediafile_1'],
                            file_upload_path=namespace)

    uuid = file_up.get_response_key('uuid')
    media_id = file_up.get_response_key('mediaId')

    # Upload file part
    file_up.upload_file_part(setup_session, baseurl=baseurl, local_file_name=config['media_items']['mediafile_1'],
                             local_file_path=config['path']['media'], uuid=uuid)

    # Commit Upload
    file_up.upload_finished(setup_session, baseurl=baseurl, uuid=uuid)

    file_up_template = File_upload(api_version_fileupload)

    # Initiate Upload of Template file for use in this test suite
    file_up_template.initiate_upload(setup_session, baseurl=baseurl,
                                     local_file_name=config['template_items']['templatefile_3'],
                                     file_upload_path=namespace + this_function_name())

    # Upload File
    uuid = file_up_template.get_response_key('uuid')
    template_id = file_up_template.get_response_key('mediaId')
    file_up_template.upload_file_part(setup_session, baseurl=baseurl,
                                      local_file_name=config['template_items']['templatefile_3'],
                                      local_file_path=config['path']['templates'], uuid=uuid)

    # Commit Upload
    file_up_template.upload_finished(setup_session, baseurl=baseurl, uuid=uuid)

    # Create a channel object for use in this test case
    channel = Channels(api_version_channels)
    frameset = Frameset_template(api_version_framesets)
    frameset.list_all_available_frameset_templates(setup_session, baseurl=baseurl, fields='id,name')
    list_of_framesets = frameset.get_response_key('list')
    frameset_id = list_of_framesets[0]['id']
    channel_name = 'ab_' + namespace
    channel.create_channel(setup_session, baseurl, name='ab_' + namespace, frameset_id=frameset_id)
    channel_id = channel.get_response_key('id')

    # Create player object for use in this test case
    player_name = 'abtest_' + namespace
    player_description = 'The player used in ap testing to validate player fields in namespace ' + namespace
    player = Player(api_version_player)
    player.create_player(setup_session, baseurl, name=player_name, description=player_description)
    player_id = player.get_response_key('id')

    response = logout(setup_session, baseurl=baseurl)


def teardown():
    global baseurl, config, media_id, channel_id
    # Begin by initiating a new login session for this test case.
    logging.info('Beginning test suite teardown')
    # INITIALIZE SESSION OBJECT
    username = config['login']['username']
    password = config['login']['password']
    teardown_session = login(username, password, baseurl)

    # Delete media Object created for this test module
    media = Media(api_version_media)
    media.delete_media_by_id(teardown_session, baseurl=baseurl, id=media_id)

    # Delete channel Object created for this test
    logging.debug('Cleaning up channel')
    channel = Channels(api_version_channels)
    channel.delete_channel_by_id(session=teardown_session, baseurl=baseurl, channel_id=channel_id)

    # Delete player object created for this test
    logging.debug('Cleaning up player')
    player = Player(api_version_player)
    player.delete_player_by_id(session=teardown_session, baseurl=baseurl, id=player_id)

    response = logout(teardown_session, baseurl=baseurl)


def t_setup():
    global config, session, baseurl, media_id, namespace, api_version_media

    # Begin by initiating a new login session for this test case.
    logging.info('Beginning test setup')
    username = config['login']['username']
    password = config['login']['password']
    logging.debug('Read login info from config file and ready to begin.')
    logging.info('Initializing session for next test case.')
    media_path = config['path']['media']
    # INITIALIZE SESSION OBJECT
    session = login(username, password, baseurl)
    assert session is not None


def t_teardown():
    global session, baseurl, media_id
    response = logout(session, baseurl=baseurl)


@with_setup(t_setup, t_teardown)
def media_field_check(key_value_pair):
    '''
    Method wrapped by test_field_values test.  This method will call the validate method and assert true or false
    so it is not necessary to assert in framework code (Media object)

    Note - the key:value pair passed to this method should be the field name and the expected value of that field
    Many fields will not be able to be tested in this fashion.  Date fields, for example, cannot be tested easily for
    their value - only that the field exists.

    Thus, a value of None shall be passed if the key needs to be checked but the value ignored.
    '''
    global session, baseurl, media_id

    # logging.info('Testing for fields {} with value {}'.format)
    test_media = Media(api_version_media)
    test_media.find_media_by_id(session, baseurl=baseurl, id=media_id)
    assert test_media.validate_api_field(key_value_pair), 'Did not find {} in media object.'.format(key_value_pair)


def test_media_fields_present():
    '''
    This test will test for the existence of keys.  Where possible, values will also be compared.

    The media used is one of the media created in the t_setup for this test case

    As this media item is parameterized in testconfig, specific values for each field cannot be tested in this test.
    :return:
    '''
    global config, session, baseurl, media_id, api_version_media

    file_name = config['media_items']['mediafile_1']
    key_value_pairs_to_check = [
        {"id": media_id},
        {"name": file_name},
        {"lastModified": None},
        # {"thumbnailDownloadPaths": None}, Cannot check thumbnail downloads - they are not available fast enough
        {"downloadPath": None},
        {"webDavPath": None},
        {"path": '/content/' + namespace},
        {"audioDucking": False},
        {"playFullscreen": False},
        #        {"width": None}, Generated in thumbnail creation - not available fast enough
        #        {"height": None}, Generated in thumbnail creation - not available fast enough
        {"approvalStatus": "APPROVED"},
        {"approvalDetail": None},
        {"createdDate": None},
        {"mediaType": "IMAGE"},
        {"startValidDate": None},  #  A candidate for specific data validation
        {"length": None},  # A candidate for specific data validation
        #        {"prettifyLength": None},  Created in thumbnail generation process - cannot check
        {"revision": None},
        {"uploadedBy": None},
        {"modifiedBy": None},
        {"messagesCount": 0},
        {"playlistsCount": 0},
        {"templatesCount": 0},
        {"validDateStatus": "CURRENT_NO_EXPIRATION"},
        {"mediaItemFiles": None},  #Complex data structure - but would be greta to check in more detail - future
        #        {"prettifyType": "Image"}, Created in thumbnail generation process - cannot test easily
        #        {"status": "OK"}, Not ready in time for check
        #        {"generatingThumbnail": False},Not ready in time for check
        {"readOnly": False},
        {"uploadType": "MEDIA"}]

    for key_value_pair in key_value_pairs_to_check:
        logging.info('Beginning test of {} key value pair for Media object'.format(key_value_pair))
        # time.sleep(1)

        yield media_field_check, key_value_pair


@with_setup(t_setup, t_teardown)
def template_field_check(key_value_pair):
    '''
    Method wrapped by test_field_values test.  This method will call the validate method and assert true or false
    so it is not necessary to assert in framework code (Template object)
    '''
    global session, baseurl, template_id
    test_template = Templates(api_version_templates)
    test_template.find_tempalte_by_id(session, baseurl=baseurl, id=template_id)
    assert test_template.validate_api_field(key_value_pair), 'Did not find {} in template object.'.format(
        key_value_pair)


def test_template_field_keys():
    '''
    This test will test for the existence of keys.  Where possible, values will also be compared.

    The template used is the default template for this test suite - identified by template_id.

    As this template is parameterized in testconfig, specific values for each field cannot be tested in this test.
    '''
    global session, baseurl, template_id, api_version_templates
    key_value_pairs_to_check = [{'id': template_id},
                                {'name': None},
                                {'lastModified': None},
                                # {'thumbnailDownloadPaths':None}, Note:  Thumbnails take time to be generated and won't appear
                                {'downloadPath': None},
                                {'webDavPath': None},
                                {'path': None},
                                {'audioDucking': False},
                                {'playFullscreen': False},
                                {'width': None},
                                {'height': None},
                                # {'prettifyDuration':None},  Note:  Thumbnails take time to be generated and won't appear
                                {'approvalStatus': 'APPROVED'},
                                {'approvalDetail': None},
                                {'createdDate': None},
                                {'mediaType': 'TEMPLATE'},
                                {'startValidDate': None},
                                {'length': None},
                                {'prettifyLength': None},
                                {'revision': None},
                                {'uploadedBy': None},
                                {'modifiedBy': None},
                                {'messagesCount': None},
                                {'playlistsCount': None},
                                {'templatesCount': None},
                                {'validDateStatus': 'CURRENT_NO_EXPIRATION'},
                                {'mediaItemFiles': None},
                                {'prettifyType': 'Scala Template'},
                                # {'status':'OK'},  Status will be either Uploading or OK. No way to check w/out waiting
                                {'generatingThumbnail': None},
                                {'readOnly': False},
                                {'uploadType': 'TEMPLATE'},
                                #{'createdBy':None}, # See CM-8957
                                {'numberOfFields': None},
                                {'numberOfFiles': None},
                                {'mediaId': None},
                                # {'templateFields':None} # Generated by thumbnail process -cannot check fast!
    ]
    for key_value_pair in key_value_pairs_to_check:
        logging.info('Beginning test of {} key value pair for Templates object'.format(key_value_pair))
        yield template_field_check, key_value_pair


@with_setup(t_setup, t_teardown)
def channel_field_check(key_value_pair):
    '''
    Method wrapped by test_channel_field_keys test.  This method will call the validate method and assert true or false
    so it is not necessary to assert in framework code (Template object)
    '''
    global session, baseurl, channel_id
    test_channel = Channels(api_version_channels)
    test_channel.find_channel_by_id(session, baseurl=baseurl, id=channel_id)
    assert test_channel.validate_api_field(key_value_pair), 'Did not find {} in channel object.'.format(key_value_pair)


def test_channel_field_keys():
    global session, baseurl, channel_id, api_version_channels
    key_value_pairs_to_check = [{"id": channel_id},
                                {"name": channel_name},
                                {"type": "AUDIOVISUAL"},
                                {"playDedicatedAudioTrack": False},
                                {"audioControlledByAdManager": False},
                                {"muteAudioFromVisual": False},
                                {"lastModified": None},
                                {"frameset": None},
                                {"playerCount": 0}]

    for key_value_pair in key_value_pairs_to_check:
        logging.info('Beginning test of {} key value pair for Channel Object.'.format(key_value_pair))
        yield channel_field_check, key_value_pair


@with_setup(t_setup, t_teardown)
def player_field_check(key_value_pair):
    '''
    Method wrapped by test_channel_field_keys test.  This method will call the validate method of the framework object
    and assert true or false so it is not nessasary to assert in framework code
    :param key_value_pair: A key and value pair - e.g. {'id':45} as found in a json representation of a framework object
    :return:
    '''

    global session, baseurl, player_id

    test_player = Player(api_version_player)
    test_player.find_player_by_id(session, baseurl=baseurl, player_id=player_id)
    assert test_player.validate_api_field(key_value_pair), 'Did not find {} in player object'.format(key_value_pair)


def test_player_field_keys():
    global session, baseurl, player_id, player_name, player_description, api_version_player

    key_value_pairs_to_check = [
        {"id": player_id},
        {"name": player_name},
        {"description": player_description},
        {"uuid": None},
        {"previewPlayer": False},
        {"enabled": True},
        {"type": "SCALA"},
        {"distributionServer": None},
        {"playerDisplays": None},
        {"requestLogs": False},
        {"downloadThreads": 1},
        {"unusedFilesCache": 24},
        {"planDeliveryMethod": "CONTENT_MANAGER_DIRECT"},
        {"pollingInterval": 1},
        {"pollingUnit": "MINUTES"},
        {"logLevel": "normal"},
        {"active": "UNKNOWN"},
        {"lastModified": None}]

    for key_value_pair in key_value_pairs_to_check:
        logging.info('Beginning test of {} key value pair for Channel Object'.format(key_value_pair))
        yield player_field_check, key_value_pair