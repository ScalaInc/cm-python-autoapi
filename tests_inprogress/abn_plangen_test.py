__author__ = 'rkaye'
__author__ = 'rkaye'

from framework.languages_rest import Languages
import logging
import logging.config
import configparser
from framework.constants import *
from framework.player_rest import Player
from framework.player_metadata_rest import Player_meta_data
from framework.authentication_api_rest import Auth_api
from time import sleep
import multiprocessing
import datetime
from nose.plugins.attrib import attr


config = configparser.ConfigParser()
config.read(CONFIG_FILE_PATH)
logging.config.fileConfig(LOG_FILE_PATH)
logging.debug('Logging config file path is: {}'.format(CONFIG_FILE_PATH))
namespace = config['test']['namespace']
username = config['login']['username']
password = config['login']['password']
baseurl = config['login']['baseurl']

api_version_auth = config['api_info']['api_version_authentication']
api_version_player = config['api_info']['api_version_player']
api_version_metadata = config['api_info']['api_version_player_metadata']

auth_object = Auth_api(api_version_auth)

num_calls = 100
#num_processes = 100
num_processes = 100
n = 20 # number of iterations for each call type

class LoginController():
    def __init__(self):
        self.auth_object = Auth_api(api_version_auth)

    def __enter__(self):
        return self.auth_object.login(username=username,
                                      password=password,
                                      baseurl=baseurl)

    def __exit__(self, type, value, traceback):
        self.auth_object.logout()

with LoginController() as test_session:
    metadata_name= 'RK metadata hoha'
    #  Create a Player Metadata boolean
    player_metadata_bool = Player_meta_data(api_version_metadata)
    player_metadata_bool.create_metadata(session = test_session,
                                         baseurl = baseurl,
                                         name = metadata_name,
                                         data_type = metadata_data_type.BOOLEAN,
                                         value_type = metadata_value_type.ANY)
    metadata_id = player_metadata_bool.get_id()

#  Get a list of all players

    player_object = Player(api_version_player)
    player_object.list_players(session=test_session,
                               baseurl=baseurl,
                               limit=0,
                               fields='id,name')

    player_list = player_object.get_response_key('list')

#  Assign all players 'True' Value for the newly created metadata
    for player in player_list:
        player_object.modify_player_metadata_assignment(session=test_session,
                                                        baseurl=baseurl,
                                                        name=metadata_name,
                                                        player_id=player['id'],
                                                        metadata_id=metadata_id,
                                                        metadata_value='true',
                                                        api_version_player_metadata=api_version_metadata)



#  Store list of all players for plangen

#  Fire off the plangen and report the execution time.


player_object = Player(api_version_player)