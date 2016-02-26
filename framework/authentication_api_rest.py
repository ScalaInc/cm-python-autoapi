from framework.framework_object_rest import framework_object
from framework.authentication_rest import *
from framework.http_rest import rest_request


class Auth_api(framework_object):
    def __init__(self, api_version):
        super().__init__(api_version)
        self.api_token = ""
        self.cookie_token = ""
        self.session = requests.Session()
        self.baseurl = ""
        self.session.headers.update({'Content-type': 'application/json'})
        logging.debug("Session Object Created")

    def login(self, username, password, baseurl, networkID=0, token = True, cookie = True):
        '''
        A method that logs into the CM and returns a session object containing a valid auth token and valid token cookie

        NOTE: THis method returns the sesion object associated with the login.  This saves a lot of time with just
        a tiny departure from the model used in other objects.

        :param username: Login Username.
        :type username: String
        :param password: Login Password.
        :type password: String
        :param baseurl: Base URL for CM under test.
        :type baseurl: String
        :returns:  requests.session object for the current session with the CM.  Updates self.last_response
        :raises: ValueError if the Authorization token is not returned. This could indicate that the username/password is not correct and/or that the connection did not complete
        '''
        login_apiurl = '/api/rest/auth/login'
        self.baseurl = baseurl
        logging.debug("Attempting to log in with username: " + username + ' and password: ' + password)
        logging.debug('URL of api is: ' + login_apiurl)
        params = dict(
            networkId=networkID,
            username=username,
            password=password,
            rememberMe=True
        )
        self.last_response = rest_request(session = self.session,
                                          baseurl = baseurl,
                                          apiurl = login_apiurl,
                                          type_of_call=call_type.post,
                                          payload_params=params)
        try:
            logging.debug('Sent POST {}.  Response code = {}, response = {}'.format(login_apiurl,
                                                                                self.last_response.status_code,
                                                                                self.last_response.text))
            self.api_token = self.last_response.json().get('apiToken')
            self.cookie_token = self.last_response.json().get('token')
            logging.debug('Successful login.  Auth token is: ' + str(self.api_token))
            logging.debug('Successful login.  Token is: ' + str(self.cookie_token))
        except ValueError:
            logging.debug('Could not find apiToken or cookie token in auth request response.')
        except AttributeError:
            logging.debug('Could not find response status code - Attribute error thrown')


        if token:
            self.session.headers.update({'apiToken': self.api_token})
        if cookie:
            requests.utils.add_dict_to_cookiejar(self.session.cookies, {'token': self.cookie_token})
        return self.session


    def get_api_token(self):
        '''
        Returns the Authorization Token associated with the current session

        :param session: A logged in requests.session object
        :return: A String containing the Authorization token associated with the session
        '''
        # auth_token = ""
        # try:
        #     auth_token = session.headers['apiToken']
        #     logging.debug('Auth token is: ' + str(auth_token))
        # except ValueError:
        #     logging.error('Could not find apiToken in auth request response.')
        # return str(auth_token)
        return self.api_token

    def get_cookie_token(self):
        """
        Returns the cookie_token associated with this login session
        :return:
        """
        return self.cookie_token

    def get_session(self):
        """
        Returns the authenticated session associated with this auth object
        :return: Session object
        """
        return self.session


    def logout(self):
        '''
        Logs the session associated with this auth object out of the CM.
        :return: True if logoff is successful.  False otherwise.  Updates self.last_response
        '''

        logout_params = {'token': self.api_token}
        logout_apiurl = '/api/rest/auth/logout'
        self.last_response = rest_request(session=self.session,
                                          baseurl=self.baseurl,
                                          apiurl=logout_apiurl,
                                          type_of_call=call_type.get,
                                          payload_params=logout_params)
        #self.last_response = self.session.get(self.baseurl + '/api/rest/auth/logout', params={'token': self.api_token})
        try:
            logging.debug('Sent call to GET {}.  Response code = {}.  Response = {}'.format(logout_apiurl,
                                                                                        self.last_response.status_code,
                                                                                        self.last_response.text))
            if self.last_response.status_code == 200:
                return True
            else:
                return False
        except AttributeError:
            logging.debug('Attribute Exception thrown on logout.  Could not get status code.')

    def get_session_info(self, session, baseurl):
        '''
        Wrapper around GET /api/rest/auth/get
        :param session: Session logged into CM under test
        :param baseurl: Base URL of session under test
        :return: True if return status code is 200. False otherwise.  Updates last_response
        '''

        get_session_apiurl = '/api/rest/auth/get'

        self.last_response = rest_request(session = session,
                                          baseurl = baseurl,
                                          apiurl = get_session_apiurl,
                                          type_of_call= call_type.get)

        logging.debug('Made call to GET {}.  Response code: {}, Response {}'.format(get_session_apiurl,
                                                                                    self.last_response.status_code,
                                                                                    self.last_response.text))

        if self.last_response.status_code == 200:
            return True
        else:
            return False

    def ping_server(self, session, baseurl):
        """
        Wrapper around /api/rest/auth/ping
        :param session: Session object logged into the server under test
        :param baseurl: baseurl of CM under test
        :return: True if response code is 204, False otherwise.  Updates Last response
        """

        ping_server_apiurl = '/api/rest/auth/ping'

        self.last_response = rest_request(session=session,
                                          baseurl=baseurl,
                                          apiurl=ping_server_apiurl,
                                          type_of_call=call_type.post)

        logging.debug('Made call to POST {}. Response code: {}. Response text {}'.format(ping_server_apiurl,
                                                                                         self.last_response.status_code,
                                                                                         self.last_response.text))
        if self.last_response.status_code == 204:
            return True
        else:
            return False