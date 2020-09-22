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

__author__ = 'rkaye'


class Media_metadata():
    def __init__(self):
        '''
        self.user_data contains the json parameter needed to add this user
        to the CM.
        '''
        self.json_data = {}

    def add_attribute(self, session, attribute):
        '''
        Adds the list of key value pairs specified in attribute to the media_metadata_datp_data dictionary
        for this instance.  Attributes can be added one at a time or in a list
        :param session:  The session used to communicate with the CM for validating object ID's and names
        :param attribute: A list of dictionaries containing the attributes to add.  e.g. [{'name':'foo'},...].
        :return: True if successful.  False otherwise.

        Each key value pair is a single attribute where key is the name of the field and value is the value to be
        entered.  All key value pairs should be run through validate_attribute to make sure that they are valid
        for this data type.

        The format of the attribute field is very important and should be as follows:

        attribute = [{'<field 1>':'<value1>'},{'<field2>':'<value2>'},...{'<field n>':'<value n>'}]
        '''
        # Validate all of the keys in the key value pairs in attribute
        for key_value_pair in attribute:
            if not self.validate_attribute(key_value_pair):
                return False

                # Handle any special attributes here

        if attribute is not None:
            for key_value_pair in attribute:
                self.json_data.update(key_value_pair)
        else:
            return False

        logging.debug('user data is now: ' + json.dumps(self.json_data))
        return True

    def validate_attribute(self, attribute):
        '''
        Validates the dictionary in attribute contains a single valid key value
        pair that can be added to the user data record.  Autheticates keys based on
        Enum in framework.constants
        '''
        valid = [name for name, member in valid_media_metadata_attributes.__members__.items()]
        logging.debug('valid keys are:' + str(valid))
        logging.debug('attribute keys are:' + str([key for key in attribute]))
        for key in attribute:
            if key in valid:
                print(True)
            else:
                logging.warning('invalid user attribute: ' + key)
                return False
        return True

class Media_meta_data(framework_object):
    def __init__(self,api_version):
        super().__init__(api_version)

    def create_metadata(self,session, baseurl, name, data_type, value_type, pick_list = None):
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

        create_metadata_api_url = '/api/rest/metadata'
        create_media_metdata_parameters = {'datatype': data_type.name,
                                           'name': name,
                                           'valueType': value_type.name}
        if pick_list != None:
            # TODO: Handle pick lists defined at creation here
            pass

        self.last_response = rest_request(session,
                                          baseurl = baseurl,
                                          apiurl= create_metadata_api_url,
                                          type_of_call=call_type.post,
                                          payload_params= create_media_metdata_parameters)
        logging.debug('Made request to POST /api/rest/metadata response status code = {}, response = {}'.format(self.last_response.status_code, self.last_response.text))
        if self.last_response.status_code == 200:
            return True
        else:
            return False

    def add_picklist_values_to_media_metadata(self,session, baseurl, media_metadata_id, list_of_predefined_values):
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

        add_picklist_values_api_url = '/api/rest/metadata/multiple/' + str(media_metadata_id)
        status_code_list = []
        n = 0
        predefined_value_json_structure_list = []
        for list_item in list_of_predefined_values:
            current_predefined_value = {'id':0,'sortOrder':n,'value':list_item,'remove':'Remove'}
            predefined_value_json_structure_list.append(current_predefined_value)
            n+=1

        add_picklist_values_parameter = {'id':media_metadata_id,'predefinedValues':predefined_value_json_structure_list}

        self.last_response = rest_request(session,
                                          baseurl = baseurl,
                                          apiurl = add_picklist_values_api_url,
                                          type_of_call = call_type.put,
                                          payload_params= add_picklist_values_parameter)
        if self.last_response.status_code == 200:
            return True
        else:
            return False

    def find_metadata_by_id(self, session, baseurl, metadata_id ):


        find_metadata_apiurl = '/api/rest/metadata/' +str(metadata_id)

        return self.find_object_by_id(session = session, baseurl = baseurl, apiurl = find_metadata_apiurl,object_id = metadata_id)

    def delete_metadata_by_id(self,session,baseurl,metadata_id):

        delete_metadata_id_apiurl = '/api/rest/metadata/' + str(metadata_id)

        return self.delete_object_by_id(session = session,
                                 baseurl = baseurl,
                                 apiurl = delete_metadata_id_apiurl,
                                 object_id = metadata_id)

    def list_media_metadata(self, session, baseurl, limit = 10, offset=0, sort = None, search = None, filters = None, fields = None):
        '''
        Wrapper around GET /api/rest/metadata
        :param session: Authenticated Session object for this CM
        :param baseurl: Base URL for CM under test
        :param limit: Maximum number of metadata returned in the response
        :param offset: Offset used in paging through the metadata list
        :param sort: Sort by field name
        :param search: Serach term to search on
        :param filters: Filter object to be used in search
        :param fields: comma separated list of fields to allow in the response json object
        :return:
        '''

        list_media_metadata_apiurl = '/api/rest/metadata'

        return self.list_objects(session = session,
                          baseurl = baseurl,
                          apiurl = list_media_metadata_apiurl,
                          limit = limit,
                          offset = offset,
                          sort = sort,
                          search = search,
                          filters = filters,
                          fields = fields
        )

    def update_media_metadata(self, session, baseurl, media_metadata_id, field_change_dict):
        '''
        Wrapper around PUT /api/rest/metadata/{id}
        :param session: Logged in session object for CM under test
        :param baseurl: baseurl for CM under test
        :param media_metadata_id: ID of media metadata to update
        :param field_change_dict: JSON object to transmit during update operation
        :return:
        '''

        update_media_apiurl = '/api/rest/metadata/' + str(media_metadata_id)

        return self.update_single_object(session = session,
                                         baseurl = baseurl,
                                         apiurl = update_media_apiurl,
                                         object_id = media_metadata_id,
                                         field_change_dict=field_change_dict)



    def list_picklist_values_by_metadata_id(self, session, baseurl, metadata_id):
        '''
        Wrapper around /api/rest/metadata/{metadtaId}/picklistValues
        :param session: Authenticated Session object for this CM
        :param baseurl: Baseurl for CM under test
        :param metadata_id: ID of metadata to retrieve picklist from
        :return: Updates last_response.  True if status code = 200, False otherwise
        '''

        list_picklist_apiurl = '/api/rest/metadata/'+str(metadata_id) +'/pickListValues'

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

    def update_sort_order_media_metadata(self,session, baseurl, network_id, update_sort_order_param ):
        '''
        Wrapper around PUT /api/rest/metadata/multi/{network_id}
        :param session: Authenticated session variable on current CM
        :param baseurl: baseurl for current CM under test
        :param network_id: Network ID for query
        :param Update source order param is a list of dicts of the form:
        [{'id':<metadata id 1>,'order':<new sort order>},{'id':<metadata id 2>,'order':<new sort order>}]
        '''

        update_sort_order_apiurl = '/api/rest/metadata/multi/' + str(network_id)

        update_sort_order_parameter = {'metadataVariables':update_sort_order_param}

        self.last_response = rest_request(session = session,
                                          baseurl = baseurl,
                                          apiurl = update_sort_order_apiurl,
                                          type_of_call= call_type.put,
                                          payload_params= update_sort_order_parameter)

        logging.debug('Made call to PUT {}.  Response code: {}, Response: {}'.format(update_sort_order_apiurl,
                                                                                     self.last_response.status_code,
                                                                                     self.last_response.text))

        if self.last_response.status_code == 200:
            return True
        else:
            return False




