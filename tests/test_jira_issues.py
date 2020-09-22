__author__ = 'richardkaye'

import logging
import logging.config
import configparser
from framework.constants import CONFIG_FILE_PATH, LOG_FILE_PATH, metadata_data_type
from framework.authentication_rest import login, logout, get_auth_token
from framework.http_rest import *
from framework.fileupload_rest import File_upload
from framework.templates_rest import Templates
from framework.media_rest import Media
from framework.channel_rest import Channels
from framework.frameset_template_rest import Frameset_template
from framework.player_rest import Player
from framework.playlist_rest import Playlist
from framework.message_rest import Message
from framework.media_metadata_rest import Media_meta_data
from framework.users_rest import Users
from framework.player_metadata_rest import Player_meta_data
from framework.roles_rest import Roles
from framework.authentication_api_rest import Auth_api
from framework.category_rest import Category
from framework.distributions_rest import Distribution
from framework.heartbeats_rest import Heartbeats
from framework.hosted_networks_rest import Hosted_Networks
from framework.languages_rest import Languages
from framework.misc_rest import Misc
from framework.networks_rest import Network
from framework.player_health_rest import Player_Health
from framework.license_rest import License


import inspect
import requests
import datetime
from nose.tools import nottest

# import time

config = configparser.ConfigParser()
config.read(CONFIG_FILE_PATH)
baseurl = config['login']['baseurl']
logging.config.fileConfig(LOG_FILE_PATH)
logging.debug('Logging config file path is: {}'.format(CONFIG_FILE_PATH))
session = requests.Session()
namespace = config['test']['namespace']
try:
    media_timeout = int(config['test']['media_upload_timeout'])
except ValueError:
    media_timeout = 0

api_version = config['api_info']['api_version']
api_version_templates = config['api_info']['api_version_templates']
api_version_fileupload = config['api_info']['api_version_fileupload']
api_version_media = config['api_info']['api_version_media']
api_version_messages = config['api_info']['api_version_messages']
api_version_channels = config['api_info']['api_version_channels']
api_version_framesets = config['api_info']['api_version_framesets']
api_version_player = config['api_info']['api_version_player']
api_version_media_metadata = config['api_info']['api_version_media_metadata']
api_version_player_metadata = config['api_info']['api_version_player_metadata']
api_version_playlist = config['api_info']['api_version_playlist']
api_version_roles = config['api_info']['api_version_roles']
api_version_users = config['api_info']['api_version_users']
api_version_authentication = config['api_info']['api_version_authentication']
api_version_category = config['api_info']['api_version_category']
api_version_distribution = config['api_info']['api_version_distribution']
api_version_heartbeats = config['api_info']['api_version_heartbeats']
api_version_hosted_networks = config['api_info']['api_version_hosted_networks']
api_version_languages = config['api_info']['api_version_languages']
api_version_license = config['api_info']['api_version_license']
api_version_miscellaneous = config['api_info']['api_version_miscellaneous']
api_version_network = config['api_info']['api_version_network']
api_version_player_health = config['api_info']['api_version_player_health']

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


'''
This module is for testing Jira issues and making sure that if they return, we have coverage that catches them cold.

Unlike other tests, each individual set of tests for a specific jira issue is wrapped in a test class named
for the issue ID in Jira of that issue.
'''


