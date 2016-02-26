__author__ = 'rkaye'


from nose import with_setup
from nose.tools import nottest
import logging
import logging.config
import configparser
from framework.constants import CONFIG_FILE_PATH, LOG_FILE_PATH, metadata_data_type, PERF_LOG_FILE_PATH, PERF_TEST_RESULTS_FILE_PATH
from framework.authentication_rest import login, logout, get_auth_token
from framework.http_rest import *
from framework.hosted_networks_rest import Hosted_Networks
from framework.fileupload_rest import File_upload
from framework.templates_rest import Templates
from framework.media_rest import Media
from framework.channel_rest import Channels
from framework.frameset_template_rest import Frameset_template
from framework.player_rest import Player
from framework.message_rest import Message
from framework.media_metadata_rest import Media_meta_data
from framework.storage_rest import Storage
from framework.heartbeats_rest import Heartbeats
from framework.heartbeats_rest import Heartbeat_event
from framework.player_health_rest import Player_Health
from framework.playlist_rest import Playlist
from framework.authentication_api_rest import Auth_api
from framework.category_rest import Category
from framework.workgroup_rest import Workgroup
from framework.playergroup_rest import Player_group
from framework.distributions_rest import Distribution
from framework.misc_rest import Misc
import inspect
import csv
import json
from statistics import median
import yaml

from datetime import timedelta
import time

config = configparser.ConfigParser()
config.read(CONFIG_FILE_PATH)
baseurl = config['login']['baseurl']
logging.config.fileConfig(LOG_FILE_PATH)
logging.debug('Logging config file path is: {}'.format(CONFIG_FILE_PATH))
#session = requests.Session()
namespace = config['test']['namespace']
try:
    num_players = config['performance']['num_players']
except ValueError:
    num_players = 0

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
api_version_distribution = config['api_info']['api_version_distribution']
api_version_miscellaneous = config['api_info']['api_version_miscellaneous']
api_version_authorization = config['api_info']['api_version_authorization']

template_id = 0
frameset_id = 0
channel_id = 0
player_id = 0
player_name = ""
player_description = ""
channel_name = ""
media_id = 0
n = 10

def this_function_name():
    return inspect.stack()[1][3]

def timedelta_milliseconds(td):
    return td.days*86400000 + td.seconds*1000 + td.microseconds/1000

