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

n=3

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

        # # Create 3 templates
        # for template in [config['template_items']['templatefile_6'], config['template_items']['templatefile_7'],
        #                  config['template_items']['templatefile_8']]:
        #     file_up_template = File_upload(api_version_fileupload)
        #
        #     file_up_template.initiate_upload(session=self.test_session, baseurl=baseurl, local_file_name=template,
        #                                      file_upload_path=self.unique_name)
        #
        #     # Upload File
        #     uuid = file_up_template.get_response_key('uuid')
        #     self.template_id_list.append(file_up_template.get_response_key('mediaId'))
        #     file_up_template.upload_file_part(session=self.test_session, baseurl=baseurl, local_file_name=template,
        #                                       local_file_path=config['path']['templates'], uuid=uuid)
        #
        #     # Commit Upload
        #     file_up_template.upload_finished(session=self.test_session, baseurl=baseurl, uuid=uuid)

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

        # # Create 3 messages based on the three templates
        # for message_number in range(len(self.template_id_list)):
        #     message_object = Message(api_version_messages)
        #     message_name = namespace + ' Message for template ' + str(message_number)
        #     caption = 'Caption for message ' + str(message_number)
        #     fields = [{'name': 'photo', 'value': self.media_id_list[message_number], 'type': 'IMAGE'},
        #               {'name': 'caption', 'value': caption}]
        #     message_object.create_message(session=self.test_session,
        #                                   baseurl=baseurl,
        #                                   name=message_name,
        #                                   template_id=self.template_id_list[message_number],
        #                                   fields=fields)
        #     self.message_id_list.append(message_object.get_response_key('id'))
        #
        # logging.debug('Created {} messages with ids of {}'.format(len(self.message_id_list), self.message_id_list))

        # Create 2 categories
        self.category_id_list = []
        category_obj = Category(api_version_category)
        category_obj.create_category(session = self.test_session,
                                     baseurl = self.baseurl,
                                     description = self.unique_name,
                                     name = self.unique_name + "c1",
                                     )

        self.category_id_list.append(category_obj.get_response_key('id'))

        category_obj.create_category(session = self.test_session,
                                     baseurl = self.baseurl,
                                     description = self.unique_name,
                                     name = self.unique_name + "c2",
                                     )

        self.category_id_list.append(category_obj.get_response_key('id'))

        # Create 2 workgroups
        self.workgroup_id_list = []
        workgroup_object = Workgroup(api_version_workgroups)
        workgroup_object.create_workgroup(session = self.test_session,
                                          baseurl = self.baseurl,
                                          name = self.unique_name + "w1")

        self.workgroup_id_list.append(workgroup_object.get_response_key('id'))


        workgroup_object.create_workgroup(session = self.test_session,
                                          baseurl = self.baseurl,
                                          name = self.unique_name + "w2")

        self.workgroup_id_list.append(workgroup_object.get_response_key('id'))

        # Create two playlists for this test - one playlist and one subplaylist
        playlist_object = Playlist(api_version_playlist)
        self.playlist_id_list = []
        playlist_name_1 = self.unique_name + " playlist 1"
        playlist_name_2 = self.unique_name + " playlist 2"

        playlist_object.create_playlist(session = self.test_session,
                                        baseurl = self.baseurl,
                                        name = playlist_name_1,
                                        description = self.unique_name,
                                        )

        self.playlist_id_list.append(playlist_object.get_response_key("id"))

        playlist_object.create_playlist(session = self.test_session,
                                        baseurl = self.baseurl,
                                        name = playlist_name_2,
                                        description = self.unique_name)

        self.playlist_id_list.append(playlist_object.get_response_key('id'))

        time.sleep(3)

        # Fill the playlists
        for media in self.media_id_list:
            playlist_object.add_media_to_normal_playlist(session = self.test_session,
                                                     baseurl = self.baseurl,
                                                     playlist_id = self.playlist_id_list[0],
                                                     media_id = media)
            logging.debug("Added media with id  = {} to playlist with id = {}".format(media,self.playlist_id_list[0]))
        #
        # for message in self.message_id_list:
        #     playlist_object.add_media_to_normal_playlist(session = self.test_session,
        #                                                  baseurl = self.baseurl,
        #                                                  playlist_id = self.playlist_id_list[0],
        #                                                  media_id = message)
        #     logging.debug("Added message with id  = {} to playlist with id = {}".format(message,self.playlist_id_list[0]))

        # Add subplaylist
        playlist_object.add_subplaylist_to_playlist(session = self.test_session,
                                                    baseurl = self.baseurl,
                                                    playlist_id = self.playlist_id_list[0],
                                                    name = playlist_name_1,
                                                    subplaylistId= self.playlist_id_list[1])


        # Assert that the setup is complete by counting the number of entries in the final playlist

        playlist_object.find_normal_playlist_by_id(session = self.test_session,
                                                   baseurl = self.baseurl,
                                                   playlist_id = self.playlist_id_list[0])
        assert playlist_object.last_response.status_code == 200
        number_of_playlist_items = len(playlist_object.get_response_key("playlistItems"))
        logging.debug("Expected 4 items in playlist.  Found {}".format(number_of_playlist_items))
        assert number_of_playlist_items == 4, "Expected 7 items in test playlsit.  Found " + str(number_of_playlist_items)

        # Update category and workgroup settings on playlist
        playlist_object.find_normal_playlist_by_id(session = self.test_session,
                                                   baseurl = self.baseurl,
                                                   playlist_id = self.playlist_id_list[0])
        dto = playlist_object.last_response.json()

        dto['workgroups']=[{'id':self.workgroup_id_list[0],'owner':True}]
        dto['categories']=[{'id':self.category_id_list[0]}]

        playlist_object.update_playlist(session  = self.test_session,
                                        baseurl = self.baseurl,
                                        playlist_id = self.playlist_id_list[0],
                                        field_change_dict=dto)
    #                                        field_change_dict={'name': playlist_name_1,'workgroups':[{'id':self.workgroup_id_list[0],'owner':True}],'categories':[{'id':self.category_id_list[0]}]})



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

    @parameterized([
    #    param("name", "blubbosnubbo"), NOte: Name is tested in every other instance and does not need it's own test
       param("controlledByAdManager",True),
       param("description","hogobogologonogo"),
       param("htmlDuration", 92),
       param("imageDuration", 91),
       param("maxDuration", 3),
       param("minDuration", 13),
       param("pickPolicy", "SHUFFLE"),
    #     "playlistType": "MEDIA_PLAYLIST",
    #    param("transition", {'positionY': 0, 'positionX': 14, 'id': 5, 'name': 'Dissolve'}),
        param("transitionDuration", 13)
    ])
    def test_modify_playlist(self, p_key,p_value):
        """
        This test validates that the preceding parameterized list of values can be modified by the /api/rest/playlists/<id>/partial
        call:
        :param p_key:
        :param p_value:
        :return:
        """
        logging.debug("Now modifying playlist {} to be {}".format(p_key,p_value))
        playlist_obj = Playlist(api_version_playlist)
        fields = None# 'id,name,controlledByAdManager,playlistType,pickPolicy,transitionDuration,readOnly,healthy'
        playlist_obj.find_normal_playlist_by_id(session = self.test_session,
                                                baseurl = self.baseurl,
                                                playlist_id = self.playlist_id_list[0],
                                                fields = fields)
        playlist_dto = playlist_obj.last_response.json()

        logging.debug("Found playlist under test: {}".format(playlist_dto))
        playlist_dto.pop('id') #The ID is a system field which is always returned
        try:
            playlist_dto.pop(p_key)
        except KeyError:
            logging.debug("Did not find {} in playlist dto - may be optional field".format(p_key))

        logging.debug("playlist dto after id removed is: {}".format(playlist_dto))
        playlist_dto[p_key] = p_value # Replace the key under test with the test parameter
        playlist_dto["name"] = p_key + " test"

        logging.debug(logging.debug("Modifying playlist_under test: {}".format(playlist_dto)))

        assert playlist_obj.update_partial_playlist(session = self.test_session,
                                                    baseurl = self.baseurl,
                                                    playlist_id = self.playlist_id_list[0],
                                                    playlist = playlist_dto)

        playlist_obj.find_normal_playlist_by_id(session = self.test_session,
                                                baseurl = self.baseurl,
                                                playlist_id = self.playlist_id_list[0])

        if type(p_value) is dict:
            #This is ugly but a good way to compare the two dicts.  Create a hash and make sure digests are the same.
            #Hey!  This doesn't work.  I'll do this another way.
            p_value_string = json.dumps(p_value, sort_keys = True)
            playlist_value_string = json.dumps(playlist_obj.get_json_data()[p_key], sort_keys = True)
            logging.debug('compare two dicts {} and {}'.format(p_value_string,playlist_value_string))
            one = hashlib.sha1(bytes(p_value_string,'ascii')).hexdigest()
            two = hashlib.sha1(bytes(playlist_value_string,'ascii')).hexdigest
            assert one == two, 'Hashes of dicts found in playlist did not match'
        else:
            logging.info("After test, expected value of {} to be {} but found {}".format(p_key,p_value,str(playlist_obj.get_response_key(p_key))))
            assert playlist_obj.get_response_key(p_key) == p_value , "Expected value of " + p_key + " to be " + str(p_value) +" but found " + str(playlist_obj.get_response_key(p_key))

        number_of_items_in_playlist = len(playlist_obj.get_response_key("playlistItems"))

        assert number_of_items_in_playlist == 4, "Did not find 4 items in playlist after partial modify"

    def test_modify_category(self):
        """
        This test validates that the category value can be modified by the /api/rest/playlists/<id>/partial
        Note:  This test does NOT check for any changes except that playlistItems are not removed by the call
        call:
        :param p_key:
        :param p_value:
        :return:
        """
        logging.debug("Now modifying playlist category to be {}")

        # Use call to /api/rest/playlists/id/partial to modify the category on playlist 1 to catagory 2
        playlist_dto = {}
        playlist_dto["name"] = "category test"
        playlist_dto['categories']=[{'id':self.category_id_list[1]}] # Note - this should change the category
        playlist_obj = Playlist(api_version_playlist)
        assert playlist_obj.update_partial_playlist(session = self.test_session,
                                                    baseurl = self.baseurl,
                                                    playlist_id = self.playlist_id_list[0],
                                                    playlist = playlist_dto)

        # Assert that the setup is complete by counting the number of entries in the final playlist

        playlist_obj.find_normal_playlist_by_id(session = self.test_session,
                                                   baseurl = self.baseurl,
                                                   playlist_id = self.playlist_id_list[0])
        assert playlist_obj.last_response.status_code == 200
        number_of_playlist_items = len(playlist_obj.get_response_key("playlistItems"))
        logging.debug("Expected 4 items in playlist.  Found {}".format(number_of_playlist_items))
        assert number_of_playlist_items == 4, "Expected 7 items in test playlsit.  Found " + str(number_of_playlist_items)


    def test_modify_workgroup(self):
        """
        This test validates that the category value can be modified by the /api/rest/playlists/<id>/partial
        Note:  This test does NOT check for any changes except that playlistItems are not removed by the call
        call:
        :param p_key:
        :param p_value:
        :return:
        """

        # Use call to /api/rest/playlists/id/partial to modify the category on playlist 1 to catagory 2
        playlist_dto = {}
        playlist_dto["name"] = "workgroup test"
        playlist_dto['workgroups']=[{'id':self.workgroup_id_list[1],'owner':True}] # This should change the workgroup
        playlist_obj = Playlist(api_version_playlist)
        assert playlist_obj.update_partial_playlist(session = self.test_session,
                                                    baseurl = self.baseurl,
                                                    playlist_id = self.playlist_id_list[0],
                                                    playlist = playlist_dto)

        # Assert that the setup is complete by counting the number of entries in the final playlist

        playlist_obj.find_normal_playlist_by_id(session = self.test_session,
                                                baseurl = self.baseurl,
                                                playlist_id = self.playlist_id_list[0])
        assert playlist_obj.last_response.status_code == 200
        number_of_playlist_items = len(playlist_obj.get_response_key("playlistItems"))
        logging.debug("Expected 4 items in playlist.  Found {}".format(number_of_playlist_items))
        assert number_of_playlist_items == 4, "Expected 4 items in test playlsit.  Found " + str(number_of_playlist_items)

    def test_modify_only_name(self):
        playlist_dto = {}
        playlist_dto["name"] = "NameOnly"
        playlist_obj = Playlist(api_version_playlist)
        assert playlist_obj.update_partial_playlist(session = self.test_session,
                                                    baseurl = self.baseurl,
                                                    playlist_id = self.playlist_id_list[0],
                                                    playlist = playlist_dto)

        playlist_obj.find_normal_playlist_by_id(session = self.test_session,
                                                baseurl = self.baseurl,
                                                playlist_id = self.playlist_id_list[0])
        assert playlist_obj.last_response.status_code == 200
        number_of_playlist_items = len(playlist_obj.get_response_key("playlistItems"))
        logging.debug("Expected 4 items in playlist.  Found {}".format(number_of_playlist_items))
        assert number_of_playlist_items == 4, "Expected 4 items in test playlist.  Found " + str(number_of_playlist_items)