class test_jira_cm_8456_media():
    '''
    Tests GET /api/rest/media with filters on metadata.  Test one filter of each type:
    boolean, int_any, int_picklist, string_any, and string_picklist

    Create all of the media metadata types indicated, upload 3 media.  Set two of the media to have
    the correct metadata for the filter, the GET /api/rest/media on that filter
    '''

    def setup(self):
        # Begin by initiating a new login session for this test case.
        logging.info('Beginning test setup')
        self.baseurl = config['login']['baseurl']
        self.username = config['login']['username']
        self.password = config['login']['password']
        logging.debug('Read login info from config file and ready to begin.')
        logging.info('Initializing session for test module setup.')

        # INITIALIZE SESSION OBJECT
        self.test_session = login(self.username, self.password, self.baseurl)

        # Step 1: add media metadata to the CM for this test
        mmd = Media_meta_data(api_version_media_metadata)

        # Create Boolean Metadata
        mm_name1 = namespace + '_boolean_metadata_cm8456'
        mmd.create_metadata(self.test_session,
                            baseurl=self.baseurl,
                            name=mm_name1,
                            data_type=metadata_data_type.BOOLEAN,
                            value_type=metadata_value_type.ANY)
        self.boolean_metadata_id = mmd.get_id()
        logging.info('ID of boolean metadata is: {}'.format(self.boolean_metadata_id))

        # Create string_any Metadata
        self.mm_name2 = namespace + '_string_any_metadata_cm8456'
        mmd.create_metadata(self.test_session,
                            baseurl=self.baseurl,
                            name=self.mm_name2,
                            data_type=metadata_data_type.STRING,
                            value_type=metadata_value_type.ANY)
        self.string_any_metadata_id = mmd.get_id()
        logging.info('ID of string any metadata is: {}'.format(self.string_any_metadata_id))

        # Create String Picklist Metadata
        self.mm_name3 = namespace + '_string_picklist_metadata_cm8456'
        mmd.create_metadata(self.test_session,
                            baseurl=self.baseurl,
                            name=self.mm_name3,
                            data_type=metadata_data_type.STRING,
                            value_type=metadata_value_type.PICKLIST)
        self.string_picklist_id = mmd.get_id()
        logging.info('ID of string picklist metadata is: {}'.format(self.string_picklist_id))

        # Populate String Picklist Metadata

        list_of_string_picklist_items = ['aardvark', 'bird', 'cat', 'dog', 'elephant', 'fish']
        mmd.add_picklist_values_to_media_metadata(session=self.test_session,
                                                  baseurl=self.baseurl,
                                                  media_metadata_id=self.string_picklist_id,
                                                  list_of_predefined_values=list_of_string_picklist_items)


        # Create int Any metadata
        self.mm_name4 = namespace + '_int_any_metadata_cm8456'
        mmd.create_metadata(self.test_session,
                            baseurl=self.baseurl,
                            name=self.mm_name4,
                            data_type=metadata_data_type.INTEGER,
                            value_type=metadata_value_type.ANY)
        self.int_any_id = mmd.get_id()
        logging.info('ID of int any metadata is: {}'.format(self.int_any_id))

        # Create int Picklist metadata
        self.mm_name5 = namespace + '_int_picklist_metadata_cm8456'
        mmd.create_metadata(self.test_session,
                            baseurl=self.baseurl,
                            name=self.mm_name5,
                            data_type=metadata_data_type.INTEGER,
                            value_type=metadata_value_type.PICKLIST)
        self.int_picklist_id = mmd.get_id()
        logging.info('ID of int picklist metadata is: {}'.format(self.int_picklist_id))

        # Populate Int Picklist Metadata
        int_picklist_items = [2, 3, 5, 7, 11, 13]
        mmd.add_picklist_values_to_media_metadata(session=self.test_session,
                                                  baseurl=self.baseurl,
                                                  media_metadata_id=self.int_picklist_id,
                                                  list_of_predefined_values=int_picklist_items)

        # Add Media Items in order to run the test
        # Upload 3 media items
        self.media_id_list = []
        path = namespace + "cm_8456"
        media_object = Media(api_version_media)
        for media_item in [config['media_items']['mediafile_1'], config['media_items']['mediafile_2'],
                           config['media_items']['mediafile_3']]:
            # Create a media item for use in this test suite
            file_up = File_upload(api_version_fileupload)

            # Initiate Upload of media item
            file_up.initiate_upload(session=self.test_session, baseurl=self.baseurl, local_file_name=media_item,
                                    file_upload_path=path)

            uuid = file_up.get_response_key('uuid')
            media_id = file_up.get_response_key('mediaId')
            self.media_id_list.append(media_id)

            # Upload file part
            file_up.upload_file_part(session=self.test_session, baseurl=self.baseurl, local_file_name=media_item,
                                     local_file_path=config['path']['media'], uuid=uuid)

            # Commit Upload
            file_up.upload_finished(session=self.test_session, baseurl=self.baseurl, uuid=uuid)

            # Wait for thumbnail to become available
            if media_object.wait_for_media_upload(session=self.test_session,
                                                  baseurl=self.baseurl,
                                                  max_wait_seconds=media_timeout,
                                                  media_id=media_id):
                logging.debug('Thumbnail complete for media id = {}'.format(media_id))
            else:
                logging.error('Media with id = {} did not have thumbnail complete after {} seconds.'.format(media_id,
                                                                                                            media_timeout))

        logging.debug('media_id_list is = {}'.format(self.media_id_list))


    def teardown(self):

        media_object = Media(api_version_media)
        for identifier in self.media_id_list:
            media_object.delete_media_by_id(session=self.test_session, baseurl=self.baseurl, id=identifier)

        media_metadata_object = Media_meta_data(api_version_media_metadata)

        for metadata_id in [self.int_any_id, self.int_picklist_id, self.boolean_metadata_id,
                            self.string_any_metadata_id, self.string_picklist_id]:
            media_metadata_object.delete_metadata_by_id(session=self.test_session,
                                                        baseurl=self.baseurl,
                                                        metadata_id=metadata_id)

        logout(self.test_session, self.baseurl)

    # def modify_media_metadata_assignment(self, media_id, metadata_id, metadata_value):
    #     # Assign a value of True for media metadata boolean on media 1
    #     metadata_object = Media_meta_data(api_version_media_metadata)
    #     media_object = Media(api_version_media)
    #     assert metadata_object.find_metadata_by_id(session = self.test_session,
    #                                         baseurl = self.baseurl,
    #                                         metadata_id = metadata_id), 'Could not find boolean metadata with ID =' + str(metadata_id)
    #     # Ugly bit where I pull down the metadata object from the CM and modify it so it can be
    #     # Changed on the media object - the field 'order' must be removed
    #     metadata_json = metadata_object.get_last_response().json()
    #     metadata_json.pop('order')
    #
    #     # If the Metadata is a PICKLIST, we need to specify the value field as the picklist ID, not as the actual value
    #     value_placeholder = metadata_value # The default case for when we have an ANY type metadata
    #
    #     if metadata_json['valueType'] == 'PICKLIST':
    #         logging.debug('Determination of type of metadata: {}'.format(metadata_json['valueType']))
    #         for picklist_item in metadata_json['predefinedValues']:
    #             logging.debug('Determination of picklist value is: {}, id: {}, metadata value: {}'.format(picklist_item['value'],picklist_item['id'],metadata_value))
    #             if picklist_item['value']==str(metadata_value):
    #                 logging.debug('Determination of picklist value is {}.  Metadata value is {}.  Picklist ID is {}'.format(picklist_item['value'],metadata_value,picklist_item['id']))
    #                 value_placeholder = picklist_item['id'] # Remap the value to the ID in a PICKLIST
    #
    #     changed_metadata_definition = {'metadataValue':[{'value':value_placeholder,'metadata':metadata_json}]}
    #     logging.debug('Determined {}'.format(json.dumps(changed_metadata_definition)))
    #
    #     assert media_object.update_single_media(session = self.test_session,
    #                                      baseurl = self.baseurl,
    #                                      media_id = media_id,
    #                                      field_change_dict = changed_metadata_definition), 'Failed to update the media with the new metadata value: {}'.format(media_object.get_last_response().text)

    def example_media_set(self):
        # Add the boolean metadata to a single media item created in setup
        media_object = Media(api_version_media)

        media_object.modify_media_metadata_assignment(session=self.test_session,
                                                      baseurl=self.baseurl,
                                                      media_id=self.media_id_list[2],
                                                      metadata_id=self.boolean_metadata_id,
                                                      metadata_value=True,
                                                      api_version_media_metadata=api_version_media_metadata)
        media_object.modify_media_metadata_assignment(session=self.test_session,
                                                      baseurl=self.baseurl,
                                                      media_id=self.media_id_list[2],
                                                      metadata_id=self.int_any_id,
                                                      metadata_value=4444,
                                                      api_version_media_metadata=api_version_media_metadata)

        media_object.modify_media_metadata_assignment(session=self.test_session,
                                                      baseurl=self.baseurl,
                                                      media_id=self.media_id_list[2],
                                                      metadata_id=self.int_picklist_id,
                                                      metadata_value=7,
                                                      api_version_media_metadata=api_version_media_metadata)

        media_object.modify_media_metadata_assignment(session=self.test_session,
                                                      baseurl=self.baseurl,
                                                      media_id=self.media_id_list[2],
                                                      metadata_id=self.string_picklist_id,
                                                      metadata_value='dog',
                                                      api_version_media_metadata=api_version_media_metadata)

    def test_bool_metadata_filter(self):
        '''
        Test filtering on a boolean media Metdata filter
        :return:
        '''
        # Set boolean metadata on two of the media objects to True
        media_object = Media(api_version_media)
        media_object.modify_media_metadata_assignment(session=self.test_session,
                                                      baseurl=self.baseurl,
                                                      media_id=self.media_id_list[1],
                                                      metadata_id=self.boolean_metadata_id,
                                                      metadata_value=True,
                                                      api_version_media_metadata=api_version_media_metadata)
        media_object.modify_media_metadata_assignment(session=self.test_session,
                                                      baseurl=self.baseurl,
                                                      media_id=self.media_id_list[2],
                                                      metadata_id=self.boolean_metadata_id,
                                                      metadata_value=True,
                                                      api_version_media_metadata=api_version_media_metadata)

        boolean_filter = "{'metadata': {'metaValues':[{'id' :" + str(
            self.boolean_metadata_id) + " , 'values': [ 'true' ] }]}}"
        assert media_object.list_media(session=self.test_session,
                                       baseurl=self.baseurl,
                                       filters=boolean_filter,
        )
        response_id_list = [response_item['id'] for response_item in media_object.last_response.json()['list']]
        logging.debug('Found the following media IDs in filtered response: {}'.format(response_id_list))

        assert self.media_id_list[1] in response_id_list, 'Could not find first media item in filtered response'
        assert self.media_id_list[2] in response_id_list, 'Could not find second media item in filtered response'
        assert len(media_object.last_response.json()['list']) == 2, 'Expected 2 objects in filtered list, got ' + str(
            len(media_object.last_response.json()['list']))

    def test_int_picklist_filter(self):
        '''
        Test filtering on an int picklist Metadata filter
        :return:
        '''
        # Set int picklist metadata on two of the media objects to 13
        media_object = Media(api_version_media)
        media_metadata_object = Media_meta_data(api_version_media_metadata)
        media_object.modify_media_metadata_assignment(session=self.test_session,
                                                      baseurl=self.baseurl,
                                                      media_id=self.media_id_list[1],
                                                      metadata_id=self.int_picklist_id,
                                                      metadata_value=13,
                                                      api_version_media_metadata=api_version_media_metadata)
        media_object.modify_media_metadata_assignment(session=self.test_session,
                                                      baseurl=self.baseurl,
                                                      media_id=self.media_id_list[2],
                                                      metadata_id=self.int_picklist_id,
                                                      metadata_value=13,
                                                      api_version_media_metadata=api_version_media_metadata)
        picklist_value = 13
        picklist_item_id = media_metadata_object.get_picklist_item_id(session=self.test_session,
                                                                      baseurl=self.baseurl,
                                                                      metadata_id=self.int_picklist_id,
                                                                      picklist_value=picklist_value)
        logging.debug('Picklist value {} has a picklist value of {}'.format(picklist_value, picklist_item_id))
        int_picklist_filter = "{'metadata': {'metaValues':[{'id' :" + str(
            self.int_picklist_id) + " , 'picklistId': " + str(picklist_item_id) + "  }]}}"
        assert media_object.list_media(session=self.test_session,
                                       baseurl=self.baseurl,
                                       filters=int_picklist_filter,
        )
        response_id_list = [response_item['id'] for response_item in media_object.last_response.json()['list']]

        assert self.media_id_list[1] in response_id_list, 'Could not find first media item in filtered response'
        assert self.media_id_list[2] in response_id_list, 'Could not find second media item in filtered response'
        assert len(media_object.last_response.json()['list']) == 2, 'Expected 2 objects in filtered list, got ' + str(
            len(media_object.last_response.json()['list']))

    def test_int_any_filter(self):
        '''
        Test filtering on int any filter
        :return:
        '''
        media_object = Media(api_version_media)

        media_object.modify_media_metadata_assignment(session=self.test_session,
                                                      baseurl=self.baseurl,
                                                      media_id=self.media_id_list[1],
                                                      metadata_id=self.int_any_id,
                                                      metadata_value=20701,
                                                      api_version_media_metadata=api_version_media_metadata)
        media_object.modify_media_metadata_assignment(session=self.test_session,
                                                      baseurl=self.baseurl,
                                                      media_id=self.media_id_list[2],
                                                      metadata_id=self.int_any_id,
                                                      metadata_value=20701,
                                                      api_version_media_metadata=api_version_media_metadata)

        int_any_filter = "{'metadata': {'metaValues':[{'id' :" + str(self.int_any_id) + " , 'values': [ '20701' ] }]}}"
        assert media_object.list_media(session=self.test_session,
                                       baseurl=self.baseurl,
                                       filters=int_any_filter,
        )
        response_id_list = [response_item['id'] for response_item in media_object.last_response.json()['list']]

        assert self.media_id_list[1] in response_id_list, 'Could not find first media item in filtered response'
        assert self.media_id_list[2] in response_id_list, 'Could not find second media item in filtered response'
        assert len(media_object.last_response.json()['list']) == 2, 'Expected 2 objects in filtered list, got ' + str(
            len(media_object.last_response.json()['list']))

    def test_string_any_filter(self):
        '''
        Test filtering on string_any metadata
        :return:
        '''
        media_object = Media(api_version_media)

        media_object.modify_media_metadata_assignment(session=self.test_session,
                                                      baseurl=self.baseurl,
                                                      media_id=self.media_id_list[1],
                                                      metadata_id=self.string_any_metadata_id,
                                                      metadata_value="bongo bongo bongo",
                                                      api_version_media_metadata=api_version_media_metadata)
        media_object.modify_media_metadata_assignment(session=self.test_session,
                                                      baseurl=self.baseurl,
                                                      media_id=self.media_id_list[2],
                                                      metadata_id=self.string_any_metadata_id,
                                                      metadata_value='bongo bongo bongo',
                                                      api_version_media_metadata=api_version_media_metadata)

        string_any_filter = "{'metadata': {'metaValues':[{'id' :" + str(
            self.string_any_metadata_id) + " , 'values': [ 'bongo bongo bongo' ] }]}}"
        assert media_object.list_media(session=self.test_session,
                                       baseurl=self.baseurl,
                                       filters=string_any_filter,
        )
        response_id_list = [response_item['id'] for response_item in media_object.last_response.json()['list']]

        assert self.media_id_list[1] in response_id_list, 'Could not find first media item in filtered response'
        assert self.media_id_list[2] in response_id_list, 'Could not find second media item in filtered response'
        assert len(media_object.last_response.json()['list']) == 2, 'Expected 2 objects in filtered list, got ' + str(
            len(media_object.last_response.json()['list']))

    def test_string_picklist_filter(self):
        '''
        Test filtering on an string picklist Metadata filter
        :return:
        '''
        # Set int picklist metadata on two of the media objects to 13
        media_object = Media(api_version_media)
        media_metadata_object = Media_meta_data(api_version_media_metadata)
        media_object.modify_media_metadata_assignment(session=self.test_session,
                                                      baseurl=self.baseurl,
                                                      media_id=self.media_id_list[1],
                                                      metadata_id=self.string_picklist_id,
                                                      metadata_value='cat',
                                                      api_version_media_metadata=api_version_media_metadata)
        media_object.modify_media_metadata_assignment(session=self.test_session,
                                                      baseurl=self.baseurl,
                                                      media_id=self.media_id_list[2],
                                                      metadata_id=self.string_picklist_id,
                                                      metadata_value='cat',
                                                      api_version_media_metadata=api_version_media_metadata)
        picklist_value = 'cat'
        picklist_item_id = media_metadata_object.get_picklist_item_id(session=self.test_session,
                                                                      baseurl=self.baseurl,
                                                                      metadata_id=self.string_picklist_id,
                                                                      picklist_value=picklist_value)
        logging.debug('Picklist value {} has a picklist value of {}'.format(picklist_value, picklist_item_id))
        int_picklist_filter = "{'metadata': {'metaValues':[{'id' :" + str(
            self.string_picklist_id) + " , 'picklistId': " + str(picklist_item_id) + "  }]}}"
        assert media_object.list_media(session=self.test_session,
                                       baseurl=self.baseurl,
                                       filters=int_picklist_filter,
        )
        response_id_list = [response_item['id'] for response_item in media_object.last_response.json()['list']]

        assert self.media_id_list[1] in response_id_list, 'Could not find first media item in filtered response'
        assert self.media_id_list[2] in response_id_list, 'Could not find second media item in filtered response'
        assert len(media_object.last_response.json()['list']) == 2, 'Expected 2 objects in filtered list, got ' + str(
            len(media_object.last_response.json()['list']))


