__author__ = 'richardkaye'
from framework.constants import call_type
from framework.framework_object_rest import framework_object
from framework.http_rest import rest_request
import logging

class PlayerGroup(framework_object):

    def __init__(self, api_version):
        super().__init__(api_version)

    def create_player_group(self, session, baseurl, name, description = None):
        """
        Wrapper around POST /api/rest/playergroup
        :param session: Authenticated session on CM under test
        :param baseurl: Base URL of CM under tes
        :param name: Name of playergroup to create
        :param description: Description of playergroup to create
        :return: True if response code is 200.  False otherwise.  Updates self.last_response
        """

        create_player_apiurl = '/api/rest/playergroup'
        create_player_parameter = {'name':name}
        if description is not None:
            create_player_parameter['description'] = description

        self.last_response = rest_request(session = session,
                                          baseurl = baseurl,
                                          apiurl = create_player_apiurl,
                                          type_of_call= call_type.post,
                                          payload_params=create_player_parameter)

        logging.debug('Made call to POST {}.  Response code = {}, Response = {}'.format(create_player_apiurl,
                                                                                        self.last_response.status_code,
                                                                                        self.last_response.text))

        if self.last_response.status_code == 200:
            return True
        else:
            return False

    def delete_player_group_by_id(self,session, baseurl, player_group_id):
        """
        Wrapper around DELETE /api/rest/playergroup/{id}
        :param session: Authenticated session object associated with CM under test
        :param baseurl:Base url of CM under test
        :param player_group_id: ID of player group to delete
        :return: True if response code is 200.  False otherwise.  Updates self.last_response
        """
        delete_player_apiurl = '/api/rest/playergroup/' + str(player_group_id)
        return self.delete_object_by_id(session = session,
                                        baseurl = baseurl,
                                        apiurl = delete_player_apiurl,
                                        object_id= player_group_id)

    def find_player_group_by_id(self, session, baseurl, player_group_id, fields = None):
        """
        Wrapper around DELETE /api/rest/playergroup/{id}
        :param session: Authenticated session object associated with CM under test
        :param baseurl: Base url of CM under test
        :param player_group_id: ID of player group to find
        :param fields: Comma separated list of fields to return in the response
        :return: True if response code is 200.  False otherwise.  Updates self.last_response
        """

        find_player_group_by_id_apiurl = '/api/rest/playergroup/' +str(player_group_id)
        return self.find_object_by_id(session = session,
                                      baseurl = baseurl,
                                      apiurl = find_player_group_by_id_apiurl,
                                      object_id=player_group_id,
                                      fields = fields)

    def get_assigned_for_player_group(self, session,baseurl, ids = None):
        """
        Wrapper around GET /api/rest/playergroup/usage
        :param session: Authenticated session object associated with CM under test
        :param baseurl: Base url of CM under test
        :param ids: String containing a comma separated list of player group ID's for which
        the assignments should be calculated
        :return: True if response code is 200.  False otherwise.  Updates self.last_response
        """

        get_assigned_apiurl = '/api/rest/playergroup/usage'
        query_params = None
        if ids is not None:
            query_params = {'ids': ids}

        self.last_response = rest_request(session = session,
                                          baseurl = baseurl,
                                          apiurl= get_assigned_apiurl,
                                          type_of_call=call_type.get,
                                          query_params=query_params)

        logging.debug('Made call to GET {}, response code = {}, response = {}'.format(get_assigned_apiurl,
                                                                                      self.last_response.status_code,
                                                                                      self.last_response.text))

        if self.last_response.status_code == 200:
            return True
        else:
            return False

    def list_player_groups(self, session, baseurl, limit = 10, offset = 0, sort = 'name', filters = None, search = None, fields = None):
        """
        Wrapper around GET /api/rest/playergroup

        Utilizes super class method framework_object.list_objects

        :param session: Authenticated session object associated with CM under test
        :param baseurl: Base url of CM under test
        :param limit:
        :param offset:
        :param sort:
        :param filters:
        :param search:
        :param fields:
        :return:
        """
        list_player_groups_apiurl = '/api/rest/playergroup'

        return self.list_objects(session = session,
                                 baseurl = baseurl,
                                 apiurl = list_player_groups_apiurl,
                                 limit = limit,
                                 offset = offset,
                                 sort = sort,
                                 search = search,
                                 filters =filters,
                                 fields = fields)

    def multi_update_player_groups(self, session, baseurl, uuid, description):
        """
        Wrapper around PUT /api/rest/playergroup
        Note:  The UUID parameter is the UUID created with the store value api:  POST /api/rest/storage.
        The form of that storage object must be {'ids':[<list of player group ids]}
        E.G. {'ids':[3,4,5,6,7]}

        :param session: Authenticated session object associated with CM under test
        :param baseurl: Base url of CM under test
        :param uuid: UUID of storage object with list of ID's
        :param description: Description is currently the only field supported by this API call
        :return: True if response code is 200.  False otherwise.  Updates self.last_response
        """

        multi_update_playergroup_apiurl = '/api/rest/playergroup'

        multi_update_payload_params = {'uuid':uuid, 'fields':{'description':description}}

        self.last_response = rest_request(session = session,
                                         baseurl = baseurl,
                                         apiurl = multi_update_playergroup_apiurl,
                                         type_of_call=call_type.put,
                                         payload_params=multi_update_payload_params)

        logging.debug('Made call to PUT {}, Response code = {}, Response = {}'.format(multi_update_playergroup_apiurl,
                                                                                      self.last_response.status_code,
                                                                                      self.last_response.text))

        if self.last_response.status_code == 200:
            return True
        else:
            return False

    def update_player_group_by_id(self, session, baseurl, player_group_id, update_dict):
        """
        Wrapper around PUT /api/rest/playergroup{id}
        :param session: Authenticated session object associated with CM under test
        :param baseurl: Base url of CM under test
        :param player_group_id: ID of player group to update
        :param update_dict: Dict containing records to update
        :return: True if response code is 200.  False otherwise.  Updates self.last_response
        """

        update_playergroup_id_apiurl = '/api/rest/playergroup/' + str(player_group_id)

        return self.update_single_object(session = session,
                                         baseurl = baseurl,
                                         apiurl = update_playergroup_id_apiurl,
                                         object_id=player_group_id,
                                         field_change_dict=update_dict)





