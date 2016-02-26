__author__ = 'richardkaye'
from framework.framework_object_rest import framework_object
from framework.constants import *
from framework.http_rest import rest_request
import logging
import logging.config


class License(framework_object):
    '''
    Class that wraps around License API
    '''

    def __init__(self,api_version):
        super().__init__(api_version)
        self.events = []

    def cancel_new_license(self,session,baseurl):
        """
        Wrapper around DELETE /api/rest/license/cancelNewLicense
        :return: True if response is 200, False otherwise.  Updates self.last_response
        """
        cancel_new_license_apiurl = '/api/rest/license/cancelNewLicense'

        self.last_response = rest_request(session=session,
                           baseurl=baseurl,
                           apiurl=cancel_new_license_apiurl,
                           type_of_call=call_type.delete)
        logging.debug('Sent call to GET {}, status code = {}, response = {}'.format(cancel_new_license_apiurl,
                                                                                    self.last_response.status_code,
                                                                                    self.last_response.text))
        if self.last_response.status_code == 200:
            return True
        else:
            return False


    def check_feature_enable(self, session, baseurl, name):
        """
        Wrapper around  GET /api/rest/license/isFeatureEnabled/{name}
        :param session: Authenticated session object
        :param baseurl: Base URL of CM under test
        :param name: Name of CM under test
        :return: True if response is 200, false otherwise.  Updates self.last_response
        """

        check_feature_enable_apiurl = '/api/rest/license/isFeatureEnabled/' + str(name)

        self.last_response = rest_request(session=session,
                                          baseurl=baseurl,
                                          apiurl=check_feature_enable_apiurl,
                                          type_of_call=call_type.get)

        logging.debug('Sent GET {}.  Response code = {}.  Response = {}'.format(check_feature_enable_apiurl,
                                                                                self.last_response.status_code,
                                                                                self.last_response.text))

        if self.last_response.status_code == 200:
            return True
        else:
            return False

    def import_license_with_ie(self, session, baseurl, filename):
        """
        Wrapper around POST /api/rest/license/importLicense/{filename}
        :param session: Authenticated session object
        :param baseurl: Base URL of CM under test
        :param filename: name of file to upload
        :return: True if response code is 200.  False otherwise.  Updates self.last_response
        """

        import_license_file_apiurl = '/api/rest/license/importLicense/' + str(filename)

        self.last_response = rest_request(session=session,
                                          baseurl=baseurl,
                                          apiurl=import_license_file_apiurl,
                                          type_of_call=call_type.post)

        logging.debug('Made call to POST {}, response code = {}, response = {}'.format(import_license_file_apiurl,
                                                                                       self.last_response.status_code,
                                                                                       self.last_response.text))
        if self.last_response.status_code == 200:
            return True
        else:
            return False