class test_jira_cm_8456_player():
    '''
    Tests GET /api/rest/player with filters on metadata.  Test one filter of each type:
    boolean, int_any, int_picklist, string_any, and string_picklist

    Create all of the media metadata types indicated, upload 3 media.  Set two of the media to have
    the correct metadata for the filter, the GET /api/rest/media on that filter
    '''

    def setup(self):
        # Begin by initiating a new login session for this test case.
        logging.info('Beginning test setup')
        self.baseurl = config['login']['baseurl']
        self.username = config['login']['username']
        self.password = config['login']['password']
        logging.debug('Read login info from config file and ready to begin.')
        logging.info('Initializing session for test module setup.')

        # INITIALIZE SESSION OBJECT
        self.test_session = login(self.username, self.password, self.baseurl)

        # Step 1: add media metadata to the CM for this test
        pmd = Player_meta_data(api_version_player_metadata)

        # Create Boolean Metadata
        mm_name1 = namespace + '_boolean_metadata_cm8456'
        pmd.create_metadata(self.test_session,
                            baseurl=self.baseurl,
                            name=mm_name1,
                            data_type=metadata_data_type.BOOLEAN,
                            value_type=metadata_value_type.ANY)
        self.boolean_metadata_id = pmd.get_id()
        logging.info('ID of boolean metadata is: {}'.format(self.boolean_metadata_id))

        # Create string_any Metadata
        self.mm_name2 = namespace + '_string_any_metadata_cm8456'
        pmd.create_metadata(self.test_session,
                            baseurl=self.baseurl,
                            name=self.mm_name2,
                            data_type=metadata_data_type.STRING,
                            value_type=metadata_value_type.ANY)
        self.string_any_metadata_id = pmd.get_id()
        logging.info('ID of string any metadata is: {}'.format(self.string_any_metadata_id))

        # Create String Picklist Metadata
        self.mm_name3 = namespace + '_string_picklist_metadata_cm8456'
        pmd.create_metadata(self.test_session,
                            baseurl=self.baseurl,
                            name=self.mm_name3,
                            data_type=metadata_data_type.STRING,
                            value_type=metadata_value_type.PICKLIST)
        self.string_picklist_id = pmd.get_id()
        logging.info('ID of string picklist metadata is: {}'.format(self.string_picklist_id))

        # Populate String Picklist Metadata

        list_of_string_picklist_items = ['aardvark', 'bird', 'cat', 'dog', 'elephant', 'fish']
        pmd.add_picklist_values_to_player_metadata(session=self.test_session,
                                                   baseurl=self.baseurl,
                                                   metadata_id=self.string_picklist_id,
                                                   list_of_predefined_values=list_of_string_picklist_items)


        # Create int Any metadata
        self.mm_name4 = namespace + '_int_any_metadata_cm8456'
        pmd.create_metadata(self.test_session,
                            baseurl=self.baseurl,
                            name=self.mm_name4,
                            data_type=metadata_data_type.INTEGER,
                            value_type=metadata_value_type.ANY)
        self.int_any_id = pmd.get_id()
        logging.info('ID of int any metadata is: {}'.format(self.int_any_id))

        # Create int Picklist metadata
        self.mm_name5 = namespace + '_int_picklist_metadata_cm8456'
        pmd.create_metadata(self.test_session,
                            baseurl=self.baseurl,
                            name=self.mm_name5,
                            data_type=metadata_data_type.INTEGER,
                            value_type=metadata_value_type.PICKLIST)
        self.int_picklist_id = pmd.get_id()
        logging.info('ID of int picklist metadata is: {}'.format(self.int_picklist_id))

        # Populate Int Picklist Metadata
        int_picklist_items = [2, 3, 5, 7, 11, 13]
        pmd.add_picklist_values_to_player_metadata(session=self.test_session,
                                                   baseurl=self.baseurl,
                                                   metadata_id=self.int_picklist_id,
                                                   list_of_predefined_values=int_picklist_items)

        # Add Player Items in order to run the test
        #create 10 players

        player_object = Player(api_version_player)

        player_object.create_multiple_players(session=self.test_session,
                                              baseurl=self.baseurl,
                                              name="Player_#_8456_" + namespace,
                                              start_at_player_number=1,
                                              number_of_players=5)

        self.player_id_list = player_object.get_response_key('ids')

        path = namespace + "cm_8456"

        logging.debug('player_id_list is = {}'.format(self.player_id_list))

    def get_player_name(self, player_number):
        return "Player_" + str(player_number) + "_8456_" + namespace


    def teardown(self):
        player_object = Player(api_version_player)
        for player_id in self.player_id_list:
            player_object.delete_player_by_id(session=self.test_session,
                                              baseurl=self.baseurl,
                                              id=player_id)

        player_metadata_object = Player_meta_data(api_version_player_metadata)

        for metadata_id in [self.int_any_id, self.int_picklist_id, self.boolean_metadata_id,
                            self.string_any_metadata_id, self.string_picklist_id]:
            player_metadata_object.delete_metadata_by_id(session=self.test_session,
                                                         baseurl=self.baseurl,
                                                         metadata_id=metadata_id)

        logout(self.test_session, self.baseurl)

    def test_bool_metadata_filter(self):
        '''
        Test filtering on a boolean media Metdata filter
        :return:
        '''
        # Set boolean metadata on two of the media objects to True
        player_object = Player(api_version_player)
        player_object.modify_player_metadata_assignment(session=self.test_session,
                                                        baseurl=self.baseurl,
                                                        name=self.get_player_name(2),
                                                        player_id=self.player_id_list[1],
                                                        metadata_id=self.boolean_metadata_id,
                                                        metadata_value=True,
                                                        api_version_player_metadata=api_version_player_metadata)
        player_object.modify_player_metadata_assignment(session=self.test_session,
                                                        baseurl=self.baseurl,
                                                        name=self.get_player_name(3),
                                                        player_id=self.player_id_list[2],
                                                        metadata_id=self.boolean_metadata_id,
                                                        metadata_value=True,
                                                        api_version_player_metadata=api_version_player_metadata)

        boolean_filter = "{'metadata': {'metaValues':[{'id' :" + str(
            self.boolean_metadata_id) + " , 'values': [ 'true' ] }]}}"
        assert player_object.list_players(session=self.test_session,
                                          baseurl=self.baseurl,
                                          filters=boolean_filter,
        )
        response_id_list = [response_item['id'] for response_item in player_object.last_response.json()['list']]
        logging.debug('Found the following media IDs in filtered response: {}'.format(response_id_list))

        assert self.player_id_list[1] in response_id_list, 'Could not find first media item in filtered response'
        assert self.player_id_list[2] in response_id_list, 'Could not find second media item in filtered response'
        assert len(player_object.last_response.json()['list']) == 2, 'Expected 2 objects in filtered list, got ' + str(
            len(player_object.last_response.json()['list']))

    def test_int_picklist_filter(self):
        '''
        Test filtering on an int picklist Metadata filter
        :return:
        '''
        # Set int picklist metadata on two of the media objects to 13
        player_object = Player(api_version_player)
        player_metadata_object = Player_meta_data(api_version_player_metadata)
        player_object.modify_player_metadata_assignment(session=self.test_session,
                                                        baseurl=self.baseurl,
                                                        name=self.get_player_name(2),
                                                        player_id=self.player_id_list[1],
                                                        metadata_id=self.int_picklist_id,
                                                        metadata_value=13,
                                                        api_version_player_metadata=api_version_player_metadata)
        player_object.modify_player_metadata_assignment(session=self.test_session,
                                                        baseurl=self.baseurl,
                                                        name=self.get_player_name(3),
                                                        player_id=self.player_id_list[2],
                                                        metadata_id=self.int_picklist_id,
                                                        metadata_value=13,
                                                        api_version_player_metadata=api_version_player_metadata)
        picklist_value = 13
        picklist_item_id = player_metadata_object.get_picklist_item_id(session=self.test_session,
                                                                       baseurl=self.baseurl,
                                                                       metadata_id=self.int_picklist_id,
                                                                       picklist_value=picklist_value)
        logging.debug('Picklist value {} has a picklist value of {}'.format(picklist_value, picklist_item_id))
        int_picklist_filter = "{'metadata': {'metaValues':[{'id' :" + str(
            self.int_picklist_id) + " , 'picklistId': " + str(picklist_item_id) + "  }]}}"
        assert player_object.list_players(session=self.test_session,
                                          baseurl=self.baseurl,
                                          filters=int_picklist_filter,
        )
        response_id_list = [response_item['id'] for response_item in player_object.last_response.json()['list']]

        assert self.player_id_list[1] in response_id_list, 'Could not find first media item in filtered response'
        assert self.player_id_list[2] in response_id_list, 'Could not find second media item in filtered response'
        assert len(player_object.last_response.json()['list']) == 2, 'Expected 2 objects in filtered list, got ' + str(
            len(player_object.last_response.json()['list']))


    def test_int_any_filter(self):
        '''
        Test filtering on int any filter
        :return:
        '''
        player_object = Player(api_version_player)

        player_object.modify_player_metadata_assignment(session=self.test_session,
                                                        baseurl=self.baseurl,
                                                        name=self.get_player_name(2),
                                                        player_id=self.player_id_list[1],
                                                        metadata_id=self.int_any_id,
                                                        metadata_value=20701,
                                                        api_version_player_metadata=api_version_player_metadata)
        player_object.modify_player_metadata_assignment(session=self.test_session,
                                                        baseurl=self.baseurl,
                                                        name=self.get_player_name(3),
                                                        player_id=self.player_id_list[2],
                                                        metadata_id=self.int_any_id,
                                                        metadata_value=20701,
                                                        api_version_player_metadata=api_version_player_metadata)

        int_any_filter = "{'metadata': {'metaValues':[{'id' :" + str(self.int_any_id) + " , 'values': [ '20701' ] }]}}"
        assert player_object.list_players(session=self.test_session,
                                          baseurl=self.baseurl,
                                          filters=int_any_filter,
        )
        response_id_list = [response_item['id'] for response_item in player_object.last_response.json()['list']]

        assert self.player_id_list[1] in response_id_list, 'Could not find first media item in filtered response'
        assert self.player_id_list[2] in response_id_list, 'Could not find second media item in filtered response'
        assert len(player_object.last_response.json()['list']) == 2, 'Expected 2 objects in filtered list, got ' + str(
            len(player_object.last_response.json()['list']))

    def test_string_any_filter(self):
        '''
        Test filtering on string_any metadata
        :return:
        '''
        player_object = Player(api_version_player)

        player_object.modify_player_metadata_assignment(session=self.test_session,
                                                        baseurl=self.baseurl,
                                                        name=self.get_player_name(2),
                                                        player_id=self.player_id_list[1],
                                                        metadata_id=self.string_any_metadata_id,
                                                        metadata_value="bongo bongo bongo",
                                                        api_version_player_metadata=api_version_player_metadata)
        player_object.modify_player_metadata_assignment(session=self.test_session,
                                                        baseurl=self.baseurl,
                                                        name=self.get_player_name(3),
                                                        player_id=self.player_id_list[2],
                                                        metadata_id=self.string_any_metadata_id,
                                                        metadata_value='bongo bongo bongo',
                                                        api_version_player_metadata=api_version_player_metadata)

        string_any_filter = "{'metadata': {'metaValues':[{'id' :" + str(
            self.string_any_metadata_id) + " , 'values': [ 'bongo bongo bongo' ] }]}}"
        assert player_object.list_players(session=self.test_session,
                                          baseurl=self.baseurl,
                                          filters=string_any_filter,
        )
        response_id_list = [response_item['id'] for response_item in player_object.last_response.json()['list']]

        assert self.player_id_list[1] in response_id_list, 'Could not find first media item in filtered response'
        assert self.player_id_list[2] in response_id_list, 'Could not find second media item in filtered response'
        assert len(player_object.last_response.json()['list']) == 2, 'Expected 2 objects in filtered list, got ' + str(
            len(player_object.last_response.json()['list']))

    def test_string_picklist_filter(self):
        '''
        Test filtering on an string picklist Metadata filter
        :return:
        '''
        # Set int picklist metadata on two of the media objects to 13
        player_object = Player(api_version_player)
        player_metadata_object = Player_meta_data(api_version_player_metadata)
        player_object.modify_player_metadata_assignment(session=self.test_session,
                                                        baseurl=self.baseurl,
                                                        name=self.get_player_name(2),
                                                        player_id=self.player_id_list[1],
                                                        metadata_id=self.string_picklist_id,
                                                        metadata_value='cat',
                                                        api_version_player_metadata=api_version_player_metadata)
        player_object.modify_player_metadata_assignment(session=self.test_session,
                                                        baseurl=self.baseurl,
                                                        name=self.get_player_name(3),
                                                        player_id=self.player_id_list[2],
                                                        metadata_id=self.string_picklist_id,
                                                        metadata_value='cat',
                                                        api_version_player_metadata=api_version_player_metadata)
        picklist_value = 'cat'
        picklist_item_id = player_metadata_object.get_picklist_item_id(session=self.test_session,
                                                                       baseurl=self.baseurl,
                                                                       metadata_id=self.string_picklist_id,
                                                                       picklist_value=picklist_value)
        logging.debug('Picklist value {} has a picklist value of {}'.format(picklist_value, picklist_item_id))
        int_picklist_filter = "{'metadata': {'metaValues':[{'id' :" + str(
            self.string_picklist_id) + " , 'picklistId': " + str(picklist_item_id) + "  }]}}"
        assert player_object.list_players(session=self.test_session,
                                          baseurl=self.baseurl,
                                          filters=int_picklist_filter,
        )
        response_id_list = [response_item['id'] for response_item in player_object.last_response.json()['list']]

        assert self.player_id_list[1] in response_id_list, 'Could not find first media item in filtered response'
        assert self.player_id_list[2] in response_id_list, 'Could not find second media item in filtered response'
        assert len(player_object.last_response.json()['list']) == 2, 'Expected 2 objects in filtered list, got ' + str(
            len(player_object.last_response.json()['list']))