class test_cm_9703():
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

        # # Create 3 templates
        # for template in [config['template_items']['templatefile_6'], config['template_items']['templatefile_7'],
        #                  config['template_items']['templatefile_8']]:
        #     file_up_template = File_upload(api_version_fileupload)
        #
        #     file_up_template.initiate_upload(session=self.test_session, baseurl=baseurl, local_file_name=template,
        #                                      file_upload_path=self.unique_name)
        #
        #     # Upload File
        #     uuid = file_up_template.get_response_key('uuid')
        #     self.template_id_list.append(file_up_template.get_response_key('mediaId'))
        #     file_up_template.upload_file_part(session=self.test_session, baseurl=baseurl, local_file_name=template,
        #                                       local_file_path=config['path']['templates'], uuid=uuid)
        #
        #     # Commit Upload
        #     file_up_template.upload_finished(session=self.test_session, baseurl=baseurl, uuid=uuid)

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

        # Create two playlists for this test - one playlist and one subplaylist
        playlist_object = Playlist(api_version_playlist)
        self.playlist_id_list = []
        playlist_name_1 = self.unique_name + " playlist 1"
        playlist_name_2 = self.unique_name + " playlist 2"

        playlist_object.create_playlist(session = self.test_session,
                                        baseurl = self.baseurl,
                                        name = playlist_name_1,
                                        description = self.unique_name,
                                        )

        self.playlist_id_list.append(playlist_object.get_response_key("id"))

        playlist_object.create_playlist(session = self.test_session,
                                        baseurl = self.baseurl,
                                        name = playlist_name_2,
                                        description = self.unique_name)

        self.playlist_id_list.append(playlist_object.get_response_key('id'))

        # Create Player Groups
        self.player_group_id_list = []
        player_group_obj = PlayerGroup(api_version_player_group)

        player_group_obj.create_player_group(session = self.test_session,
                                             baseurl = self.baseurl,
                                             name = self.unique_name + " pg1")

        self.player_group_id_list.append(player_group_obj.get_response_key('id'))

        player_group_obj.create_player_group(session = self.test_session,
                                             baseurl = self.baseurl,
                                             name = self.unique_name + " pg2")

        self.player_group_id_list.append(player_group_obj.get_response_key('id'))

        # Create Player for testing
        player_obj = Player(api_version_player)
        self.player_id_list = []

        player_obj.create_player(session = self.test_session,
                                 baseurl = self.baseurl,
                                 name = self.unique_name + " p1")
        self.player_id_list.append(player_obj.get_response_key('id'))

        # # Fill the playlists
        # for media in self.media_id_list:
        #     playlist_object.add_media_to_normal_playlist(session = self.test_session,
        #                                                  baseurl = self.baseurl,
        #                                                  playlist_id = self.playlist_id_list[0],
        #                                                  media_id = media)
        #     logging.debug("Added media with id  = {} to playlist with id = {}".format(media,self.playlist_id_list[0]))
        #
        # # Add subplaylist
        # playlist_object.add_subplaylist_to_playlist(session = self.test_session,
        #                                             baseurl = self.baseurl,
        #                                             playlist_id = self.playlist_id_list[0],
        #                                             name = playlist_name_1,
        #                                             subplaylistId= self.playlist_id_list[1])


        # # Assert that the setup is complete by counting the number of entries in the final playlist
        #
        # playlist_object.find_normal_playlist_by_id(session = self.test_session,
        #                                            baseurl = self.baseurl,
        #                                            playlist_id = self.playlist_id_list[0])
        # assert playlist_object.last_response.status_code == 200
        # number_of_playlist_items = len(playlist_object.get_response_key("playlistItems"))
        # logging.debug("Expected 4 items in playlist.  Found {}".format(number_of_playlist_items))
        # assert number_of_playlist_items == 4, "Expected 7 items in test playlsit.  Found " + str(number_of_playlist_items)



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
    def test_add_n_media_item(self):
        playlist_object = Playlist(api_version_playlist)

        sd = datetime.datetime(2014,1,1)
        media_index = 1
        for i in range(n):

            sd = sd + datetime.timedelta(days = 1)
            ed = sd + datetime.timedelta(days = 1)
            logging.debug('index into media_id_list is : {}'.format(media_index))
            logging.debug('cirremt od of media_id_list is : {}'.format(media_index % len(self.media_id_list)))
            media_item_dto = playlist_object.getDefaultPlaylistItem(playlistItemType.MEDIA_ITEM,
                                                            item_id = self.media_id_list[media_index % len(self.media_id_list)],
                                                            player_id = self.player_id_list[0],
                                                            player_group_id = self.player_group_id_list[0],
                                                            start_date = str(sd),
                                                            end_date = str(ed))
            media_index += 1
            assert playlist_object.append_playlistItem(session = self.test_session,
                                            baseurl = self.baseurl,
                                            playlist_id = self.playlist_id_list[0],
                                            playlist_item_dto=media_item_dto),'Did not receive 200 when appending playlist'

        playlist_object.find_normal_playlist_by_id(session = self.test_session,
                                                   baseurl = self.baseurl,
                                                   playlist_id = self.playlist_id_list[0])

        number_of_playlist_items = len(playlist_object.get_response_key('playlistItems'))
        assert number_of_playlist_items == n, 'found incorrect number of playlist items after run.  Expected 1000, found: ' + str(number_of_playlist_items)

    def test_add_n_sub_playlists(self):
        playlist_object = Playlist(api_version_playlist)
        sd = datetime.datetime(2016, 1, 1)
        media_index = 1
        for i in range(n):
            sd = sd + datetime.timedelta(days = 1)
            ed = sd + datetime.timedelta(days = 1)
            logging.debug('index into media_id_list is : {}'.format(media_index))
            logging.debug('cirremt od of media_id_list is : {}'.format(media_index % len(self.media_id_list)))
            playlist_item_dto = playlist_object.getDefaultPlaylistItem(playlistItemType.SUB_PLAYLIST,
                                                                    item_id = self.playlist_id_list[1],
                                                                    player_id = self.player_id_list[0],
                                                                    player_group_id = self.player_group_id_list[0],
                                                                    start_date = str(sd),
                                                                    end_date = str(ed))
            media_index += 1
            assert playlist_object.append_playlistItem(session = self.test_session,
                                                baseurl = self.baseurl,
                                                playlist_id = self.playlist_id_list[0],
                                                playlist_item_dto=playlist_item_dto), "Did not receive 200 when appending to playlist"
            elapsed_timedelta = playlist_object.last_response.elapsed
            #logging.info("APPENDTIME {} days {} seconds {} microseconds".format(elapsed_timedelta.days,elapsed_timedelta.seconds,elapsed_timedelta.microseconds))
            elapsed_seconds = elapsed_timedelta.seconds + elapsed_timedelta.microseconds/1000000
            logging.info("APPENDTIME for !{}! record is !{}! seconds ! response !{}".format(i, elapsed_seconds,playlist_object.last_response.status_code))

        # playlist_object.find_normal_playlist_by_id(session = self.test_session,
        #                                            baseurl = self.baseurl,
        #                                            playlist_id = self.playlist_id_list[0])



        #number_of_playlist_items = len(playlist_object.get_response_key('playlistItems'))
        #assert number_of_playlist_items == n, 'Found incorrect number of playlist items after run.  Expected 1000, found: ' + str(number_of_playlist_items)


    #@nottest
    def test_add_n_sub_playlists_old_method(self):
        """
        Add to the system n subplaylists, where N is intended to be large.  Use the /api/rest/playlists api call to make the changes, pulling
        down the dto each time, and adding another subplaylist to it.  This is expected to scale less well than the previous test
        :return:
        """

        playlist_obj = Playlist(api_version_playlist)

        sd = datetime.datetime(2016,1,1)
        media_index = 1

        for i in range(n):
            sd = sd + datetime.timedelta(days = 1)
            ed = sd + datetime.timedelta(days = 1)
            new_playlist_item = {"playlistItemType":"SUB_PLAYLIST",
                                 "subplaylist": {"id": self.playlist_id_list[1]},
                                 "startValidDate": str(sd),
                                 "endValidDate": str(ed),
                                 "useValidRange": True,
                                 "conditions": [{'comparator': 'IS', 'hasChanged': True, 'type':'PLAYER_GROUP', 'value': self.player_group_id_list[0]},
                                                {'comparator': 'IS', 'hasChanged': True, 'type':'PLAYER_NAME', 'value': self.player_id_list[0]},
                                                {'comparator': 'IS', 'hasChanged': True, 'type':'CHANNEL_DISPLAY', 'value': "Display 1"}],
                                 "timeSchedules": [{'days': ["SUNDAY", "THURSDAY", "FRIDAY", "SATURDAY"],
                                                    'endTime': "12:00",
                                                    'hasChanged': True,
                                                    'showRemove': True,
                                                    'startTime': "00:00"},
                                                   {'days': ["SUNDAY", "MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY"],
                                                    'endTime': "24:00",
                                                    'hasChanged': True,
                                                    'showRemove': True,
                                                    'startTime': "12:01"}]}
            assert playlist_obj.find_normal_playlist_by_id(session = self.test_session,
                                                             baseurl = self.baseurl,
                                                             playlist_id = self.playlist_id_list[0])

            playlist_dto = playlist_obj.last_response.json()

            if 'playlistItems' in playlist_dto:
                playlist_dto['playlistItems'].append(new_playlist_item)
            else:
                playlist_dto['playlistItems'] = new_playlist_item

            playlist_obj.update_playlist(session = self.test_session,
                                         baseurl = self.baseurl,
                                         playlist_id = self.playlist_id_list[0],
                                         field_change_dict=playlist_dto)

            elapsed_timedelta = playlist_obj.last_response.elapsed
            #logging.info("REPLACETIME {} days {} seconds {} microseconds".format(elapsed_timedelta.days,elapsed_timedelta.seconds,elapsed_timedelta.microseconds))
            elapsed_seconds = elapsed_timedelta.seconds + elapsed_timedelta.microseconds/1000000
            logging.info("REPLACETIME for !{}! record is !{}! seconds ! response !{}".format(i, elapsed_seconds,playlist_obj.last_response.status_code))

    @nottest
    def test_specific_playlists_by_id_old_way(self):
        """
        Test to add a single playlist (sub_playlist_id) to a master playlist (master_playlist_id) and record the time using the old api-
        PUT /api/rest/playlists/<id> and the full DTO

        This test case should NOT be run in the suite, as it relies on knowing specific ID's for specific playlits.
        :return:
        """
        master_playlist_id = 37
        sub_playlist_id = 41
        playlist_obj = Playlist(api_version_playlist)
        new_playlist_item = {"playlistItemType":"SUB_PLAYLIST",
                             "subplaylist": {"id": sub_playlist_id},
                             "useValidRange": False}
        assert playlist_obj.find_normal_playlist_by_id(session = self.test_session,
                                                       baseurl = self.baseurl,
                                                       playlist_id = master_playlist_id)

        playlist_dto = playlist_obj.last_response.json()
        item_count_before = playlist_dto['itemCount']

        if 'playlistItems' in playlist_dto:
            playlist_dto['playlistItems'].append(new_playlist_item)
        else:
            playlist_dto['playlistItems'] = new_playlist_item

        playlist_obj.update_playlist(session = self.test_session,
                                     baseurl = self.baseurl,
                                     playlist_id = master_playlist_id,
                                     field_change_dict=playlist_dto)


        elapsed_timedelta = playlist_obj.last_response.elapsed
        #logging.info("REPLACETIME {} days {} seconds {} microseconds".format(elapsed_timedelta.days,elapsed_timedelta.seconds,elapsed_timedelta.microseconds))
        elapsed_seconds = elapsed_timedelta.seconds + elapsed_timedelta.microseconds/1000000
        logging.info("SINGLE_REPLACE for master id={} and slave id = {} record is !{}! seconds ! response !{}".format(master_playlist_id,sub_playlist_id, elapsed_seconds,playlist_obj.last_response.status_code))

        playlist_obj.find_normal_playlist_by_id(session = self.test_session,
                                                baseurl = self.baseurl,
                                                playlist_id = master_playlist_id,
                                                fields = "id,itemCount")

        item_count_after = playlist_obj.get_response_key('itemCount')
        logging.info("before item count = {}.  After item count = {}".format(item_count_before,item_count_after))
        assert item_count_before == (item_count_after -1), "Expected " + str(item_count_before +1) + "items in playlist but found " + str(item_count_after)

    @nottest
    def test_specific_playlists_by_id_new_way(self):
        """
        Test to add a single playlist (sub_playlist_id) to a master playlist (master_playlist_id) and record the time using the old api-
        PUT /api/rest/playlists/<id> and the full DTO

        This test case should NOT be run in the suite, as it relies on knowing specific ID's for specific playlits.
        :return:
        """
        master_playlist_id = 37
        sub_playlist_id = 41
        playlist_obj = Playlist(api_version_playlist)
        new_playlist_item = {"playlistItemType":"SUB_PLAYLIST",
                             "subplaylist": {"id": sub_playlist_id},
                             "useValidRange": False}
        assert playlist_obj.find_normal_playlist_by_id(session = self.test_session,
                                                       baseurl = self.baseurl,
                                                       playlist_id = master_playlist_id)

        playlist_dto = playlist_obj.last_response.json()
        item_count_before = playlist_dto['itemCount']

        if 'playlistItems' in playlist_dto:
            playlist_dto['playlistItems'].append(new_playlist_item)
        else:
            playlist_dto['playlistItems'] = new_playlist_item

        playlist_obj.append_playlistItem(session = self.test_session,
                                     baseurl = self.baseurl,
                                     playlist_id = sub_playlist_id,
                                     playlist_item_dto=new_playlist_item)


        elapsed_timedelta = playlist_obj.last_response.elapsed
        #logging.info("REPLACETIME {} days {} seconds {} microseconds".format(elapsed_timedelta.days,elapsed_timedelta.seconds,elapsed_timedelta.microseconds))
        elapsed_seconds = elapsed_timedelta.seconds + elapsed_timedelta.microseconds/1000000
        logging.info("SINGLE_REPLACE for master id={} and slave id = {} record is !{}! seconds ! response !{}".format(master_playlist_id,sub_playlist_id, elapsed_seconds,playlist_obj.last_response.status_code))

        playlist_obj.find_normal_playlist_by_id(session = self.test_session,
                                                baseurl = self.baseurl,
                                                playlist_id = master_playlist_id,
                                                fields = "id,itemCount")

        item_count_after = playlist_obj.get_response_key('itemCount')
        logging.info("before item count = {}.  After item count = {}".format(item_count_before,item_count_after))
        assert item_count_before == (item_count_after -1), "Expected " + str(item_count_before +1) + "items in playlist but found " + str(item_count_after)

