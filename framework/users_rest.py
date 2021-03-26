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


class user_cm():
    """
    Helper class that builds a user json object for use in API testing.
    Class methods 'help' programmers by validating data before it can be
    placed into the main data object for the instance.
    """

    def __init__(self):
        '''
        self.user_data contains the json parameter needed to add this user
        to the CM.
        '''
        self.user_data = {}
        pass

    def roles_handler(self, attribute, session):
        global user_data
        new_attribute = {}
        inv = Roles_inventory(session)
        logging.debug('attribute has a role, now converting Name to ID if needed')
        logging.debug('old_roles attribute = ' + attribute['roles'])
        if attribute['roles'].isdigit():
            logging.debug('attribute is a role, but that role is already an id: ' + str(attribute['roles']))
            new_attribute = {'id': attribute['roles']}
        else:
            new_id = inv.name_2_id(attribute['roles'])
            new_attribute = {'id': new_id}
        logging.debug('new_roles value =' + json.dumps(new_attribute))
        logging.debug('user data:' + json.dumps(self.user_data))
        if 'roles' in self.user_data:
            logging.debug('roles_handler: about to append new role to the user_data.')
            logging.debug('roles_handler: user data is: ' + json.dumps(self.user_data['roles']))
            logging.debug('roles_handler: new role is: ' + json.dumps(new_attribute))
            self.user_data['roles'].append(new_attribute)
            logging.debug('roles_handler: the user data after update is: ' + json.dumps(self.user_data['roles']))
            logging.debug('roles_handler: the user data for roles is of type: ' + str(type(self.user_data['roles'])))
            new_role = []
            [new_role.append(i) for i in self.user_data['roles'] if not i in new_role]
            logging.debug('roles_handler: list after removing duplicates is: ' + str(new_role))
        else:
            new_role = [new_attribute]
        logging.debug('roles_handler: This is the complete list of roles so far: ' + json.dumps({'roles': new_role}))
        return {'roles': new_role}


    def add_attribute(self, session, attribute):
        '''
        Adds the dictionary contained in attribute to self.user_data once
        after vaidating attribute against allowed user fields.
        self.user_data is left unchanged if any of the keys fail validation

        attribute values are not validated - only the keys.
        '''
        # Validate attribute keys against valid key list
        if not self.validate_attribute(attribute):
            return False
        # Attributes requiring special handling

        # Roles may come here as {'roles':<String role name>} or {'roles':<String ID>}
        # If needed, convert to ID before sending transaction to CM
        if 'roles' in attribute:
            attribute = self.roles_handler(attribute, session)
            # Completed validation and special handling of attributes requiring
        #it.  Update internal user_data field
        logging.debug('about to add the following attribute to the system: ' + str(attribute))
        #		self.user_data = dict(self.user_data.items() + attribute.items)
        self.user_data = dict(chain(self.user_data.items(), attribute.items()))
        logging.debug('user data is now: ' + json.dumps(self.user_data))

    def validate_attribute(self, attribute):
        '''
        Validates the dictionary in attribute contains a single valid key value
        pair that can be added to the user data record.
        '''
        valid = [name for name, member in valid_user_attributes.__members__.items()]
        logging.debug('valid keys are:' + str(valid))
        logging.debug('attribute keys are:' + str([key for key in attribute]))
        for key in attribute:
            if key in valid:
                print(True)
            else:
                logging.warning('invalid user attribute: ' + key)
                return False
        return True

    def get_json_user(self):
        return json.loads(self.user_data)