class test_cm_8601():
    '''
    Test class to validate CM-8601.  This case was solved by creating a new API call for the channels resource.
    GET /api/rest/channels/{id}/frames/{frameId}/timeslots

    This test is an endpoint test of that new API call.

    The CM UI should be using the new API instead of the old one now - which was confirmed through manual testing and
    code inspection
    '''

    def setup(self):
        # Begin by initiating a new login session for this test case.
        logging.info('Beginning test setup')
        self.baseurl = config['login']['baseurl']
        self.username = config['login']['username']
        self.password = config['login']['password']
        logging.debug('Read login info from config file and ready to begin.')
        logging.info('Initializing session for test module setup.')

        # INITIALIZE SESSION OBJECT
        self.test_session = login(self.username, self.password, self.baseurl)

        # Create a channel and assign it a frameset
        frameset_object = Frameset_template(api_version_framesets)
        channel_object = Channels(api_version_channels)

        frameset_object.list_all_available_frameset_templates(session=self.test_session,
                                                              baseurl=self.baseurl,
                                                              limit=100,
                                                              offset=0,
                                                              sort='name',
                                                              fields='id,name')
        self.frameset_id_list = [single_frameset['id'] for single_frameset in frameset_object.get_response_key('list')]

        self.channel_name = namespace + 'Channel CM-8601'
        channel_object.create_channel(session=self.test_session,
                                      baseurl=self.baseurl,
                                      name=self.channel_name,
                                      frameset_id=self.frameset_id_list[0],
                                      description='Channel for testing CM 8601' + namespace
        )
        self.channel_id = channel_object.get_id()
        self.channel_frame_id = channel_object.get_response_key('frameset')['frames'][0]['id']
        logging.debug(
            'The first frame for channel with ID = {} has id = {}'.format(self.channel_id, self.channel_frame_id))

        # Create a playlist to schedule with this channel
        playlist_object = Playlist(api_version_playlist)

        self.playlist_name = namespace + " CM-8601"
        self.playlist_description = namespace + " The playlist used to test CM-8601"

        playlist_object.create_playlist(session=self.test_session,
                                        baseurl=self.baseurl,
                                        name=self.playlist_name,
                                        description=self.playlist_description)
        self.playlist_id = playlist_object.get_id()

        # Add a scheduled timeslot to the channel and playlist
        channel_object.update_schedules(session=self.test_session,
                                        baseurl=self.baseurl,
                                        channel_id=self.channel_id,
                                        playlist_id=self.playlist_id,
                                        channel_frameset_id=self.channel_frame_id,
                                        startDate="2013-10-01",
                                        startTime="05:00:00")


    def teardown(self):
        channel_object = Channels(api_version_channels)
        playlist_object = Playlist(api_version_playlist)

        channel_object.delete_channel_by_id(session=self.test_session,
                                            baseurl=self.baseurl,
                                            channel_id=self.channel_id)

        playlist_object.delete_playlist_by_id(session=self.test_session,
                                              baseurl=self.baseurl,
                                              playlist_id=self.playlist_id)

        logout(self.test_session, self.baseurl)

    def test_channel_api_call(self):
        channel_object = Channels(api_version_channels)

        assert channel_object.find_timeslots_for_given_input_criteria(session=self.test_session,
                                                                      baseurl=self.baseurl,
                                                                      channel_id=self.channel_id,
                                                                      frame_id=self.channel_frame_id,
                                                                      fromDate="2013-09-01",
                                                                      toDate="2014-10-01")

        assert len(channel_object.last_response.json()['timeslots']) == 1, 'Found incorrect number of timeslots!'


