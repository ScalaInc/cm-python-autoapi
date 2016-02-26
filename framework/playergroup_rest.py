__author__ = 'rkaye'

import sys, json
from getpass import getpass
import requests
import logging
import logging.config
from time import sleep
import configparser
from framework.framework_object_rest import framework_object
from framework.constants import *
from framework.http_rest import rest_request
from itertools import chain

class Player_group(framework_object):
    """
    Helper class that builds a player group json object for use in API testing.
    Class methods 'help' programmers by validating data before it can be
    placed into the main data object for the instance.
    """

    def __init__(self, api_version):
        super().__init__(api_version)

    def list_player_groups(self,session, baseurl, limit=10, offset = 0, sort=None, filters = None, fields = None, search = None):
        '''
        Wrapper around GET /api/rest/playergroup  Uses superclass method list_object
        '''
        list_player_groups_apiurl = '/api/rest/playergroup'

        return self.list_objects(session = session,
                         baseurl = baseurl,
                         apiurl = list_player_groups_apiurl,
                         limit = limit,
                         offset = offset,
                         sort = sort,
                         filters = filters,
                         fields = fields,
                         search = search
                         )
