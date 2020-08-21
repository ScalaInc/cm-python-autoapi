__author__ = 'rkaye'
from framework.framework_object_rest import framework_object
from framework.player_metadata_rest import Player_meta_data
from framework.constants import *
from framework.http_rest import rest_request
import logging
import json
import logging.config

class Player(framework_object):
    '''
    Class that encapsulates all of the methods used in testing player API
    '''
    apiurl = '/api/rest/players'

    def __init__(self,api_version):
        '''
        Constructor initializes api version
        :return: VOID
        '''
        super().__init__(api_version)
        
    def create_player(self,
                      session,
                      baseurl,
                      name,
                      description=None,
                      type="SCALA",
                      distribution_server_id=1053
                      ):
        
        '''
        One cannot "assume" that the distribution_server_id is 1. Apparently the main Point to Point server is not always 1.
        If we want to use this framework - we will need to fix that. I manually change this value in order to avoid a number of
        errors that are created in the log because of this problem.
        
        Uses the POST /api/rest/players api call to create a player
        :param session: The requests.session variable used to send the API call
        :param baseurl: The base url of the CM under test e.g. http//w.x.y.z:8080/ContentManager
        :param name: Name of the player
        :param api_version: API version being tested.  Defaults to constants.DEFAULT_API_VERSION
        :param type: Type of Player - defaults to 'SCALA'
        :return: True if response code is 200, False otherwise
        '''
        type_of_call = call_type.post

        player_parameter = {'name':name, 'type':type, 'distributionServer':{'id':distribution_server_id}}
        if description != None:
            player_parameter['description'] = description
        self.last_response  = rest_request(session, type_of_call=type_of_call, baseurl=baseurl, apiurl=self.apiurl, payload_params=player_parameter)
        logging.debug('Called POST /api/rest/players: status_code = {}, response = {}, elapsed time= {}'.format(self.last_response.status_code, self.last_response.text, self.last_response.elapsed))

        if self.last_response.status_code == 200:
            return True
        else:
            return False

    def create_multiple_players(self,
                                session,
                                baseurl,
                                name,
                                type = 'SCALA',
                                start_at_player_number=1,
                                number_of_players=1,
                                distribution_server_id=1053
                                ):
        '''
        One cannot "assume" that the distribution_server_id is 1. Apparently the main Point to Point server is not always 1.
        If we want to use this framework - we will need to fix that. I manually change this value in order to avoid a number of
        errors that are created in the log because of this problem.
        
        Uses the POST /api/rest/players/multiPlayer api call to create multiple players
        :param session: The requests.session variable used to send the API call
        :param baseurl: The base url of the CM under test e.g. http//w.x.y.z:8080/ContentManager
        :param name: Name of the player- with the index represented by a # symbol. e.g. 'Player #'
        :param start_at_player_number: The starting index for the new player
        :param number_of_players: Number of players to add
        :param distribution_server_id: Defaults to 1.
        :return: True if status code is 200, False otherwise.  Updates last_response
        '''
        create_multiple_players_apiurl = '/api/rest/players/multiPlayer'

        create_multiple_players_param = {'name': name,
                                         'type': type,
                                         'startAt': start_at_player_number,
                                         'numOfPlayers': number_of_players,
                                         'distributionServer':{'id': distribution_server_id}}

        self.last_response = rest_request(session = session,
                                          baseurl = baseurl,
                                          apiurl = create_multiple_players_apiurl,
                                          type_of_call=call_type.post,
                                          payload_params=create_multiple_players_param
                                          )

        logging.debug('Sent call to POST {}.  Response code = {}, Response = {}'.format(create_multiple_players_apiurl,
                                                                                        self.last_response.status_code,
                                                                                        self.last_response.text))

        if self.last_response == 200:
            return True
        else:
            return False



    def delete_player_by_id(self,
                            session,
                            baseurl,
                            id):
        '''
        Uses the DELETE /api/rest/players/{id} API call to delete a player
        :param session: The requests.session variable used to send the API call
        :param baseurl: The base url of the CM under test. e.g. http//w.x.y.z:8080/ContentManager
        :param id: The ID parameter of the player to delete
        :return: True if the response code was 204 for the call.  False otherwise
        '''

        delete_apiurl = self.apiurl + '/' + str(id)
        type_of_call = call_type.delete

        resp = rest_request(session, type_of_call=type_of_call,baseurl = baseurl, apiurl= delete_apiurl)
        logging.debug('Attempted to delete player with id = {}.  Response was: status_code expected 204, actual {}, response = {}'.format(id, resp.status_code, resp.text))
        self.last_response = resp
        self.json_data = {} # Deleted the object so clear the json representation!
        if resp.status_code == 204:
            return True
        else:
            return False


    def update_single_player(self, session, baseurl, player_id, field_change_dict=None ):
        '''
        Implements /api/rest/players/<id>
        :param session: Session object logged into CM under test
        :param baseurl: baseurl for CM under test
        :param object_id: ID of player to update
        :param field_change_dict: The specific dictionary that contains fields to change
        :return: Returns True if response code is 200, False otherwise.  Updates self.last_response
        '''

        update_single_player_apiurl = '/api/rest/players/' + str(player_id)

        return self.update_single_object(session = session,
                                  baseurl = baseurl,
                                  apiurl = update_single_player_apiurl,
                                  object_id = player_id,
                                  field_change_dict= field_change_dict)

    def find_player_by_id(self,session,baseurl,player_id, fields = None):
        '''
        Uses GET /api/rest/players to request the JSON representation of the player specified by 'id'
        :param session: The requests.session variable used to send the API call
        :param baseurl: The base url of the CM under test e.g. http//w.x.y.z:8080/ContentManager
        :param id: The ID of the player returned
        :return: True if status code == 200, False otherwise
        '''

        get_player_apiurl = '/api/rest/players/' + str(player_id)
        # type_of_call = call_type.get
        #
        # resp = rest_request(session, type_of_call = type_of_call, baseurl = baseurl, apiurl = get_apiurl)
        # logging.debug('Attempted to GET {}.  Response was: status_code = {}, response = {}'.format(get_apiurl, resp.status_code, resp.text))
        # self.last_response = resp
        # self.json_data = resp.json()
        # if resp.status_code == 200:
        #     return True
        # else:
        #     return False
        return self.find_object_by_id(session, baseurl = baseurl, apiurl = get_player_apiurl, object_id = player_id, fields = fields)

    def generate_plan(self, session, baseurl, uuid):
        '''
        Wrapper for POST /api/rest/players/{uuid}/generatePlan

        :param session: Logged in Session object for cm under test
        :param baseurl: base url of CM under test
        :param uuid: universal unique identifier for one or more players in storage
        :return:True if return code is 200
        '''

        generate_plan_apiurl = '/api/rest/players/' + uuid + '/generatePlan'

        self.last_response = rest_request(session = session,
                             baseurl = baseurl,
                             apiurl = generate_plan_apiurl,
                             type_of_call = call_type.post)
        logging.debug('Made call to POST {}.  Response code = {}, response = {}'.format(generate_plan_apiurl,
                                                                                           self.last_response.status_code,
                                                                                           self.last_response.text))
        if self.last_response.status_code == 200:
            return True
        else:
            return False
    def get_player_plans(self, session, baseurl, player_id):
        '''
        Wrapper for /aip/rest/player/<id>/plans
        :param session:
        :param baseurl:
        :param player_id:
        :return:
        '''

        get_player_plan_apiurl = '/api/rest/players/' + str(player_id) + '/plans'

        self.last_response = rest_request(session = session,
                                          baseurl = baseurl,
                                          apiurl = get_player_plan_apiurl,
                                          type_of_call = call_type.get)
        logging.debug('made call to GET {}.  Response code = {}, response = {}'.format(get_player_plan_apiurl,
                                                                                       self.last_response.status_code,
                                                                                       self.last_response.text))

        if self.last_response.status_code == 200:
            return True
        else:
            return False

    def list_players(self,session,baseurl, limit = 10, offset = 0, sort = None, search = None, filters = None, fields = None):
        list_players_apiurl = '/api/rest/players'
        return self.list_objects(session = session,
                         baseurl=baseurl,
                         apiurl=list_players_apiurl,
                         limit = limit,
                         offset = offset,
                         sort = sort,
                         search = search,
                         filters = filters,
                         fields = fields)

    def list_players_inventory(self,session,baseurl, player_id, limit = 10, offset = 0, sort = None, search = None, filters = None, fields = None):
        list_inventory_apiurl = '/api/rest/players/' + str(player_id) +'/inventory'
        return self.list_objects(session = session,
                         baseurl=baseurl,
                         apiurl=list_inventory_apiurl,
                         limit = limit,
                         offset = offset,
                         sort = sort,
                         search = search,
                         filters = filters,
                         fields = fields)

    def list_player_versions(self, session, baseurl):
        '''
        Wrapper around /api/rest/players/versions
        :param session: Logged in session object on CM under test
        :param baseurl: baseurl of CM under test
        :return: True if status code = 200, False otherwise.  Updates self.last_response
        '''
        list_versions_apiurl = '/api/rest/players/versions'

        self.last_response = rest_request(session = session,
                                          baseurl = baseurl,
                                          apiurl = list_versions_apiurl,
                                          type_of_call=call_type.get)

        logging.debug('Sent call to GET {}, Status code = {}, response = {}'.format(list_versions_apiurl,
                                                                                    self.last_response.status_code,
                                                                                    self.last_response.text))

        if self.last_response.status_code == 200:
            return True
        else:
            return False

    def list_ex_module_licenses(self,session, baseurl):
        '''
        Wrapper around /api/rest/players/modules
        :param session: Logged in session object to CM under test
        :param baseurl: Baseurl for CM under test
        :return: True if status code ==200, False otherwise, updates self.last_response
        '''

        list_module_apiurl = '/api/rest/players/modules'
        self.last_response = rest_request(session = session,
                                          baseurl = baseurl,
                                          apiurl = list_module_apiurl,
                                          type_of_call=call_type.get)

        logging.debug('Sent call to GET {}, Status code = {}, response = {}'.format(list_module_apiurl,
                                                                                    self.last_response.status_code,
                                                                                    self.last_response.text))

        if self.last_response.status_code == 200:
            return True
        else:
            return False

    def modify_player_metadata_assignment(self,session, baseurl, name, player_id, metadata_id, metadata_value,api_version_player_metadata):

        metadata_object = Player_meta_data(api_version_player_metadata)
        metadata_object.find_metadata_by_id(session = session,
                                            baseurl = baseurl,
                                            metadata_id = metadata_id)#, 'Could not find boolean metadata with ID =' + str(metadata_id)
        # Ugly bit where I pull down the metadata object from the CM and modify it so it can be
        # Changed on the player object - the field 'order' must be removed
        metadata_json = metadata_object.get_last_response().json()
        metadata_json.pop('order')

        # If the Metadata is a PICKLIST, we need to specify the value field as the picklist ID, not as the actual value
        value_placeholder = metadata_value # The default case for when we have an ANY type metadata

        if metadata_json['valueType'] == 'PICKLIST':
            logging.debug('Determination of type of metadata: {}'.format(metadata_json['valueType']))
            for picklist_item in metadata_json['predefinedValues']:
                logging.debug('Determination of picklist value is: {}, id: {}, metadata value: {}'.format(picklist_item['value'],picklist_item['id'],metadata_value))
                if picklist_item['value']==str(metadata_value):
                    logging.debug('Determination of picklist value is {}.  Metadata value is {}.  Picklist ID is {}'.format(picklist_item['value'],metadata_value,picklist_item['id']))
                    value_placeholder = picklist_item['id'] # Remap the value to the ID in a PICKLIST

        changed_metadata_definition = {'name':name,'metadataValue':[{'value':value_placeholder,'playerMetadata':metadata_json}]}
        logging.debug('Determined {}'.format(json.dumps(changed_metadata_definition)))

        return self.update_single_player(session = session,
                                         baseurl = baseurl,
                                         player_id = player_id,
                                         field_change_dict = changed_metadata_definition), 'Failed to update the player with the new metadata value: {}'.format(self.last_response.text)

    def player_faceted_search(self, session, baseurl, limit = 10, offset = 0, sort = 'name', filters = None, facets = None, fields = None, search = None):
        '''
        Wrapper around /api/rest/players/search

        :param session: Logged in session object
        :param baseurl: baseurl of CM under test
        :param limit: Number of resources to return in the response
        :param offset: offset used in paging
        :param sort: name of the field to sort results on
        :param filters: filters - if any - to apply to the result
        :param facets: comma separated list of facets to include in response object.  Must be URL encoded
        :param fields: comman separated list of fields to include in response objects
        :param search: String to search for in the name field of the resources in the response
        :return: True if respones code is 200.  False otherwise.  Updates last_response
        '''
        player_faceted_search_apiurl = '/api/rest/players/search'
        return self.faceted_search_on_object(session = session,
                                             baseurl = baseurl,
                                             apiurl = player_faceted_search_apiurl,
                                             limit = limit,
                                             offset = offset,
                                             sort = sort,
                                             filters = filters,
                                             facets = facets,
                                             fields = fields,
                                             search = search)

    def get_state_for_one_or_more_players(self,session, baseurl, uuid):
        '''
        Wrapper around GET /api/rest/players/{uuid}/states
        :param session: Session logged into CM under test
        :param baseurl: base url of CM under test
        :param uuid: UUID for list of Player Id's to get the state on
        :return: True if response code == 200, false otherwise.  Updates self.last_response
        '''

        get_state_apiurl = '/api/rest/players/' + str(uuid) +'/states'

        self.last_response = rest_request(session = session,
                                          baseurl = baseurl,
                                          apiurl = get_state_apiurl,
                                          type_of_call= call_type.get)

        logging.debug('Made call to {}.  Response code = {}, Response = {}'.format(get_state_apiurl,
                                                                                   self.last_response.status_code,
                                                                                   self.last_response.text))

        if self.last_response.status_code == 200:
            return True
        else:
            return False

    def reset_mac_address (self, session, baseurl, id):
        '''
        Wrapper around PUT /api/rest/players/resetMAC/<id>
        :param session: Session logged into CM under test
        :param baseurl: base url of CM under test
        :param id: ID of player to return
        :return: True if response code = 200, false otherwise.  Updates self.last_response
        '''

        reset_mac_apiurl = '/api/rest/players/resetMAC/' + str(id)

        self.last_response = rest_request(session = session,
                                          baseurl = baseurl,
                                          apiurl = reset_mac_apiurl,
                                          type_of_call=call_type.put)

        logging.debug("Made call to {}.  Response code {}, Response {}".format( reset_mac_apiurl,
                                                                                self.last_response.status_code,
                                                                                self.last_response.text))

        if self.last_response.status_code == 200:
            return True
        else:
            return False
