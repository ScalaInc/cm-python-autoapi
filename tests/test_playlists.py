__author__ = 'rkaye'

from framework.languages_rest import Languages
import logging
import logging.config
import configparser
from framework.constants import *
from framework.message_rest import Message
from framework.authentication_rest import login, logout
from framework.fileupload_rest import File_upload
from framework.templates_rest import Templates
from framework.media_rest import Media
from framework.playlist_rest import Playlist
from framework.frameset_template_rest import Frameset_template
from framework.channel_rest import Channels
from framework.storage_rest import Storage
from framework.media_rest import Media
import inspect
import json
import time
import datetime
from nose.tools import nottest


config = configparser.ConfigParser()
config.read(CONFIG_FILE_PATH)
baseurl = config['login']['baseurl']
logging.config.fileConfig(LOG_FILE_PATH)
logging.debug('Logging config file path is: {}'.format(CONFIG_FILE_PATH))
namespace = config['test']['namespace']
api_version = config['api_info']['api_version']
api_version_templates = config['api_info']['api_version_templates']
api_version_fileupload = config['api_info']['api_version_fileupload']
api_version_media = config['api_info']['api_version_media']
api_version_messages = config['api_info']['api_version_messages']
api_version_channels = config['api_info']['api_version_channels']
api_version_framesets = config['api_info']['api_version_framesets']
api_version_player = config['api_info']['api_version_player']
api_version_media_metadata = config['api_info']['api_version_media_metadata']
api_version_network = config['api_info']['api_version_network']
api_version_storage = config['api_info']['api_version_storage']
api_version_heartbeats = config['api_info']['api_version_heartbeats']
api_version_player_health = config['api_info']['api_version_player_health']
api_version_playlist = config['api_info']['api_version_playlist']
api_version_category = config['api_info']['api_version_category']
api_version_workgroup = config['api_info']['api_version_workgroup']
api_version_player_group = config['api_info']['api_version_player_group']

api_version_languages = config['api_info']['api_version_languages']


def this_function_name():
    return inspect.stack()[1][3]


