'''
This test suite is designed to be run periodically - not every single night.  Tests in this suite take too long to run
in the nightly robotest suite - one minute or longer.  For example, tests that verify that the api times out after
a selected period of time can run for half an hour or more.  Running that test every night would greatly increase
the time duration of the suite.

I propose that this subset be run periodically - maybee every few nights - or every night outside of the
main test suite
'''

from framework.languages_rest import Languages
import logging
import logging.config
import configparser
from framework.constants import *
from framework.authentication_rest import login,logout
from framework.networks_rest import Network
from framework.authentication_api_rest import Auth_api
from framework.media_rest import Media
from nose_parameterized import parameterized
import time



config = configparser.ConfigParser()
config.read(CONFIG_FILE_PATH)
logging.config.fileConfig(LOG_FILE_PATH)
logging.debug('Logging config file path is: {}'.format(CONFIG_FILE_PATH))
namespace = config['test']['namespace']

api_version_languages = config['api_info']['api_version_languages']
api_version_networks = config['api_info']['api_version_networks']
api_version_authentication = config['api_info']['api_version_authentication']
api_version_media = config['api_info']['api_version_media']

class TestApiTimeout():
    """
    This test class is a data driven test to validate that the API times out after a given period.
    This is a data driven test.
    """

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
        logging.debug('Read login info from config file and ready to begin.')
        logging.info('Initializing session for test module setup.')

        self.test_session = login(self.username, self.password, self.baseurl)

    def teardown(self):
        # logout of session created for setup
        logout(self.test_session, self.baseurl)

    @parameterized([
        (1, 1), (2,1), (30,1), (300,1)
    ])
    def test_network_api_timeout(self, timeout_in_minutes, dummy):
        """
        Test case to test the conditions set forth in CM-9196.  This test takes over half an hour to run.
        It checks the timeout of the api for 1, 5 , and 30 minutes.
        :param timeout_in_minutes: The timeout specified in the @parameterized annotation which is used for each test
        :return:
        """
        network_object = Network(api_version_networks)
        auth_object = Auth_api(api_version_authentication)

        logging.debug('Starting test_network_api_timeout with timeout = {} minute(s)'.format(timeout_in_minutes))

        assert auth_object.get_session_info(session=self.test_session,
                                            baseurl=self.baseurl), ' Did not receive session info.'

        try:
            self.network_id = auth_object.get_response_key('network')['id']
        except KeyError:
            logging.debug('Could not find network ID in get session request: GET /api/rest/auth/get')
            assert False, 'Network ID not available'

        network_dict = {'id': self.network_id, 'sessionTimeout': timeout_in_minutes}

        assert network_object.update_network_settings(session=self.test_session,
                                                      baseurl=self.baseurl,
                                                      network_id=self.network_id,
                                                      network_definition=network_dict), 'Failed to change network logout time'

        media_object = Media(api_version_media)

        # Ping the server to make sure that the session timeout is cleared
        assert auth_object.ping_server(session=self.test_session,
                                       baseurl=self.baseurl)

        # Verify that a media 'get' works after the ping
        media_object.list_media(session=self.test_session,
                                baseurl=self.baseurl)

        # Wait for the duration of the timeout - 10 seconds
        time.sleep(timeout_in_minutes * 60 - 10)

        # Try the 'get' again - the timeout hasn't expired quite yet
        media_object.list_media(session=self.test_session,
                                baseurl=self.baseurl)
        logging.debug('Expecting 200 response code from media get at time = {}s.  Actual response code = {}'.format((timeout_in_minutes *60 -10), media_object.get_status_code()))

        # Wait for timeout to expire
        time.sleep(20)

        # Try the get again and verify that the response code is 401
        media_object.list_media(session=self.test_session,
                                baseurl=self.baseurl)

        logging.debug('Expecting 401 response code from media get at time = {}s.  Actual response code = {}'.format((timeout_in_minutes*60),media_object.get_status_code()))
        assert media_object.last_response.status_code == 401, 'Did not receive 401 as status code after timeout expire. Got: {}'.format(media_object.get_status_code())





        # while True:
        #     if media_object.list_media(session=self.test_session,
        #                                baseurl=self.baseurl):
        #         time.sleep(10)
        #         second_count += 10
        #         if second_count / 60 > timeout_in_minutes:
        #             logging.debug('Still getting response code = 200 after {} minutes'.format(second_count/60))
        #             assert False, 'Still getting response code = 200 after {} minutes'.format(second_count/60)
        #     else:
        #         assert True
        #         break
        # assert media_object.get_last_response().status_code == 401, 'Final response code is {}'.format(media_object.get_last_response().status_code)
        # assert second_count/60 >= timeout_in_minutes, 'After {} seconds with timeout {} got response of {}'.format(second_count,
        #                                                                                                           timeout_in_minutes,
        #                                                                                                           media_object.last_response.status_code)
        # logging.debug('After {} minutes status code is {}'.format(second_count/60,
        #                                                           media_object.get_last_response().status_code))