class test_playlist_pages_performance_yaml:
    '''
    Test for the series of calls which are used by the UI to check playlist Properties.  This class will run each
    of the filtered calls used by Indy
    '''
    template_id_list = []
    media_id_list = []
    message_id_list = []
    playlist_id_list = []
    url_list = []

    @classmethod
    def setup_class(self):

        # Begin by initiating a new login session for this test case.
        logging.info('Beginning test setup')
        baseurl = config['login']['baseurl']
        username = config['login']['username']
        password = config['login']['password']
        logging.debug('Read login info from config file and ready to begin.')
        logging.info('Initializing session for test module setup.')

        session = login(username,password,baseurl)

        # Create 3 templates
        for template in [config['template_items']['templatefile_6'],config['template_items']['templatefile_7'],config['template_items']['templatefile_8']]:
            file_up_template = File_upload(api_version_fileupload)

            file_up_template.initiate_upload(session = session, baseurl=baseurl, local_file_name=template,
                                   file_upload_path=namespace + this_function_name())

            # Upload File
            uuid = file_up_template.get_response_key('uuid')
            self.template_id_list.append(file_up_template.get_response_key('mediaId'))
            file_up_template.upload_file_part(session = session, baseurl=baseurl, local_file_name=template,
                                    local_file_path=config['path']['templates'], uuid=uuid)

            # Commit Upload
            file_up_template.upload_finished(session = session, baseurl=baseurl, uuid=uuid)

        # Upload 3 media items
        for media_item in [config['media_items']['mediafile_1'],config['media_items']['mediafile_2'],config['media_items']['mediafile_3']]:
               # Create a media item for use in this test suite
                file_up = File_upload(api_version_fileupload)

                # Initiate Upload of media item
                file_up.initiate_upload(session = session,baseurl=baseurl, local_file_name= media_item, file_upload_path= namespace)

                uuid = file_up.get_response_key('uuid')
                self.media_id_list.append(file_up.get_response_key('mediaId'))

                # Upload file part
                file_up.upload_file_part(session=session, baseurl=baseurl, local_file_name=media_item,
                                local_file_path=config['path']['media'], uuid=uuid)

                #time.sleep(1)

                # Commit Upload
                file_up.upload_finished(session=session, baseurl=baseurl, uuid=uuid)

        # IF I do not wait for one second after uploading the media - presumably for the thumbnails to land - the message creation
        # Will hose the media object -upload not complete.  Potential bug!
        time.sleep(1)

        # Create 3 messages based on the three templates
        for message_number in range(len(self.template_id_list)):
            message_object = Message(api_version_messages)
            message_name = namespace +' Message for template ' + str(message_number)
            caption = 'Caption for message ' + str(message_number)
            fields =[{'name':'photo','value':self.media_id_list[message_number],'type':'IMAGE'},{'name':'caption','value':caption}]
            message_object.create_message(session=session,
                                          baseurl = baseurl,
                                          name = message_name,
                                          template_id  = self.template_id_list[message_number],
                                          fields = fields)
            self.message_id_list.append(message_object.get_response_key('id'))

        logging.debug('Created {} messages with ids of {}'.format(len(self.message_id_list),self.message_id_list))

        # Create a Playlist which contains all three messages 18 times
        playlist_object = Playlist(api_version_playlist)
        playlist_name_a = 'Playlist_A ' + namespace
        description = namespace + " playlist used in this test case"

        playlist_object.create_playlist(session = session,
                                        baseurl = baseurl,
                                        name = playlist_name_a,
                                        description = description)
        self.playlist_id_list.append(playlist_object.get_response_key('id'))

        # Add all three messages to the playlist 18 times
        for n in range(18):
            for message_id in self.message_id_list:
                playlist_object.add_media_to_normal_playlist(session = session,
                                                         baseurl = baseurl,
                                                         playlist_id = self.playlist_id_list[0],
                                                         media_id = message_id)

        # Create a second Playlist and add the first playlist to it 18 times

        playlist_object = Playlist(api_version_playlist)
        playlist_name_b = 'Playlist_B ' + namespace

        playlist_object.create_playlist(session = session,
                                        baseurl = baseurl,
                                        name = playlist_name_b,
                                        description = description)
        self.playlist_id_list.append(playlist_object.get_response_key('id'))

        for n in range(18):
            playlist_object.add_subplaylist_to_playlist(session = session,
                                                    baseurl = baseurl,
                                                    name = playlist_name_b,
                                                    playlist_id = self.playlist_id_list[1],
                                                    subplaylistId= self.playlist_id_list[0])

        # Create a third playlist and add subplaylist B to it 18 times
        playlist_object = Playlist(api_version_playlist)
        playlist_name_c = 'Playlist_C ' + namespace

        playlist_object.create_playlist(session = session,
                                        baseurl = baseurl,
                                        name = playlist_name_c,
                                        description = description)
        self.playlist_id_list.append(playlist_object.get_response_key('id'))

        for n in range(18):
            playlist_object.add_subplaylist_to_playlist(session = session,
                                                    baseurl = baseurl,
                                                    name = playlist_name_c,
                                                    playlist_id = self.playlist_id_list[2],
                                                    subplaylistId= self.playlist_id_list[1])

        # Add one more playlist and add playlist C to it.

        playlist_object = Playlist(api_version_playlist)
        playlist_name_d = 'Playlist_D ' + namespace

        playlist_object.create_playlist(session = session,
                                        baseurl = baseurl,
                                        name = playlist_name_d,
                                        description = description)
        self.playlist_id_list.append(playlist_object.get_response_key('id'))

        playlist_object.add_subplaylist_to_playlist(session = session,
                                                    baseurl = baseurl,
                                                    name = playlist_name_d,
                                                    playlist_id = self.playlist_id_list[3],
                                                    subplaylistId= self.playlist_id_list[2])

        logging.debug("Four playlists created for test with id: {}".format(self.playlist_id_list))

        # Setup log data
        data_headers =['Test results for test_playlist_properties','Average Response Time (ms)', 'Median Response Time (ms)', 'Min Response Time (ms)','Max Response Time(ms)']
        test_playlist_pages_performance_yaml.write_result(data_headers)




        logout(session,baseurl = baseurl)

    @classmethod
    def teardown_class(self):
        #Login to perform teardown
        logging.info('Beginning test setup')
        baseurl = config['login']['baseurl']
        username = config['login']['username']
        password = config['login']['password']
        logging.debug('Read login info from config file and ready to begin.')
        logging.info('Initializing session for test module setup.')

        session = login(username,password,baseurl)

        #Delete setup objects here

        playlist_object = Playlist(api_version_playlist)
        for playlist_id in self.playlist_id_list:
            playlist_object.delete_playlist_by_id(session = session,
                                                  baseurl = baseurl,
                                                  playlist_id = playlist_id)
            logging.debug('Deleting playlist id = {} for performance test status_code = {}'.format(playlist_id, playlist_object.last_response.status_code))

        media_object = Media(api_version_media)
        all_media_list = self.media_id_list + self.message_id_list
        for media_id in all_media_list:
            media_object.delete_media_by_id(session = session,
                                            baseurl = baseurl,
                                            id = media_id)

        #logout of session created for setup
        logout(session,baseurl = baseurl)

    def setup(self):
        #Login to perform teardown
        logging.info('Beginning test setup')
        baseurl = config['login']['baseurl']
        username = config['login']['username']
        password = config['login']['password']
        logging.debug('Read login info from config file and ready to begin.')
        logging.info('Initializing session for test module setup.')
        self.test_version = config['performance']['cm_sw_version']


        self.test_session = login(username,password,baseurl)
    def teardown(self):
        #logout of session created for setup
        logout(self.test_session,baseurl = baseurl)

    @classmethod
    def write_result(cls, data_list):
        with open(PERF_TEST_RESULTS_FILE_PATH,mode = 'a', newline = '') as csv_file:
        #with open('./logs/perf_log', mode = 'a', newline= '') as csv_file:
            result_writer = csv.writer(csv_file)#, delimiter=',')
            result_writer.writerow(data_list)

    def calculate_ave_median_min_max(self,list_of_numbers):
        average = sum(list_of_numbers) / len(list_of_numbers)
        max_values = max(list_of_numbers)
        min_values = min(list_of_numbers)
        median_result = median(list_of_numbers)
        return [average, median_result, min_values, max_values]

    def run_all_calls_in_yaml_section(self, yaml_doc, num_iterations, test_version, section):
        '''
        Method yielding results for data driven experimental testtest_api_performance driven.  Deprecated
        :param yaml_doc:
        :param num_iterations:
        :param test_version:
        :param section:
        :return:
        '''

        # Load parameters needed for this test case
        enum_map = {'get':call_type.get,'post':call_type.post,'delete':call_type.delete,'put':call_type.put}

        total_time_list = []
        for iterations in range(num_iterations):
            #Create a variable to store the total elapsed time for all calls in one set
            list_of_call_times = []

            # Now, iterate through the correct api_call elements in the YAML file, adding the elapsed time to the result list each time
            for single_api_call in yaml_doc[section][test_version]:
                logging.debug('Now testing the URL associated with: {}'.format(json.dumps(single_api_call, indent = 4)))
                test_url = single_api_call['api_call']['url'].replace('****',str(self.playlist_id_list[3]))
                test_verb = single_api_call['api_call']['verb']
                response = rest_request(session = self.test_session,
                                        baseurl = baseurl,
                                        apiurl = test_url,
                                        type_of_call= enum_map[test_verb])
                logging.debug('Response from yaml request is status_code =  {}, :elapsed = {}: ms, text = {}'.format(response.status_code,
                                                                                                                   response.elapsed,
                                                                                                                   response.text))

                if response.status_code != 200:
                    return False
                list_of_call_times.append(timedelta_milliseconds(response.elapsed))

            # Take the list of call times for each individual api call in the set, and sum them - that's the time for this iteration

            total_time = sum(list_of_call_times)
            total_time_list.append(total_time)
            logging.debug('Response from all yaml requests in this set is: {}'.format(total_time))
        logging.debug('list of times for set iterations is: {}'.format(total_time_list))
        result_list = self.calculate_ave_median_min_max(total_time_list)
        data_title = ['Performance Data for {} page with {} iterations in release {}'.format(section, num_iterations, test_version)]
        data_line = [str(x) for x in result_list]
        data_line.insert(0,data_title)
        self.write_result(data_line)
        return True
    # @nottest
    # def test_api_performance_data_driven(self):
    #     '''
    #     Test Generator for performance tests defined in yaml file.  Depreciated.
    #     :return:
    #     '''
    #     test_version = config['performance']['cm_sw_version']
    #     with open(PERF_YAML_CONFIG_FILE_PATH,'r') as input_file_stream:
    #         self.yaml_urls = yaml.load(input_file_stream)
    #         logging.debug('Read object from file: {}'.format(json.dumps(self.yaml_urls, indent = 4)))
    #     for section in self.yaml_urls.keys():
    #         yield  self.run_all_calls_in_yaml_section, self.yaml_urls, n, test_version, section


    def test_api_performance_Playlist_Properties(self):
        # Create Enum to map the verb in the YAML file to an enum used by the framework.
        enum_map = {'get':call_type.get,'post':call_type.post,'delete':call_type.delete,'put':call_type.put}

        # Make a wonderful data object out of this file of YAML data.  I love YAML.  It rocks
        with open(PERF_YAML_CONFIG_FILE_PATH,'r') as input_file_stream:
            self.yaml_urls = yaml.load(input_file_stream)
        logging.debug('Read object from file: {}'.format(json.dumps(self.yaml_urls, indent = 4)))

        # Commence Testing
        total_time_list = []
        for iterations in range(n):
            #Create a variable to store the total elapsed time for all calls in one set
            list_of_call_times = []

            # Now, iterate through the correct api_call elements in the YAML file, adding the elapsed time to the result list each time
            for single_api_call in self.yaml_urls['Playlist_Property'][self.test_version]:
                logging.debug('Now testing the URL associated with: {}'.format(json.dumps(single_api_call, indent = 4)))
                # Custom handling for the ID field in the API Calls that use the ID.
                test_url = single_api_call['api_call']['url'].replace('****',str(self.playlist_id_list[3]))
                test_verb = single_api_call['api_call']['verb']

                # Send API call to the server under test
                response = rest_request(session = self.test_session,
                                        baseurl = baseurl,
                                        apiurl = test_url,
                                        type_of_call= enum_map[test_verb])
                logging.debug('Response from yaml request is status_code =  {}, :elapsed = {}: ms, text = {}'.format(response.status_code,
                                                                                                                   response.elapsed,
                                                                                                                   response.text))

                assert response.status_code == 200, 'Expected Status Code 200, received status code ' + str(response.status_code)
                list_of_call_times.append(timedelta_milliseconds(response.elapsed))

            # Take the list of call times for each individual api call in the set, and sum them - that's the time for this iteration
            total_time = sum(list_of_call_times)
            total_time_list.append(total_time)
            logging.debug('Response from all yaml requests in this set is: {}'.format(total_time))
        # Write the results to file.
        logging.debug('list of times for set iterations is: {}'.format(total_time_list))
        result_list = self.calculate_ave_median_min_max(total_time_list)
        data_title = ['Performance Data for Playlist Properties landing page with {} iterations in release {}'.format(n, self.test_version)]
        data_line = [str(x) for x in result_list]
        data_line.insert(0,data_title)
        self.write_result(data_line)
        assert True

    def test_api_performance_Playlist_Landing(self):
        # Create Enum to map the verb in the YAML file to an enum used by the framework.
        enum_map = {'get':call_type.get,'post':call_type.post,'delete':call_type.delete,'put':call_type.put}

        # Make a wonderful data object out of this file of YAML data.  I love YAML.  It rocks
        with open(PERF_YAML_CONFIG_FILE_PATH,'r') as input_file_stream:
            self.yaml_urls = yaml.load(input_file_stream)
        logging.debug('Read object from file: {}'.format(json.dumps(self.yaml_urls, indent = 4)))

        # Commence Testing
        total_time_list = []
        for iterations in range(n):
            #Create a variable to store the total elapsed time for all calls in one set
            list_of_call_times = []

            # Now, iterate through the correct api_call elements in the YAML file, adding the elapsed time to the result list each time
            for single_api_call in self.yaml_urls['Playlist_Landing'][self.test_version]:
                logging.debug('Now testing the URL associated with: {}'.format(json.dumps(single_api_call, indent = 4)))
                # Custom handling for the ID field in the API Calls that use the ID.
                test_url = single_api_call['api_call']['url'].replace('****',str(self.playlist_id_list))
                test_verb = single_api_call['api_call']['verb']

                # Send API call to the server under test
                response = rest_request(session = self.test_session,
                                        baseurl = baseurl,
                                        apiurl = test_url,
                                        type_of_call= enum_map[test_verb])
                logging.debug('Response from yaml request is status_code =  {}, :elapsed = {}: ms, text = {}'.format(response.status_code,
                                                                                                                   response.elapsed,
                                                                                                                   response.text))

                assert response.status_code == 200,  'Expected Status Code 200, received status code ' + str(response.status_code)
                list_of_call_times.append(timedelta_milliseconds(response.elapsed))

            # Take the list of call times for each individual api call in the set, and sum them - that's the time for this iteration
            total_time = sum(list_of_call_times)
            total_time_list.append(total_time)
            logging.debug('Response from all yaml requests in this set is: {}'.format(total_time))
        # Write the results to file.
        logging.debug('list of times for set iterations is: {}'.format(total_time_list))
        result_list = self.calculate_ave_median_min_max(total_time_list)
        data_title = ['Performance Data for Playlist Landing page with {} iterations in release {}'.format(n, self.test_version)]
        data_line = [str(x) for x in result_list]
        data_line.insert(0,data_title)
        self.write_result(data_line)
        assert True

