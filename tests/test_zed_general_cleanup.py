import logging
import logging.config
import configparser
from nose_parameterized import parameterized
from framework.constants import *
from framework.authentication_api_rest import Auth_api
from framework.http_rest import rest_request
from framework.users_rest import Users
from framework.roles_rest import Roles
from framework.storage_rest import Storage
from framework.file_directory_rest import FileDirectory
from framework.templates_rest import Templates
import datetime
import time
import json

from nose.plugins.attrib import attr

config = configparser.ConfigParser()
config.read(CONFIG_FILE_PATH)
baseurl = config['login']['baseurl']
logging.config.fileConfig(LOG_FILE_PATH)
logging.debug('Logging config file path is: {}'.format(CONFIG_FILE_PATH))
namespace = config['test']['namespace']

api_version_auth = config['api_info']['api_version_authentication']
api_version_users = config['api_info']['api_version_users']
api_version_roles = config['api_info']['api_version_roles']
api_version_storage = config['api_info']['api_version_storage']
api_version_file_directory = config['api_info']['api_version_file_directory']
api_version_templates = config['api_info']['api_version_templates']

class test_zed_general_cleanup():
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
        logging.debug("self.test_session {}".format(str(self.test_session)))

        # need a variable to store the folder id list
        self.folder_path_list = []
        # need a variable to store the user id list
        self.user_id_list = []
        # need a variable to store the template id list
        self.template_id_list = []

    def teardown(self):
        # logout of session created for setup
        self.api_auth_object.logout()

    def test_cleanup_templates(self):
        template_object = Templates(api_version_templates)
        template_object.list_templates(session=self.test_session,
                                         baseurl=self.baseurl,
                                         limit=1000,
                                         offset=0)
        try:
            template_list = template_object.get_response_key('list')

            for template in template_list:
                self.template_id_list.append(template['id'])

            logging.debug(self.template_id_list)

            # delete templates by id
            for template_id in self.template_id_list:
                if template_object.delete_template_by_id(session=self.test_session,
                                                      baseurl=self.baseurl,
                                                      id=template_id):
                    logging.debug("Successfully delete template with templateId: {}".format(template_id))
                else:
                    logging.debug("Could not delete template with teamplateId: {}".format(template_id))

        except KeyError:
            pass
        except Exception as ex:
            logging.error(ex)


    def test_cleanup_users(self):
        user_object = Users(api_version_users)
        # get the list of users
        user_list = user_object.return_user_list(session=self.test_session,
                                           baseurl=self.baseurl,
                                           limit=1000)
        user_json = json.loads(user_list)
        try:
            # find the usersnames that start with tst01
            for user in user_json['list']:
                if user['username'].startswith("tst01"):
                    self.user_id_list.append(user['id'])

            logging.debug(self.user_id_list)

            # delete the user by id
            for user_id in self.user_id_list:
                if user_object.delete_user(session=self.test_session, baseurl=self.baseurl, user_id=user_id):
                    logging.debug("Successfully deleted the user with the userId of {}".format(user_id))
                else:
                    logging.debug("Unabled to delete the user with the userId of {}".format(user_id))

        except KeyError:
            logging.debug("No users to delete")
            pass

    @parameterized([
        ('')
    ])
    def test_zed_cleanup_folders(self, directory_path):
        """
        Cleaning up Directories that were needed for testing and were not deleted after the test was completed
        """
        # logging.info("Sleeping for 5 seconds to allow delete threads to complete")
        # time.sleep(5)
        # Generate the strings I need for this test case:
        bottom_level_generated = directory_path.split('/')[-1]
        top_level_generated = directory_path.split('/')[0]
        list_path_generated = '|' + '|'.join(directory_path.split('/')[0:-1])

        file_directory_object = FileDirectory(api_version_file_directory)

        # self.folder_path_list.extend(file_directory_object.return_list_of_directories(
        #     session=self.test_session,
        #     baseurl=self.baseurl,
        #     bar_file_path=list_path_generated))
        file_directories = file_directory_object.return_list_of_directories(
            session=self.test_session,
            baseurl=self.baseurl,
            bar_file_path=list_path_generated
        )

        # logging.debug("List of directories: {}", str(file_directories))

        folder_json = json.loads(file_directories)
        try:
            self.folder_path_list = folder_json['list']

            logging.debug(self.folder_path_list)
            for folder in self.folder_path_list:
                file_path = folder['name']

                if file_directory_object.delete_directory(session=self.test_session,
                                                       baseurl=self.baseurl,
                                                       file_path=file_path):
                    logging.debug("Successfully deleled file directory: {}".format(file_path))
                else:
                    logging.debug("Unable to delete file directory: {}".format(file_path))
        except KeyError:
            # when there are no folders we should get a KeyError,
            # this is an expected error. Swallow the Error and move on.
            logging.debug("No Folders to Delete")
            pass