class test_dot2dot_cm_9704():
    """
    Test fixture to validate CM-9704 -
    DELETE /api/rest/playlists/{id}/playlistItems/{playlistItemId}
    """

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

        # Create two playlists for this test - one playlist and one subplaylist
        playlist_object = Playlist(api_version_playlist)
        self.playlist_id_list = []
        playlist_name_1 = self.unique_name + " playlist 1"
        playlist_name_2 = self.unique_name + " playlist 2"

        playlist_object.create_playlist(session = self.test_session,
                                        baseurl = self.baseurl,
                                        name = playlist_name_1,
                                        description = self.unique_name,
                                        )

        self.playlist_id_list.append(playlist_object.get_response_key("id"))

        playlist_object.create_playlist(session = self.test_session,
                                        baseurl = self.baseurl,
                                        name = playlist_name_2,
                                        description = self.unique_name)

        self.playlist_id_list.append(playlist_object.get_response_key('id'))
        # Fill the playlists
        for media in self.media_id_list:
            playlist_object.add_media_to_normal_playlist(session = self.test_session,
                                                         baseurl = self.baseurl,
                                                         playlist_id = self.playlist_id_list[0],
                                                         media_id = media)
            logging.debug("Added media with id  = {} to playlist with id = {}".format(media,self.playlist_id_list[0]))

        # Add subplaylist
        playlist_object.add_subplaylist_to_playlist(session = self.test_session,
                                                    baseurl = self.baseurl,
                                                    playlist_id = self.playlist_id_list[0],
                                                    name = playlist_name_1,
                                                    subplaylistId= self.playlist_id_list[1])


        # Assert that the setup is complete by counting the number of entries in the final playlist

        playlist_object.find_normal_playlist_by_id(session = self.test_session,
                                                   baseurl = self.baseurl,
                                                   playlist_id = self.playlist_id_list[0])
        assert playlist_object.last_response.status_code == 200
        number_of_playlist_items = len(playlist_object.get_response_key("playlistItems"))
        logging.debug("Expected 4 items in playlist.  Found {}".format(number_of_playlist_items))
        assert number_of_playlist_items == 4, "Expected 4 items in test playlist.  Found " + str(number_of_playlist_items)


    def teardown(self):
        self.api_auth_object.logout()

    def test_delete_subplaylist(self):
        """
        Delete the subplaylist from the master playlist
        :return:
        """

        playlist_obj = Playlist(api_version_playlist)
        playlist_obj.list_all_available_playlist_items(session = self.test_session,
                                                       baseurl = self.baseurl,
                                                       playlist_id = self.playlist_id_list[0],
                                                       fields = "id,sortOrder,media,subPlaylist")

        playlist_items = playlist_obj.last_response.json()
        num_deleted = 0
        for item in playlist_items['list']:
            if "subplaylist" in item:
                logging.debug("PlaylistItem id = {} is a sub-playlist.  Deleting")
                num_deleted += 1
                assert playlist_obj.delete_media_from_normal_playlist(session = self.test_session,
                                                               baseurl = self.baseurl,
                                                               playlist_id= self.playlist_id_list[0],
                                                               playlist_item_id= item['id'])

                assert playlist_obj.find_normal_playlist_by_id(session = self.test_session,
                                                        baseurl = self.baseurl,
                                                        playlist_id = self.playlist_id_list[0],
                                                        fields = 'id,name,itemCount,playlistItems')
                logging.debug("num_deleted = {}, itemCount = {}".format(num_deleted,
                                                                        playlist_obj.get_response_key('itemCount')))
                assert playlist_obj.get_response_key('itemCount') == len(playlist_items['list']) - num_deleted,"Expected " + str(len(playlist_items['list']) - num_deleted) + " items in playlist, but found " + playlist_obj.get_response_key('itemCount')
            else:
                logging.debug("Item is not a playlist playlist item id = {}".format(item['id']))


    def test_delete_media(self):
        """
        Test that the playlist media items are correctly deleted
        :return:
        """

        playlist_obj = Playlist(api_version_playlist)
        playlist_obj.list_all_available_playlist_items(session = self.test_session,
                                                       baseurl = self.baseurl,
                                                       playlist_id = self.playlist_id_list[0],
                                                       fields = "id,sortOrder,media,subPlaylist")

        playlist_items = playlist_obj.last_response.json()
        num_deleted = 0
        for item in playlist_items['list']:
            if "media" in item:
                logging.debug("PlaylistItem id = {} is a media.  Deleting")
                num_deleted += 1
                assert playlist_obj.delete_media_from_normal_playlist(session = self.test_session,
                                                                      baseurl = self.baseurl,
                                                                      playlist_id= self.playlist_id_list[0],
                                                                      playlist_item_id= item['id'])

                assert playlist_obj.find_normal_playlist_by_id(session = self.test_session,
                                                               baseurl = self.baseurl,
                                                               playlist_id = self.playlist_id_list[0],
                                                               fields = 'id,name,itemCount,playlistItems')
                logging.debug("num_deleted = {}, itemCount = {}".format(num_deleted,
                                                                        playlist_obj.get_response_key('itemCount')))
                assert playlist_obj.get_response_key('itemCount') == len(playlist_items['list']) - num_deleted,"Expected " + str(len(playlist_items['list']) - num_deleted) + " items in playlist, but found " + playlist_obj.get_response_key('itemCount')
            else:
                logging.debug("Item is not a playlist playlist item id = {}".format(item['id']))


