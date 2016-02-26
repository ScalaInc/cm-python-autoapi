__author__ = 'rkaye'
import sys, json
import requests
import logging
import logging.config
from framework.http_rest import rest_request
from framework.framework_object_rest import framework_object
from framework.constants import call_type
from itertools import chain

__author__ = 'rkaye'


class Network(framework_object):
    def __init__(self, api_version):
        """
        Constructor for networks.  Sets the JSON object json_data to empty.
        :return: VOID
        """
        super().__init__(api_version)

    def update_network_settings(self, session, baseurl, network_id, network_definition):
        """
        Wrapper around PUT /api/rest/networks/{id}
        :param session: Logged in session object to the CM under test
        :param baseurl: base url of CM under test
        :param network_id: ID of network to update
        :param network_definition: Dict containing the fields to update
        :return:True if response code is 200.  False otherwise.  Updates self.last_response
        """

        update_network_apiurl = '/api/rest/networks/' + str(network_id)

        return self.update_single_object(session=session,
                                         baseurl=baseurl,
                                         apiurl=update_network_apiurl,
                                         object_id=network_id,
                                         field_change_dict=network_definition)

    def get_network_information(self, session, baseurl, network_id, fields = None):
        """
        Wrapper around GET /api/rest/networks/{id}
        :param session: Logged in session object to CM under test
        :param baseurl: base url of CM under test
        :param network_id: ID of network under test
        :return:True if response code is 200.  False otherwise.  Updates self.last_response
        """

        get_network_info_apiurl = '/api/rest/networks/' + str(network_id)

        return self.find_object_by_id(session = session,
                                      baseurl = baseurl,
                                      apiurl = get_network_info_apiurl,
                                      object_id = network_id)

    def create_first_network(self, session, baseurl, network_name):
        """
        Wrapper around POST /api/rest/networks/first

        Since this method can only be run when the system is first set up, and I think
        that it only runs from the CM locally (Security check), it may not be used by
        the framework at all.  Including it for completeness

        :param session: Authenticated session to CM under test
        :param baseurl: base url of CM under test
        :param network_name: Name of network to create
        :return: True if status code is 200, False otherwise
        """

        create_first_network_apiurl = '/api/rest/networks/first'
        payload_params = {'name': network_name}

        self.last_response = rest_request(session = session,
                                          baseurl = baseurl,
                                          apiurl = create_first_network_apiurl,
                                          type_of_call= call_type.post,
                                          payload_params=payload_params)

        logging.debug('Made call to POST {}.  Response code = {}. Response = {}'.format(create_first_network_apiurl,
                                                                                        self.last_response.status_code,
                                                                                        self.last_response.text))

        if self.last_response.status_code == 200:
            return True
        else:
            return False