__author__ = 'richardkaye'
from framework.framework_object_rest import framework_object
from framework.player_metadata_rest import Player_meta_data
from framework.constants import *
from framework.http_rest import rest_request
import logging
import json
import logging.config

class Distribution(framework_object):
    '''
    Class that incasoluates all methods used to test distributions
    '''

    def __init__(self,api_version):
        '''
        Constructor initializes api version of super class framework_object
        :param api_version:
        :return:
        '''

        super().__init__(api_version)

    def list_distribution_servers(self, session, baseurl, limit = 10, offset = 0, sort = 'name', filters = None, fields = None, search = None):
        '''
        Wrapper around GET /api/rest/distributions

        :param session:  Session object authenticated on the CM
        :param baseurl: Baseurl of system under test
        :param limit: number of objects to return in the response
        :param offset: Offset used for paging through DTO's
        :param sort: comma separated list of fields to sort by
        :param filters: One or more filter JSON objects
        :param fields: comma separated list of fields to sort on
        :param search: string to search for in the name of the distribution
        :return: True if response code is 200.  False otherwise.  Updates self.last_response
        '''
        list_distribution_apiurl = '/api/rest/distributions'

        return self.list_objects(session = session,
                                 baseurl = baseurl,
                                 apiurl = list_distribution_apiurl,
                                 limit = limit,
                                 offset = offset,
                                 sort = sort,
                                 filters = filters,
                                 fields = fields,
                                 search = search)