class Test_playlists():
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
        username = config['login']['username']
        password = config['login']['password']
        logging.debug('Read login info from config file and ready to begin.')
        logging.info('Initializing session for test module setup.')

        self.test_session = login(username, password, baseurl)
        self.template_id_list = []
        self.media_id_list = []
        self.message_id_list = []
        self.playlist_id_list = []
        self.n = 4

        # Create 3 templates
        for template in [config['template_items']['templatefile_6'], config['template_items']['templatefile_7'],
                         config['template_items']['templatefile_8']]:
            file_up_template = File_upload(api_version_fileupload)

            file_up_template.initiate_upload(session=self.test_session, baseurl=baseurl, local_file_name=template,
                                             file_upload_path=namespace + this_function_name())

            # Upload File
            uuid = file_up_template.get_response_key('uuid')
            self.template_id_list.append(file_up_template.get_response_key('mediaId'))
            file_up_template.upload_file_part(session=self.test_session, baseurl=baseurl, local_file_name=template,
                                              local_file_path=config['path']['templates'], uuid=uuid)

            # Commit Upload
            file_up_template.upload_finished(session=self.test_session, baseurl=baseurl, uuid=uuid)

        # Upload 3 media items
        for media_item in [config['media_items']['mediafile_1'], config['media_items']['mediafile_2'],
                           config['media_items']['mediafile_3']]:
            # Create a media item for use in this test suite
            file_up = File_upload(api_version_fileupload)

            # Initiate Upload of media item
            file_up.initiate_upload(session=self.test_session, baseurl=baseurl, local_file_name=media_item,
                                    file_upload_path=namespace)

            uuid = file_up.get_response_key('uuid')
            current_media_id = file_up.get_response_key('mediaId')
            self.media_id_list.append(file_up.get_response_key('mediaId'))

            # Upload file part
            file_up.upload_file_part(session=self.test_session, baseurl=baseurl, local_file_name=media_item,
                                     local_file_path=config['path']['media'], uuid=uuid)
            # time.sleep(1)
            # Commit Upload
            file_up.upload_finished(session=self.test_session, baseurl=baseurl, uuid=uuid)

            # Wait for Thumbnail to be generated
            media_object = Media(api_version_media)
            media_object.wait_for_media_upload(session=self.test_session,
                                               baseurl=baseurl,
                                               max_wait_seconds=60,
                                               media_id=current_media_id)

        # Create 3 messages based on the three templates
        for message_number in range(len(self.template_id_list)):
            message_object = Message(api_version_messages)
            message_name = namespace + ' Message for template ' + str(message_number)
            caption = 'Caption for message ' + str(message_number)
            fields = [{'name': 'photo', 'value': self.media_id_list[message_number], 'type': 'IMAGE'},
                      {'name': 'caption', 'value': caption}]
            message_object.create_message(session=self.test_session,
                                          baseurl=baseurl,
                                          name=message_name,
                                          template_id=self.template_id_list[message_number],
                                          fields=fields)
            self.message_id_list.append(message_object.get_response_key('id'))

        logging.debug('Created {} messages with ids of {}'.format(len(self.message_id_list), self.message_id_list))

        # Create 1 playlist for tests that do not need to actually create their own playlist.
        playlist_object = Playlist(api_version_playlist)
        playlist_name = namespace + ' Playlist 1'
        playlist_description = namespace + ' Playlist 1 for test_playlists'

        playlist_object.create_playlist(session=self.test_session,
                                        baseurl=self.baseurl,
                                        name=playlist_name,
                                        description=playlist_description)

        self.playlist_id_list.append(playlist_object.get_response_key('id'))

        # Create n more of similar play lists to be referenced by test cases

        playlist_name_base = namespace + ' PL booga '
        playlist_description_base = namespace + ' Playlist for test_playlist.py number '

        for playlist_number in range(self.n):
            playlist_object.create_playlist(session=self.test_session,
                                            baseurl=self.baseurl,
                                            name=playlist_name_base + str(playlist_number),
                                            description=playlist_description_base + str(playlist_number))

            self.playlist_id_list.append(playlist_object.get_response_key('id'))


    def teardown(self):
        # Delete objects created for this set of tests
        media_object = Media(api_version_media)
        template_object = Templates(api_version_templates)
        playlist_object = Playlist(api_version_playlist)

        for message_id in self.message_id_list:
            media_object.delete_media_by_id(session=self.test_session,
                                            baseurl=self.baseurl,
                                            id=message_id)

        for media_id in self.media_id_list:
            media_object.delete_media_by_id(session=self.test_session,
                                            baseurl=self.baseurl,
                                            id=media_id)

        for template_id in self.template_id_list:
            template_object.delete_template_by_id(session=self.test_session,
                                                  baseurl=self.baseurl,
                                                  id=template_id)

        for playlist_id in self.playlist_id_list:
            playlist_object.delete_playlist_by_id(session=self.test_session,
                                                  baseurl=self.baseurl,
                                                  playlist_id=playlist_id)
        # Logout of test session
        logout(self.test_session, baseurl=baseurl)

    def test_add_playlist(self):
        '''
        Tests POST /api/rest/playlists
        At the end of the test, adds the newly created playlist to self.playlist_id_list so it can be
        deleted at teardown.  If the test
        :return:
        '''

        playlist_object = Playlist(api_version_playlist)
        playlist_name = namespace + ' Playlist Create Test'
        playlist_description = namespace + ' Playlist for test_create_normal_playlist'

        assert playlist_object.create_playlist(session=self.test_session,
                                               baseurl=self.baseurl,
                                               name=playlist_name,
                                               description=playlist_description)

        created_playlist_id = playlist_object.get_response_key('id')
        assert created_playlist_id is not None  # Checks to make sure there was an 'id' in the response
        self.playlist_id_list.append(
            created_playlist_id)  # adds this playlist to the list that will be cleaned up by teardown

    def test_delete_playlist(self):
        '''
        Tests DELETE /api/rest/playlists
        :return:
        '''
        playlist_object = Playlist(api_version_playlist)
        playlist_name = namespace + ' Playlist Delete Test'
        playlist_description = namespace + ' Playlist for test_delete_playlist'

        assert playlist_object.create_playlist(session=self.test_session,
                                               baseurl=self.baseurl,
                                               name=playlist_name,
                                               description=playlist_description)

        created_playlist_id = playlist_object.get_response_key('id')
        assert playlist_object.delete_playlist_by_id(session=self.test_session,
                                                     baseurl=self.baseurl,
                                                     playlist_id=created_playlist_id)

        # Verify the list was deleted
        assert not playlist_object.find_normal_playlist_by_id(session=self.test_session,
                                                              baseurl=self.baseurl,
                                                              playlist_id=created_playlist_id)

        self.playlist_id_list.append(
            created_playlist_id)  # adds this playlist to the list that will be cleaned up by teardown

    def test_add_media_to_normal_playlist(self):
        '''
        Validate PUT /api/rest/playlits/<id>/playlistItems<ids>
        :return:
        '''
        playlist_object = Playlist(api_version_playlist)
        assert playlist_object.add_media_to_normal_playlist(session=self.test_session,
                                                            baseurl=self.baseurl,
                                                            playlist_id=self.playlist_id_list[0],
                                                            media_id=self.media_id_list[0])

        # Validate that the playlist contains the media Just added

        playlist_object.list_all_available_playlist_items(session=self.test_session,
                                                          baseurl=self.baseurl,
                                                          playlist_id=self.playlist_id_list[0],
                                                          fields='media')

        playlist_media_id_list = [item_list['media']['id'] for item_list in playlist_object.get_response_key('list')]
        assert self.media_id_list[0] in playlist_media_id_list, 'Could not find media item added to playlist'

    def test_duplicate_playlist(self):
        '''
        Test the POST /api/rest/playlists/<id>/duplicate API Call
        Test is run on media only playlist.  In a different test, we will check for subplaylists
        :return:
        '''

        playlist_object = Playlist(api_version_playlist)
        for media_id in self.media_id_list:
            playlist_object.add_media_to_normal_playlist(session=self.test_session,
                                                         baseurl=self.baseurl,
                                                         playlist_id=self.playlist_id_list[0],
                                                         media_id=media_id
            )

        # Log the playlist items so that they can be compared at the end of the test case
        playlist_object.list_all_available_playlist_items(session=self.test_session,
                                                          baseurl=self.baseurl,
                                                          playlist_id=self.playlist_id_list[0],
                                                          fields='media')

        list_of_media_items_in_playlist = playlist_object.get_response_key('list')

        # Duplicate the playlist
        new_playlist_description = 'Playlist created by test_duplicate_playlist'
        new_playlist_name = namespace + ' duplicate_playlist'

        assert playlist_object.duplicate_playlist(session=self.test_session,
                                                  baseurl=self.baseurl,
                                                  playlist_id=self.playlist_id_list[0],
                                                  new_playlist_name=new_playlist_name,
                                                  new_playlist_description=new_playlist_description)

        duplicate_playlist_id = playlist_object.get_id()

        # Add the duplicate playlist to the list of playlists to be deleted by cleanup
        self.playlist_id_list.append(duplicate_playlist_id)

        # Now get the playlist items inside the duplicate playlist and compare to those archived above in list_of_media_items_in_playlist

        playlist_object.list_all_available_playlist_items(session=self.test_session,
                                                          baseurl=self.baseurl,
                                                          playlist_id=duplicate_playlist_id,
                                                          fields='media')

        list_of_media_items_in_duplicate_playlist = playlist_object.get_response_key('list')

        # Create a list containing ID's of all media in original playlist
        original_media_id_list = [item['media']['id'] for item in list_of_media_items_in_playlist]
        duplicate_media_id_list = [dup_item['media']['id'] for dup_item in list_of_media_items_in_duplicate_playlist]

        logging.debug('original playlist ids: {}'.format(json.dumps(original_media_id_list)))
        logging.debug('duplicate playlist ids: {}'.format(json.dumps(duplicate_media_id_list)))
        assert set(original_media_id_list) == set(
            duplicate_media_id_list), 'Could not verify that duplicate playlist matched original'

    def test_duplicate_playlist_with_subplaylist(self):
        '''
        Add a playlist to another as a subplaylist, then validate that the duplicate playlist method works
        and that the duplicated playlist contains the subplaylist
        :return:
        '''
        playlist_object = Playlist(api_version_playlist)

        master_playlist_name = namespace + ' Playlist update  Test'
        master_playlist_description = namespace + 'Playlist for test_duplicate_playlist_with_sub_playlist'

        # Create a playlist to serve as master playlist
        playlist_object.create_playlist(session=self.test_session,
                                        baseurl=self.baseurl,
                                        name=master_playlist_name,
                                        description=master_playlist_description)

        master_playlist_id = playlist_object.get_id()
        # Add the newly created subplaylist to the end of the list for deletion at the end of this test case
        self.playlist_id_list.append(master_playlist_id)

        # Now add the setup playlist to the newly created master playlist
        playlist_object.add_subplaylist_to_playlist(session=self.test_session,
                                                    baseurl=self.baseurl,
                                                    playlist_id=master_playlist_id,
                                                    name=master_playlist_name,
                                                    subplaylistId=self.playlist_id_list[0])

        duplicate_playlist_name = namespace + 'Duplicate Playlist'

        assert playlist_object.duplicate_playlist(session=self.test_session,
                                                  baseurl=self.baseurl,
                                                  playlist_id=master_playlist_id,
                                                  new_playlist_name=duplicate_playlist_name,
                                                  new_playlist_description=duplicate_playlist_name)

        # Que up the duplicated playlist for deletion by adding it to the delete list
        self.playlist_id_list.append(playlist_object.get_id())

        # Verify that the playlist comes back, it has one subplaylist, and the ID of the subplaylist matches
        # the one we added to the master playlist

        playlist_items = playlist_object.get_response_key('playlistItems')
        logging.debug('Duplicate playlist contains {} items, expected 1'.format(len(playlist_items)))
        assert len(playlist_items) == 1, 'Expected only one subplaylist in duplicate playlist'
        logging.debug(
            'Duplicate playlist contains playlist with ID = {}'.format(playlist_items[0]['subplaylist']['id']))
        assert playlist_items[0]['subplaylist']['id'] == self.playlist_id_list[
            0], 'Unexpected subplaylist found in duplciate'

    def test_find_normal_playlist_by_id(self):
        '''
        Tets the GET /api/rest/playlists/{id}
        :return:
        '''
        playlist_object = Playlist(api_version_playlist)
        assert playlist_object.find_normal_playlist_by_id(session=self.test_session,
                                                          baseurl=self.baseurl,
                                                          playlist_id=self.playlist_id_list[0])

        assert playlist_object.get_id() == self.playlist_id_list[0]

    def test_get_usage_for_playlist(self):
        '''
        Basic test for GET /api/rest/playlists/usage

        Because the setup is extensive - set up a channel, a playlist etc, I have opted to test this
        in it's own test class Test_get_usage_for_playlist.
        :return:
        '''
        # See class Test_get_usage_for_playlist below
        pass

    @nottest
    def test_list_available_thumbnails_for_playlist(self):
        '''
        Add three media items to a normal playlist, then verify that the thumbnail count comes out to 3.
        :return:
        '''
        playlist_object = Playlist(api_version_playlist)
        for media_id in self.media_id_list:
            playlist_object.add_media_to_normal_playlist(session=self.test_session,
                                                         baseurl=self.baseurl,
                                                         playlist_id=self.playlist_id_list[0],
                                                         media_id=media_id)
        time.sleep(5)

        assert playlist_object.list_available_thumbnails_for_playlist_items(session=self.test_session,
                                                                            baseurl=self.baseurl,
                                                                            playlist_id=self.playlist_id_list[0])

        response_list_of_thumbnails = playlist_object.get_response_key('thumbnails')
        logging.debug(
            'Retrieved thumbnail list for test playlist: {}'.format(json.dumps(response_list_of_thumbnails, indent=4)))
        assert len(response_list_of_thumbnails) == len(self.media_id_list)
        for response_thumbnail in response_list_of_thumbnails:
            logging.debug('Current Thumbnail record is faa: '.format(json.dumps(response_thumbnail, indent=4)))
            assert 'thumbnailDownloadPaths' in response_thumbnail
            assert 'type' in response_thumbnail
            assert response_thumbnail['type'] == 'IMAGE'
            assert response_thumbnail['duration'] == 700


    def test_list_playlist_types(self):
        '''
        Verifies the reference API GET /api/rest/playlists/types
        :return:
        '''
        playlist_object = Playlist(api_version_playlist)
        assert playlist_object.list_playlist_types(session=self.test_session,
                                                   baseurl=self.baseurl)

        version11_response = [
            {
                "type": "AUDIO_PLAYLIST",
                "prettifyType": "com.scala.pojo.modules.playlist.PlaylistType AUDIO_PLAYLIST"
            },
            {
                "type": "DATA_PLAYLIST",
                "prettifyType": "com.scala.pojo.modules.playlist.PlaylistType DATA_PLAYLIST"
            },
            {
                "type": "MEDIA_PLAYLIST",
                "prettifyType": "com.scala.pojo.modules.playlist.PlaylistType MEDIA_PLAYLIST"
            },
            {
                "type": "SMART_AUDIO_PLAYLIST"
            },
            {
                "type": "SMART_DATA_PLAYLIST"
            },
            {
                "type": "SMART_MEDIA_PLAYLIST"
            }
        ]
        assert playlist_object.get_response_key(
            'types') == version11_response, 'Incorrect return from reference fucntion test_list_playlist_types'

    def test_list_playlists(self):
        '''
        Test List playlists api
        :return:
        '''

        playlist_object = Playlist(api_version_playlist)

        assert playlist_object.list_playlists(session=self.test_session,
                                              baseurl=self.baseurl,
                                              limit=3), 'Did not receive 200 from list playlist call'

        number_of_playlists_retrieved = playlist_object.get_response_key('list')
        logging.debug(
            'Number of playlists returned from list with limit = 3 was {}'.format(len(number_of_playlists_retrieved)))
        assert len(number_of_playlists_retrieved) == 3, 'Did not return the expected number of playlists'

    def test_list_playlists_with_search(self):
        '''
        Test list playlists with a search term
        :return:
        '''

        playlist_object = Playlist(api_version_playlist)

        # n+1 of the playlists created in the setup have 'booga' in the title.
        assert playlist_object.list_playlists(session=self.test_session,
                                              baseurl=self.baseurl,
                                              limit=40,
                                              search='booga'), 'Did not return 200 from list playlists'
        num_playlists_returned = len(playlist_object.get_response_key('list'))
        logging.debug('Returned {} playlists with "booga" in the title'.format(num_playlists_returned))
        assert num_playlists_returned == self.n ,'Found ' + str(num_playlists_returned) + ' playlists but expected ' + str(self.n)  # N playlists have 'booga' in them

    def test_list_playlists_for_landing(self):
        '''
        Test List playlists api
        :return:
        '''

        playlist_object = Playlist(api_version_playlist)

        assert playlist_object.list_playlists_for_landing_page(session=self.test_session,
                                                               baseurl=self.baseurl,
                                                               limit=3), 'Did not receive 200 from list playlist call'

        number_of_playlists_retrieved = playlist_object.get_response_key('list')
        logging.debug(
            'Number of playlists returned from list with limit = 3 was {}'.format(len(number_of_playlists_retrieved)))
        assert len(number_of_playlists_retrieved) == 3, 'Did not return the expected number of playlists'

    def test_list_playlists_with_search_for_landing(self):
        '''
        Test list playlists with a search term
        :return:
        '''

        playlist_object = Playlist(api_version_playlist)

        # n+1 of the playlists created in the setup have 'booga' in the title.
        assert playlist_object.list_playlists_for_landing_page(session=self.test_session,
                                                               baseurl=self.baseurl,
                                                               limit=40,
                                                               search='booga'), 'Did not return 200 from list playlists'
        num_playlists_returned = len(playlist_object.get_response_key('list'))
        logging.debug('Returned {} playlists with "booga" in the title'.format(num_playlists_returned))
        assert num_playlists_returned == self.n, 'Incorrect number of playlists returned by search.  Expected ' + str(self.n) + ' got ' + str(num_playlists_returned)

    def test_list_transitions(self):
        '''
        Test list transitions /api/rest/playlists/transition
        :return:
        '''

        playlist_object = Playlist(api_version_playlist)

        assert playlist_object.list_transitions(self.test_session,
                                                baseurl=self.baseurl), 'Test list transitions did not return status code 200'

        num_transitions_returned = len(playlist_object.get_response_key('transitions'))
        logging.debug('List Transitions returned {} transitions on system'.format(num_transitions_returned))
        assert num_transitions_returned >= 10

    def test_list_transitions_by_groups(self):
        '''
        Test list transitions /api/rest/playlists/listTransitions
        :return:
        '''

        playlist_object = Playlist(api_version_playlist)

        assert playlist_object.list_transitions_by_group(self.test_session,
                                                         baseurl=self.baseurl), 'Test list transitions did not return status code 200'

        transitions = len(playlist_object.get_response_key('list'))
        logging.debug('List Transitions returned {} transitions groups system'.format(transitions))
        assert transitions >= 9
        for transition_group in playlist_object.get_response_key('list'):
            assert 'name' in transition_group
            assert 'transitions' in transition_group
            assert 'sortOrder' in transition_group

    def test_multi_playlist_update_description(self):
        '''
        Test Update multiple players at PUT  /api/rest/playlists/multi/{uuid}

        This test has a few steps:
        1)  Generate a UUID using PYTHON
        1)  Set up a 'storage' object with a list of ID's in it POST /api/rest/storage
        2)  Post a value to the
        2)  Modify the description field of a set of playlists by using the values in the storage and
        PUT /api/rest/playlists/multi/{uuid}
        :return:
        '''

        storage_object = Storage(api_version_storage)
        string_list_of_ids = [str(x) for x in self.playlist_id_list]

        id_list_for_storage = {'ids': string_list_of_ids}

        # Assert the storage api call b/c the rest of the test fails if this fails
        assert storage_object.store_value(session=self.test_session,
                                          baseurl=self.baseurl,
                                          value=id_list_for_storage), 'Failed to store list of playlist IDs'

        id_list_uuid = storage_object.get_response_key('value')

        playlist_object = Playlist(api_version_playlist)
        new_description = 'blah blah blah'

        assert storage_object.get_stored_value_by_uuid(session=self.test_session,
                                                       baseurl=self.baseurl,
                                                       uuid=id_list_uuid)

        logging.debug('The UUID returned from the CM is: {}'.format(storage_object.last_response.text))

        assert playlist_object.multi_update_playlists(session=self.test_session,
                                                      baseurl=self.baseurl,
                                                      uuid=id_list_uuid,
                                                      item_to_change='description',
                                                      value=new_description), 'Did not receive 200 status code from multi-update playlists'

        for playlist in self.playlist_id_list:
            playlist_object.find_normal_playlist_by_id(session=self.test_session,
                                                       baseurl=self.baseurl,
                                                       playlist_id=playlist)
            current_playlist_description = playlist_object.get_response_key('description')
            logging.debug('After multi update, playlist with id {} has description {}'.format(playlist,
                                                                                              current_playlist_description))
            assert current_playlist_description == new_description

    def test_update_normal_playlist_description(self):
        '''
        Test the api call at:
        GET /api/rest/playlists/{id}

        This test only checks the description field - future test cases should have more tests for other updates of
        other fields
        :return:
        '''
        playlist_object = Playlist(api_version_playlist)

        playlist_object.find_normal_playlist_by_id(session=self.test_session,
                                                   baseurl=self.baseurl,
                                                   playlist_id=self.playlist_id_list[0])
        playlist_name = playlist_object.get_response_key('name')
        new_playlist_description = 'hooga googa booga no29452 !!!'
        update_playlist_param = {'name': playlist_name, 'description': new_playlist_description}

        assert playlist_object.update_playlist(session=self.test_session,
                                               baseurl=self.baseurl,
                                               playlist_id=self.playlist_id_list[0],
                                               field_change_dict=update_playlist_param)

        playlist_object.find_normal_playlist_by_id(session=self.test_session,
                                                   baseurl=self.baseurl,
                                                   playlist_id=self.playlist_id_list[0])
        assert playlist_object.get_response_key('description') == new_playlist_description

    def test_find_playlist_with_given_name(self):
        '''
        Tests GET /api/rest/playlists/findByName/(name)
        :return:
        '''

        playlist_object = Playlist(api_version_playlist)

        playlist_object.find_normal_playlist_by_id(session=self.test_session,
                                                   baseurl=self.baseurl,
                                                   playlist_id=self.playlist_id_list[0])

        playlist_name_to_find = playlist_object.get_response_key('name')
        playlist_id_to_find = playlist_object.get_id()

        assert playlist_object.find_playlist_with_given_name(session=self.test_session,
                                                             baseurl=self.baseurl,
                                                             name=playlist_name_to_find), 'Could not find playlist with name'

        logging.debug(
            "Searching for playlist with name = {} yielded id {}".format(playlist_name_to_find, playlist_id_to_find))

        assert playlist_object.get_id() == playlist_id_to_find, "Found playlist by name but ID does not match"


