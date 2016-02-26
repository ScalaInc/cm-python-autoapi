__author__ = 'rkaye'

from framework.languages_rest import Languages
import logging
import logging.config
import configparser
from framework.constants import *
from framework.authentication_api_rest import Auth_api
from framework.player_group_rest import PlayerGroup
from framework.player_rest import Player
from framework.storage_rest import Storage
import datetime
from nose.plugins.attrib import attr


config = configparser.ConfigParser()
config.read(CONFIG_FILE_PATH)
baseurl = config['login']['baseurl']
logging.config.fileConfig(LOG_FILE_PATH)
logging.debug('Logging config file path is: {}'.format(CONFIG_FILE_PATH))
namespace = config['test']['namespace']

api_version_auth = config['api_info']['api_version_authentication']
api_version_playergroup = config['api_info']['api_version_player_group']
api_version_player = config['api_info']['api_version_player']
api_version_storage = config['api_info']['api_version_storage']

class test_player_groups():
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

        self.player_group_id_list = []
        self.player_id_list = []
        pgroup_object = PlayerGroup(api_version_playergroup)

        # Create 10 player groups for this test case
        for player_group_index in range(10):
            pgroup_name = str(player_group_index) + " " + self.unique_name
            pgroup_description = self.unique_name + " Test case test_create_playergroup_endpoint unique description"

            pgroup_object.create_player_group(session=self.test_session,
                                                     baseurl=self.baseurl,
                                                     name=pgroup_name,
                                                     description=pgroup_description), 'Incorrect status code returned from create playergroup call'
            self.player_group_id_list.append(pgroup_object.get_id())

        # Create 5 players to add to the player groups
        player_object = Player(api_version_player)
        player_object.create_multiple_players(session = self.test_session,
                                              baseurl = self.baseurl,
                                              name = self.unique_name + " ##",
                                              number_of_players= 5
                                              )
        # Create list of player ID's for deletion
        self.player_id_list = self.player_id_list + player_object.get_response_key('ids')




    def teardown(self):

        # Remove players which were created in this test
        player_object = Player(api_version_player)
        for player_id in self.player_id_list:
            player_delete_result = player_object.delete_player_by_id(session = self.test_session,
                                                              baseurl = self.baseurl,
                                                              id = player_id)
            logging.debug('Cleanup result for player ID = {} is {}'.format(player_id,player_delete_result))

        # Remove player groups which were created in this test
        player_group_object = PlayerGroup(api_version_playergroup)

        for player_group_id in self.player_group_id_list:
            group_delete_result = player_group_object.delete_player_group_by_id(session = self.test_session,
                                                                          baseurl = self.baseurl,
                                                                          player_group_id=player_group_id)
            logging.debug('Cleanup result for playergroup ID = {} is {}'.format(player_group_id, group_delete_result))

        # logout of session created for setup
        self.api_auth_object.logout()

    @attr('smoke')
    def test_create_player_group_endpoint(self):
        """
        Tests the POST /api/rest/playergroup api - create one playergroup
        :return:
        """

        pgroup_object = PlayerGroup(api_version_playergroup)
        pgroup_name = self.unique_name
        pgroup_description = self.unique_name + " Test case test_create_playergroup_endpoint unique description"

        assert pgroup_object.create_player_group(session = self.test_session,
                                                 baseurl = self.baseurl,
                                                 name = pgroup_name,
                                                 description = pgroup_description), 'Incorrect status code returned from create playergroup call'

        # Add player group to teardown list so it is deleted at the end of the test run

        playergroup_id = pgroup_object.get_id()
        self.player_group_id_list.append(playergroup_id)

        assert pgroup_object.find_player_group_by_id(session = self.test_session,
                                                     baseurl = self.baseurl,
                                                     player_group_id=playergroup_id), 'Did not find player group after it was created'

    @attr('smoke')
    def test_delete_player_group_endpoint(self):
        """
        Tests the DELETE /api/rest/playergroup/{id} api.  - Create and then delete one player
        :return:
        """
        pgroup_object = PlayerGroup(api_version_playergroup)
        pgroup_name = self.unique_name
        pgroup_description = self.unique_name + " Test case test_create_playergroup_endpoint unique description"

        assert pgroup_object.create_player_group(session=self.test_session,
                                                 baseurl=self.baseurl,
                                                 name=pgroup_name,
                                                 description=pgroup_description), 'Incorrect status code returned from create playergroup call'

        # Add player group to teardown list so it is deleted at the end of the test run

        player_group_id = pgroup_object.get_id()
        self.player_group_id_list.append(player_group_id)

        assert pgroup_object.find_player_group_by_id(session=self.test_session,
                                                     baseurl=self.baseurl,
                                                     player_group_id=player_group_id), 'Did not find player group after it was created'


        # Delete the player (main test is here)

        assert pgroup_object.delete_player_group_by_id(session=self.test_session,
                                                       baseurl=self.baseurl,
                                                       player_group_id=player_group_id), 'Incorrect response from DELETE playergroup call'

        # Verify that the playergroup no longer exists


        assert not pgroup_object.find_player_group_by_id(session=self.test_session,
                                                         baseurl=self.baseurl,
                                                         player_group_id=player_group_id), 'Did not find player group after it was created'
    @attr('smoke')
    def test_find_player_group_by_id_endpoint(self):
        """
        Tests GET /api/rest/playergroup/{id}.  Note: this test does more than just test a simple get.  It validates
        that field filtering works.
        :return:
        """
        pgroup_object = PlayerGroup(api_version_playergroup)

        assert pgroup_object.find_player_group_by_id(session = self.test_session,
                                                     baseurl = self.baseurl,
                                                     player_group_id = self.player_group_id_list[0],
                                                     fields='name'), 'Could not find player group created during setup'

        assert 'id' in pgroup_object.last_response.json(), 'Did not find id field in field filtered playergroup'
        assert 'name' in pgroup_object.last_response.json(), 'Did not find name field in field filtered playergroup'
        assert 'description' not in pgroup_object.last_response.json(), 'Unexpectedly found description in field filtered playergroup'

        assert pgroup_object.find_player_group_by_id(session = self.test_session,
                                                     baseurl = self.baseurl,
                                                     player_group_id = self.player_group_id_list[0],
                                                     fields='description'), 'Could not find player group created during setup'

        assert 'id' in pgroup_object.last_response.json(), 'Did not find id field in field filtered playergroup'
        assert 'name' not in pgroup_object.last_response.json(), 'Unexpectedly found name in field filtered playergroup'
        assert 'description' in pgroup_object.last_response.json(), 'Did not find description field in field filtered playergroup'

        assert pgroup_object.find_player_group_by_id(session = self.test_session,
                                             baseurl = self.baseurl,
                                             player_group_id = self.player_group_id_list[0],
                                             fields='id'), 'Could not find player group created during setup'

        assert 'id' in pgroup_object.last_response.json(), 'Did not find id field in field filtered playergroup'
        assert 'name' not in pgroup_object.last_response.json(), 'Unexpectedly found name in field filtered playergroup'
        assert 'description' not in pgroup_object.last_response.json(), 'Unexpectedly found description in field filtered playergroup'

    @attr('smoke')
    def test_get_assigned_for_player_group_endpoint(self):
        """
        TEst of GET /api/rest/playergroup/usage

        1)  Add player group assignment to the first player in the list of those created in setup

        :return:
        """

        pgroup_object = PlayerGroup(api_version_playergroup)
        player_object = Player(api_version_player)
        one_playergroup_parameter = [{'id':self.player_group_id_list[0]}]

        # Frist, modify a player in this test so that it belongs to player groups

        assert player_object.find_player_by_id(session = self.test_session,
                                        baseurl = self.baseurl,
                                        player_id = self.player_id_list[0],
                                        fields = 'id,name'), 'Incorrect response code when retrieving player record'

        player_update_parameter = player_object.last_response.json()
        player_update_parameter['playergroups'] = one_playergroup_parameter

        assert player_object.update_single_player(session = self.test_session,
                                                  baseurl = self.baseurl,
                                                  player_id = self.player_id_list[0],
                                                  field_change_dict=player_update_parameter), 'Incorrect response code when updating player with player group'

        # Now assert that the usage for this player group has advanced by one.

        assert pgroup_object.get_assigned_for_player_group(session = self.test_session,
                                                           baseurl = self.baseurl,
                                                           ids = self.player_group_id_list[0]), 'Incorrect response code when retrieving player group usage'

        assert pgroup_object.get_response_key('playersCount') == 1, 'Incorrect number of players in player group.  Expected 1, got {}'.format(pgroup_object.get_response_key('playersCount'))

    @attr('smoke')
    def test_list_player_groups_endpoint(self):
        """
        List all player groups and verify that the ones created by setup are in the list
        :return:
        """

        pgroup_object = PlayerGroup(api_version_playergroup)

        assert pgroup_object.list_player_groups(session = self.test_session,
                                         baseurl = self.baseurl,
                                         limit = 999,
                                         offset = 0,
                                         fields = 'id'),'Incorrect response code received from list player groups'

        response_player_group_list = pgroup_object.get_response_key('list') # in the form [{'id':<id>},...]

        response_id_list = [player_group['id'] for player_group in response_player_group_list]

        result = True
        logging.debug('Looking for this list of playergroup ids in the list response: {}'.format(self.player_group_id_list))
        for pgroup_id in self.player_group_id_list:
            if pgroup_id not in response_id_list:
                result = False
                logging.debug('Did not find playergroup with id {} in list player group response'.format(pgroup_id))

        assert result, 'Not all player groups added in setup were found by playergroup list api call'

    @attr('smoke')
    def test_update_multiple_player_groups_endpoint(self):
        """
        Test of PUT /api/rest/playergroup

        1)  Create storage object which is a list of ID's
        2)  read the UUID from the storage call response
        3)  Use that UUID to change the description for all of the player groups to 'foo'
        4)  List all player groups and verify that the description is 'foo'
        :return:
        """
        stored_id_list = {'ids': self.player_group_id_list}
        storage_object = Storage(api_version_storage)
        assert storage_object.store_value(session = self.test_session,
                                   baseurl = self.baseurl,
                                   value = stored_id_list),'Unexpected response code when trying to store ids of player groups'

        uuid = storage_object.get_response_key('value')

        pgroup_object = PlayerGroup(api_version_playergroup)

        assert pgroup_object.multi_update_player_groups(session = self.test_session,
                                                        baseurl = self.baseurl,
                                                        uuid = uuid,
                                                        description = 'foo'), 'Unexpected response code when trying to multi update player groups'

        for player_group_id in self.player_group_id_list:
            assert pgroup_object.find_player_group_by_id(session = self.test_session,
                                                  baseurl = self.baseurl,
                                                  player_group_id=player_group_id), 'Could not find player group from setup by id!'
            description = pgroup_object.get_response_key('description')
            assert description == 'foo','Unexpected description after test case execution.  Expected foo got {}'.format(description)

    @attr('smoke')
    def test_update_player_group_by_id_endpoint(self):
        """
        Test of PUT /api/rest/playergroup/{id}
        :return:
        """
        pgroup_object = PlayerGroup(api_version_playergroup)

        # Form the update message by getting the player group name and picking a new description
        assert pgroup_object.find_player_group_by_id(session = self.test_session,
                                                     baseurl = self.baseurl,
                                                     player_group_id = self.player_group_id_list[0]), 'Incorrect Response from get Player group by ID'
        pg_name = pgroup_object.get_response_key('name')
        new_description = 'fladie fladie floo floo bar bar boo'
        update_dict = {'name':pg_name,'description': new_description}

        # Update the descripton on one player group record
        assert pgroup_object.update_player_group_by_id(session = self.test_session,
                                                       baseurl = self.baseurl,
                                                       player_group_id = self.player_group_id_list[0],
                                                       update_dict= update_dict), 'Incorrect response from update player group by id'

        # Get the modified player by id and validate that the descriptoion
        assert pgroup_object.find_player_group_by_id(session = self.test_session,
                                                     baseurl = self.baseurl,
                                                     player_group_id = self.player_group_id_list[0]), 'Incorrect Response from get Player group by ID'
        assert pgroup_object.get_response_key('description') == new_description, 'Incorrect description in player group record after PUT call'

