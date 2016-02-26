__author__ = 'rkaye'

from framework.languages_rest import Languages
import logging
import logging.config
import configparser
from framework.constants import *
from framework.authentication_api_rest import Auth_api
import datetime
from nose.plugins.attrib import attr


config = configparser.ConfigParser()
config.read(CONFIG_FILE_PATH)
baseurl = config['login']['baseurl']
logging.config.fileConfig(LOG_FILE_PATH)
logging.debug('Logging config file path is: {}'.format(CONFIG_FILE_PATH))
namespace = config['test']['namespace']

api_version_auth = config['api_info']['api_version_authentication']

class test_():
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
        logging.debug('Read login info from config file and ready to begin.')
        logging.info('Initializing session for test module setup.')

        self.test_session = self.api_auth_object.login(self.username, self.password, self.baseurl)

        # Set up unique string associated with this test for naming objects
        now = datetime.datetime.now()
        self.unique_name = namespace + " " +now.strftime("%Y_%m_%d_%H%S.%f")

    def teardown(self):
        # logout of session created for setup
        self.api_auth_object.logout()




if __main__ ==