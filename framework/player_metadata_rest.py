__author__ = 'rkaye'
import sys, json
import requests
import logging
import logging.config
from time import sleep
import configparser
from framework.constants import *
from framework.http_rest import rest_request
from framework.authentication_rest import login
from framework.framework_object_rest import framework_object


class Player_meta_data(framework_object):
    def __init__(self,api_version):
        super().__init__(api_version)

    def create_metadata(self,session, baseurl,name, data_type, value_type, pick_list = None):
        '''
        Implements POST /api/rest/metadata

        Create a new media_metadata object with the associated parameters.  Leave the response in last_response
        :param session: Logged in Session object
        :param baseurl: baseurl for CM under test
        :param name: Name of the metadata object
        :param data_type: constants.metadata_data_type
        :param value_type: constants.metadata_value_type
        :param picklist: List of key value pairs [{'value':<value>,'sortOrder':<order>,'variableId':<metadata ID>}]
        :return: True if response code is 200, false otherwise and update the self.last_response variable for this object
        '''

        create_metadata_api_url = '/api/rest/playerMetadata'
        create_player_metadata_parameters = {'datatype':data_type.name,
                                           'name': name,
                                           'valueType':value_type.name}
        if pick_list != None:
            # TODO: Handle pick lists defined at creation here
            pass

        self.last_response = rest_request(session,
                                          baseurl = baseurl,
                                          apiurl= create_metadata_api_url,
                                          type_of_call=call_type.post,
                                          payload_params= create_player_metadata_parameters)
        logging.debug('Made request to POST {} response status code = {}, response = {}'.format(create_metadata_api_url,
                                                                                                self.last_response.status_code,
                                                                                                self.last_response.text))
        if self.last_response.status_code == 200:
            return True
        else:
            return False

    def add_picklist_values_to_player_metadata(self,session, baseurl, metadata_id, list_of_predefined_values):
        '''
        Implements PUT /api/rest/metdata/multiple/{metadataId}

        Add the list_of_predefined_values to the media metadata item under test.

        E.G. ['dog','cat','fish','penguin'] would add 4 picklist items to the picklist.

        This is how to populate the picklists on a media metadata object.

        :param session: Logged in session object
        :param baseurl: baseurl for the CM under test
        :param media_metadata_id: ID of media metadata item to
        :param list_of_predefined_values: A list of the picklist items in the form: {id:<id>,'sortOrder':<sortorder>,'value':<value>}
        :return: True if status code is 200 for ALL adds, False otherwise, updates last response
        '''

        add_picklist_values_api_url = '/api/rest/playerMetadata/multiple/' + str(metadata_id)
        status_code_list = []
        n = 0
        predefined_value_json_structure_list = []
        for list_item in list_of_predefined_values:
            current_predefined_value = {'id':0,'sortOrder':n,'value':list_item,'remove':'Remove'}
            predefined_value_json_structure_list.append(current_predefined_value)
            n+=1

        add_picklist_values_parameter = {'id':metadata_id,'predefinedValues':predefined_value_json_structure_list}

        self.last_response = rest_request(session,
                                          baseurl = baseurl,
                                          apiurl = add_picklist_values_api_url,
                                          type_of_call = call_type.put,
                                          payload_params= add_picklist_values_parameter)
        if self.last_response.status_code == 200:
            return True
        else:
            return False

    def list_player_metadata(self, session, baseurl, limit = 10, offset = 0, sort = 'name', filters = None, fields = None, search = None):
        '''
        Wrapper around GET /api/rest/playerMetadata
        :param session: Session logged into CM under test
        :param baseurl: Base URL of CM under test
        :param limit: Max number of metadata to return in the response
        :param offset: offset used in paging through the responses
        :param sort: string of comma separated fields to sort by
        :param filters:
        :param fields: string of comma separated fields to limit the response to
        :param search: string to search in the name of metadata in the response
        :return:  True if http response code is 200.  False otherwise.  Updates self.last_response
        '''
        list_player_metadata_apiurl = '/api/rest/playerMetadata'

        return self.list_objects(session = session,
                                 baseurl = baseurl,
                                 apiurl = list_player_metadata_apiurl,
                                 limit = limit,
                                 offset = offset,
                                 sort = sort,
                                 filters = filters,
                                 fields = fields,
                                 search = search)

    def find_metadata_by_id(self, session, baseurl, metadata_id ):

        find_metadata_apiurl = '/api/rest/playerMetadata/' +str(metadata_id)

        return self.find_object_by_id(session = session, baseurl = baseurl, apiurl = find_metadata_apiurl,object_id = metadata_id)

    def delete_metadata_by_id(self,session,baseurl,metadata_id):

        delete_metadata_id_apiurl = '/api/rest/playerMetadata/' + str(metadata_id)

        return self.delete_object_by_id(session = session,
                                        baseurl = baseurl,
                                        apiurl = delete_metadata_id_apiurl,
                                        object_id = metadata_id)

    def list_picklist_values_by_metadata_id(self, session, baseurl, metadata_id):
        '''
        Wrapper around /api/rest/playerMetadata/{metadtaId}/picklistValues
        :param session: Authenticated Session object for this CM
        :param baseurl: Baseurl for CM under test
        :param metadata_id: ID of metadata to retrieve picklist from
        :return: Updates last_response.  True if status code = 200, False otherwise
        '''

        list_picklist_apiurl = '/api/rest/playerMetadata/'+str(metadata_id) +'/pickListValues'

        self.last_response = rest_request(session = session,
                                          baseurl = baseurl,
                                          type_of_call=call_type.get,
                                          apiurl = list_picklist_apiurl)
        logging.debug('Made call to GET {}.  Response status code is: {} Response is {}'.format(list_picklist_apiurl,
                                                                                                self.last_response.status_code,
                                                                                                self.last_response.text))
        if self.last_response.status_code == 200:
            return True
        else:
            return False

    def get_picklist_item_id(self,session, baseurl, metadata_id, picklist_value):
        '''
        For a given metadata with ID = metadata_id using a picklist, find the picklist ID associated with picklist_value
        :param session:
        :param baseurl:
        :param metadata_id:
        :param picklist_value:
        :param api_version_media_metadata:
        :return: The picklist ID associated with picklist_value, or None if it is not found
        '''
        self.find_metadata_by_id(session = session,
                                            baseurl = baseurl,
                                            metadata_id = metadata_id)
        metadata_json = self.get_last_response().json()
        for picklist_item in metadata_json['predefinedValues']:
            logging.debug('Determination of picklist value is: {}, id: {}, metadata value: {}'.format(picklist_item['value'],picklist_item['id'],picklist_value))
            if picklist_item['value']==str(picklist_value):
                logging.debug('Determination of picklist value is {}.  Metadata value is {}.  Picklist ID is {}'.format(picklist_item['value'],picklist_value,picklist_item['id']))
                return picklist_item['id']
        return None

    def modify_player_metadata_assignment(self,session, baseurl, player_id, metadata_id, metadata_value,api_version_player_metadata):
        """
        Modify the metadata assignment for a given player
        :param session: Authenticated session object on CM under test
        :param baseurl: Base url of CM under test
        :param player_id: ID of player to modify
        :param metadata_id: ID of metadata to modify
        :param metadata_value: Value of metadata to change to
        :param api_version_player_metadata: Version of metadata api to use when making this change
        :return:
        """

        metadata_object = Player_meta_data(api_version_player_metadata)
        metadata_object.find_metadata_by_id(session = session,
                                            baseurl = baseurl,
                                            metadata_id = metadata_id)#, 'Could not find boolean metadata with ID =' + str(metadata_id)
        # Ugly bit where I pull down the metadata object from the CM and modify it so it can be
        # Changed on the media object - the field 'order' must be removed
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

        changed_metadata_definition = {'metadataValue':[{'value':value_placeholder,'metadata':metadata_json}]}
        logging.debug('Determined {}'.format(json.dumps(changed_metadata_definition)))

        return self.update_single_player(session = session,
                                         baseurl = baseurl,
                                         player_id = player_id,
                                         field_change_dict = changed_metadata_definition), 'Failed to update the media with the new metadata value: {}'.format(self.last_response.text)

    def update_player_metadata(self, session, baseurl, player_metadata_id, field_change_dict = None):
        """
        Wrapper around  /api/rest/playerMetadata/{id}
        :param session: Authenticated session objcect
        :param baseurl: Base url of CM under test
        :param player_metadata_id: Id of metadata to update
        :param field_change_dict: Fields to change
        :return: True if response code is 200.  False otherwise.  Updates
        """

        update_player_metadata_apiurl = '/api/rest/playerMetadata/' + str(player_metadata_id)
        return self.update_single_object(session = session,
                                         baseurl = baseurl,
                                         apiurl = update_player_metadata_apiurl,
                                         object_id=player_metadata_id,
                                         field_change_dict=field_change_dict)