class test_players_performance_yaml:
    '''
    Test for the series of calls which are used by the UI to check Player Properties.  This class will run each
    of the filtered calls used by Indy
    '''
    template_id_list = []
    media_id_list = []
    message_id_list = []
    playlist_id_list = []
    url_list = []

    @classmethod
    def setup_class(self):

        # Begin by initiating a new login session for this test case.
        logging.info('Beginning test setup')
        baseurl = config['login']['baseurl']
        username = config['login']['username']
        password = config['login']['password']
        logging.debug('Read login info from config file and ready to begin.')
        logging.info('Initializing session for test module setup.')

        session = login(username,password,baseurl)

        # Identify point to point distribution server
        distribution_object = Distribution(api_version_distribution)

        distribution_object.list_distribution_servers(session = session,
                                                      baseurl = baseurl,
                                                      fields = 'name,id')
        main_dist_server_id = None
        for dist_server in distribution_object.get_response_key('list'):
            if dist_server['name'] == 'Main':
                main_dist_server_id = dist_server['id']

        logging.debug('Found Main distribution server - ID = {}'.format(main_dist_server_id))

        # Create 1000 players
        player_object = Player(api_version_player)

        player_object.create_multiple_players(session = session,
                                              baseurl = baseurl,
                                              name = 'performance test player # booga',
                                              number_of_players = 3,
                                              distribution_server_id = main_dist_server_id
                                              )

        # Setup log data
        data_headers =['Test results for test_playlist_properties','Average Response Time (ms)', 'Median Response Time (ms)', 'Min Response Time (ms)','Max Response Time(ms)']
        test_players_performance_yaml.write_result(data_headers)

        logout(session,baseurl = baseurl)

    @classmethod
    def teardown_class(self):
        #Login to perform teardown
        logging.info('Beginning test setup')
        baseurl = config['login']['baseurl']
        username = config['login']['username']
        password = config['login']['password']
        logging.debug('Read login info from config file and ready to begin.')
        logging.info('Initializing session for test module setup.')

        session = login(username,password,baseurl)

        #Delete setup objects here
        player_object = Player(api_version_player)

        player_object.list_players(session = session,
                                   baseurl = baseurl,
                                   limit = 2000,
                                   fields = 'id',
                                   search = 'booga')

        player_list = player_object.get_response_key('list')
        for player in player_list:
            player_object.delete_player_by_id(session = session,
                                              baseurl = baseurl,
                                              id = player['id'])



        #logout of session created for setup
        logout(session,baseurl = baseurl)

    @classmethod
    def write_result(cls, data_list):
        with open(PERF_TEST_RESULTS_FILE_PATH,mode = 'a', newline = '') as csv_file:
        #with open('./logs/perf_log', mode = 'a', newline= '') as csv_file:
            result_writer = csv.writer(csv_file)#, delimiter=',')
            result_writer.writerow(data_list)

    def calculate_ave_median_min_max(self,list_of_numbers):
        average = sum(list_of_numbers) / len(list_of_numbers)
        max_values = max(list_of_numbers)
        min_values = min(list_of_numbers)
        median_result = median(list_of_numbers)
        return [average, median_result, min_values, max_values]

    def setup(self):
        #Login to perform teardown
        logging.info('Beginning test setup')
        baseurl = config['login']['baseurl']
        username = config['login']['username']
        password = config['login']['password']
        logging.debug('Read login info from config file and ready to begin.')
        logging.info('Initializing session for test module setup.')
        self.test_version = config['performance']['cm_sw_version']

        self.num_players = 2
        self.test_session = login(username,password,baseurl)
    def teardown(self):
        #logout of session created for setup
        logout(self.test_session,baseurl = baseurl)

    def test_players_landing_page(self):
             # Create Enum to map the verb in the YAML file to an enum used by the framework.
        enum_map = {'get':call_type.get,'post':call_type.post,'delete':call_type.delete,'put':call_type.put}

        # Make a wonderful data object out of this file of YAML data.  I love YAML.  It rocks
        with open(PERF_YAML_CONFIG_FILE_PATH,'r') as input_file_stream:
            self.yaml_urls = yaml.load(input_file_stream)
        logging.debug('Read object from file: {}'.format(json.dumps(self.yaml_urls, indent = 4)))

        # Commence Testing
        total_time_list = []
        for iterations in range(n):
            #Create a variable to store the total elapsed time for all calls in one set
            list_of_call_times = []

            uuid = None
            id_list = None

            # There are some data dependancies in the test cases.  I need a list of all ID's of all players
            # in the test for one of the calls.  Let me create that now.

            player_object = Player(api_version_player)
            player_object.list_players(session = self.test_session,
                                       baseurl = baseurl,
                                       limit = 99999,
                                       offset = 0,
                                       fields = 'id',
                                       search = 'booga')

            player_id_list = [player['id'] for player in player_object.get_response_key('list')]
            uuid = ""

            # Now, iterate through the correct api_call elements in the YAML file, adding the elapsed time to the result list each time
            for single_api_call in self.yaml_urls['Player_Landing'][self.test_version]:
                logging.debug('Now testing the URL associated with: {}'.format(json.dumps(single_api_call, indent = 4)))
                # Custom handling for the ID field in the API Calls that use the ID.
                logging.debug('foo foo foo {}'.format(uuid))
                test_url = single_api_call['api_call']['url'].replace('xxxx',uuid)
                test_verb = single_api_call['api_call']['verb']
                test_pp = None
                if 'pp' in single_api_call['api_call']:
                    test_pp = single_api_call['api_call']['pp'].replace('xxxx',json.dumps(player_id_list))

                # Send API call to the server under test
                response = rest_request(session = self.test_session,
                                        baseurl = baseurl,
                                        apiurl = test_url,
                                        type_of_call= enum_map[test_verb],
                                        payload_params= test_pp)
                logging.debug('Response from yaml request is status_code =  {}, :elapsed = {}: ms, text = {}'.format(response.status_code,
                                                                                                                   response.elapsed,
                                                                                                                   response.text))
                # Check if the test URL data I need for a future call
                logging.debug('url is foo foo foo {}'.format(test_url))
                if 'storage' in test_url:
                    logging.debug('foo foo foo uuid in response is {}'.format(response.json()['value']))
                    uuid = response.json()['value']
                elif 'players/search' in test_url:
                    id_list = [player['id'] for player in response.json()['list']]

                assert response.status_code == 200, 'Expected Status Code 200, received status code ' + str(response.status_code)
                list_of_call_times.append(timedelta_milliseconds(response.elapsed))

            # Take the list of call times for each individual api call in the set, and sum them - that's the time for this iteration
            total_time = sum(list_of_call_times)
            total_time_list.append(total_time)
            logging.debug('Response from all yaml requests in this set is: {}'.format(total_time))
        # Write the results to file.
        logging.debug('list of times for set iterations is: {}'.format(total_time_list))
        result_list = self.calculate_ave_median_min_max(total_time_list)
        data_title = ['Performance Data for Playlist Properties landing page with {} iterations in release {}'.format(n, self.test_version)]
        data_line = [str(x) for x in result_list]
        data_line.insert(0,data_title)
        self.write_result(data_line)
        assert True


