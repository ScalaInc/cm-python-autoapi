__author__ = 'rkaye'

from framework.languages_rest import Languages
import logging
import logging.config
import configparser
from nose_parameterized import parameterized
from framework.constants import *
from framework.authentication_api_rest import Auth_api
from framework.users_rest import Users
from framework.roles_rest import Roles
from framework.storage_rest import Storage
import datetime
import time
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

class test_users():
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
        self.unique_name = namespace + "_" +now.strftime("%Y_%m_%d_%H%S.%f")

        # Create a data structure with all the role ID and name information for use by test cases
        role_object = Roles(api_version_roles)
        role_object.list_roles(session = self.test_session,
                               baseurl = self.baseurl,
                               limit = 100,
                               fields = 'name,id')
        self.role_list_response = role_object.get_response_key('list')

        # Set up data structures to keep track of resources to delete at cleanup
        self.user_id_list = []
        user_object = Users(api_version_users)
        # Create 5 users that are used by test cases and automatically cleaned up after
        for user_number in range(5):
            assert user_object.create_user(session = self.test_session,
                                baseurl = self.baseurl,
                                firstname = self.unique_name + " setup" + str(user_number),
                                lastname = self.unique_name + " setup" + str(user_number),
                                password = "a12345678",
                                emailAddress= self.unique_name + str(user_number) +'setup@' + 'blah.com',
                                username=self.unique_name + " setup" + str(user_number),
                                name = "setup setup" + str(user_number),
                                role_list = self.role_list_response), 'create user failed in setup for test_users.py'
            self.user_id_list.append(user_object.get_response_key('id'))


    def teardown(self):
        # Delete users created during this test case
        user_object = Users(api_version_users)
        for user_id in self.user_id_list:
            user_object.delete_user(session = self.test_session,
                                    baseurl = self.baseurl,
                                    user_id = user_id)

        # logout of session created for setup
        self.api_auth_object.logout()

    @attr('smoke')
    def test_create_users_endpoint(self):
        """
        Validates POST /api/rest/users

        Create one user with all roles
        :return:
        """
        user_object = Users(api_version_users)
        user_email = 'blah@blah.com'
        user_password = 'nah12345AAA'

        assert user_object.create_user(session = self.test_session,
                                       baseurl = self.baseurl,
                                       firstname = self.unique_name,
                                       lastname = self.unique_name,
                                       password = user_password,
                                       emailAddress= user_email,
                                       username=self.unique_name,
                                       name = self.unique_name + " " + self.unique_name,
                                       role_list = self.role_list_response), 'Incorrect response code detected when creating new user'

        user_id = user_object.get_response_key('id')
        self.user_id_list.append(user_id)

        assert user_object.find_user_by_id(session = self.test_session,
                                           baseurl = self.baseurl,
                                           user_id = user_id), 'Could not retrieve user after POST /api/rest/user'

        assert user_id == user_object.get_response_key('id'), 'ID of user record returned does not match response from POST'

    @attr('smoke')
    def test_delete_users_endpoint(self):
        """
        Creates a user and then deletes it using POST /api/rest/users and DELETE /api/rest/users respectively
        :return:
        """
        user_object = Users(api_version_users)
        user_email = 'blah@blah.com'
        user_password = 'nah12345AAA'
        user_role_list = self.role_list_response


        assert user_object.delete_user(session = self.test_session,
                                       baseurl = self.baseurl,
                                       user_id = self.user_id_list[0]),'Incorrect response code when attempting to delete newly created user'

        # TODO - the delete of a user takes a little time - for reasons that are not clear to me yet...
        time.sleep(5)
        assert not user_object.find_user_by_id(session = self.test_session,
                                           baseurl = self.baseurl,
                                           user_id = self.user_id_list[0]), 'Incorrect response from find user by id'

        assert user_object.last_response.status_code == 400, 'Did not receive status code 400 from get call on deleted user'

    @attr('smoke')
    def test_find_user_by_id_endpoint(self):
        """
        Tests find user by id.  Will use the user created in setup to do this
        :return:
        """

        user_object = Users(api_version_users)

        assert user_object.find_user_by_id(session = self.test_session,
                                    baseurl = self.baseurl,
                                    user_id = self.user_id_list[0]), 'Did not find user created in setup'


    @attr('smoke')
    def test_list_users_endpoint(self):
        """
        Endpoint test for GET /api/rest/users
        :return:
        """
        user_object = Users(api_version_users)

        assert user_object.list_users(session = self.test_session,
                               baseurl = self.baseurl,
                               limit = 100), 'List users did not return correct response code'

    @attr('smoke')
    def test_find_user_property_by_name_endpoint(self):
        """
        Endpoint test for GET /api/rest/users/userProperties/{name}
        :return:
        """

        user_object = Users(api_version_users)

        property_name = "gui.schedules.lastworking.frame.id"

        user_object.process_user_property(session = self.test_session,
                                          baseurl = self.baseurl,
                                          name = property_name,
                                          value = 'boo bah fah')

        #Set the property for this user
        user_object.process_user_property(session = self.test_session,
                                          baseurl = self.baseurl,
                                          name = property_name,
                                          value = 'doo doo doo')

        assert user_object.find_user_property_by_name(session = self.test_session,
                                               baseurl = self.baseurl,
                                               property_name = property_name), 'Did not get 200 response code from GET /api/rest/users/userProperties/{name}'

        assert 'id' in user_object.last_response.json(), 'Did not find ID field in response from GET /api/rest/useres/userproperties/(name)'
        assert user_object.get_response_key('name') == 'gui.schedules.lastworking.frame.id', 'Name field in response to GET /api/rest/users/userproperties/(name) is not correct'
        assert 'value' in user_object.last_response.json(),'Did not find field "value" in response from GET /api/rest/users/userproperties/(name)'

    @attr('smoke')
    def test_user_multi_update_language_endpoint(self):
        """
        Multi update on all of the users created in setup.  Change language assignment in a few players
        :return:
        """
        # Create a storage object with the list of ID's to update
        storage_object = Storage(api_version_storage)
        assert storage_object.store_value(session = self.test_session,
                                   baseurl = self.baseurl,
                                   value= {'ids':self.user_id_list}), 'Failed to add storage value containing IDs to the server'
        uuid = storage_object.get_response_key('value')

        user_object = Users(api_version_users)


        # Multi update
        assert user_object.update_multi_users(session = self.test_session,
                                       baseurl = self.baseurl,
                                       uuid = uuid,
                                       language = 'da'),'Incorrect response code when multi-updating user language codes'

        # Verify that the language code change took place
        for user_id in self.user_id_list:
            user_object.find_user_by_id(session= self.test_session,
                                        baseurl = self.baseurl,
                                        user_id = user_id,
                                        fields = 'languageCode')
            assert user_object.get_response_key('languageCode') == 'da', 'Incorrect language code detected in user after change'

    @attr('smoke')
    def test_user_multi_update_roles_endpoint(self):
        """
        Multi update on all users created in setup.  Change role assignment to the last one in the role list.
        :return:
        """
        storage_object = Storage(api_version_storage)
        assert storage_object.store_value(session = self.test_session,
                                      baseurl = self.baseurl,
                                      value= {'ids':self.user_id_list}), 'Failed to add storage value containing IDs to the server'
        uuid = storage_object.get_response_key('value')

        user_object = Users(api_version_users)

        assert user_object.update_multi_users(session = self.test_session,
                                              baseurl = self.baseurl,
                                              uuid = uuid,
                                              role_list = self.role_list_response[-1]),'Incorrect response code when multi-updating user role codes'

        # Verify that the language code change took place
        for user_id in self.user_id_list:
            user_object.find_user_by_id(session= self.test_session,
                                        baseurl = self.baseurl,
                                        user_id = user_id,
                                        fields = 'roles')
        assert user_object.get_response_key('roles')[0]['name'] == self.role_list_response[-1]['name'], 'Incorrect language code detected in user after change'
    @attr('smoke')
    @parameterized([
        (['foo','bar'],['unga','bunga']),
        (['1','2','3','4'],['a','b','c','d'])
    ])
    def test_process_multiple_properties_endpoint(self,property_name_list, property_value_list):
        """
        Add two or more user properties to the system.  Pull them back by name to validate that they landed
        :return:
        """
        assert len(property_name_list) == len(property_value_list), 'Invalid data - num of names is different than num of values'

        full_property_list = []

        # Construct the property list from the input data [{'name':<name0>,'value':<value0>},{...]
        for index in range(len(property_value_list)):
            current_property = {}
            current_property['name'] = property_name_list[index]
            current_property['value'] = property_value_list[index]
            full_property_list.append(current_property)

        user_object = Users(api_version_users)

        assert user_object.process_user_multiple_properties(session = self.test_session,
                                                            baseurl = self.baseurl,
                                                            list_of_user_properties= full_property_list), 'Incorrect response code from update multiple properties'

        # Check to see that each key-value pair landed

        for index in range(len(property_name_list)):
            assert user_object.find_user_property_by_name(session = self.test_session,
                                                          baseurl = self.baseurl,
                                                          property_name = property_name_list[index]), 'Incorrect response code from find property by name'
            assert user_object.get_response_key('value') == property_value_list[index], 'Search on key resulted in incorrect value being returned'

    @attr('smoke')
    def test_process_single_property_endpoint(self):
        """
        Add a user property to the system, then request it by name to validate that it comes back.
        :return:
        """
        user_object = Users(api_version_users)
        property_name = self.unique_name.replace(" ","_") + ".name"
        property_value = self.unique_name.replace(" ","_") + ".value"

        assert user_object.process_user_property(session = self.test_session,
                                          baseurl = self.baseurl,
                                          name = property_name,
                                          value = property_value), 'Incorrect response code received from process property'

        assert user_object.find_user_property_by_name(session = self.test_session,
                                                      baseurl = self.baseurl,
                                                      property_name = property_name), 'Incorrect response code received from find property by name'

        assert user_object.get_response_key('value') == property_value, "Incorrect value returned from for property created by process single property"


    @attr('smoke')
    def test_get_users_by_network_id_endpoint(self):
        """
        Tests the get users by network id api endpoint.  However, it can't check
        multiple networks b/c the servers we test on are not multi network aware
        :return:
        """

        auth_object = Auth_api(api_version_auth)

        auth_object.get_session_info(session = self.test_session,
                                     baseurl = self.baseurl)

        network_id = auth_object.get_response_key('network')['id']

        user_object = Users(api_version_users)

        assert user_object.retrieve_list_of_users_by_network(session = self.test_session,
                                                      baseurl = self.baseurl,
                                                      network_id = network_id,
                                                      limit = 1000,
                                                      search = namespace,
                                                      fields = 'name,id'), 'Incorrect response code from list users by network id'

        list_of_user_ids = [user['id'] for user in user_object.get_response_key('list')]

        for setup_user_id in self.user_id_list:
            assert setup_user_id in list_of_user_ids, 'Did not find user created by test case in the list response'

    @attr('smoke')
    @parameterized([
        ('username', 'bungahungahoo'),
        #('password', 'abcdefg123'), Not in DTO used to check change b/c password not sent in clear
        #('oldPassword','foobar'), Not in DTO but used to change password
        ('firstname', 'bababa'),
        ('lastname', 'bobobo'),
        ('emailaddress', 'hungry@hippos.com'),
        ('dateFormat', 'dd/MM/yyyy'),
        ('dateFormat', 'dd.MM.yyyy'),
        ('dateFormat', 'dd-MM-yyyy'),
        ('dateFormat', 'yyyy/MM/dd'),
        ('dateFormat', 'yyyy.MM.dd'),
        ('dateFormat', 'yyyy-MM-dd'),
        ('dateFormat', 'MM/dd/yyyy'),
        ('dateFormat', 'MM.dd.yyyy'),
        ('dateFormat', 'MM-dd-yyyy'),
        ('timeFormat', '24h'),
        ('timeFormat', '12h'),
        ('languageCode', 'es'),
        ('languageCode', 'en'),
        ('languageCode', 'fr'),
        ('languageCode', 'ja'),
        ('languageCode', 'ko'),
        ('languageCode', 'nl'),
        ('languageCode', 'no'),
        ('languageCode', 'pl'),
        ('languageCode', 'pt-br'),
        ('languageCode', 'ru'),
        ('languageCode', 'sv'),
        ('languageCode', 'tr-tr'),
        ('languageCode', 'zh-hant'),
        ('languageCode', 'zh-hans'),
        # ('isAsiaSpeakingLanguage', True), See CM-9423
        # ('isAsiaSpeakingLanguage', False), See CM-9423
        ('canChangePassword', True),
        ('canChangePassword', False),
        # ('isSuperAdministrator', True),  This field set by system
        # ('isSuperAdministrator', False),
        ('isAutoMediaApprover', True),
        ('isAutoMediaApprover', False),
        ('receiveEmailAlerts', True),
        ('receiveEmailAlerts', False),
        ('isWebserviceUser', False),  # May be deprecated field
        #('isWebserviceUser', True) ,   # Cannot be set to true in Indy - no more SOAP
        ('enabled', True),
        ('enabled', False),
        ('receiveApprovalEmails', True),
        ('receiveApprovalEmails', False),
        #('authenticationMethod', "???"), Need more information about LDAP to use
        ('canChangePassword', False)
    ])
    def test_update_user_by_id_endpoint(self, field, value):
        """
        Updates the field specified with the value specified.  Then verify the same
        :param field: The field that is to be updated
        :param value: The value to be checked
        :return:
        """

        user_object = Users(api_version_users)
        test_user_id = self.user_id_list[0]
        if field == 'password':
            logging.info('foo bar bar')
        user_object.find_user_by_id(session = self.test_session,
                                    baseurl = self.baseurl,
                                    user_id = test_user_id)

        user_record = user_object.last_response.json()
        user_record[field] = value

        assert user_object.update_user(session =self.test_session,
                                       baseurl = self.baseurl,
                                       identifier = test_user_id,
                                       update_user_dict = user_record),'Did not receive 200 response code from update user'

        user_object.find_user_by_id(session = self.test_session,
                            baseurl = self.baseurl,
                            user_id = test_user_id)

        assert user_object.get_response_key(field) == value, 'New value not found after update for field = ' + field + " and value = " + str(value)





