__author__ = 'rkaye'
from framework.constants import LOG_FILE_PATH, CONFIG_FILE_PATH
from framework.authentication_api_rest import Auth_api
from framework.heartbeats_rest import Heartbeats, Heartbeat_event
from framework.player_rest import Player
import sys
import logging
import time
import configparser
import time

config = configparser.ConfigParser()
config.read(CONFIG_FILE_PATH)
baseurl = config['login']['baseurl']
logging.config.fileConfig(LOG_FILE_PATH)
logging.debug('Logging config file path is: {}'.format(CONFIG_FILE_PATH))
namespace = config['test']['namespace']

api_version_auth = config['api_info']['api_version_authentication']

def main(argv):

    baseurl = config['login']['baseurl']
    admin_username = config['login']['username']
    admin_password = config['login']['password']
    player_username = config['login']['player_username']
    player_password = config['login']['player_password']

    player_tuple = setup(admin_username, admin_password)
    logging.debug("Player to use for this test is uuid: {} id: {}".format(player_tuple[0],player_tuple[1]))

    player_auth_object = Auth_api(1.0)
    while(True):
        #  Log into the CM as a player user
        player_session = player_auth_object.login(username=admin_username,
                                                  password=admin_password,
                                                  baseurl=baseurl)
        # Create a Heartbeat event
        heartbeat_problem_message = 'Test Heartbeat message for ns ' + namespace
        heartbeat = Heartbeat_event(api_version=1.0, problemMessage=heartbeat_problem_message)

        # Send the heartbeat message to the player under test
        heartbeat_controller = Heartbeats(1.0)
        if heartbeat_controller.report_heartbeat(session=player_session,
                                                 baseurl=baseurl,
                                                 uuid=player_tuple[0],
                                                 events=[heartbeat.get_json_data()] ):
            logging.debug('Sent one heartbeat')
        else:
            logging.debug('Oh noes - the heartbeat is still in the building status code = {}'.format(heartbeat_controller.get_status_code()))
        player_auth_object.logout()
        time.sleep(1)


def setup(admin_username, admin_password):
    auth_object= Auth_api(1.0)
    admin_session = auth_object.login(username=admin_username,
                                      password=admin_password,
                                      baseurl=baseurl)
    player_object = Player(1.0)
    player_name = time.strftime("%H:%M:%S" + " booba player").replace(':', '_')
    player_description = "This player is delicious as a big mac on a cloudy day"
    if player_object.create_player(session=admin_session,
                                baseurl=baseurl,
                                name=player_name,
                                description=player_description):
        logging.info("Player " + player_name + "Created")
        uuid = player_object.get_response_key('uuid')
        id = player_object.get_response_key('id')
        auth_object.logout()
        return (uuid, id)
    else:
        logging.error("Could not add player for test.  Call returned: {} ".format(player_object.get_status_code()))
        auth_object.logout
        sys.exit(2)





if __name__ == "__main__":
    main(sys.argv[1:])



