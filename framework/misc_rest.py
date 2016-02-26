__author__ = 'richardkaye'
from framework.framework_object_rest import framework_object
from framework.http_rest import rest_request
from framework.constants import call_type
import logging
import json
import logging.config

class Misc(framework_object):
    '''
    Class that encapsulates all of the methods used in testing miscellaneous API
    '''
    apiurl = '/api/rest/misc'

    def __init__(self,api_version):
        '''
        Constructor initializes api version
        :return: VOID
        '''
        super().__init__(api_version)

    def get_product_info(self, session, baseurl):
        '''
        Wrapper around GET /api/rest/misc/productinfo
        :param session: Authenticated session on CM under test
        :param baseurl: baseurl of system under test
        :return:  True if response code is 200.  False otherwise.  Updates self.last_response
        '''

        get_prod_apiurl = '/api/rest/misc/productinfo'

        self.last_response = rest_request(session = session,
                                          baseurl = baseurl,
                                          apiurl = get_prod_apiurl,
                                          type_of_call=call_type.get)

        logging.debug('Made call to GET {}.  Response code = {}.  Response = {}'.format(get_prod_apiurl,
                                                                                        self.last_response.status_code,
                                                                                        self.last_response.text))

        if self.last_response.status_code == 200:
            return True
        else:
            return False

    def get_server_time(self, session, baseurl):
        """
        Wrapper around GET /api/rest/misc/time
        :param session: Authenticated session on CM under test
        :param baseurl: baseurl of system under tes
        :return: True if response code is 200.  False otherwise.  Updates self.last_response
        """

        get_server_time_apiurl = '/api/rest/misc/time'

        self.last_response = rest_request(session = session,
                                           baseurl = baseurl,
                                           apiurl = get_server_time_apiurl,
                                           type_of_call=call_type.get,
                                           )
        logging.debug('Made call to GET {}.  Response code = {}, Response = {}'.format(get_server_time_apiurl,
                                                                                       self.last_response.status_code,
                                                                                       self.last_response.text))
        if self.last_response.status_code == 200:
            return True
        else:
            return False

    def get_network_id_by_name(self,session, baseurl, network_name):
        """
        Wrapper around '/api/rest/misc/network/{name}
        :param session: Authenticated session on CM under test
        :param baseurl: Base URL of CM under test
        :param network_name: Name of network to return the ID for
        :return:True if status code = 200, False otherwise.  Updates self.last_response
        """

        get_network_by_id_apiurl = '/ap/rest/misc/network' + str(name)

        self.last_response = rest_request(session = session,
                                          baseurl = baseurl,
                                          apiurl = get_network_by_id_apiurl,
                                          type_of_call=call_type.get,
                                          )
        logging.debug('Made call to GET {}.  Response code = {}, Response = {}'.format(get_network_by_id_apiurl,
                                                                                       self.last_response.status_code,
                                                                                       self.last_response.text))
        if self.last_response.status_code == 200:
            return True
        else:
            return False