@nottest
class test_jira_9121():
    '''
    This test is to validate jira CM-9121.

    In the setup for this test the following actions take place:
            1)  A channel is created and frameset assigned
            2)  A Playlist is created

    The result of this test is found by looking in the CM log to
    and determining if there are any exceptions.
    This test is an endpoint test of that new API call.

    The CM UI should be using the new API instead of the old one now - which was confirmed through manual testing and
    code inspection
    '''

    def setup(self):
        # Begin by initiating a new login session for this test case.
        logging.info('Beginning test setup')
        self.baseurl = config['login']['baseurl']
        self.username = config['login']['username']
        self.password = config['login']['password']
        logging.debug('Read login info from config file and ready to begin.')
        logging.info('Initializing session for test module setup.')

        # INITIALIZE SESSION OBJECT
        self.test_session = login(self.username, self.password, self.baseurl)

        # Create a channel and assign it a frameset
        frameset_object = Frameset_template(api_version_framesets)
        channel_object = Channels(api_version_channels)

        frameset_object.list_all_available_frameset_templates(session=self.test_session,
                                                              baseurl=self.baseurl,
                                                              limit=100,
                                                              offset=0,
                                                              sort='name',
                                                              fields='id,name')
        self.frameset_id_list = [single_frameset['id'] for single_frameset in frameset_object.get_response_key('list')]

        self.channel_name = namespace + 'Channel CM-9121'
        channel_object.create_channel(session=self.test_session,
                                      baseurl=self.baseurl,
                                      name=self.channel_name,
                                      frameset_id=self.frameset_id_list[0],
                                      description='Channel for testing CM 8601' + namespace
        )
        self.channel_id = channel_object.get_id()
        self.channel_frame_id = channel_object.get_response_key('frameset')['frames'][0]['id']
        logging.debug(
            'The first frame for channel with ID = {} has id = {}'.format(self.channel_id, self.channel_frame_id))

        # Create a playlist to schedule with this channel
        playlist_object = Playlist(api_version_playlist)

        self.playlist_name = namespace + " CM-9121"
        self.playlist_description = namespace + " The playlist used to test CM-9121"

        playlist_object.create_playlist(session=self.test_session,
                                        baseurl=self.baseurl,
                                        name=self.playlist_name,
                                        description=self.playlist_description)
        self.playlist_id = playlist_object.get_id()

    def test_9121(self):
        '''
        Add n timeslots to the channel.  Afterwards, check the CM logs to see if the exception from the bug occurs.

        Start by adding a 5 minute event at 12:00 noon.  Advance by 5 minute intervals adding timeslots as you go
        :return:
        '''

        time_delta = datetime.timedelta(minutes=5)
        start_time = datetime.datetime(100, 1, 1, 1, 0, 0)
        end_time = start_time + time_delta
        channel_object = Channels(api_version_channels)

        for added_timeslot in range(19):
            result = channel_object.update_schedules(session=self.test_session,
                                                     baseurl=self.baseurl,
                                                     channel_id=self.channel_id,
                                                     playlist_id=self.playlist_id,
                                                     channel_frameset_id=self.channel_frame_id,
                                                     startDate="2015-08-18",
                                                     startTime=str(start_time.time()),
                                                     endTime=str(end_time.time()),
                                                     color=None)
            logging.debug('Result of PUT call for CM-9121 is {}'.format(result))
            assert result
            start_time = start_time + time_delta + time_delta
            end_time = end_time + time_delta + time_delta
            #logging.debug("Adding timeslot {}. Status code from last add was: {}".format(added_timeslot, channel_object.last_response.status_code))

    def teardown(self):
        # channel_object = Channels(api_version_channels)
        # playlist_object = Playlist(api_version_playlist)
        #
        # channel_object.delete_channel_by_id(session=self.test_session,
        #                                     baseurl=self.baseurl,
        #                                     channel_id=self.channel_id)
        #
        # playlist_object.delete_playlist_by_id(session=self.test_session,
        #                                       baseurl=self.baseurl,
        #                                       playlist_id=self.playlist_id)

        logout(self.test_session, self.baseurl)

@nottest
class test_jira_sup_2065():
    '''
    This test is to validate jira SUP-2065.

    In the setup for this test the following actions take place:
            1)  A channel is created and frameset assigned
            2)  A Playlist is created

    The result of this test is found by looking in the CM log to
    and determining if there are any exceptions.

    This test validates the case when there is a weekly repitition, with no days specified in the schedule DTO



    '''

    def setup(self):
        # Begin by initiating a new login session for this test case.
        logging.info('Beginning test setup')
        self.baseurl = config['login']['baseurl']
        self.username = config['login']['username']
        self.password = config['login']['password']
        logging.debug('Read login info from config file and ready to begin.')
        logging.info('Initializing session for test module setup.')

        # INITIALIZE SESSION OBJECT
        self.test_session = login(self.username, self.password, self.baseurl)

        # Create a channel and assign it a frameset
        frameset_object = Frameset_template(api_version_framesets)
        channel_object = Channels(api_version_channels)

        frameset_object.list_all_available_frameset_templates(session=self.test_session,
                                                              baseurl=self.baseurl,
                                                              limit=100,
                                                              offset=0,
                                                              sort='name',
                                                              fields='id,name')
        self.frameset_id_list = [single_frameset['id'] for single_frameset in frameset_object.get_response_key('list')]

        self.channel_name = namespace + 'Channel CM-9121'
        channel_object.create_channel(session=self.test_session,
                                      baseurl=self.baseurl,
                                      name=self.channel_name,
                                      frameset_id=self.frameset_id_list[0],
                                      description='Channel for testing CM 8601' + namespace
        )
        self.channel_id = channel_object.get_id()
        self.channel_frame_id = channel_object.get_response_key('frameset')['frames'][0]['id']
        logging.debug(
            'The first frame for channel with ID = {} has id = {}'.format(self.channel_id, self.channel_frame_id))

        # Create a playlist to schedule with this channel
        playlist_object = Playlist(api_version_playlist)

        self.playlist_name = namespace + " CM-9121"
        self.playlist_description = namespace + " The playlist used to test CM-9121"

        playlist_object.create_playlist(session=self.test_session,
                                        baseurl=self.baseurl,
                                        name=self.playlist_name,
                                        description=self.playlist_description)
        self.playlist_id = playlist_object.get_id()

    def test_sup_2065(self):
        '''
        Add n timeslots to the channel.  Afterwards, check the CM logs to see if the exception from the bug occurs.

        Start by adding a 5 minute event at 12:00 noon.  Advance by 5 minute intervals adding timeslots as you go
        :return:
        '''

        time_delta = datetime.timedelta(minutes=5)
        start_time = datetime.datetime(100, 1, 1, 1, 0, 0)
        end_time = start_time + time_delta
        channel_object = Channels(api_version_channels)

        result = channel_object.update_schedules(session=self.test_session,
                                                 baseurl=self.baseurl,
                                                 channel_id=self.channel_id,
                                                 playlist_id=self.playlist_id,
                                                 channel_frameset_id=self.channel_frame_id,
                                                 startDate="2015-08-18",
                                                 startTime=str(start_time.time()),
                                                 endTime=str(end_time.time()),
                                                 weekdays=[],
                                                 color=None)

        assert result
        start_time = start_time + time_delta + time_delta
        end_time = end_time + time_delta + time_delta
        #logging.debug("Adding timeslot {}. Status code from last add was: {}".format(added_timeslot, channel_object.last_response.status_code))

    def teardown(self):
        # channel_object = Channels(api_version_channels)
        # playlist_object = Playlist(api_version_playlist)
        #
        # channel_object.delete_channel_by_id(session=self.test_session,
        #                                     baseurl=self.baseurl,
        #                                     channel_id=self.channel_id)
        #
        # playlist_object.delete_playlist_by_id(session=self.test_session,
        #                                       baseurl=self.baseurl,
        #                                       playlist_id=self.playlist_id)

        logout(self.test_session, self.baseurl)


