__author__ = 'richardkaye'

from framework.framework_object_rest import framework_object
from framework.http_rest import rest_request
import logging

class Log(framework_object):
    """
    Helper class that builds a LOG json object for use in API testing.
    Class methods 'help' programmers by validating data before it can be
    placed into the main data object for the instance.
    """

    def __init__(self, api_version):
        super().__init__(api_version)

    def list_modules(self,session,baseurl):
        '''
        Wrapper around GET /api/rest/log/modules
        :param session: session object authenticated on the CM under test
        :param baseurl: baseurl of CM under test
        :return:True if status_code is 200, False otherwise.  Updates last_resposne
        '''

        list_modules_apiurl = '/api/rest/log/modules'

        self.last_response = rest_request(session = session,
                                          baseurl = baseurl,
                                          apiurl = list_modules_apiurl)

        logging.debug('Sent request to GET {}.  Response status code: {}. Response {}'.format(list_modules_apiurl,
                                                                                              self.last_response.status_code,
                                                                                              self.last_response.text))
        if self.last_response.status_code == 200:
            return True
        else:
            return False

    def tail_end_of_current_log(self,session,baseurl, limit = 500, offset = 0, filters = None ):
        '''
        Wrapper around GET /api/rest/log

        log filtering is not yet implemented, but hooks are in place for a future release.
        :param session:session object authenticated on CM under test
        :param baseurl:Base URL of the CM under test
        :param limit: Limits number of logs to search
        :param offset:  Used for filtering log entries from specific ids.  Setting offset to 30 is the same as setting a filter to id>30
        :param filters:  Not suppoorted in this version of the test api
        :return:
        '''

    def zip_player_log(self):
        '''
        Requires a player be attached to the system under test.  Not a candidate for automation
        :return:
        '''