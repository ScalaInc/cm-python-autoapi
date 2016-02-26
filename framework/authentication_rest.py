import sys, json
from getpass import getpass
import requests
import logging
import logging.config
from time import sleep
import configparser
from framework.constants import *


""" ..py:module:: authentication_rest
A module with helper methods to permit user login into the CM
"""


def login(username, password, base_url, networkID=0):
    '''
    A method that logs into the CM and returns a session object containing a valid auth token and valid token cookie

    :param username: Login Username.
    :type username: String
    :param password: Login Password.
    :type password: String
    :param base_url: Base URL for CM under test.
    :type base_url: String
    :returns:  requests.session object for the current session with the CM
    :raises: ValueError if the Authorization token is not returned. This could indicate that the username/password is not correct and/or that the connection did not complete
    '''
    session = requests.Session()
    session.headers.update({'Content-type': 'application/json'})
    logging.debug("Session Object Created")
    authurl = base_url + '/api/rest/auth/login'
    logging.debug("Attempting to log in with username: " + username + ' and password: ' + password)
    logging.debug('URL of api is: ' + authurl)
    params = dict(
        networkId=networkID,
        username=username,
        password=password,
        rememberMe=True
    )
    auth_token = ""
    cookie_token = ""
    resp = session.post(authurl, data=json.dumps(params), proxies=None)
    logging.debug('login request response is: ' + str(resp.status_code))
    try:
        auth_token = resp.json().get('apiToken')
        cookie_token = resp.json().get('token')
        logging.debug('Successful login.  Auth token is: ' + str(auth_token))
        logging.debug('Successful login.  Token is: ' + str(cookie_token))
    except ValueError:
        logging.debug('Could not find apiToken or cookie token in auth request response.')
    session.headers.update({'apiToken': auth_token})
    requests.utils.add_dict_to_cookiejar(session.cookies, {'token': cookie_token})
    return session


def get_auth_token(session):
    '''
    Returns the Authorization Token associated with the current session

    :param session: A logged in requests.session object
    :return: A String containing the Authorization token associated with the session
    '''
    auth_token = ""
    try:
        auth_token = session.headers['apiToken']
        logging.debug('Auth token is: ' + str(auth_token))
    except ValueError:
        logging.error('Could not find apiToken in auth request response.')
    return str(auth_token)


def logout(session, baseurl):
    '''
    Logs the current session out of the CM.

    :param session: The requests.session object that will be logged out
    :param baseurl: The base url for the CM under test (defaults to http://<IP>:<udp port>/ContentManager/)
    :return: True if logoff is successful.  False otherwise.
    '''
    logging.info('logging out of the CM')
    logging.debug('type of session variable is: ' + str(type(session)))
    response = session.get(baseurl + '/api/rest/auth/logout',params = {'token':get_auth_token(session)})
    logging.debug('HTTP response code for logout is: ' + str(response.status_code))
    logging.debug('Response for logout api call is: ' + response.text)
    if response.status_code == 200:
        return True
    else:
        return False

def get_session_info():
    # Placeholder for new auth API commands found in authentication_api_rest which follows the new framework pattern OO
    pass


if __name__ == '__main__':
    ''' Test Code for authentication_rest module'''
    configuration = configparser.ConfigParser()
    configuration.read(CONFIG_FILE_PATH)
    baseurl = configuration['login']['baseurl']
    username = configuration['login']['username']
    password = configuration['login']['password']
    logging.config.fileConfig("config/log_config")
    logging.debug('Read from config file and ready to begin.')
    session = login(username=username, password=password, base_url=baseurl)
    logout(session, baseurl)