class test_jira_cm_9164():
    '''
    A fleet of tests of the various problems detected during the investigation into jira CM-9164
    '''

    def setup(self):
        # Begin by initiating a new login session for this test case.
        logging.info('Beginning test setup')
        self.baseurl = config['login']['baseurl']
        self.username = config['login']['username']
        self.password = config['login']['password']
        logging.debug('Read login info from config file and ready to begin.')
        logging.info('Initializing session for test module setup.')

        self.test_session = login(self.username, self.password, self.baseurl)
        self.user_id_list = []


        # Determine ID of Administrator role
        role_object = Roles(api_version_roles)
        role_object.list_roles(self.test_session,
                               baseurl=self.baseurl,
                               limit=100,
                               offset=0,
                               fields='name,id')
        logging.debug("Response from list roles is: {}".format(role_object.last_response.text))
        for item in role_object.last_response.json()['list']:
            if item['name'] == 'Administrator':
                self.admin_role_id = item['id']

    def teardown(self):
        user_object = Users(api_version_users)
        for user_id in self.user_id_list:
            user_object.delete_user(self.test_session, self.baseurl, user_id=user_id)
        logout(self.test_session, self.baseurl)

    def test_add_user_delete_user(self):
        '''
        Add 100 users and delete them in rapid succession.  After adding each one, be sure to add them to
        the list of users to delete at the end of the session (in teardown) since they were not
        created in the setup segment
        :return:
        '''
        user_object = Users(api_version_users)
        n = 1000
        user_firstname = namespace + ' firstname'
        user_lastname = namespace + ' lastname'
        user_password = 'abcdabcd'
        user_email = 'abcd@efgh.com'
        user_name = user_firstname + " " + user_lastname
        user_username = "tst"
        user_role_list = [{'id': self.admin_role_id}]

        for user in range(n):
            current_username = user_username + str(user)
            assert user_object.create_user(session=self.test_session,
                                           baseurl=self.baseurl,
                                           emailAddress=user_email,
                                           firstname=user_firstname,
                                           lastname=user_lastname,
                                           password=user_password,
                                           name=user_name,
                                           username=current_username,
                                           role_list=user_role_list), 'Failed to add User'
            self.user_id_list.append(user_object.get_response_key('id'))

