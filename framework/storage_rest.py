__author__ = 'rkaye'

from framework.framework_object_rest import framework_object
from framework.http_rest import rest_request
from framework.constants import *
import logging
import logging.config

class Storage(framework_object):
    '''
    Class that encapsulates all methods used in testing the Storage API
    '''
    def __init__(self,api_version):
        '''
        Constructor initializes api version
        :return: VOID
        '''
        super().__init__(api_version)

    def store_value(self,session, baseurl, value):
        '''
        Wrapper around POST /api/rest/storage
        Return true if the status code is 200.  Update last response.
        :param session: session object under test
        :param baseurl: base url of the CM under test
        :param value: The value of the string or JSON object to be stored
        :return:True if response = 200, false otherwise
        '''
        store_value_apiurl = '/api/rest/storage'

        self.last_response = rest_request(session,
                                          baseurl = baseurl,
                                          apiurl = store_value_apiurl,
                                          type_of_call = call_type.post,
                                          payload_params=value)
        logging.debug('Made call to POST {}.  Response code = {}, response = {}'.format(store_value_apiurl,
                                                                                        self.last_response.status_code,
                                                                                        self.last_response.text))

        if self.last_response.status_code == 200:
            return True
        else:
            return False
    def get_stored_value_by_uuid(self, session, baseurl, uuid):
        '''
        Wrapper around Get Stored value associated with UUID
        GET /api/rest/storage/{uuid}

        :param session: session object logged into CM under test
        :param baseurl: baseurl of CM under test
        :param uuid: UUID associated with data to return
        :return: True if status code = 200, False otherwise.  Updates last response
        '''

        get_stored_value_apiurl = '/api/rest/storage/' + str(uuid)

        self.last_resposne = rest_request(session = session,
                                          baseurl=baseurl,
                                          apiurl = get_stored_value_apiurl,
                                          type_of_call = call_type.get)

        logging.debug('Made call to GET {}.  Response code = {}.  Response = {}'.format(get_stored_value_apiurl,
                                                                                        self.last_response.status_code,
                                                                                        self.last_response.text))

        if self.last_response.status_code == 200:
            return True
        else:
            return False