class Test_get_usage_for_playlist:
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

        self.playlist_name = namespace + " sub_playlist"
        self.playlist_description = namespace + " Playlist used in testing get usage.  After setup should have 1 subplaylist useage and one timeslot useage"

        playlist_object.create_playlist(session=self.test_session,
                                        baseurl=self.baseurl,
                                        name=self.playlist_name,
                                        description=self.playlist_description)
        self.subplaylist_playlist_id = playlist_object.get_id()

        self.master_playlist_name = namespace + " Master playlist"
        self.master_playlist_description = namespace + " Master playlist used in test_get_usage"

        playlist_object.create_playlist(session=self.test_session,
                                        baseurl=self.baseurl,
                                        name=self.master_playlist_name,
                                        description=self.master_playlist_description)

        self.master_playlist_id = playlist_object.get_id()

        # Add a scheduled timeslot to the channel for subplaylist
        channel_object.update_schedules(session=self.test_session,
                                        baseurl=self.baseurl,
                                        channel_id=self.channel_id,
                                        playlist_id=self.subplaylist_playlist_id,
                                        channel_frameset_id=self.channel_frame_id,
                                        startDate="2013-10-01",
                                        startTime="05:00:00")

        # Add subplaylist to master playlist
        playlist_object.add_subplaylist_to_playlist(session=self.test_session,
                                                    baseurl=self.baseurl,
                                                    playlist_id=self.master_playlist_id,
                                                    name=self.master_playlist_name,
                                                    subplaylistId=self.subplaylist_playlist_id)

    def teardown(self):
        channel_object = Channels(api_version_channels)
        playlist_object = Playlist(api_version_playlist)

        channel_object.delete_channel_by_id(session=self.test_session,
                                            baseurl=self.baseurl,
                                            channel_id=self.channel_id)

        playlist_object.delete_playlist_by_id(session=self.test_session,
                                              baseurl=self.baseurl,
                                              playlist_id=self.subplaylist_playlist_id)

        playlist_object.delete_playlist_by_id(session=self.test_session,
                                              baseurl=self.baseurl,
                                              playlist_id=self.master_playlist_id)

        logout(self.test_session, self.baseurl)

    def test_get_usage_for_playlist(self):
        '''
        Test for get usage for playlist
        :return:
        '''
        playlist_object = Playlist(api_version_playlist)
        assert playlist_object.get_playlist_usage(session=self.test_session,
                                                  baseurl=self.baseurl,
                                                  playlist_ids=str(self.subplaylist_playlist_id))

        logging.debug(
            'After getting usage on the test playlist, received: {}'.format(playlist_object.last_response.text))
        assert playlist_object.get_response_key('timeSlotCount') == 1, 'Incorrect number of timeslots detected'
        assert playlist_object.get_response_key('subPlaylistCount') == 1, 'Incorrect number of supplaylists detected'