class test_jira_cm_5558():
    """
    Test to validate XSRF attack possible on CM - CM-5558
    This test will log into the CM and then create session objects that contain a valid token cookie,
    but no apiToken header.  It will then run a selection of POST, PUT and DELETE requests to validate that they
    fail.  This test will also validate that GET requests will pass under these circumstances
    """

    @classmethod
    def setup_class(cls):
        pass

    @classmethod
    def teardown_class(cls):
        pass

    def setup(self):
        # Login to perform teardown
        logging.info('Beginning test setup')
        self.baseurl = config['login']['baseurl']
        self.username = config['login']['username']
        self.password = config['login']['password']
        self.test_session_auth_object = Auth_api(api_version_authentication)
        self.setup_session_auth_object= Auth_api(api_version_authentication)
        logging.debug('Read login info from config file and ready to begin.')
        logging.info('Initializing session for test module setup.')

        self.test_session = self.test_session_auth_object.login(self.username, self.password, self.baseurl, token=False)
        self.setup_session = self.setup_session_auth_object.login(self.username, self.password, self.baseurl)

        # Create a player to be used in this test
        player_object = Player(api_version_player)
        player_object.create_player(session = self.setup_session,
                                    baseurl = self.baseurl,
                                    name = namespace + ' Player5558')
        self.player_id = player_object.get_id()
        self.player_uuid = player_object.get_response_key('uuid')


        # Define network ID for use in this test
        hosted_network_object = Hosted_Networks(api_version_hosted_networks)

        hosted_network_object.list_hosted_networks(session = self.setup_session,
                                                   baseurl = self.baseurl,
                                                   )
        self.network_id = 0
        try:
            self.network_id = hosted_network_object.get_response_key('list')[0]['id']
        except KeyError:
            logging.error('Failed to identify current network on this system for test case')

    def teardown(self):
        # Delete the player used in this test
        player_object = Player(api_version_player)
        player_object.delete_player_by_id(session = self.setup_session,
                                          baseurl = self.baseurl,
                                          id = self.player_id)


        # logout of session created for setup
        self.test_session_auth_object.logout()
        self.setup_session_auth_object.logout()

    def test_category(self):
        """
        Test requests on Category object with partial authentication
        :return:
        """

        # Perform get request
        category_object = Category(api_version_category)
        assert category_object.list_categories(session=self.test_session,
                                               baseurl=self.baseurl,
                                               limit=10), 'GET request did not return 200 response code'

        # Perform Post request
        assert not category_object.create_category(session=self.test_session,
                                                   baseurl=self.baseurl,
                                                   name=namespace + ' 5558 test_category',
                                                   description=namespace + ' 5558 test_category description'), 'Response code for post category was {}.  Expected 401 unauthorized'.format(
            category_object.last_response.status_code)
        assert category_object.last_response.status_code == 401, 'Expected 401 status code returned.  Received {}'.format(category_object.last_response.status_code)

        # Perform Delete category

        assert not category_object.delete_category_by_id(session = self.test_session,
                                                         baseurl = self.baseurl,
                                                         category_id = 5558)
        assert category_object.last_response.status_code == 401, 'Expected 401 status code returned.  Received {}'.format(category_object.last_response.status_code)

        # Perform PUT request

        assert not category_object.update_single_cateogry(session = self.test_session,
                                                          baseurl = self.baseurl,
                                                          category_id = 5558,
                                                          category_object={'name':'ba ba boo','description':'nah ha noo'})
        assert category_object.last_response.status_code == 401, 'Expected 401 status code returned.  Received {}'.format(category_object.last_response.status_code)

    def test_channel(self):
        """
        Test the partial login response for the channel object.
        :return:
        """
        # Perform GET request
        channel_object = Channels(api_version_channels)
        assert channel_object.list_channels(session=self.test_session,
                                        baseurl=self.baseurl,
                                        limit=10), 'GET request did not return 200 response code'
        # Perform Post request
        assert not channel_object.create_channel(session=self.test_session,
                                                 baseurl=self.baseurl,
                                                 name='test channel cm5558',
                                                 frameset_id=1), 'Response code for post channel was {}.  Expected 401 unauthorized'.format(channel_object.last_response.status_code)
        assert channel_object.last_response.status_code == 401, 'Expected 401 status code returned.  Received {}'.format(channel_object.last_response.status_code)

        # Perform Delete category

        assert not channel_object.delete_channel_by_id(session=self.test_session,
                                                       baseurl=self.baseurl,
                                                       channel_id=5558)
        assert channel_object.last_response.status_code == 401, 'Expected 401 status code returned.  Received {}'.format(channel_object.last_response.status_code)

        # Perform PUT request

        assert not channel_object.update_channel(session=self.test_session,
                                                 baseurl=self.baseurl,
                                                 channel_id=5558,
                                                 channel_json={'name': 'ba ba boo', 'description': 'nah ha noo'})
        assert channel_object.last_response.status_code == 401, 'Expected 401 status code returned.  Received {}'.format(channel_object.last_response.status_code)

    def test_frameset_object(self):
        # Test GET request
        frameset_object = Frameset_template(api_version_framesets)
        assert frameset_object.list_all_available_frameset_templates(session=self.test_session,
                                                                     baseurl=self.baseurl,
                                                                     limit=10), 'GET request did not return 200 response code'
        # Perform POST
        assert not frameset_object.create_frameset_template(session=self.test_session,
                                                            baseurl=self.baseurl,
                                                            name='booga wooga booga wooga',
                                                            list_of_frames=[],
                                                            height=90,
                                                            width=49), 'Frameset POST returned 200 even though cookie token absent'
        assert frameset_object.last_response.status_code == 401, 'Expected 401 status code response.  Received {}'.format(frameset_object.last_response.status_code)

        # Perform PUT
        assert not frameset_object.update_frameset_template(session = self.test_session,
                                                            baseurl = self.baseurl,
                                                            frameset_id= 44,
                                                            field_change_dict = {})
        assert frameset_object.last_response.status_code == 401, 'Expected 401 status code response.  Received {}'.format(frameset_object.last_response.status_code)

    def test_heartbeats(self):
        """
        Test of Heartbeat object response.  There is no PUT or Delete for this interface
        :return:
        """
        heartbeat_object = Heartbeats(api_version_heartbeats)

        # Test GET
        assert heartbeat_object.get_current_heartbeat_sequence_of_player(session=self.test_session,
                                                                         baseurl=self.baseurl,
                                                                         uuid=self.player_uuid), 'GET request did not return 200 response code'
        # Test POST
        assert not heartbeat_object.report_heartbeat(session=self.test_session,
                                                     baseurl=self.baseurl,
                                                     uuid='abc'), 'Expected'
        assert heartbeat_object.last_response.status_code == 401, 'Heartbeat returned status code {}, expected 401'.format(
            heartbeat_object.last_response.status_code)

    def test_hosted_networks(self):
        hosted_network_object = Hosted_Networks(api_version_hosted_networks)
        # Test GET
        assert hosted_network_object.list_hosted_networks(session=self.test_session,
                                                          baseurl=self.baseurl,
                                                          limit=10), 'GET request did not return 200 response code'
        # Test POST
        # There is no POST for hosted networks.

        # Test DELETE
        assert not hosted_network_object.delete_hosted_network_by_id(session = self.test_session,
                                                                     baseurl=self.baseurl,
                                                                     network_id=4),'DELETE request returned 200 when cookie token not present'
        assert hosted_network_object.last_response.status_code == 401, 'Received http response of {}, expected 401.'.format(hosted_network_object.last_response.status_code)

        # Test PUT
        assert not hosted_network_object.update_hosted_network(session=self.test_session,
                                                               baseurl=self.baseurl,
                                                               network_id=4)
        assert hosted_network_object.last_response.status_code == 401, 'Received http response of {}, expected 401'.format(hosted_network_object.last_response.status_code)

    def test_languages(self):
        """
        Test for languages API using a partially authenticated Session - no cookie token
        Note: THere are only GET methods in this api
        :return:
        """
        # Test GET
        languages_object = Languages(api_version_languages)
        assert languages_object.list_languages(session=self.test_session,
                                               baseurl=self.baseurl,
                                               limit=10), 'GET request did not return 200 response code'

    def test_media_metadata(self):
        """
        Test for media_metadata api with partially authenticated session - no cookie token
        :return:
        """
        # Test GET
        media_metadata_object = Media_meta_data(api_version_media_metadata)
        assert media_metadata_object.list_media_metadata(session=self.test_session,
                                                         baseurl=self.baseurl,
                                                         limit=10), 'GET request did not return 200 response code'

        # Test POST
        assert not media_metadata_object.create_metadata(session = self.test_session,
                                                         baseurl = self.baseurl,
                                                         name = 'boo bah ha ha',
                                                         data_type=metadata_data_type.INTEGER,
                                                         value_type=metadata_value_type.PICKLIST), 'POST request succeeded without Cookie authorization'
        assert media_metadata_object.last_response.status_code == 401, 'Expected http response 401, got {}'.format(media_metadata_object.last_response.status_code)

        # Test DELETE
        assert not media_metadata_object.delete_metadata_by_id(session=self.test_session,
                                                               baseurl=self.baseurl,
                                                               metadata_id=44), 'DELETE call worked without Cookie token'
        assert media_metadata_object.last_response.status_code == 401,'Expected 401 response, got {}'.format(media_metadata_object.last_response.status_code)

        # Test PUT
        assert not media_metadata_object.update_media_metadata(session=self.test_session,
                                                               baseurl=self.baseurl,
                                                               media_metadata_id=44,
                                                               field_change_dict={}), 'PUT call worked without cookie token'
        assert media_metadata_object.last_response.status_code == 401, 'Expected 401 response, got {}'.format(media_metadata_object.last_response.status_code)

    def test_license(self):
        """
        Test for license API with partially authenticated session - no cookie token
        There is no PUT method in the license API
        :return:
        """
        # test GET
        license_object = License(api_version_license)

        assert license_object.check_feature_enable(session=self.test_session,
                                                   baseurl=self.baseurl,
                                                   name="PlayerMap"), 'GET request failed unexpectedly without cookie authentication'
        # Test POST
        assert not license_object.import_license_with_ie(session=self.test_session,
                                                         baseurl=self.baseurl,
                                                         filename="abc"), 'POST request succeeded without cookie token'
        assert license_object.last_response.status_code == 401, 'Expected 401 response code, got {}'.format(self.last_response.status_code)

        # Test DELETE
        assert not license_object.cancel_new_license(session=self.test_session,
                                                     baseurl=self.baseurl), 'DELETE request succeeded without cookie token.'
        assert license_object.last_response.status_code == 401, 'Expected 401 response code, got {}'.format(self.last_response.status_code)

    def test_messages(self):
        '''
        Test for message api with partially authenticated session - no cookie token
        Note: No delete API call for message (Deprecated)
        :return:
        '''

        # Test GET
        message_object = Message(api_version_messages)
        assert message_object.list_messages(session = self.test_session,
                                     baseurl = self.baseurl), 'GET request failed unexpectedly without cookie authentciation'

        # Test POST
        assert not message_object.create_message(session=self.test_session,
                                                 baseurl = self.baseurl,
                                                 name = 'ooga booga',
                                                 template_id = 44),'Received 200 response code from POST without cookie authentication'
        assert message_object.last_response.status_code == 401,'Expected 401 response code, but got {}'.format(message_object.last_response.status_code)

        # Test Delete
        # Note: Delete message by ID is deprecated.

        # Test PUT
        assert not message_object.update_message(session = self.test_session,
                                                 baseurl = self.baseurl,
                                                 message_id = 44,
                                                 message_json= {}), 'Recieved 200 response code from PUT withotu cookie authentication'
        assert message_object.last_response.status_code == 401, 'Expected 401 response code, but got {}'.format(message_object.last_response.status_code)


    def test_misc(self):
        """
        Test for misc api with partially authenticated session - no cookie token

        The MISC api only has GET requests...
        :return:
        """
        # Test GET
        misc_object = Misc(api_version_miscellaneous)
        assert misc_object.get_product_info(session = self.test_session,
                                            baseurl = self.baseurl), 'GET request failed unexpectedly without cookie authentication'


    def test_networks(self):
        """
        Test for network api with partially authenticated session - no cookie token
        Note:  Assume that there is only one network on the system
        Note:  There is no DELETE call in this API

        :return:
        """
        network_object = Network(api_version_network)



        # Test GET

        assert network_object.get_network_information(session = self.test_session,
                                                      baseurl = self.baseurl,
                                                      network_id = self.network_id), "GET request failed unexpectedly without cookie authentication"

        # Test POST

        assert not network_object.create_first_network(session = self.test_session,
                                                       baseurl = self.baseurl,
                                                       network_name='bah boo boo bah'), 'Succeded with POST operation while partially authenticated'
        assert network_object.last_response.status_code == 401, 'Expected 401 from partially authenticated POST.  Got {}'.format(network_object.last_response.status_code)

        # Test PUT
        assert not network_object.update_network_settings(session = self.test_session,
                                                          baseurl = self.baseurl,
                                                          network_id = self.network_id,
                                                          network_definition= {'description':'boo bah boo','active': True}), 'Succeeded with POST operation while partially authenticated'
        assert network_object.last_response.status_code == 401, 'Expected 401 from partially authenticated POST.  Got {}'.format(network_object.last_response.status_code)

    def test_player_health(self):
        """
        Test for player health api with partially authenticated session - no cookie token
        Note: Player health API has no POST method
        :return:
        """
        player_health_object = Player_Health(api_version_player_health)


        # Test GET
        assert player_health_object.list_player_health(session = self.test_session,
                                                       baseurl = self.baseurl),"GET request failed unexpectedly without cookie authentication"

        # No POST method in API

        # Test DELETE
        assert not player_health_object.clear_all_problems(session = self.test_session,
                                                           baseurl = self.baseurl), 'Succeded with DELETE operation while partially authenticated (no cookie)'
        assert player_health_object.last_response.status_code == 401, 'Expected 401 from partially authenticated POST.  Got {}'.format(player_health_object.last_response.status_code)

        # Test PUT
        assert not player_health_object.update_player_health_settings(session = self.test_session,
                                                                      baseurl = self.baseurl,
                                                                      identifier = 4342,
                                                                      key_dict = {' clearNetworkErrorAfterNDays': 7})
        assert player_health_object.last_response.status_code == 401, 'Expected 401 from partially authenticated PUT.  Got {}'.format(player_health_object.last_response.status_code)

    def test_player_metadata(self):
        """
        Test for player_metadata api with partially authenticated session - no cookie token
        :return:
        """
        # Test GET
        player_metadata_object = Player_meta_data(api_version_player_metadata)
        assert player_metadata_object.list_player_metadata(session=self.test_session,
                                                           baseurl=self.baseurl,
                                                           limit=10), 'GET request did not return 200 response code'

        # Test POST
        assert not player_metadata_object.create_metadata(session=self.test_session,
                                                          baseurl=self.baseurl,
                                                          name='boo bah ha ha',
                                                          data_type=metadata_data_type.INTEGER,
                                                          value_type=metadata_value_type.PICKLIST), 'POST request succeeded without Cookie authorization'
        assert player_metadata_object.last_response.status_code == 401, 'Expected http response 401, got {}'.format(
            player_metadata_object.last_response.status_code)

        # Test DELETE
        assert not player_metadata_object.delete_metadata_by_id(session=self.test_session,
                                                                baseurl=self.baseurl,
                                                                metadata_id=44), 'DELETE call worked without Cookie token'
        assert player_metadata_object.last_response.status_code == 401, 'Expected 401 response, got {}'.format(
            player_metadata_object.last_response.status_code)

        # Test PUT
        assert not player_metadata_object.update_player_metadata(session=self.test_session,
                                                                 baseurl=self.baseurl,
                                                                 player_metadata_id=44,
                                                                 field_change_dict={}), 'PUT call worked without cookie token'
        assert player_metadata_object.last_response.status_code == 401, 'Expected 401 response, got {}'.format(
            player_metadata_object.last_response.status_code)

    def test_player(self):
        """
        Test Player Object for response to incomplete authentication
        :return:
        """
        player_object = Player(api_version_player)
        # test GET
        assert player_object.list_players(session = self.test_session,
                                          baseurl = self.baseurl), 'GET request did not return 200 response code'

        # test POST
        assert not player_object.create_player(session = self.test_session,
                                               baseurl = self.baseurl,
                                               name = 'bah bah boo'), 'POST call worked without cookie token'
        assert player_object.last_response.status_code == 401, 'Expected 401 response, got {}'.format(player_object.last_response.status_code)

        # test DELETE
        assert not player_object.delete_player_by_id(session = self.test_session,
                                                     baseurl = self.baseurl,
                                                     id = 44),'DELETE call worked without cookie token'
        assert player_object.last_response.status_code == 401, 'Expected 401 response, got {}'.format(player_object.last_response.status_code)

        # test PUT
        assert not player_object.update_single_player(session = self.test_session,
                                                      baseurl = self.baseurl,
                                                      player_id = 444,
                                                      field_change_dict={}), 'PUT call worked without cookie token'
        assert player_object.last_response.status_code == 401, 'Expected 401 response, got {}'.format(player_object.last_response.status_code)

    def test_playlist(self):
        """
        Test Playlist API for response to incomplete authentication
        :return:
        """

        playlist_object = Playlist(api_version_playlist)

        # Test GET
        assert playlist_object.list_playlist_types(session = self.test_session,
                                                   baseurl = self.baseurl),'GET request did not return 200 response code'
        # Test POST
        assert not playlist_object.create_playlist(session = self.test_session,
                                                   baseurl = self.baseurl,
                                                   name = 'boo bah bah boo'),'POST request did not return 200 response code'
        assert playlist_object.last_response.status_code == 401, 'Expected 401 response, got {}'.format(playlist_object.last_response.status_code)

        # TEST DELETE
        assert not playlist_object.delete_playlist_by_id(session = self.test_session,
                                                         baseurl = self.baseurl,
                                                         playlist_id = 432), 'DELETE request did not return 200 response code'
        assert playlist_object.last_response.status_code == 401, 'Expected 401 response, got {}'.format(playlist_object.last_response.status_code)

        # TEST PUT
        assert not playlist_object.update_playlist(session = self.test_session,
                                                   baseurl = self.baseurl,
                                                   playlist_id = 432,
                                                   field_change_dict = {}),'PUT request did not return 200 response code'
        assert playlist_object.last_response.status_code == 401, 'Expected 401 response, got {}'.format(playlist_object.last_response.status_code)


    def test_roles(self):
        """
        Test Roles API for response to complete authentication
        :return:
        """

        roles_object = Roles(api_version_roles)

        # test GET
        assert roles_object.list_roles(session = self.test_session,
                                       baseurl = self.baseurl), 'GET request did not return 200 response code'

        # test POST
        assert not roles_object.create_role(session = self.test_session,
                                            baseurl = self.baseurl,
                                            name = "goob a gooba",
                                            resources_list = [],
                                            system = False), 'POST request did not return 200 response code'
        assert roles_object.last_response.status_code == 401, 'Expected 401 response, got {}'.format(roles_object.last_response.status_code)

        # test DELETE
        assert not roles_object.delete_role_by_id(session = self.test_session,
                                                  baseurl = self.baseurl,
                                                  role_id = 432), 'DELETE request did not return 200 response code'
        assert roles_object.last_response.status_code == 401, 'Expected 401 response, got {}'.format(roles_object.last_response.status_code)

        # test PUT
        assert not roles_object.update_role(session = self.test_session,
                                            baseurl = self.baseurl,
                                            role_id = 432,
                                            field_change_dict={}), 'PUT request did not return 200 response code'
        assert roles_object.last_response.status_code == 401, 'Expected 401 response, got {}'.format(roles_object.last_response.status_code)

    def test_users(self):
        """
        Test Users API for response to complete authentication
        :return:
        """
        user_object = Users(api_version_users)

        # Test GET
        assert user_object.list_users(session = self.test_session,
                               baseurl = self.baseurl), 'GET request did not return 200 response code'

        # Test POST
        assert not user_object.create_user(session = self.test_session,
                                       baseurl = self.baseurl,
                                       emailAddress='wa@co.no',
                                       firstname= 'Will',
                                       lastname = 'Short',
                                       name='Suprize!',
                                       password ='bobaba',
                                       role_list = [],
                                       username = 'hawgaga'),'POST request did not return 200 response code'
        assert user_object.last_response.status_code == 401, 'Expected 401 response, got {}'.format(user_object.last_response.status_code)

        # Test DELTE
        assert not user_object.delete_user(session = self.test_session,
                                           baseurl = self.baseurl,
                                           user_id = 342), 'DELETE request did not return 200 response code'
        assert user_object.last_response.status_code == 401, 'Expected 401 response, got {}'.format(user_object.last_response.status_code)

        # Test PUT
        assert not user_object.update_user(session = self.test_session,
                                           baseurl = self.baseurl,
                                           identifier = 234,
                                           update_user_dict={}),'PUT request did not return 200 response code'
        assert user_object.last_response.status_code == 401, 'Expected 401 response, got {}'.format(user_object.last_response.status_code)


    def test_user(self):
        """
        Test
        :return:
        """
    @nottest
    def not_test_yet(self):

        # file_upload_object = File_upload(api_version_fileupload)
        # Note - no GET's in file upload API
