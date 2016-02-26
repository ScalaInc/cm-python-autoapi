__author__ = 'rkaye'
__author__ = 'rkaye'

from framework.languages_rest import Languages
import logging
import logging.config
import configparser
from framework.constants import *
from framework.authentication_api_rest import Auth_api
from framework.media_rest import Media
from framework.fileupload_rest import File_upload
import datetime
from nose_parameterized import parameterized
from nose.plugins.attrib import attr


config = configparser.ConfigParser()
config.read(CONFIG_FILE_PATH)
baseurl = config['login']['baseurl']
logging.config.fileConfig(LOG_FILE_PATH)
logging.debug('Logging config file path is: {}'.format(CONFIG_FILE_PATH))
namespace = config['test']['namespace']

api_version_auth = config['api_info']['api_version_authentication']
api_version_media = config['api_info']['api_version_media']
api_version_fileupload = config['api_info']['api_version_fileupload']


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
        self.unique_name = namespace + " " + now.strftime("%Y_%m_%d_%H%S.%f")

        self.media_id_list = []

    def teardown(self):
        # Delete the media object created by this iteration
        media_object = Media(api_version_media)
        for identifier in self.media_id_list:
            media_object.delete_media_by_id(session=self.test_session, baseurl=self.baseurl, id=identifier)

        # logout of session created for setup
        self.api_auth_object.logout()

    # @parameterized([
    # (['01_auto.jpg',
    #     '01.jpg',
    #     '02_auto.jpg',
    #     '02.jpg',
    #     '03_auto.jpg',
    #     '03.jpg',
    #     '04.jpg',
    #     '05.jpg',
    #     '06.jpg',
    #     '07.jpg',
    #     '08.jpg',
    #     '09.jpg',
    #     '10.jpg',
    #     '11.jpg',
    #     '12.jpg',
    #     '13.jpg',
    #     '14.jpg',
    #     '15.jpg',
    #     '16.jpg',
    #     '17.jpg',
    #     '18.jpg',
    #     '19.jpg',
    #     '20.jpg',
    #     '21.jpg',
    #     '22.jpg',
    #     '23.jpg',
    #     '24.jpg',
    #     '25.jpg',
    #     '26.jpg',
    #     '27.jpg',
    #     '28.jpg',
    #     '29.jpg',
    #     '30.jpg',
    #     'The_Sandman_008.jpg',
    #     'Vorlon.jpg'])
    # ])
    def test_a_bunch_of_media_uploads(self):
        """
        Upload a bunch of media items, then delete them.  Trying to pop the media upload problem
        :return:
        """

        path = namespace + "_test_a_bunch_of_uploads"
        media_object = Media(api_version_media)

        filename_list = ['01_auto.jpg',
                         '01.jpg',
                         '02_auto.jpg',
                         '02.jpg',
                         '03_auto.jpg',
                         '03.jpg',
                         '04.jpg',
                         #'05.jpg',
                         '06.jpg',
                         '07.jpg',
                         '08.jpg',
                         '09.jpg',
                         '10.jpg',
                         '11.jpg',
                         '12.jpg',
                         '13.jpg',
                         '14.jpg',
                         '15.jpg',
                         '16.jpg',
                         '17.jpg',
                         '18.jpg',
                         '19.jpg',
                         '20.jpg',
                         '21.jpg',
                         '22.jpg',
                         '23.jpg',
                         '24.jpg',
                         '25.jpg',
                         '26.jpg',
                         '27.jpg',
                         '28.jpg',
                         '29.jpg',
                         '30.jpg',
                         'The_Sandman_008.jpg',
                         'Vorlon.jpg',
                         '01_auto.jpg',
                         '01.jpg',
                         '02_auto.jpg',
                         '02.jpg',
                         '03_auto.jpg',
                         '03.jpg',
                         '04.jpg',
                         #'05.jpg',
                         '06.jpg',
                         '07.jpg',
                         '08.jpg',
                         '09.jpg',
                         '10.jpg',
                         '11.jpg',
                         '12.jpg',
                         '13.jpg',
                         '14.jpg',
                         '15.jpg',
                         '16.jpg',
                         '17.jpg',
                         '18.jpg',
                         '19.jpg',
                         '20.jpg',
                         '21.jpg',
                         '22.jpg',
                         '23.jpg',
                         '24.jpg',
                         '25.jpg',
                         '26.jpg',
                         '27.jpg',
                         '28.jpg',
                         '29.jpg',
                         '30.jpg',
                         'The_Sandman_008.jpg',
                         'Vorlon.jpg',
                         '01_auto.jpg',
                         '01.jpg',
                         '02_auto.jpg',
                         '02.jpg',
                         '03_auto.jpg',
                         '03.jpg',
                         '04.jpg',
                         #'05.jpg',
                         '06.jpg',
                         '07.jpg',
                         '08.jpg',
                         '09.jpg',
                         '10.jpg',
                         '11.jpg',
                         '12.jpg',
                         '13.jpg',
                         '14.jpg',
                         '15.jpg',
                         '16.jpg',
                         '17.jpg',
                         '18.jpg',
                         '19.jpg',
                         '20.jpg',
                         '21.jpg',
                         '22.jpg',
                         '23.jpg',
                         '24.jpg',
                         '25.jpg',
                         '26.jpg',
                         '27.jpg',
                         '28.jpg',
                         '29.jpg',
                         '30.jpg',
                         'The_Sandman_008.jpg',
                         'Vorlon.jpg']

        for filename in filename_list:
            # Create a media item for use in this test suite
            file_up = File_upload(api_version_fileupload)

            # Initiate Upload of media item
            assert file_up.initiate_upload(session=self.test_session, baseurl=self.baseurl, local_file_name=filename,
                                           file_upload_path=path)

            uuid = file_up.get_response_key('uuid')
            media_id = file_up.get_response_key('mediaId')
            self.media_id_list.append(media_id)

            # Upload file part
            assert file_up.upload_file_part(session=self.test_session, baseurl=self.baseurl, local_file_name=filename,
                                            local_file_path=config['path']['media'], uuid=uuid)

            # Commit Upload
            assert file_up.upload_finished(session=self.test_session, baseurl=self.baseurl, uuid=uuid)

            # Wait for upload to finish
            assert media_object.wait_for_media_upload(session=self.test_session,
                                                      baseurl=self.baseurl,
                                                      max_wait_seconds=20,
                                                      media_id=media_id)
        logging.debug('media_id_list is = {}'.format(self.media_id_list))
