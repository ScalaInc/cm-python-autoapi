__author__ = 'rkaye'


from nose import with_setup
from nose.tools import nottest
import logging
import logging.config
import configparser
from framework.constants import CONFIG_FILE_PATH, LOG_FILE_PATH, metadata_data_type
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
api_version_media_metadata = config['api_info']['api_version_media_metadata']
api_version_network = config['api_info']['api_version_network']
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

class test_hosted_networks:
    def setup(self):
        # Begin by initiating a new login session for this test case.
        logging.info('Beginning test setup')
        self.baseurl = config['login']['baseurl']
        self.username = config['login']['username']
        self.password = config['login']['password']
        logging.debug('Read login info from config file and ready to begin.')
        logging.info('Initializing session for test module setup.')

        self.session = login(self.username,self.password,self.baseurl)

    def teardown(self):
        response = logout(self.session,self.baseurl)

    def test_endpoint_list_hosted_networks(self):
        '''
        Implements GET /api/rest/hostednetworks
        :return:
        '''
        network = Hosted_Networks(api_version_network)

        get_hosted_networks_apiurl = '/api/rest/hostednetworks'

        assert network.list_objects(session = self.session,
                                        baseurl = self.baseurl,
                                        apiurl = get_hosted_networks_apiurl,
                                        limit = 100,
                                        offset = 0), 'Response from list_objects was false'

    def test_endpoint_get_hosted_network_by_id(self):
        '''
        Implements Get /api/rest/hostednetworks/{id}
        :return:
        '''
        network = Hosted_Networks(api_version_network)
        get_hosted_networks_apiurl = '/api/rest/hostednetworks'


        assert network.list_objects(session = self.session,
                                    baseurl = self.baseurl,
                                    apiurl = get_hosted_networks_apiurl,
                                    limit = 100,
                                    offset = 0), 'Failed to list networks to retrieve id of a network on the system'
        assert network.get_last_response().json()['count'] >= 1, 'Zero networks found on the system under test'
        network_id = network.get_last_response().json()['list'][0]['id']

        get_hosted_network_by_id_apirul = '/api/rest/hostednetworks/' + str(network_id)

        logging.debug('Network ID to be checekd is {}')
        assert network.find_object_by_id(session = self.session,
                                 baseurl = self.baseurl,
                                 apiurl = get_hosted_network_by_id_apirul,
                                 object_id = network_id)

    def test_endpoint_update_hosted_network(self):
        '''
        Endpoint test for /api/rest/hostednetworks/{id}
        :return:
        '''

        network = Hosted_Networks(api_version_network)
        list_hosted_networks_apirul = '/api/rest/hostednetworks/'

        assert network.list_objects(session = self.session,
                                    baseurl = self.baseurl,
                                    apiurl = list_hosted_networks_apirul,
                                    limit = 100,
                                    offset = 0), 'Failed to list networks to retrieve id of a network on the system'
        assert network.get_last_response().json()['count'] >= 1, 'Zero networks found on the system under test'
        network_id = network.get_last_response().json()['list'][0]['id']

        hosted_network_description = 'This network is a boo bah bah boo'
        assert network.update_hosted_network(session = self.session,
                                             baseurl = self.baseurl,
                                             network_id = network_id,
                                             description = hosted_network_description),'Did not get 200 return code for PUT /api/rest/hostednetworks/({})'.format(network_id)
        # Check that the change took effect
        assert network.find_object_by_id(session = self.session,
                                         baseurl = self.baseurl,
                                         apiurl = list_hosted_networks_apirul,
                                         object_id = network_id)

        after_hosted_network_description =network.get_last_response().json()['description']
        assert after_hosted_network_description == hosted_network_description, 'Description did not change after PUT api call.  Expected {} got {}.'.format(hosted_network_description,after_hosted_network_description)