class test_subplaylist_nesting:
    '''
    Create a playlist 4 steps deep.  Verify that the playlists nest without issue.

    Create playlist a which contains 54 media items
    Create playlist b which contains 18 subplaylists (a)
    Create playlist c which contains 18 subplaylists (b)
    Create playlist d which contains 1 subplaylist (c)
    '''
    template_id_list = []
    media_id_list = []
    message_id_list = []
    playlist_id_list = []
    url_list = []
    unique_id = ""

    @classmethod
    def setup_class(self):

        # Begin by initiating a new login session for this test case.
        logging.info('Beginning test setup')
        baseurl = config['login']['baseurl']
        username = config['login']['username']
        password = config['login']['password']
        logging.debug('Read login info from config file and ready to begin.')
        logging.info('Initializing session for test module setup.')

        session = login(username, password, baseurl)
        now = datetime.datetime.now()
        self.unique_name = namespace + " " + now.strftime("%Y_%m_%d_%H%S.%f")

        # Create 3 templates
        media_object = Media(api_version_media)
        for template in [config['template_items']['templatefile_6'], config['template_items']['templatefile_7'],
                         config['template_items']['templatefile_8']]:
            file_up_template = File_upload(api_version_fileupload)

            file_up_template.initiate_upload(session=session, baseurl=baseurl, local_file_name=template,
                                             file_upload_path=self.unique_name)

            # Upload File
            uuid = file_up_template.get_response_key('uuid')
            template_id = file_up_template.get_response_key('mediaId')
            self.template_id_list.append(template_id)
            file_up_template.upload_file_part(session=session, baseurl=baseurl, local_file_name=template,
                                              local_file_path=config['path']['templates'], uuid=uuid)

            # Commit Upload
            file_up_template.upload_finished(session=session, baseurl=baseurl, uuid=uuid)

            # # Wait for thumbnails to appear on the newly uploaded template
            # media_object.wait_for_media_upload(session=session,
            #                                    baseurl=baseurl,
            #                                    max_wait_seconds=10,
            #                                    media_id=template_id)

        logging.debug('Created {} messages with ids of {}'.format(len(self.template_id_list), self.template_id_list))

        # Upload 3 media items

        for media_item in [config['media_items']['mediafile_1'], config['media_items']['mediafile_2'],
                           config['media_items']['mediafile_3']]:
            # Create a media item for use in this test suite
            file_up = File_upload(api_version_fileupload)

            # Initiate Upload of media item
            file_up.initiate_upload(session=session, baseurl=baseurl, local_file_name=media_item,
                                    file_upload_path=self.unique_name)

            uuid = file_up.get_response_key('uuid')
            media_id = file_up.get_response_key('mediaId')
            self.media_id_list.append(media_id)

            # Upload file part
            file_up.upload_file_part(session=session, baseurl=baseurl, local_file_name=media_item,
                                     local_file_path=config['path']['media'], uuid=uuid)

            # Commit Upload
            file_up.upload_finished(session=session, baseurl=baseurl, uuid=uuid)

            # Wait for thumbnails to become available
            media_object.wait_for_media_upload(session=session,
                                               baseurl=baseurl,
                                               max_wait_seconds=10,
                                               media_id=media_id)
            logging.debug('Created {} messages with ids of {}'.format(len(self.media_id_list), self.media_id_list))

        # Create 3 messages based on the three templates
        for message_number in range(len(self.template_id_list)):
            message_object = Message(api_version_messages)
            message_name = namespace + ' Message for template ' + str(message_number)
            caption = 'Caption for message ' + str(message_number)
            fields = [{'name': 'photo', 'value': self.media_id_list[message_number], 'type': 'IMAGE'},
                      {'name': 'caption', 'value': caption}]
            message_object.create_message(session=session,
                                          baseurl=baseurl,
                                          name=message_name,
                                          template_id=self.template_id_list[message_number],
                                          fields=fields)
            self.message_id_list.append(message_object.get_response_key('id'))

        logging.debug('Created {} messages with ids of {}'.format(len(self.message_id_list), self.message_id_list))

    @classmethod
    def teardown_class(self):
        # Login to perform teardown
        logging.info('Beginning test setup')
        baseurl = config['login']['baseurl']
        username = config['login']['username']
        password = config['login']['password']
        logging.debug('Read login info from config file and ready to begin.')
        logging.info('Initializing session for test module setup.')

        session = login(username, password, baseurl)

        # Delete setup objects here

        playlist_object = Playlist(api_version_playlist)
        for playlist_id in self.playlist_id_list:
            playlist_object.delete_playlist_by_id(session=session,
                                                  baseurl=baseurl,
                                                  playlist_id=playlist_id)
            logging.debug('Deleting playlist id = {} for performance test status_code = {}'.format(playlist_id,
                                                                                                   playlist_object.last_response.status_code))

        media_object = Media(api_version_media)
        all_media_list = self.media_id_list + self.message_id_list
        for media_id in all_media_list:
            media_object.delete_media_by_id(session=session,
                                            baseurl=baseurl,
                                            id=media_id)

        # logout of session created for setup
        logout(session, baseurl=baseurl)

    def setup(self):
        # Login to perform teardown
        logging.info('Beginning test setup')
        baseurl = config['login']['baseurl']
        username = config['login']['username']
        password = config['login']['password']
        logging.debug('Read login info from config file and ready to begin.')
        logging.info('Initializing session for test module setup.')
        self.test_version = config['performance']['cm_sw_version']

        self.test_session = login(username, password, baseurl)

    def teardown(self):
        # logout of session created for setup
        logout(self.test_session, baseurl=baseurl)

    def test_nested_play_lists(self):
        # Create a Playlist which contains all three messages 18 times
        playlist_object = Playlist(api_version_playlist)
        playlist_name_a = 'Playlist_A ' + self.unique_name
        description = namespace + " playlist used in this test case"

        assert playlist_object.create_playlist(session=self.test_session,
                                               baseurl=baseurl,
                                               name=playlist_name_a,
                                               description=description), 'Create Playlist A returned incorrect status'
        self.playlist_id_list.append(playlist_object.get_response_key('id'))

        # Add all three messages to the playlist 18 times
        for n in range(18):
            for message_id in self.message_id_list:
                assert playlist_object.add_media_to_normal_playlist(session=self.test_session,
                                                                    baseurl=baseurl,
                                                                    playlist_id=self.playlist_id_list[0],
                                                                    media_id=message_id), 'Failed to add message id ' + str(
                    message_id) + ' to test playlist A'

        # Create a second Playlist and add the first playlist to it 18 times

        playlist_object = Playlist(api_version_playlist)
        playlist_name_b = 'Playlist_B ' + self.unique_name

        assert playlist_object.create_playlist(session=self.test_session,
                                               baseurl=baseurl,
                                               name=playlist_name_b,
                                               description=description), 'Create Playlist B returned incorrect status'
        self.playlist_id_list.append(playlist_object.get_response_key('id'))

        for n in range(18):
            assert playlist_object.add_subplaylist_to_playlist(session=self.test_session,
                                                               baseurl=baseurl,
                                                               name=playlist_name_b,
                                                               playlist_id=self.playlist_id_list[1],
                                                               subplaylistId=self.playlist_id_list[
                                                                   0]), 'Failed to add the' + str(
                n) + 'th playlist to Playlist B'

        # Create a third playlist and add subplaylist B to it 18 times
        playlist_object = Playlist(api_version_playlist)
        playlist_name_c = 'Playlist_C ' + self.unique_name

        assert playlist_object.create_playlist(session=self.test_session,
                                               baseurl=baseurl,
                                               name=playlist_name_c,
                                               description=description), 'Create Playlist C returned incorrect status'
        self.playlist_id_list.append(playlist_object.get_response_key('id'))

        for n in range(18):
            assert playlist_object.add_subplaylist_to_playlist(session=self.test_session,
                                                               baseurl=baseurl,
                                                               name=playlist_name_c,
                                                               playlist_id=self.playlist_id_list[2],
                                                               subplaylistId=self.playlist_id_list[
                                                                   1]), 'Failed to add the' + str(n) + 'th playlist to Playlist C'

        # Add one more playlist and add playlist C to it.

        playlist_object = Playlist(api_version_playlist)
        playlist_name_d = 'Playlist_D ' + self.unique_name

        assert playlist_object.create_playlist(session=self.test_session,
                                               baseurl=baseurl,
                                               name=playlist_name_d,
                                               description=description), 'Create Playlist D returned incorrect status'
        self.playlist_id_list.append(playlist_object.get_response_key('id'))

        assert playlist_object.add_subplaylist_to_playlist(session=self.test_session,
                                                           baseurl=baseurl,
                                                           name=playlist_name_d,
                                                           playlist_id=self.playlist_id_list[3],
                                                           subplaylistId=self.playlist_id_list[
                                                               2]), 'Failed to add playlist C to playlist D'

        logging.debug("Four playlists created for test with id: {}".format(self.playlist_id_list))





