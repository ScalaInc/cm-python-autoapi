__author__ = 'rkaye'
from nose import with_setup
from nose.tools import nottest
import logging
import logging.config
import configparser
from framework.constants import CONFIG_FILE_PATH, LOG_FILE_PATH
from framework.authentication_rest import login, logout, get_auth_token
from framework.http_rest import *
from framework.player_rest import Player
from framework.heartbeats_rest import Heartbeats, Heartbeat_event

import inspect

print(CONFIG_FILE_PATH)
config = configparser.ConfigParser()
config.read(CONFIG_FILE_PATH)
baseurl = config['login']['baseurl']
logging.config.fileConfig(LOG_FILE_PATH)
logging.debug('Logging config file path is: {}'.format(CONFIG_FILE_PATH))
session = requests.Session()
namespace = config['test']['namespace']
api_version = config['api_info']['api_version']
player_id = 0


def this_function_name():
    return inspect.stack()[1][3]


def t_setup():
    '''
    In order to test this case, a new user must be created and the session must be logged in as this new user.
    That user must create a media and then approve it.
    You must put a healthy player_id in the testconfig file in the ['player']['player_id']
    entry
    '''

    # Begin by initiating a new login session for this test case.
    global config, session, media_id_list, baseurl, namespace, player_id, api_version
    logging.info('Beginning test setup')
    baseurl = config['login']['baseurl']
    username = config['login']['username']
    password = config['login']['password']
    # player_id = config['player']['player_id']
    api_version_player = config['api_info']['api_version_player']
    distribution_server_id = config['distribution']['distribution_server_id']
    logging.debug('Read login info from config file and ready to begin.')
    logging.info('Initializing session for next test case.')
    media_path = config['path']['media']
    # INITIALIZE SESSION OBJECT
    session = login(username, password, baseurl)
    assert session is not None

    # Create a player to run these tests against
    player = Player(api_version=api_version_player)
    player_name = namespace + "_" + this_function_name() + "_" + "player"
    player_create_result = player.create_player(session=session, baseurl=baseurl, name=player_name, distribution_server_id=distribution_server_id)
    logging.info('Result from create player call in test case setup is: ()'.format(player_create_result))
    player_id = player.get_id()


def t_teardown():
    global session, player_id, api_version
    # Delete Player created for this test case
    api_version_player = config['api_info']['api_version_player']
    player = Player(api_version=api_version_player)
    player.delete_player_by_id(session, baseurl, id=player_id)

    response = logout(session, config['login']['baseurl'])
    assert response


@with_setup(t_setup, t_teardown)
def test_get_current_heartbeat_sequence():
    '''
    Use GET /api/rest/players/{id} to pull in the player data for this test case
    pull out the UUID of the player returned by the GET
    Use GET /api/rest/heartbeats/sequence/{uuid} - validate that it starts at 0
    :return:
    '''
    global config, session, namespace, baseurl, api_version, player_id
    api_version_player = config['api_info']['api_version_player']
    logging.info('Beginning {}'.format(this_function_name()))
    # player_id = 87569
    # Get the Player data and parse the UUID
    player = Player(api_version=api_version_player)
    player_get_result = player.find_player_by_id(session, baseurl=baseurl, player_id=player_id)
    logging.debug('Current Player in use for this test case is: {}'.format(player.last_response.text))
    uuid = player.get_response_key('uuid')

    # Get the sequence number of the heartbeats
    heartbeat_controller = Heartbeats(api_version)
    assert heartbeat_controller.get_current_heartbeat_sequence_of_player(session, baseurl=baseurl, uuid=uuid), 'Failed to retrieve sequence number.'
    sequence = heartbeat_controller.get_json_data()
    logging.info('Current sequence number is: {}'.format(sequence))
    assert sequence == 0, 'Sequence number should be 0.  Sequence number is {}'.format(sequence)


@with_setup(t_setup, t_teardown)
def test_report_heartbeat():
    '''
    Use POST /api/rest/heartbeats to add a heartbeat message to the player created in the setup
    Use GET /api/rest/players to pull the player down and examine the heartbeat - make sure it is present.
    :return:
    '''
    global session, baseurl, player_id, api_version, namespace
    logging.info('Beginning {}'.format(this_function_name()))
    # player_id = 87569
    # Get UUID of player under test
    player = Player(api_version)
    player.find_player_by_id(session, baseurl=baseurl, player_id=player_id)
    logging.debug('Current Player in use for this test case is: {}'.format(player.last_response.text))
    uuid = player.get_response_key('uuid')

    # Create a Heartbeat event
    heartbeat_problem_message = 'Test Heartbeat message for ns ' + namespace
    heartbeat = Heartbeat_event(api_version = api_version, problemMessage = heartbeat_problem_message)

    # Send the heartbeat message to the player under test
    heartbeat_controller = Heartbeats(api_version)

    assert heartbeat_controller.report_heartbeat(session, baseurl=baseurl, uuid=uuid, events=[heartbeat.get_json_data()] ), 'Incorrect response code from report heartbeat message.'

    # Verify that the heartbeat message got added to the player under test


@nottest
@with_setup(t_setup, t_teardown)
def test_increment_get_heartbeat_sequence():
    pass


