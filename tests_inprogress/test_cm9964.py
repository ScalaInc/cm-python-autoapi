__author__ = 'rkaye'

from framework.languages_rest import Languages
import logging
import logging.config
import configparser
from framework.constants import *
from framework.authentication_api_rest import Auth_api
from framework.fileupload_rest import File_upload
from framework.media_rest import Media
from framework.category_rest import Category
from framework.message_rest import Message
from framework.workgroup_rest import Workgroup
from framework.playlist_rest import Playlist
from framework.player_rest import Player
from framework.player_group_rest import PlayerGroup
import datetime
import hashlib
import json
import time
from nose_parameterized import parameterized, param
from nose.tools import nottest
from nose.plugins.attrib import attr


config = configparser.ConfigParser()
config.read(CONFIG_FILE_PATH)
baseurl = config['login']['baseurl']
logging.config.fileConfig(LOG_FILE_PATH)
logging.debug('Logging config file path is: {}'.format(CONFIG_FILE_PATH))
namespace = config['test']['namespace']

api_version_auth = config['api_info']['api_version_authentication']
api_version_fileupload = config['api_info']['api_version_fileupload']
api_version_messages = config['api_info']['api_version_messages']
api_version_media = config['api_info']['api_version_media']
api_version_playlist = config['api_info']['api_version_playlist']
api_version_category = config['api_info']['api_version_category']
api_version_workgroups = config['api_info']['api_version_workgroup']
api_version_player = config['api_info']['api_version_player']
api_version_player_group = config ['api_info']['api_version_player_group']

n=10000

class test_cm_9707():
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
        self.api_auth_object = Auth_api(api_version_auth)
        self.template_id_list = []
        self.media_id_list = []
        self.message_id_list = []

        logging.debug('Read login info from config file and ready to begin.')
        logging.info('Initializing session for test module setup.')

        self.test_session = self.api_auth_object.login(self.username, self.password, self.baseurl)

        # Set up unique string associated with this test for naming objects
        now = datetime.datetime.now()
        self.unique_name = namespace + " " +now.strftime("%Y_%m_%d_%H%S.%f")

        # Upload media for this test case - some of each type - use a new directory for each item
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

            # Commit Upload
            file_up.upload_finished(session=self.test_session, baseurl=baseurl, uuid=uuid)

            # Wait for Thumbnail to be generated
            media_object = Media(api_version_media)
            media_object.wait_for_media_upload(session=self.test_session,
                                               baseurl=baseurl,
                                               max_wait_seconds=60,
                                               media_id=current_media_id)


        # Create a playlists for this test
        playlist_object = Playlist(api_version_playlist)
        self.playlist_id_list = []
        playlist_name_1 = self.unique_name + " playlist 1"

        playlist_object.create_playlist(session = self.test_session,
                                        baseurl = self.baseurl,
                                        name = playlist_name_1,
                                        description = self.unique_name,
                                        )

        self.playlist_id_list.append(playlist_object.get_response_key("id"))

        time.sleep(3)

        # Fill the playlists
        for media in self.media_id_list:
            playlist_object.add_media_to_normal_playlist(session = self.test_session,
                                                     baseurl = self.baseurl,
                                                     playlist_id = self.playlist_id_list[0],
                                                     media_id = media)
            logging.debug("Added media with id  = {} to playlist with id = {}".format(media,self.playlist_id_list[0]))



    def teardown(self):

        # # Delete playlists used in testing
        # playlist_object = Playlist(api_version_playlist)
        #
        # for playlist in self.playlist_id_list:
        #     result = playlist_object.delete_playlist_by_id(session = self.test_session,
        #                                                    baseurl = self.baseurl,
        #                                                    playlist_id = playlist )
        #     logging.debug("Deleted Playlist with ID = {} result = {}".format(playlist, result))
        #
        # # Delete workgroups
        #
        # workgroup_object = Workgroup(api_version_workgroups)
        #
        # for workgroup in self.workgroup_id_list:
        #     result = workgroup_object.delete_workgroup(session = self.test_session,
        #                                                baseurl = self.baseurl,
        #                                                workgroup_id = workgroup)
        #     logging.debug("Deleted workgroup with ID = {}  result = {}".format(workgroup, result))
        #
        # # Delete Categories
        # category_object = Category(api_version_category)
        #
        # for category in self.category_id_list:
        #     result = category_object.delete_category_by_id(session = self.test_session,
        #                                                    baseurl = self.baseurl,
        #                                                    category_id = category)
        #     logging.debug("Deleted category with ID = {}  result = {}".format(category, result))

        # # Delete media and messages and templates
        # media_object = Media(api_version_media)
        # for media in self.media_id_list: #+ self.message_id_list + self.template_id_list:
        #     result = media_object.delete_media_by_id(session = self.test_session,
        #                                              baseurl = self.baseurl,
        #                                              id = media)
        #     logging.debug("Deleted Media with id = {} result = {}".format(media,result))

        self.api_auth_object.logout()



    def test_setup(self):
        pass

    def update_playlist_name(self, counter):
        return playlist

    def test_cm_9964(self):
        playlist_name_counter = 0
        playlist_name = self.unique_name + " playlist " + str(playlist_name_counter)
        playlist_object = Playlist(api_version_playlist)
        playlist_id_list=[]

        # Create first playlist
        playlist_object.create_playlist(session = self.test_session,
                                    baseurl = self.baseurl,
                                    name = playlist_name,
                                    description = self.unique_name,
                                    )
        playlist_id_list.append(playlist_object.get_id())

        playlist_object.create_playlist(session = self.test_session,
                                        baseurl = self.baseurl,
                                        name = playlist_name,
                                        description = self.unique_name,
                                        )

        playlist_id_list.append(playlist_object.get_id())