class Users(framework_object):
    def __init__(self, api_version):
        '''
        Constructor for Users object.
        :param api_version: version of USERS api
        :return:
        '''
        super().__init__(api_version)

    def add_user_to_network(self):
        """
        Wrapper around
        :return:
        """
        # Note - not tested until we have a multi-network solution for the automation framework



    def create_user(self,session, baseurl,
                    emailAddress,
                    username,
                    firstname,
                    lastname,
                    password,
                    name,
                    role_list,
                    dateFormat = 'MM-dd-yyyy',
                    enabled = True,
                    isAsiaSpeakingLanguage = True,
                    isSuperAdministrator = True,
                    isWebserviceUser = True,
                    language = 'English',
                    languageCode = 'en',
                    receiveApprovalEmails = False,
                    receiveEmailAlerts = False,
                    timeFormat = '12h'):
        '''
        Wrapper around POST /api/rest/users

        :param session:  Session object logged into the framework
        :param baseurl:  Base url for system under test
        :param emailAddress:
        :param username:
        :param firstname:
        :param lastname:
        :param password:
        :param name:
        :param role_list:
        :param dateFormat:
        :param enabled:
        :param isAsiaSpeakingLanguage:
        :param isSuperAdministrator:
        :param isWebserviceUser:
        :param language:
        :param languageCode:
        :param receiveApprovalEmails:
        :param receiveEmailAlerts:
        :param timeFormat:
        :return: True if return code is 200, False otherwise.  Updates last_response
        '''

        create_user_apiurl = '/api/rest/users'

        user_parameters = {
        'dateFormat': dateFormat,
        'emailaddress': emailAddress,
        'enabled': enabled,
        'firstname': firstname,
        'isAsiaSpeakingLanguage': isAsiaSpeakingLanguage,
        'isSuperAdministrator': isSuperAdministrator,
        'isWebserviceUser': isWebserviceUser,
        'language': language,
        'languageCode': languageCode,
        'lastname': lastname,
        'password': password,
        'name': name,
        'receiveApprovalEmails': receiveApprovalEmails,
        'receiveEmailAlerts': receiveEmailAlerts,
        'timeFormat':timeFormat ,
        'roles': role_list,
        'username': username
        }

        logging.debug("create_user: payload_params/user_parameters: {}".format(user_parameters))

        self.last_response = rest_request(session,type_of_call=call_type.post, baseurl = baseurl,  apiurl= create_user_apiurl, payload_params=user_parameters)

        logging.debug("Made call to POST {}.  Response code = {}, Response = {}".format(create_user_apiurl,
                                                                                      self.last_response.status_code,
                                                                                      self.last_response.text))
        if self.last_response.status_code == 200:
            return True
        else:
            return False


    def create_user_for_specific_network(self, session, baseurl,
                                         emailAddress,
                                         username,
                                         firstname,
                                         lastname,
                                         password,
                                         name,
                                         network_id,
                                         role_list=[],
                                         dateFormat='MM-dd-yyyy',
                                         enabled=True,
                                         timeFormat="24",
                                         isAsiaSpeakingLanguage=True,
                                         isAutoMediaApprover = True,
                                         isSuperAdministrator=True,
                                         isWebserviceUser=True,
                                         language='English',
                                         languageCode='en',
                                         receiveApprovalEmails=False,
                                         receiveEmailAlerts=False,
                                         canChangePassword=True,
                                         webserviceUser = True
                                         ):
        '''
        Wrapper around POST /api/rest/usernetworks/{networkID}

        :param session:  Session object logged into the framework
        :param baseurl:  Base url for system under test
        :param emailAddress:
        :param username:
        :param firstname:
        :param lastname:
        :param password:
        :param name:
        :param role_list:
        :param dateFormat:
        :param enabled:
        :param isAsiaSpeakingLanguage:
        :param isSuperAdministrator:
        :param isWebserviceUser:
        :param language:
        :param languageCode:
        :param receiveApprovalEmails:
        :param receiveEmailAlerts:
        :param timeFormat:
        :return: True if return code is 200, False otherwise.  Updates last_response
        '''

        user_dto = {"username": username,
            "firstname": firstname,
            "lastname": lastname,
            "password":password,
            "emailaddress":emailAddress,
            "dateFormat":dateFormat,
            "timeFormat": timeFormat,
            "name": name,
            "language": language,
            "languageCode": languageCode,
            "isAsiaSpeakingLanguage": isAsiaSpeakingLanguage,
            "canChangePassword": canChangePassword,
            "isSuperAdministrator": isSuperAdministrator,
            "isAutoMediaApprover": isAutoMediaApprover,
            "receiveEmailAlerts": receiveEmailAlerts,
            "isWebserviceUser": isWebserviceUser,
            "enabled": enabled,
            "receiveApprovalEmails": receiveApprovalEmails,
            "authenticationMethod": "DIRECT",
            "roles": role_list,
            "webserviceUser": webserviceUser
        }

        create_user_networks_apiurl = '/api/rest/users/usernetworks/' + str(network_id)
        #users_fields = ['receiveApprovalEmails', 'canChangePassword', 'timeFormat', 'receiveEmailAlerts', 'isAsiaSpeakingLanguage', 'languageCode', 'isAutoMediaApprover', 'username', 'language', 'isWebserviceUser', 'authenticationMethod', 'emailaddress', 'webserviceUser', 'firstname', 'roles', 'dateFormat', 'lastname', 'isSuperAdministrator', 'name', 'enabled']

        self.last_response = rest_request(session,type_of_call=call_type.post, baseurl = baseurl,  apiurl= create_user_networks_apiurl, payload_params=user_dto)

        logging.debug("Made call to POST {}.  Response code = {}, Response = {}".format(create_user_networks_apiurl,
                                                                                      self.last_response.status_code,
                                                                                      self.last_response.text))
        if self.last_response.status_code == 200:
            return True
        else:
            return False



    def delete_user(self, session, baseurl, user_id):
        '''
        Wrapper around DELETE /api/rest/users/{id}
        '''

        delete_user_apiurl = '/api/rest/users/' + str(user_id)
        return self.delete_object_by_id(session = session,
                                 baseurl = baseurl,
                                 apiurl = delete_user_apiurl,
                                 object_id = user_id)

    def find_user_by_id(self, session, baseurl, user_id, fields=None):
        """
        Wrapper around /api/rest/users/{id}
        :param session: Authenticated session object
        :param baseurl: baseurl of session under test
        :param user_id: ID of user
        :return: True if response code is 200, and False otherwise.  Updates self.last_resposne
        """

        find_user_by_id_apiurl = '/api/rest/users/' + str(user_id)

        return self.find_object_by_id(session = session,
                                      baseurl = baseurl,
                                      apiurl = find_user_by_id_apiurl,
                                      object_id = user_id,
                                      fields = fields)

    def list_users(self, session, baseurl, limit = 10, offset = 0, sort = 'username', filters = None, fields = None, search = None):
        """
        Wrapper around GET /api/rest/users
        Uses super method list_objects
        :param session: Authenticated session object
        :param baseurl: Base URL of system under test
        :param limit: Max number of user DTO's to return in the response
        :param offset: Offset used in paging through useres
        :param sort: Comma separated list of fields to sort the response by
        :param filters: Filter JSON object
        :param fields: Comma separated list of fields to include in each DTO
        :param search: Search term - search in name and username
        :return: True if response code is 200. False otherise. Updates last_response
        """

        list_users_apiurl = '/api/rest/users'

        return self.list_objects(session = session,
                                 baseurl = baseurl,
                                 apiurl = list_users_apiurl,
                                 limit = limit,
                                 offset = offset,
                                 sort = sort,
                                 filters = filters,
                                 fields = fields,
                                 search = search)

    def return_user_list(self, session, baseurl, limit, offset=0, sort=None, filters=None, fields=None, search=None):
        list_users_apiurl = '/api/rest/users'

        query_parameters = {'limit':limit, 'offset':offset}

        if sort != None:
            query_parameters['sort'] = sort
        if filters != None:
            query_parameters['filters'] = filters
        if fields != None:
            query_parameters['fields'] = fields
        if search != None:
            query_parameters['search'] = search

        self.last_response = rest_request(session,
                                          type_of_call=call_type.get,
                                          baseurl=baseurl,
                                          apiurl=list_users_apiurl,
                                          query_params=query_parameters)

        return self.last_response.text


    def update_user(self, session, baseurl, identifier, update_user_dict):
        """
        Wrapper around /api/rest/users/{id}
        :param session: Authenticated session object
        :param baseurl: Base URL of CM under test
        :param identifier: System ID of the user record to update.  Not the username, the ID
        :param update_user_dict: JSON object containg fields to change
        :return:True if response code is 200.  False otherwise.  Updates self.last_response
        """

        update_user_apiurl = '/api/rest/users/' + str(identifier)

        return self.update_single_object(session = session,
                                         baseurl= baseurl,
                                         apiurl=update_user_apiurl,
                                         object_id=identifier,
                                         field_change_dict=update_user_dict)

    def update_multi_users(self, session, baseurl, uuid, role_list = None, workgroup_list = None, language = None):
        """
        Wrapper around /api/rest/users/multi/{uuid}

        :param session: Authenticated session object
        :param baseurl: Base url for CM under test
        :param uuid: UUID of the storage object containing the id's of users to update of the form-
        {'ids':[<list of user ids>]}
        :param role_list: list of role id's for the roles that are to be updated of the form-
        {'roles':[{'id':<role id>, 'value':<role name>},...]
        :param workgroup_list:  List of workgroup ids for the workgroups that are to be updated of the form-
         {workgroup: {id: <workgroup id>, value: <workgroup name>}}
        :param language: The iso language code associated with the language change
        :return:True if response code is 200.  False otherwise.  Updates self.last_response
        """

        update_multi_users_apiurl = '/api/rest/users/multi/' + uuid
        update_multi_payload_param = {'id':uuid,'uuid':uuid,'item':{}}

        if role_list is not None:
            update_multi_payload_param['item']['roles'] = role_list
        if workgroup_list is not None:
            update_multi_payload_param['item']['workgroup'] = workgroup_list
        if language is not None:
            update_multi_payload_param['item']['language'] = ""
            update_multi_payload_param['item']['languageCode'] = language

        self.last_response = rest_request(session = session,
                                          baseurl = baseurl,
                                          apiurl = update_multi_users_apiurl,
                                          type_of_call=call_type.put,
                                          payload_params=update_multi_payload_param)

        logging.debug('Made call to PUT {}. Response code = {}. Response = {}'.format(update_multi_users_apiurl,
                                                                                      self.last_response.status_code,
                                                                                      self.last_response.text))

        if self.last_response.status_code == 200:
            return True
        else:
            return False


    def find_user_property_by_name(self, session, baseurl, property_name):
        """
        Wrapper around GET /api/rest/userProperties/{name}
        :param session: Authenticated session object
        :param baseurl: baseurl for CM under test
        :param property_name: name of user property to test
        :return:True if response code is 200.  False otherwise.  Updates self.last_response
        """

        find_user_property_apiurl = '/api/rest/users/userProperties/' + str(property_name)

        self.last_response = rest_request(session = session,
                                          baseurl = baseurl,
                                          apiurl = find_user_property_apiurl,
                                          type_of_call=call_type.get)

        logging.debug('Made call to GET {}.  Response code = {}, response = {}'.format(find_user_property_apiurl,
                                                                                        self.last_response.status_code,
                                                                                        self.last_response.text))
        if self.last_response.status_code == 200:
            return True
        else:
            return False

    def process_user_property(self, session, baseurl, name, value ):
        """
        Wrapper around POST /api/rest/users/userProperties

        :param session: Authenticated session object
        :param baseurl: Baseurl for CM under test
        :param name: Name of the new property
        :param value: value of the new property
        :return: True if response code is 200.  False otherwise. Updates self.last_response
        """

        process_user_property_apiurl = '/api/rest/users/userProperties'
        process_user_property_parameters = {'name':name, 'value':value}

        self.last_response = rest_request(session = session,
                                          baseurl = baseurl,
                                          apiurl = process_user_property_apiurl,
                                          type_of_call=call_type.post,
                                          payload_params=process_user_property_parameters)
        logging.debug('Made call to POST {}.  Response code = {}.  Response = {}'.format(process_user_property_apiurl,
                                                                                         self.last_response.status_code,
                                                                                         self.last_response.text))
        if self.last_response.status_code == 200:
            return True
        else:
            return False

    def process_user_multiple_properties(self,session, baseurl, list_of_user_properties):
        """
        Wrapper around POST /api/rest/users/userMultiProperties

        :param session:  Authenticated session object
        :param baseurl:  Baseurl for CM under test
        :param list_of_user_properties: list of user properties of the form-
        [{'name':<property 1 name>,'value':<property 1 value>}, {'name':<property 2 name>,'value':<property 2 value>}, ...]
        :return: True if response code is 200.  False otherwise. Updates self.last_response
        """

        process_multiple_user_properties_apiurl = '/api/rest/users/userMultiProperties'
        process_multiple_user_properties_parameter = {'userProperties':list_of_user_properties}

        self.last_response = rest_request(session = session,
                                          baseurl = baseurl,
                                          apiurl = process_multiple_user_properties_apiurl,
                                          type_of_call=call_type.post,
                                          payload_params=process_multiple_user_properties_parameter)
        logging.debug('Made call to POST {}.  Response code = {}.  Response = {}'.format(process_multiple_user_properties_apiurl,
                                                                                         self.last_response.status_code,
                                                                                         self.last_response.text))
        if self.last_response.status_code == 200:
            return True
        else:
            return False

    def retrieve_list_of_users_by_network(self, session, baseurl, network_id, limit = 10, offset = 0,  sort = 'username', filters = None, fields = None, search = None):
        """
        Wrapper around GET /api/rest/users/networks/{network id}

        :param session: Authenticated session object
        :param baseurl: Baseurl of CM under test
        :param network_id: Network ID to return user list for
        :param limit: Limits the number of resources in the response json object
        :param offset: Offset for paging the responses
        :param sort: Sort field defaults to username
        :param filters: Filter dicts
        :param fields: comma separated list of fields to include in the response
        :param search: Search for usernames matching this field
        :return: True if response code is 200.  False otherwise.  Updates last_response.  Uses super method
        """

        retrieve_user_list_apiurl = '/api/rest/users/networks/' + str(network_id)
        return self.list_objects(session = session,
                                 baseurl = baseurl,
                                 apiurl = retrieve_user_list_apiurl,
                                 limit = limit,
                                 offset = offset,
                                 sort = sort,
                                 filters = filters,
                                 fields = fields,
                                 search = search)
