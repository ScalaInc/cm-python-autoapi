__author__ = 'rkaye'
import sys, json
import requests
import logging
import logging.config
from time import sleep
import configparser
from framework.constants import *
from framework.authentication_rest import *
from framework.http_rest import rest_request
from framework.inventory import Roles_inventory
from itertools import chain
from framework.constants import call_type
from framework.framework_object_rest import framework_object


class Roles(framework_object):
    def __init__(self, api_version):
        '''
        Constructor for Roles object
        :param api_version:
        :return:
        '''
        super().__init__(api_version)

    def list_roles(self,session, baseurl, limit = 10, offset = 0, sort = None, search = None, filters = None, fields = None):
        list_roles_apiurl = '/api/rest/roles'
        return self.list_objects(session = session,
                                 baseurl = baseurl,
                                 apiurl = list_roles_apiurl,
                                 limit = limit,
                                 offset = offset,
                                 sort = sort,
                                 search = search,
                                 filters = filters,
                                 fields = filters)

    def create_role(self, session, baseurl, name, resources_list, system ):
        """
        Wrapper around POST /api/rest/roles

        :param session: authenticated session object
        :param baseurl: Base URL of CM under test
        :param name: Name of new Role
        :param resources_list: List of resources assigned to this role of the form:
        "resources": [
        {
            "id": 1,
            "name": "Everything",
            "description": "Everything",
            "sortOrder": 10
        }
        ]
        :param system: Boolean, True if the role is a system role
        :return: True if response code is 200, False otherwise.  Updates self.last_resonse
        """

        create_role_apiurl = '/api/rest/roles'
        role_param = {'name': name,
                      'system': system,
                      'resources': resources_list
        }

        self.last_response = rest_request(session = session,
                                          baseurl = baseurl,
                                          apiurl = create_role_apiurl,
                                          type_of_call= call_type.post,
                                          payload_params=role_param)

        logging.debug('Sent call to POST {}, Response code = {}, Response = {}'.format(create_role_apiurl,
                                                                                       self.last_response.status_code,
                                                                                       self.last_response.text))
        if self.last_response.status_code == 200:
            return True
        else:
            return False

    def delete_role_by_id(self, session, baseurl, role_id):
        """
        Wrapper around DELETE /api/rest/roles/{id}
        :param session: Authenticated session object
        :param baseurl: Base url of system under test
        :param role_id: ID of role to delete from system
        :return:True if response code is 204, False otherwise, updates self.last_response
        """
        delete_role_by_id_apiurl = '/api/rest/roles/' + str(role_id)
        return self.delete_object_by_id(session = session,
                                        baseurl=baseurl,
                                        apiurl = delete_role_by_id_apiurl,
                                        object_id=role_id)

    def update_role(self, session, baseurl, role_id, field_change_dict):
        """
        Wrapper around PUT /api/rest/roles?{id}
        Uses super method - Update Object
        :param session: Authenticated session object
        :param baseurl: Baseurl of CM under test
        :param role_id: ID of role to modify
        :param field_change_dict: Fields to modify
        :return:True if response code is 200.  False otherwise.  Updates self.last_response
        """

        update_role_apiurl = '/api/rest/roles/' + str(role_id)

        return self.update_single_object(session = session,
                                         baseurl = baseurl,
                                         apiurl = update_role_apiurl,
                                         object_id = role_id,
                                         field_change_dict=field_change_dict)