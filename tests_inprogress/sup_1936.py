__author__ = 'rkaye'

from framework.languages_rest import Languages
import logging
import logging.config
import configparser
from framework.constants import *
from framework.player_rest import Player
from framework.authentication_api_rest import Auth_api
import multiprocessing
import datetime
from nose.plugins.attrib import attr


config = configparser.ConfigParser()
config.read(CONFIG_FILE_PATH)
baseurl = config['login']['baseurl']
logging.config.fileConfig(LOG_FILE_PATH)
logging.debug('Logging config file path is: {}'.format(CONFIG_FILE_PATH))
namespace = config['test']['namespace']
username = config['login']['username']
password = config['login']['password']
baseurl = config['login']['baseurl']

api_version_auth = config['api_info']['api_version_authentication']
api_version_player = config['api_info']['api_version_player']

auth_object = Auth_api(api_version_auth)

num_calls = 100
#num_processes = 100
num_processes = 100

class LoginController():
    def __init__(self):
        self.auth_object = Auth_api(api_version_auth)

    def __enter__(self):
        return self.auth_object.login(username=username,
                                         password=password,
                                         baseurl=baseurl)

    def __exit__(self, type, value, traceback):
        self.auth_object.logout()


player_object = Player(api_version_player)

def work():
    for x in range(num_calls):
        with LoginController() as test_session:
            player_object.list_players(session=test_session,
                                       baseurl=baseurl,
                                       limit=0,
                                       fields = 'id,name,metadataValue')
            '''player_object.player_faceted_search(session=test_session,
                                                baseurl=baseurl,
                                                limit=0,
                                                fields='id,name,metadataValue')'''
    logging.info('Ending worker Process')

if __name__ == '__main__':
    jobs = []
    for i in range(num_processes):
        p = multiprocessing.Process(target = work)
        jobs.append(p)
        p.start()
        logging.info('Starting worker Process')