class TestPlayerPerformance:

    '''
    Test for the series of calls which are used by the UI to check Player pages.  This class will run each
    of the filtered calls used by Indy
    '''
    template_id_list = []
    media_id_list = []
    message_id_list = []
    playlist_id_list = []
    url_list = []

    @classmethod
    def setup_class(self):

        # Begin by initiating a new login session for this test case.
        logging.info('Beginning test setup')
        baseurl = config['login']['baseurl']
        username = config['login']['username']
        password = config['login']['password']
        logging.debug('Read login info from config file and ready to begin.')
        logging.info('Initializing session for test module setup.')

        session = login(username,password,baseurl)

        # Identify point to point distribution server
        distribution_object = Distribution(api_version_distribution)

        distribution_object.list_distribution_servers(session = session,
                                                      baseurl = baseurl,
                                                      fields = 'name,id')
        main_dist_server_id = None
        for dist_server in distribution_object.get_response_key('list'):
            if dist_server['name'] == 'Main':
                main_dist_server_id = dist_server['id']

        logging.debug('Found Main distribution server - ID = {}'.format(main_dist_server_id))

        # Create 1000 players
        player_object = Player(api_version_player)

        player_object.create_multiple_players(session = session,
                                              baseurl = baseurl,
                                              name = 'performance test player # booga',
                                              number_of_players = num_players,
                                              distribution_server_id = main_dist_server_id
                                              )

        # Setup log data
        data_headers =['Test results for TestPlayerPerformance','Average Response Time (ms)', 'Median Response Time (ms)', 'Min Response Time (ms)','Max Response Time(ms)']
        test_players_performance_yaml.write_result(data_headers)

        logout(session,baseurl = baseurl)

    @classmethod
    def teardown_class(self):
        #Login to perform teardown
        logging.info('Beginning test setup')
        baseurl = config['login']['baseurl']
        username = config['login']['username']
        password = config['login']['password']
        logging.debug('Read login info from config file and ready to begin.')
        logging.info('Initializing session for test module setup.')

        session = login(username,password,baseurl)

        #Delete setup objects here
        player_object = Player(api_version_player)

        player_object.list_players(session = session,
                                   baseurl = baseurl,
                                   limit = 2000,
                                   fields = 'id',
                                   search = 'booga')

        player_list = player_object.get_response_key('list')
        for player in player_list:
            player_object.delete_player_by_id(session = session,
                                              baseurl = baseurl,
                                              id = player['id'])



        #logout of session created for setup
        logout(session,baseurl = baseurl)

    def setup(self):
        #Login to perform teardown
        logging.info('Beginning test setup')
        self.baseurl = config['login']['baseurl']
        username = config['login']['username']
        password = config['login']['password']
        logging.debug('Read login info from config file and ready to begin.')
        logging.info('Initializing session for test module setup.')
        self.test_version = config['performance']['cm_sw_version']

        self.test_session = login(username,password,baseurl)
    def teardown(self):
        #logout of session created for setup
        logout(self.test_session,baseurl = baseurl)

    @classmethod
    def write_result(cls, data_list):
        with open(PERF_TEST_RESULTS_FILE_PATH,mode = 'a', newline = '') as csv_file:
        #with open('./logs/perf_log', mode = 'a', newline= '') as csv_file:
            result_writer = csv.writer(csv_file)#, delimiter=',')
            result_writer.writerow(data_list)

    def calculate_ave_median_min_max(self,list_of_numbers):
        average = sum(list_of_numbers) / len(list_of_numbers)
        max_values = max(list_of_numbers)
        min_values = min(list_of_numbers)
        median_result = median(list_of_numbers)
        return [average, median_result, min_values, max_values]

    def test_player_landing_page(self):
        '''
        Test performace for the player landing page
        :return:
        '''

        if self.test_version == 'Indy':
            total_time_list = []
            for iterations in range(n):
                logging.debug("PERFORMANCE: Iteration starts")
                #GET  /api/rest/misc/productinfo
                misc_object = Misc(api_version_miscellaneous)
                assert misc_object.get_product_info(session = self.test_session,
                                             baseurl = self.baseurl)
                get_product_info_elapsed = timedelta_milliseconds(misc_object.last_response.elapsed)

                #GET  /api/rest/auth/get
                auth_object = Auth_api(api_version_authorization)
                assert auth_object.get_session_info(session = self.test_session,
                                                    baseurl = self.baseurl)
                get_session_info_elapsed = timedelta_milliseconds(auth_object.last_response.elapsed)

                #GET  /api/rest/players/search?offset=0&limit=1000&search=&sort=name&count=0&filters={}&facets=type,playergroup,playergroupAssigned,channel,channelAssigned,distribution,softwareVersion,TTEL,WBEL,CEL,WEL,VCEL,MEL,N3DEL,QUEUE,LOCALVALEL,heartbeatOverdue,activePlayer,unhealthyPlayer&fields=id,name,enabled,type,channelName,active
                player_object = Player(api_version_player)
                facets = 'type,playergroup,playergroupAssigned,channel,channelAssigned,distribution,softwareVersion,TTEL,WBEL,CEL,WEL,VCEL,MEL,N3DEL,QUEUE,LOCALVALEL,heartbeatOverdue,activePlayer,unhealthyPlayer&fields=id,name,enabled,type,channelName,active'
                assert player_object.player_faceted_search(session = self.test_session,
                                                           baseurl = self.baseurl,
                                                           limit = 1000,
                                                           facets = facets,
                                                           )
                player_faceted_search_elapsed = timedelta_milliseconds(player_object.last_response.elapsed)

                player_id_list = [player['id'] for player in player_object.get_response_key('list')]

                #POST /api/rest/storage with ids of players returned in the search
                storage_object = Storage(api_version_storage)
                ids = {'ids':player_id_list}
                assert storage_object.store_value(session = self.test_session,
                                           baseurl = self.baseurl,
                                           value = ids)
                store_ids_elapsed = timedelta_milliseconds(storage_object.last_response.elapsed)
                uuid = storage_object.get_response_key('value')

                #GET  /api/rest/distributions?offset=0&limit=99999&search=&sort=name&count=0&filters={"id":{"values":[1]}}&fields=id,name,driver
                distribution_object = Distribution(api_version_distribution)
                filters = '{"id":{"values":[1]}}'
                assert distribution_object.list_distribution_servers(session = self.test_session,
                                                                     baseurl = self.baseurl,
                                                                     limit = 99999,
                                                                     filters = filters,
                                                                     fields = 'id,name,driver')

                get_distributions_elapsed = timedelta_milliseconds(distribution_object.last_response.elapsed)

                #GET  /api/rest/players/xxxx/states where xxxx is UUID returned from storage call above

                assert player_object.get_state_for_one_or_more_players(session = self.test_session,
                                                                baseurl = self.baseurl,
                                                                uuid = uuid)

                get_player_state_elapsed = timedelta_milliseconds(player_object.last_response.elapsed)
                logging.debug('Logging for this iteration - times to follow')
                logging.debug('Call log: {} get_product_info_elapsed'.format(get_product_info_elapsed))
                logging.debug('Call log: {} get_session_info_elapsed'.format(get_session_info_elapsed))
                logging.debug('Call log: {} player_faceted_search_elapsed'.format(player_faceted_search_elapsed))
                logging.debug('Call log: {} store_ids_elapsed'.format(store_ids_elapsed))
                logging.debug('Call log: {} get_distributions_elapsed'.format(get_distributions_elapsed))
                logging.debug('Call log: {} get_player_state_elapsed'.format(get_player_state_elapsed))

                call_set_time = get_product_info_elapsed + get_session_info_elapsed + player_faceted_search_elapsed + store_ids_elapsed + get_distributions_elapsed + get_player_state_elapsed
                total_time_list.append(call_set_time)
                logging.debug('Call durations list is {}'.format(total_time_list))
                logging.debug('Call Set time = {}'.format(call_set_time))
            logging.debug('list of times for set iterations is: {}'.format(total_time_list))
            result_list = self.calculate_ave_median_min_max(total_time_list)
            data_title = ['Performance Data for {} page with {} iterations in release {} with {} Players'.format('Player Landing', n, self.test_version, num_players)]
            data_line = [str(x) for x in result_list]
            data_line.insert(0,data_title)
            self.write_result(data_line)

        elif self.test_version == 'CM10.4':
            total_time_list = []
            for iterations in range(n):
                set_time = []
                logging.debug("PERFORMANCE: Iteration starts")
                #GET  /api/rest/misc/productinfo
                misc_object = Misc(api_version_miscellaneous)
                assert misc_object.get_product_info(session = self.test_session,
                                             baseurl = self.baseurl)
                get_product_info_elapsed = timedelta_milliseconds(misc_object.last_response.elapsed)
                set_time.append(get_product_info_elapsed)

                #GET  /api/rest/auth/get
                auth_object = Auth_api(api_version_authorization)
                assert auth_object.get_session_info(session = self.test_session,
                                                    baseurl = self.baseurl)
                get_session_info_elapsed = timedelta_milliseconds(auth_object.last_response.elapsed)
                set_time.append(get_session_info_elapsed)

                #GET http://192.168.126.130:8080/ContentManager/api/rest/players?offset=0&limit=10&search=&sort=name&count=0&filters={}&fields=id,name,enabled,type,distributionServerDriver,channelName,active
                player_object = Player(api_version_player)
                assert player_object.list_players(session = self.test_session,
                                                  baseurl = self.baseurl,
                                                  limit = 1000,
                                                  fields = 'id,name,enabled,type,distributionServerDriver,channelName,active')
                list_players_elapsed = timedelta_milliseconds(player_object.last_response.elapsed)
                set_time.append(list_players_elapsed)
                list_of_player_ids = [player['id'] for player in player_object.get_response_key('list')]

                #GET http://192.168.126.130:8080/ContentManager/api/rest/channels?offset=0&limit=999999&search=&sort=name&count=0&filters={}&fields=id,name
                channel_object = Channels(api_version_channels)
                assert channel_object.list_channels(session = self.test_session,
                                             baseurl = self.baseurl,
                                             limit = 99999,
                                             fields = 'id,name')

                list_channels_elapsed = timedelta_milliseconds(channel_object.last_response.elapsed)
                set_time.append(list_channels_elapsed)

                # GET http://192.168.126.130:8080/ContentManager/api/rest/distributions?offset=0&limit=99999&search=&sort=name&count=0&filters={}&fields=id,name,driver
                distribution_object = Distribution(api_version_distribution)
                assert distribution_object.list_distribution_servers(session = self.test_session,
                                                                     baseurl = self.baseurl,
                                                                     limit = 99999,
                                                                     fields = 'id,name')

                get_distributions_elapsed = timedelta_milliseconds(distribution_object.last_response.elapsed)
                set_time.append(get_distributions_elapsed)

                # GET 192.168.126.130:8080/ContentManager/api/rest/playergroup?offset=0&limit=999999&search=&sort=name&count=0&filters={}
                player_group_object = Player_group(api_version_player_group)
                assert player_group_object.list_player_groups(session = self.test_session,
                                                             baseurl = self.baseurl,
                                                             limit = 999999,
                                                             )
                get_player_groups_elapsed = timedelta_milliseconds(player_group_object.last_response.elapsed)
                set_time.append(get_player_groups_elapsed)

                # GET http://192.168.126.130:8080/ContentManager/api/rest/players/modules

                assert player_object.list_ex_module_licenses(session = self.test_session,
                                                             baseurl = self.baseurl)

                get_player_modules_elapsed = timedelta_milliseconds(player_object.last_response.elapsed)
                set_time.append(get_player_modules_elapsed)

                # GET http://192.168.126.130:8080/ContentManager/api/rest/players/versions

                assert player_object.list_player_versions(session = self.test_session,
                                                          baseurl = self.baseurl,
                                                          )
                get_versions_elapsed = timedelta_milliseconds(player_object.last_response.elapsed)
                set_time.append(get_versions_elapsed)

                #POST /api/rest/storage with ids of players returned in the search
                storage_object = Storage(api_version_storage)
                ids = {'ids':list_of_player_ids}
                assert storage_object.store_value(session = self.test_session,
                                           baseurl = self.baseurl,
                                           value = ids)
                store_ids_elapsed = timedelta_milliseconds(storage_object.last_response.elapsed)
                uuid = storage_object.get_response_key('value')
                set_time.append(store_ids_elapsed)

                #GET  /api/rest/players/xxxx/states where xxxx is UUID returned from storage call above
                assert player_object.get_state_for_one_or_more_players(session = self.test_session,
                                                                baseurl = self.baseurl,
                                                                uuid = uuid)
                get_player_state_elapsed = timedelta_milliseconds(player_object.last_response.elapsed)
                set_time.append(get_player_state_elapsed)

                total_time_list.append(sum(set_time))
                logging.debug('Call Set time = {}'.format(total_time_list[-1]))
            logging.debug('list of times for set iterations is: {}'.format(total_time_list))
            result_list = self.calculate_ave_median_min_max(total_time_list)
            data_title = ['Performance Data for {} page with {} iterations in release {} with {} players'.format('Player Landing', n, self.test_version, num_players)]
            data_line = [str(x) for x in result_list]
            data_line.insert(0,data_title)
            self.write_result(data_line)


            #http://192.168.126.130:8080/ContentManager/api/rest/misc/productinfo
            #http://192.168.126.130:8080/ContentManager/api/rest/auth/get
            #http://192.168.126.130:8080/ContentManager/api/rest/players?offset=0&limit=10&search=&sort=name&count=0&filters=%7B%7D&fields=id%2Cname%2Cenabled%2Ctype%2CdistributionServerDriver%2CchannelName%2Cactive
            #http://192.168.126.130:8080/ContentManager/api/rest/channels?offset=0&limit=999999&search=&sort=name&count=0&filters=%7B%7D&fields=id%2Cname
            #http://192.168.126.130:8080/ContentManager/api/rest/distributions?offset=0&limit=99999&search=&sort=name&count=0&filters=%7B%7D&fields=id%2Cname%2Cdriver
            #http://192.168.126.130:8080/ContentManager/api/rest/playergroup?offset=0&limit=999999&search=&sort=name&count=0&filters=%7B%7D
            #http://192.168.126.130:8080/ContentManager/api/rest/players/modules
            #http://192.168.126.130:8080/ContentManager/api/rest/players/versions
            #http://192.168.126.130:8080/ContentManager/api/rest/storage with {"ids":[1]}
            #http://192.168.126.130:8080/ContentManager/api/rest/players/6940ccaa-4e83-4c7f-b517-61ef3ce13bc0/states
