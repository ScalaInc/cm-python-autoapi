__author__ = 'rkaye'

from framework.framework_object_rest import framework_object
from framework.constants import *
from framework.http_rest import rest_request
import logging

class FileDirectory(framework_object):
    '''
    Class that incapsolates all methods used to test file_directory API calls
    '''

    def __init__(self, api_version):
        '''
        Constructor initializes api version of super class framework_object
        :param api_version:
        :return:
        '''

        super().__init__(api_version)

    def create_directory(self, session, baseurl, file_path):
        """
        Wrapper around POST /api/rest/directory
        :param file_path: String containing the unescaped path to the new directory.  E.G. "data/mystuff"
        :return: True if response code is 200.  False otherwise.  Updates self.last_repsonse
        """

        create_directory_apiurl = '/api/rest/directory'
        create_directory_parameters = {'path': file_path}

        self.last_response = rest_request(session = session,
                                          baseurl = baseurl,
                                          type_of_call=call_type.post,
                                          apiurl = create_directory_apiurl,
                                          payload_params= create_directory_parameters)
        logging.debug('Sent call to POST {}.  Response code = {}, Response = {}'.format(create_directory_apiurl,
                                                                                        self.last_response.status_code,
                                                                                        self.last_response.text))
        if self.last_response.status_code == 200:
            return True
        else:
            return False

    def delete_directory(self, session, baseurl, file_path):
        """
        Wrapper around DELETE /api/rest/directory
        :param file_path: String containing the unescaped path to the new directory.  E.G. "data/mystuff"
        :return: True if response code is 204.  False otherwise.  Updates self.last_repsonse
        """

        delete_directory_apiurl = '/api/rest/directory'
        delete_directory_parameters = {'path': file_path}

        self.last_response = rest_request(session = session,
                                          baseurl = baseurl,
                                          type_of_call=call_type.delete,
                                          apiurl = delete_directory_apiurl,
                                          payload_params= delete_directory_parameters)
        logging.debug('Sent call to DELETE {}.  Response code = {}, Response = {}'.format(delete_directory_apiurl,
                                                                                        self.last_response.status_code,
                                                                                        self.last_response.text))
        if self.last_response.status_code == 204:
            return True
        else:
            return False

    def list_content_directory(self, session, baseurl, bar_file_path):
        """
        Wrapper around GET /api/rest/directory/{path}

        Lists directories and child directories
        :param session: Authenticated session object
        :param baseurl: Base url of CM under test
        :param bar_file_path: File path to list, separated by '|' (vertical bar) in stead of '/'.  This discrepancy
        is because the '/' character is the path separator in URL's.  The bar_file_path must start with a '|' (vertical bar)
        :return: True if status code == 200, False otherwise.  Updates self.last_response
        """

        list_content_directory_apiurl = '/api/rest/directory/' + str(bar_file_path)

        self.last_response = rest_request(session = session,
                                          baseurl = baseurl,
                                          type_of_call = call_type.get,
                                          apiurl = list_content_directory_apiurl)

        logging.debug('Sent call to GET {}.  Response code = {}, Response = {}'.format(list_content_directory_apiurl,
                                                                                       self.last_response.status_code,
                                                                                       self.last_response.text))

        if self.last_response.status_code == 200:
            return True
        else:
            return False

    def return_list_of_directories(self, session, baseurl, bar_file_path):
        """
        Wrapper around GET /api/rest/directory/{path}

        Lists directories and child directories
        :param session: Authenticated session object
        :param baseurl: Base url of CM under test
        :param bar_file_path: File path to list, separated by '|' (vertical bar) in stead of '/'.  This discrepancy
        is because the '/' character is the path separator in URL's.  The bar_file_path must start with a '|' (vertical bar)
        :return: True if status code == 200, False otherwise.  Updates self.last_response
        """

        list_content_directory_apiurl = '/api/rest/directory/' + str(bar_file_path)

        self.last_response = rest_request(session = session,
                                          baseurl = baseurl,
                                          type_of_call = call_type.get,
                                          apiurl = list_content_directory_apiurl)

        logging.debug('Sent call to GET {}.  Response code = {}, Response = {}'.format(list_content_directory_apiurl,
                                                                                       self.last_response.status_code,
                                                                                       self.last_response.text))

        if self.last_response.status_code == 200:
            return self.last_response.text
        else:
            return []