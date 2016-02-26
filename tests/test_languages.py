__author__ = 'rkaye'

from framework.languages_rest import Languages
import logging
import logging.config
import configparser
from framework.constants import *
from framework.authentication_rest import login,logout



config = configparser.ConfigParser()
config.read(CONFIG_FILE_PATH)
baseurl = config['login']['baseurl']
logging.config.fileConfig(LOG_FILE_PATH)
logging.debug('Logging config file path is: {}'.format(CONFIG_FILE_PATH))
namespace = config['test']['namespace']

api_version_languages = config['api_info']['api_version_languages']

class test_languages_endpoint():

    language_id_list = []

    @classmethod
    def setup_class(cls):
        pass



    @classmethod
    def teardown_class(cls):
        pass

    def setup(self):
        #Login to perform teardown
        logging.info('Beginning test setup')
        baseurl = config['login']['baseurl']
        username = config['login']['username']
        password = config['login']['password']
        logging.debug('Read login info from config file and ready to begin.')
        logging.info('Initializing session for test module setup.')

        self.test_session = login(username,password,baseurl)
        #Populate the language list
        self.language_id_list = []

        language_object = Languages(api_version_languages)

        language_object.list_languages(session = self.test_session,
                                       baseurl = baseurl,
                                       limit = 1000)

        for language in language_object.get_response_key('list'):
            self.language_id_list.append(language['id'])
        logging.debug('List ov valid IDs for languages is: {}'.format(self.language_id_list))


    def teardwon(self):
        #logout of session created for setup
        logout(self.test_session,baseurl = baseurl)

    def test_find_language_by_id(self):
        language_object = Languages(api_version_languages)

        result_list = []
        for language_id in self.language_id_list:
            result_list.append(language_object.find_language_by_id(session = self.test_session,
                                                                   baseurl = baseurl,
                                                                   id = language_id,
                                                                   ))
        logging.debug('List of results for get language by id is: {}'.format(result_list))

        assert False not in result_list

    def test_list_languages(self):
        language_object = Languages(api_version_languages)

        assert language_object.list_languages(session = self.test_session,
                                              baseurl = baseurl,
                                              limit = 1000)

        logging.info('List Languages returned {} languages on system'.format(len(language_object.get_response_key('list'))))

    def test_find_language_by_iso(self):
        language_object = Languages(api_version_languages)

        assert language_object.find_language_by_iso_code(session = self.test_session,
                                                         baseurl = baseurl,
                                                         isocode = 'en'
                                                         )
        assert language_object.get_response_key('name') =='English'