if __name__ == '__main__':
    configuration = configparser.ConfigParser()
    configuration.read(CONFIG_FILE_PATH)
    baseurl = configuration['login']['baseurl']
    username = configuration['login']['username']
    password = configuration['login']['password']
    logging.config.fileConfig("config/log_config")
    logging.debug('Read from config file and ready to begin.')
    s = login(username, password, baseurl, 0)

    mmd1 = Media_metadata()

    params1 = [{'name':'a'}, {'datatype':'STRING'},{'valueType':'ANY'}]
    params2 = [{'name':'b'}, {'datatype':'INTEGER'},{'valueType':'ANY'}]
    params3 = [{'name':'c'}, {'datatype':'BOOLEAN'},{'valueType':'ANY'}]
    params4 = [{'name':'d'}, {'datatype':'STRING'},{'valueType':'PICKLIST'}]
    params5 = [{'name':'e'}, {'datatype':'INTEGER'},{'valueType':'PICKLIST'}]
    params6 = [{'name':'f'}, {'datatype':'BOOLEAN'},{'valueType':'PICKLIST'}]

    mmd1.add_attribute(s,attribute = params1)
    resp = rest_request(s, call_type.post, baseurl=baseurl, apiurl="/api/rest/metadata", payload_params=mmd1.json_data, proxy=False)

    mmd1.add_attribute(s,attribute = params2)
    resp = rest_request(s, call_type.post, baseurl=baseurl, apiurl="/api/rest/metadata", payload_params=mmd1.json_data, proxy=False)

    mmd1.add_attribute(s,attribute = params3)
    resp = rest_request(s, call_type.post, baseurl=baseurl, apiurl="/api/rest/metadata", payload_params=mmd1.json_data, proxy=False)

    mmd1.add_attribute(s,attribute = params4)
    resp = rest_request(s, call_type.post, baseurl=baseurl, apiurl="/api/rest/metadata", payload_params=mmd1.json_data, proxy=False)

    mmd1.add_attribute(s,attribute = params5)
    resp = rest_request(s, call_type.post, baseurl=baseurl, apiurl="/api/rest/metadata", payload_params=mmd1.json_data, proxy=False)
#Note:  Media type Boolean and datatype Picklist is not a leagal addition to the CM.  This should be rejected
    mmd1.add_attribute(s,attribute = params6)
    resp = rest_request(s, call_type.post, baseurl=baseurl, apiurl="/api/rest/metadata", payload_params=mmd1.json_data, proxy=False)