__author__ = 'rkaye'

from framework.languages_rest import Languages
import logging
import logging.config
import configparser
from framework.constants import *
from framework.authentication_api_rest import Auth_api
from framework.roles_rest import Roles
from framework.users_rest import Users
from framework.media_rest import Media
import datetime
from nose.plugins.attrib import attr


config = configparser.ConfigParser()
config.read(CONFIG_FILE_PATH)
baseurl = config['login']['baseurl']
logging.config.fileConfig(LOG_FILE_PATH)
logging.debug('Logging config file path is: {}'.format(CONFIG_FILE_PATH))
namespace = config['test']['namespace']

api_version_auth = config['api_info']['api_version_authentication']
api_version_roles = config['api_info']['api_version_roles']
api_version_user = config['api_info']['api_version_users']
api_version_media = config['api_info']['api_version_media']

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
        assert self.test_session is not None, 'Could not log into CM'

        # Set up unique string associated with this test for naming objects
        now = datetime.datetime.now()
        self.unique_name = namespace + " " +now.strftime("%Y_%m_%d_%H%S.%f")

        # Set up variables used in this test
        approval_status_username = self.unique_name
        approval_status_password = 'approvalStatusPassword'
        self.user_id_list = []
        self.media_id_list = []

        #Determine the ID of Administrator role
        role_object = Roles(api_version_roles)
        role_object.list_roles(session=self.test_session,
                               baseurl=self.baseurl,
                               search='Administrator')
        assert 'id' in role_object.get_response_key('list')[0], 'Could not determine ID of Administrator'

        self.admin_role_id = role_object.get_response_key('list')[0]['id']

        # set up default user parameter for this test
        """self.user_parameters = {
            'dateFormat': 'MM-dd-yyyy',
            'emailaddress': 'approval_status@scala.com',
            'enabled': True,
            'firstname': 'Approval',
            'isAsiaSpeakingLanguage': True,
            'isSuperAdministrator': True,
            'isWebserviceUser': True,
            'language': 'English',
            'languageCode': 'en',
            'lastname': 'Status',
            'password': approval_status_password,
            'name': 'user first name and last name',
            'receiveApprovalEmails': 'false',
            'receiveEmailAlerts': 'false',
            'timeFormat': '12h',
            'roles': [{'id': self.admin_role_id}],
            'username': approval_status_username
        }"""

        user_object = Users(api_version_user)
        assert user_object.create_user(session=self.test_session,
                                baseurl=self.baseurl,
                                name=self.unique_name,
                                emailAddress='approval_status@scala.com',
                                firstname='Approval',
                                lastname ='Status',
                                username=approval_status_username,
                                password=approval_status_password,
                                role_list=[{'id': self.admin_role_id}]), 'Failed to create user during setup'

        self.user_id_list.append(user_object.get_response_key('id'))

        # Log in as new user
        self.api_auth_object2 = Auth_api(api_version_auth)

        self.new_user_session = self.api_auth_object2.login(username=approval_status_username,
                                                            password=approval_status_password,
                                                            baseurl=self.baseurl)
        assert self.new_user_session is not None, 'Failed to log into CM using user created during setup'

        # Create a media object to run this test on

        media_object = Media(api_version_media)
        assert media_object.create_media(session=self.new_user_session,
                                  baseurl=self.baseurl,
                                  name=self.unique_name,
                                  uri='http://approval_status.com'), 'Failed to create media object during setup'
        self.media_id_list.append(media_object.get_id())

        # Create approval object for user created above on media created above

        media_object.update_single_media(session=self.new_user_session,
                                         baseurl=self.baseurl,
                                         media_id=self.media_id_list[0],
                                         field_change_dict={'approval': {'action': 'APPROVE'}})


    def teardown(self):
        # Delete media item created in this test case
        media_object = Media(api_version_media)
        for media_id in self.media_id_list:
            media_object.delete_media_by_id(session=self.test_session,
                                            baseurl=self.baseurl,
                                            id=media_id)

        # Delete user item created in this test case
        user_object = Users(api_version_user)
        for user_id in self.user_id_list:
            user_object.delete_user(session=self.test_session,
                                    baseurl=self.baseurl,
                                    user_id=user_id)

        # logout of session created for setup
        self.api_auth_object.logout()
        self.api_auth_object2.logout()

    @attr('smoke')
    def test_endpoint_list_approver_media(self):
        pass