#       license_object = License(api_version_license)

        media_object = Media(api_version_media)
        assert media_object.list_media(session=self.test_session,
                                       baseurl=self.baseurl,
                                       limit=10), 'GET request did not return 200 response code'

@nottest
class test_jira_9476_jira_9457():
    """
    From:
    https://www.yammer.com/scalabeta/#/Threads/show?threadId=478499682
    Entered by Gavin Melling on Tues 1/20 at 7:01am:
    Player search is only returning 10 items, when '0' (unlimited) is requested, can set '1000' as maximum retrieved alternately.
    If we need more information from the customer, broke this out as a new thread here:
    https://www.yammer.com/scalabeta/#/Threads/show?threadId=489354344

    This test will validate this issue.
    1)  Create 15 players
    2)  Perform a faceted search on the players with appropriate search term to yield all 15 of the players created
    but using a limit of 0
    3)  Confirm that 15 items are returned
    """
    @classmethod
    def setup_class(cls):
        pass

    @classmethod
    def teardown_class(cls):
        pass

    def setup(self):
        # Login to perform teardown
        logging.info('Beginning test setup')
        self.baseurl = config['login']['baseurl']
        self.username = config['login']['username']
        self.password = config['login']['password']
        self.api_auth_object = Auth_api(api_version_authentication)
        logging.debug('Read login info from config file and ready to begin.')
        logging.info('Initializing session for test module setup.')

        self.test_session = self.api_auth_object.login(self.username, self.password, self.baseurl)

        # Set up unique string associated with this test for naming objects
        now = datetime.datetime.now()
        self.unique_name = namespace + " " +now.strftime("%Y_%m_%d_%H%S.%f")

        # Create 15 players
        player_object = Player(api_version_player)
        self.player_name_base = self.unique_name + ' #'
        player_create_result = player_object.create_multiple_players(session = self.test_session,
                                              baseurl = self.baseurl,
                                              name = self.player_name_base,
                                              type = 'SCALA',
                                              number_of_players = 15)

        if not player_create_result:
            logging.error('Failed to create 15 players during setup of {}'.format(self.__class__.__name__))

        self.player_id_list = player_object.get_response_key('ids')

    def teardown(self):
        player_object = Player(api_version_player)
        for player_id in self.player_id_list:
            player_delete_result = player_object.delete_player_by_id(session = self.test_session,
                                              baseurl = self.baseurl,
                                              id = player_id)
            if not player_delete_result:
                logging.error('Failed to delete player with id = {} during test case teardown for {}'.format(player_id,
                                                                                                             self.__class__.__name__))
        # logout of session created for setup
        self.api_auth_object.logout()

    def test_faceted_search_limit_zero(self):
        """
        Tests for a limit = 0 response from faceted search should return all records
        :return:
        """
        player_object = Player(api_version_player)
        assert player_object.player_faceted_search(session=self.test_session,
                                                   baseurl=self.baseurl,
                                                   limit=0,
                                                   fields='name,id',
                                                   search=self.unique_name), 'Player faceted search call returned incorrect status code'
        num_players_found = len(player_object.get_response_key('list'))
        assert num_players_found == 15, 'Found '+ str(num_players_found) + ' players but expected 15'

    def test_search_limit_zero(self):
        """
        Test for a limit = 0 response from old style list search should return all records
        :return:
        """
        player_object = Player(api_version_player)
        assert player_object.list_players(session=self.test_session,
                                          baseurl=self.baseurl,
                                          limit=0,
                                          fields = 'name,id',
                                          search=self.unique_name), 'Player list search call returned incorrect status code'
        num_players_found = len(player_object.get_response_key('list'))
        assert num_players_found == 15, 'Found '+ str(num_players_found) + ' players but expected 15'






