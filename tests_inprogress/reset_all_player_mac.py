__author__ = 'rkaye'
import logging
import logging.config
import configparser
from framework.constants import *
from framework.player_rest import Player
from framework.authentication_api_rest import Auth_api
import datetime


config = configparser.ConfigParser()
config.read(CONFIG_FILE_PATH)
baseurl = config['login']['baseurl']
logging.config.fileConfig(LOG_FILE_PATH)
logging.debug('Logging config file path is: {}'.format(CONFIG_FILE_PATH))
namespace = config['test']['namespace']

api_version_auth = config['api_info']['api_version_authentication']
api_version_players = config['api_info']['api_version_player']

# Login to perform teardown
logging.info('Beginning test setup')
baseurl = config['login']['baseurl']
username = config['login']['username']
password = config['login']['password']
api_auth_object = Auth_api(api_version_auth)
logging.debug('Read login info from config file and ready to begin.')
logging.info('Initializing session for test module setup.')

test_session = api_auth_object.login(username, password, baseurl)

# Set up unique string associated with this test for naming objects
now = datetime.datetime.now()
unique_name = namespace + " " +now.strftime("%Y_%m_%d_%H%S.%f")

player_object = Player(api_version_players)


player_object.list_players(session = test_session,
                         baseurl = baseurl,
                         limit = 10000,
                         offset = 0,
                         sort = None,
                         fields = 'id,name,uuid')

list_of_players = player_object.last_response.json()
logging.debug('list_of_players is: ' + str(list_of_players))

for player in list_of_players['list']:
    if(player_object.reset_mac_address(session = test_session,
                                    baseurl = baseurl,
                                    id = player['id'])):
        logging.info('Successfuly reset mac address for player id={}'.format(player['id']))




