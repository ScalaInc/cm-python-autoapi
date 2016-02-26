__author__ = 'rkaye'

import logging
import logging.config
import configparser
from framework.constants import CONFIG_FILE_PATH, LOG_FILE_PATH, metadata_data_type
from framework.authentication_rest import login, logout
from framework.http_rest import *
from framework.fileupload_rest import File_upload
from framework.media_rest import Media
from framework.player_metadata_rest import Player_meta_data
from framework.authentication_api_rest import Auth_api
from nose.tools import nottest
import datetime

config = configparser.ConfigParser()
config.read(CONFIG_FILE_PATH)
logging.config.fileConfig(LOG_FILE_PATH)
logging.debug('Logging config file path is: {}'.format(CONFIG_FILE_PATH))

api_version_player_metadata = config['api_info']['api_version_media_metadata']
api_version_fileupload = config['api_info']['api_version_fileupload']
api_version_media = config['api_info']['api_version_media']
api_version_authentication = config['api_info']['api_version_authentication']

namespace = config['test']['namespace']

class TestPlayerMetadataEndpoint():
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
        pmd = Player_meta_data(api_version_player_metadata)

        # Create Boolean Metadata
        pm_name1 = namespace + ' boolean_metadata'
        pmd.create_metadata(self.test_session,
                            baseurl=self.baseurl,
                            name=pm_name1,
                            data_type=metadata_data_type.BOOLEAN,
                            value_type=metadata_value_type.ANY)
        self.boolean_metadata_id = pmd.get_id()
        logging.info('ID of boolean metadata is: {}'.format(self.boolean_metadata_id))

        # Create string_any Metadata
        self.pm_name2 = namespace + ' string_any_metadata'
        pmd.create_metadata(self.test_session,
                            baseurl=self.baseurl,
                            name=self.pm_name2,
                            data_type=metadata_data_type.STRING,
                            value_type=metadata_value_type.ANY)
        self.string_any_metadata_id = pmd.get_id()
        logging.info('ID of string any metadata is: {}'.format(self.string_any_metadata_id))

        # Create String Picklist Metadata
        self.pm_name3 = namespace + ' string_picklist_metadata'
        pmd.create_metadata(self.test_session,
                            baseurl=self.baseurl,
                            name=self.pm_name3,
                            data_type=metadata_data_type.STRING,
                            value_type=metadata_value_type.PICKLIST)
        self.string_picklist_id = pmd.get_id()
        logging.info('ID of string picklist metadata is: {}'.format(self.string_picklist_id))

        # Populate String Picklist Metadata

        self.string_picklist_items = ['aardvark', 'bird', 'cat', 'dog', 'elephant', 'fish']
        pmd.add_picklist_values_to_player_metadata(session = self.test_session,
                                                  baseurl = self.baseurl,
                                                  metadata_id = self.string_picklist_id,
                                                  list_of_predefined_values=self.string_picklist_items)


        # Create int Any metadata
        self.pm_name4 = namespace + ' int_any_metadata'
        pmd.create_metadata(self.test_session,
                            baseurl=self.baseurl,
                            name=self.pm_name4,
                            data_type=metadata_data_type.INTEGER,
                            value_type=metadata_value_type.ANY)
        self.int_any_id = pmd.get_id()
        logging.info('ID of int any metadata is: {}'.format(self.int_any_id))

        # Create int Picklist metadata
        self.pm_name5 = namespace + ' int_picklist_metadata'
        pmd.create_metadata(self.test_session,
                            baseurl=self.baseurl,
                            name=self.pm_name5,
                            data_type=metadata_data_type.INTEGER,
                            value_type=metadata_value_type.PICKLIST)
        self.int_picklist_id = pmd.get_id()
        logging.info('ID of int picklist metadata is: {}'.format(self.int_picklist_id))

        # Populate Int Picklist Metadata
        self.int_picklist_items = [2, 3, 5, 7, 11, 13]
        pmd.add_picklist_values_to_player_metadata(session = self.test_session,
                                                  baseurl = self.baseurl,
                                                  metadata_id = self.int_picklist_id,
                                                  list_of_predefined_values=self.int_picklist_items)

        # Add Media Items in order to run the test
                # Upload 3 media items
        self.media_id_list = []
        cur_datetime = datetime.datetime.now()
        path = namespace + "player_metadata_" + cur_datetime.strftime("%Y%m%d_T%H%M%S")
        media_object = Media(api_version_media)
        for media_item in [config['media_items']['mediafile_1'],config['media_items']['mediafile_2'],config['media_items']['mediafile_3']]:
               # Create a media item for use in this test suite
                file_up = File_upload(api_version_fileupload)

                # Initiate Upload of media item
                file_up.initiate_upload(session = self.test_session,baseurl=self.baseurl, local_file_name= media_item, file_upload_path= path)

                uuid = file_up.get_response_key('uuid')
                media_id = file_up.get_response_key('mediaId')
                self.media_id_list.append(media_id)

                # Upload file part
                file_up.upload_file_part(session=self.test_session, baseurl=self.baseurl, local_file_name=media_item,
                                local_file_path=config['path']['media'], uuid=uuid)

                # Commit Upload
                file_up.upload_finished(session=self.test_session, baseurl=self.baseurl, uuid=uuid)

                # Wait for Thumbnail to be available.
                media_object.wait_for_media_upload(session = self.test_session,
                                                   baseurl = self.baseurl,
                                                   max_wait_seconds = 60,
                                                   media_id = media_id)

        logging.debug('media_id_list is = {}'.format(self.media_id_list))

        # Create a variable to contain media metadata objects created by test cases

        self.player_metadata_id_list = [self.int_any_id, self.int_picklist_id, self.boolean_metadata_id, self.string_any_metadata_id, self.string_picklist_id]


    def teardown(self):

        media_object = Media(api_version_media)
        for identifier in self.media_id_list:
            media_object.delete_media_by_id(session = self.test_session,baseurl = self.baseurl, id = identifier)
            logging.debug('Delete of media object for test_player_metadatat teardown returned status code of: {}'.format(media_object.last_response.status_code))
        player_metadata_object = Player_meta_data(api_version_player_metadata)

        #Clean up the metadata created in setup section
        for metadata_id in self.player_metadata_id_list:
            player_metadata_object.delete_metadata_by_id(session = self.test_session,
                                                    baseurl = self.baseurl,
                                                    metadata_id = metadata_id)

        logout(self.test_session,self.baseurl)

    def test_create_metadata(self):
        '''
        Test for POST /api/rest/metadata
        :return:
        '''

        player_meta_data_object = Player_meta_data(api_version_player_metadata)

        test_data = [(metadata_data_type.BOOLEAN, metadata_value_type.ANY),
                     (metadata_data_type.INTEGER, metadata_value_type.ANY),
                     (metadata_data_type.INTEGER, metadata_value_type.PICKLIST),
                     (metadata_data_type.STRING, metadata_value_type.ANY),
                     (metadata_data_type.STRING, metadata_value_type.PICKLIST)]

        for metadata in test_data:
            assert player_meta_data_object.create_metadata(session = self.test_session,
                                              baseurl = self.baseurl,
                                              data_type = metadata[0],
                                              name = namespace + ' ' +metadata[0].name + ' ' + metadata[1].name,
                                              value_type = metadata[1]),'Could not add media metadata object type ' + metadata[0].name + ' value ' + metadata[1].name

            self.player_metadata_id_list.append(player_meta_data_object.get_id())

    def test_delete_metadata(self):
        '''
        Test for DELETE /api/rest/metadata/{id}
        :return:
        '''

        player_metadata_object = Player_meta_data(api_version_player_metadata)

        test_data = [(metadata_data_type.BOOLEAN, metadata_value_type.ANY),
                     (metadata_data_type.INTEGER, metadata_value_type.ANY),
                     (metadata_data_type.INTEGER, metadata_value_type.PICKLIST),
                     (metadata_data_type.STRING, metadata_value_type.ANY),
                     (metadata_data_type.STRING, metadata_value_type.PICKLIST)]

        self.delete_ids = []

        for metadata in test_data:
            assert player_metadata_object.create_metadata(session = self.test_session,
                                              baseurl = self.baseurl,
                                              data_type = metadata[0],
                                              name = namespace + ' ' +metadata[0].name + ' ' + metadata[1].name,
                                              value_type = metadata[1]),'Could not add media metadata object type ' + metadata[0].name + ' value ' + metadata[1].name

            self.player_metadata_id_list.append(player_metadata_object.get_id())
            self.delete_ids.append(player_metadata_object.get_id())
            logging.debug('adding {} to delete IDs'.format(player_metadata_object.get_id()))
            logging.debug('full list of delete IDs is {}'.format(self.delete_ids))

        logging.debug('list of media metadata to delete in test case is: {}'.format(self.delete_ids))

        for metadata_id in self.delete_ids:
            assert player_metadata_object.delete_metadata_by_id(session = self.test_session,
                                                               baseurl = self.baseurl,
                                                               metadata_id = metadata_id), 'Could not delete metadata id with id = ' + str(metadata_id)

    def test_add_picklist_values_to_player_integer_metadata(self):
        '''
        Endpoint test for /api/rest/metadata/multiple/{metadataId}
        :return:
        '''

        player_metadata_object = Player_meta_data(api_version_player_metadata)
        test_data_list = [100,200,300]

        assert player_metadata_object.add_picklist_values_to_player_metadata(session = self.test_session,
                                                                           baseurl = self.baseurl,
                                                                           metadata_id = self.int_picklist_id,
                                                                           list_of_predefined_values= test_data_list), 'Call to add picklist items to integer picklist player metadata did not return 200'

        player_metadata_object.find_metadata_by_id(session = self.test_session,
                                                  baseurl = self.baseurl,
                                                  metadata_id = self.int_picklist_id)

        list_of_metadata_picklist_values = [predefined_value['value'] for predefined_value in player_metadata_object.last_response.json()['predefinedValues']]
        logging.debug("List of picklist items pulled back from CM is: {}".format(list_of_metadata_picklist_values))

        for test_data_item in test_data_list:
            logging.debug('Checking for value {} in list of picklist items'.format(test_data_item))
            assert str(test_data_item) in list_of_metadata_picklist_values, 'Did not find test data in integer picklist metadata.  Searching for ' + str(test_data_item)

    def test_add_picklist_values_to_player_string_metadata(self):
        '''
        Endpoint test for /api/rest/metadata/multiple/{metadataId}
        :return:
        '''

        player_metadata_object = Player_meta_data(api_version_player_metadata)
        test_data_list = ['bow wow', 'meow', 'cluck cluck']

        assert player_metadata_object.add_picklist_values_to_player_metadata(session = self.test_session,
                                                                           baseurl = self.baseurl,
                                                                           metadata_id = self.string_picklist_id,
                                                                           list_of_predefined_values= test_data_list), 'Call to add picklist items to string picklist player metadata did not return 200'

        player_metadata_object.find_metadata_by_id(session = self.test_session,
                                                  baseurl = self.baseurl,
                                                  metadata_id = self.string_picklist_id)

        list_of_metadata_picklist_values = [predefined_value['value'] for predefined_value in player_metadata_object.last_response.json()['predefinedValues']]
        logging.debug("List of picklist items pulled back from CM is: {}".format(list_of_metadata_picklist_values))

        for test_data_item in test_data_list:
            logging.debug('Checking for value {} in list of picklist items'.format(test_data_item))
            assert str(test_data_item) in list_of_metadata_picklist_values, 'Did not find test data in string picklist metadata.  Searching for ' + str(test_data_item)

    def test_find_metadata_by_id(self):
        '''
        Tests GET /api/rest/metadata/{id}
        :return:
        '''

        player_metadata_object = Player_meta_data(api_version_player_metadata)

        for media_metadata_id in self.player_metadata_id_list:
            assert player_metadata_object.find_metadata_by_id(session = self.test_session,
                                                         baseurl = self.baseurl,
                                                         metadata_id = media_metadata_id), 'Could not find media metadata with id = ' + str(media_metadata_id)

    def test_list_picklist_values_by_metadata_id_integer(self):
        '''
        Tests /api/rest/metadata/{metadataid}/pickListValues
        :return:
        '''

        player_metdata_object = Player_meta_data(api_version_player_metadata)

        assert player_metdata_object.list_picklist_values_by_metadata_id(session = self.test_session,
                                                                        baseurl = self.baseurl,
                                                                        metadata_id = self.int_picklist_id), 'Called list Picklist Items by metadata ID for Int picklist and did not receive 200 response code'
        list_of_returned_picklist_values = [metadata_value['value'] for metadata_value in player_metdata_object.last_response.json()['list']]

        for metadata_value in self.int_picklist_items:
            assert str(metadata_value) in list_of_returned_picklist_values,'Did not find ' + str(metadata_value) + ' in list picklist items response'

    def test_list_picklist_values_by_metadata_id_string(self):
        '''
        Tests /api/rest/metadata/{metadataid}/pickListValues
        :return:
        '''

        player_metadata_object = Player_meta_data(api_version_player_metadata)

        assert player_metadata_object.list_picklist_values_by_metadata_id(session = self.test_session,
                                                                        baseurl = self.baseurl,
                                                                        metadata_id = self.string_picklist_id), 'Called list Picklist Items by metadata ID for String picklist and did not receive 200 response code'
        list_of_returned_picklist_values = [metadata_value['value'] for metadata_value in player_metadata_object.last_response.json()['list']]

        for metadata_value in self.string_picklist_items:
            logging.debug('Testing to see if {} is in the list of responses from CM: {}'.format(metadata_value, list_of_returned_picklist_values))
            assert metadata_value in list_of_returned_picklist_values,'Did not find ' + metadata_value + ' in list picklist items response'

    def test_list_player_metadata(self):
        '''
        Tests GET /api/rest/metadata
        :return:
        '''

        player_metadata_object = Player_meta_data(api_version_player_metadata)

        assert player_metadata_object.list_player_metadata(session = self.test_session,
                                                         baseurl = self.baseurl,
                                                         limit = 100), 'Did not receive 200 status code from list media metadata call'

        # Validate that the objects created in the setup are in the response

        returned_metadata_id_list = [metadata['id'] for metadata in player_metadata_object.get_response_key('list')]

        for media_metadata_id in self.player_metadata_id_list:
            logging.debug('Testing for {} in {}'.format(media_metadata_id, returned_metadata_id_list))
            assert media_metadata_id in returned_metadata_id_list, 'Could not find media id ' + str(media_metadata_id) + ' in ' + str(returned_metadata_id_list)


    def test_update_player_metadata(self):
        '''
        Tests PUT /api/rest/metadata/{id}

        Simply changes the name of the media metadata object under test
        :return:
        '''

        player_metadata_object = Player_meta_data(api_version_player_metadata)

        new_name = 'foo foo foo pitang!'

        update_parameter = {'name': new_name}

        assert player_metadata_object.update_player_metadata(session = self.test_session,
                                                    baseurl = self.baseurl,
                                                    player_metadata_id = self.string_any_metadata_id,
                                                    field_change_dict= update_parameter)

        player_metadata_object.find_metadata_by_id(session = self.test_session,
                                                  baseurl = self.baseurl,
                                                  metadata_id = self.string_any_metadata_id)

        name_after_update = player_metadata_object.get_response_key('name')

        logging.debug('After update, expected: {}, got: {}'.format("MediaItem." + new_name, name_after_update))

        assert name_after_update == "Player." + new_name, 'After update, name did not change correctly.  Expected ' + new_name + ' got ' + name_after_update

    @nottest
    def test_update_sort_order(self):
        '''
        Tests PUT /api/rest/metadata/multi/{id}
        :return:
        '''

        player_metadata_object = Player_meta_data(api_version_player_metadata)

        authorization_object = Auth_api(api_version_authentication)

        authorization_object.get_session_info(session = self.test_session,
                                              baseurl = self.baseurl)

        network_id = authorization_object.get_response_key('network')['id']

        player_metadata_object.list_player_metadata(session = self.test_session,
                                                  baseurl = self.baseurl,
                                                  limit = 500,
                                                  fields = 'id,order',
                                                  sort = 'order')

        list_of_metadata = player_metadata_object.get_response_key('list')

        assert len(list_of_metadata) > 1, 'One or less media metadata found during test.  Setup creates at least 4'

        first_metadata_order = list_of_metadata[0]['order']
        first_metadata_id = list_of_metadata[0]['id']
        last_metadata_order = list_of_metadata[-1]['order']
        last_metadata_id = list_of_metadata[-1]['id']

        # Swap first and last metadata in the ordered list - then send the request off to swap them in the CM
        # logging.debug('Before swap, the metadata record looks like this: {}'.format(json.dumps(list_of_metadata, indent=4, separators=(',', ': '))))
        #
        # list_of_metadata[0]['order'] = last_metadata_order
        # list_of_metadata[-1]['order'] = first_metadata_order
        #
        # logging.debug('After swap, the metadata record looks like this: {}'.format(json.dumps(list_of_metadata, indent=4, separators=(',', ': '))))

        sort_metadata_order_param = [{'id':first_metadata_id,'order':last_metadata_order},{'id':last_metadata_id,'order':first_metadata_order}]

        logging.debug('About to send the swap metadata order with the following parameter: {}'.format(sort_metadata_order_param))

        assert player_metadata_object.update_sort_order_player_metadata(session = self.test_session,
                                                               baseurl = self.baseurl,
                                                               network_id = network_id,
                                                               update_sort_order_param= sort_metadata_order_param)

        player_metadata_object.list_player_metadata(session = self.test_session,
                                                  baseurl = self.baseurl,
                                                  limit = 500,
                                                  fields = 'id,order',
                                                  sort = 'order')

        new_list_of_metadata = player_metadata_object.get_response_key('list')

        assert new_list_of_metadata[0]['order'] == last_metadata_order, 'After swapping the order of first and last media metadata, could not confirm order change in DTO'
        assert new_list_of_metadata[-1]['order']  == first_metadata_order, 'After swapping the order of first and last media metadata, could not confirm order change in DTO'




