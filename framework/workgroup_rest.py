import sys, json
import requests
import logging
import logging.config
from time import sleep
import configparser
from framework.constants import *
from framework.authentication_rest import *
from framework.http_rest import *
from framework.inventory import Workgroups_inventory
from framework.framework_object_rest import framework_object
import requests
from itertools import chain

__author__ = 'rkaye'


class Workgroup(framework_object):
    def __init__(self,api_version):
        '''
        Constructor for workgroup_rest.  Sets the JSON object user_data to empty.
        :return: VOID
        '''
        '''
        :return:
        '''
        super().__init__(api_version)
        self.json_data = {}
        self.last_response = requests.Response

    def add_attribute(self, session, attribute):
        '''
        Adds the list of key value pairs specified in attribute to the json_data dictionary
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
        # Before adding attributes to json request, special handling may be required.  Do that here.

        # Handle name attributes which define the tree structure of the work group
        attribute_nonames = self.handle_name(attribute, session)
        logging.debug('the full attribute is: {}'.format(attribute))
        logging.debug('about to add the following attribute to the system: ' + str(attribute_nonames))

        if attribute_nonames is not None:
            for key_value_pair in attribute_nonames:
                self.json_data.update(key_value_pair)

                # self.json_data = dict(self.json_data.items() + attribute.items)
                # self.json_data = dict(chain(self.json_data.items(), attribute.items()))
        logging.debug('user data is now: ' + json.dumps(self.json_data))
        return True

    def validate_attribute(self, attribute):
        '''
        Validates the dictionary in attribute contains a single valid key value
        pair that can be added to the user data record.  Autheticates keys based on
        Enum in framework.constants
        '''
        valid = [name for name, member in valid_workgroup_attributes.__members__.items()]
        logging.debug('valid keys are:' + str(valid))
        logging.debug('attribute keys are:' + str([key for key in attribute]))
        for key in attribute:
            if key in valid:
                print(True)
            else:
                logging.warning('invalid user attribute: ' + key)
                return False
        return True


    def get_json(self):
        return json.loads(self.json_data)

    def clear(self):
        self.json_data = {}

    def handle_name(self, attribute, session):
        '''
        This method determines the parentId of the workgorup passed as an attribute, and adds the correct 'parentId' kvp
        to the json_data object.  It also adds the 'name' parameter into the json_data.  It then returns
        whatever key value pairs are left to be processed.

        Best explained with an example.

        If the workgroup hierarchy in the CM is:

        wg1 (id = 1)--->wg2 (id = 5) --> wg3 (id = 8)

        And the attribute added is:
        attribute = [{'name':'wg1'},{'name':'wg2'},{'name':'wg3'},{'name':'blah'},{'description':'this is a workgroup'}]

        The following two key value pairs will be added to the json_data:
        {'name':'blah'} <---as the last wg name in attribute, this is the name of the new workgroup
        {'parentId':8} <---the ID of wg3, which is the parent of blah.

        The method would then return whatever was left in the attribute, in this case [{'description':'this is a workgroup'}]

        If this method fails, it returns None.

        Returns
        :param attribute: Adds the parentId key value pair to self.json_data for this workgroup based on the 'name'
        key value pairs passed in attribute.
        :return: List of dictionaries in attribute, less the 'name' key value pairs or None if parsing fails.
        '''

        wgi = Workgroups_inventory(session)
        # First, split off the name attributes into a new list
        name_attribute_list = [item for item in attribute if 'name' in item.keys() and '' not in item.values()]
        logging.debug('length of list of names is: {}'.format(len(name_attribute_list)))

        # Check to see if we're adding a top level workgroup.  If so, no parentId is needed in the JSON request.  Just return
        if len(name_attribute_list) == 1:
            logging.debug(
                'Found case where top level workgroup to be added.  Name list is: {}'.format(name_attribute_list))
            self.json_data['name'] = name_attribute_list[0]['name']
            return [item for item in attribute if 'name' not in item.keys()]

        # # Take the first name off the top of the top of the '
        # first_id_list = wgi.name_2_ids(name_attribute_list.[0]['name'])
        # # Check the returned values for one that has no parent - that's the root of the tree
        # parent_id = 0
        # final_parent_id = 0
        # logging.debug('At start of loop, parent_id is: {}'.format(parent_id))
        # for identifier in first_id_list:
        # logging.debug(
        #         'handle_name: checking workgroup with identifier = {} to see if it has a parent'.format(identifier))
        #     if wgi.get_parent_id(identifier) is None:
        #         logging.debug('Found top level workgroup with id = {}'.format(identifier))
        #         parent_id = identifier
        #         logging.debug('Top level workgroup id is: {}'.format(parent_id))
        # if parent_id == 0:
        #     logging.debug(
        #         'handle_name: checked for top level workgroup with these ids and found none: {} '.format(first_id_list))
        #     return None

        #  Form the first parent tuple so that I can run down the tree

        parent_name = name_attribute_list[0]['name']
        parent_ids = wgi.name_2_ids(parent_name)
        parent_id = 0

        # Before I can create the top node tuple, I need to determine which of the ID's I have
        # found is the one which has no parent

        for identifier in parent_ids:
            if wgi.get_parent_id(identifier) is None:
                parent_id = identifier

        logging.debug('starting to perform search for parentId: {}'.format(name_attribute_list))
        parent_tuple = (parent_id, parent_name)
        name_attribute_list.pop(0)
        # Walk down the tree according to the names passed in the name_attribute list
        for item in name_attribute_list:
            logging.debug('Starting search for named tuple: {}, with parent of {}'.format(item,parent_tuple))
            child_tuple = wgi.get_child_tuple_by_name(parent_tuple, item['name'])
            if child_tuple == None:
                parent_id, parent_name = parent_tuple
                self.json_data['parentId'] = parent_id
                self.json_data['name'] = item['name']
                logging.info('json_data is now: {}'.format(self.json_data))
            else:
                parent_tuple = child_tuple
        return [item for item in attribute if 'name' not in item.keys()]


    def delete_workgroup(self, session, baseurl, workgroup_id):
        """
        Wrapper around DELETE /api/rest/workgroups/<id>
        :param session: Authenticated session object
        :param baseurl: base url of system under test
        :param workgroup_id: ID of workgroup to delete
        :return:True if response code is 204, False otherwise
        """

        delete_workgroup_apiurl = '/api/rest/workgroups/' + str(workgroup_id)

        return self.delete_object_by_id(session = session,
                                        baseurl = baseurl,
                                        apiurl= delete_workgroup_apiurl,
                                        object_id=workgroup_id)

    def list_workgroups(self,session,baseurl,limit = 10, offset = 0, sort = None, filters = None, fields = None, search = None):
        '''
        Wrapper around the GET /aip/rest/workgroups API.  Uses framework object supermethod - list_objects
        :param session: Session object logged into the system under test
        :param baseurl: Base url of the system under test
        :param limit: Max number of objects in the response
        :param offset: Page offset into data
        :param sort: sort by field
        :param filters: filter for fields
        :param fields: Comma separated list of fields to display in response
        :param search: Search term for the response
        :return:
        '''

        list_workgroups_apiurl = '/api/rest/workgroups'

        return self.list_objects(session = session,
                                 baseurl = baseurl,
                                 apiurl = list_workgroups_apiurl,
                                 limit = limit,
                                 offset = offset,
                                 sort = sort,
                                 filters = filters,
                                 fields = fields,
                                 search = search)
    def create_workgroup(self, session,baseurl,name, parent_id = None):
        '''
        Wrapper around POST /api/rest/workgroups
        :param session: Session object logged into the system under test
        :param baseurl: Base url of the system under test
        :param name: Name of workgroup to be created
        :param description: Description of workgroup to be created
        :param parent_id: The parent workgroup ID
        :return: True if status code is 200, False otherwise.  Updates last_response
        '''

        create_workgroup_apiurl = '/api/rest/workgroups'
        create_workgroup_params = {'name':name}

        if parent_id !=None:
            create_workgroup_params['parentId'] = parent_id


        self.last_response = rest_request(session = session,
                                          baseurl = baseurl,
                                          apiurl= create_workgroup_apiurl,
                                          type_of_call=call_type.post,
                                          payload_params=create_workgroup_params)

        logging.debug('Made call to POST {}.  Response code = {}, Response = {}'.format(create_workgroup_apiurl,
                                                                                        self.last_response.status_code,
                                                                                        self.last_response.text))
        if self.last_response.status_code == 200:
            return True
        else:
            return False

    def find_workgroup_by_id(self, session, baseurl, workgroup_id):
        '''
        Wrapper around GET /api/rest/workgroups.  Uses super class method
        :param session: Session object logged into the system under test
        :param baseurl: Base url of the system under test
        :param workgroup_id: ID of workgroup to find
        :return:True if status code is 200.  False otherwise.  Updates self.last_response
        '''
        get_workgroup_apiurl = '/api/rest/workgroups/'
        return self.find_object_by_id(session = session,
                                      baseurl = baseurl,
                                      apiurl = get_workgroup_apiurl,
                                      object_id = workgroup_id)

    def return_id_of_named_child(self,session, baseurl, child_name, parent_id = None):
        '''
        Utility method used to walk the tree of workgroups.  Returns the ID of the named workgroup with parent ID specified
        if no parent ID is specified, returns the id of the top level workgroup with the specified name.  If the named
        child is not found, returns None

        This method updates the self.last_Response to the record associated with the name child if that named child exists
        If the parent ID is None, then the last_response is updated to a get of the top level workgroup named in the call
        :param child_name: Name of child to find
        :param parent_id: ID of parent workgroup.  None if top level workgroup
        :return: Returns ID of named child if child exists.  If named child does not exist, returns None
        '''

        # First, check to see if this is a top level WG.  If so, return top level WG with matching name
        if parent_id == None:
            self.list_workgroups(session = session,
                                 baseurl = baseurl,
                                 limit = 1000,
                                 fields = 'id,name') # Note: by limiting to id and name, child records don't show up
            print('response from list workgroups = {}'.format(json.dumps(self.last_response.json())))
            for top_level_workgroup in self.last_response.json()['list']:
                if top_level_workgroup['name'] == child_name:
                    print('response: Found it!  ID is: {}'.format(top_level_workgroup['id']))
                    self.find_workgroup_by_id(session=session,
                          baseurl=baseurl,
                          workgroup_id=top_level_workgroup['id'])
                    print('response: returning: {}'.format(top_level_workgroup['id']))
                    return top_level_workgroup['id']
            return None


        if self.find_workgroup_by_id(session = session,
                                  baseurl = baseurl,
                                  workgroup_id=parent_id):
            pass # find_workgroup_by_id updates the last_response
            logging.debug('Found workgroup with ID = {}'.format(self.last_response.json()['id']))
            print('Debug: found the workgroup parent')
            # print(json.dumps(self.last_response.json()))
            # print(json.dumps(self.last_response.json()['children']))
        else:
            return None

        if 'children' in self.last_response.json():
            #print('Debug: Found children in parent record')
            for child in self.last_response.json()['children']:

                if child['name'] == child_name:
                    self.find_workgroup_by_id(session=session,
                                              baseurl=baseurl,
                                              workgroup_id=child['id'])
                    return child['id']
        return None





if __name__ == '__main__':
    import os
    print(os.getcwd())
    configuration = configparser.ConfigParser()
    configuration.read(CONFIG_FILE_PATH)
    print (CONFIG_FILE_PATH)
    baseurl = configuration['login']['baseurl']
    username = configuration['login']['username']
    password = configuration['login']['password']
    logging.config.fileConfig("config/log_config")
    logging.debug('Read from config file and ready to begin.')
    s = login(username, password, baseurl, 0)

    w1 = Workgroup(1)
    child_id = w1.return_id_of_named_child(session = s,
                                baseurl = baseurl,
                                child_name = 'l2 New Workgroup',
                                parent_id = 60)

    print ('child_id is: {}'.format(child_id))

    child_id_2 = w1.return_id_of_named_child(session = s,
                                baseurl = baseurl,
                                child_name = 'abc')
    print('top level workgroup id is: {} '.format(child_id_2))






    # w1 = Workgroup()
    # w2 = Workgroup()
    # w3 = Workgroup()
    #
    # params1 = [{'name': 'a'}, {'description': 'Workgroup name is a'}]
    # params2 = [{'name': 'b'}, {'description': 'Workgroup name is b'}]
    # params3 = [{'name': 'c'}, {'description': 'Workgroup name is c'}]
    #
    # w1.add_attribute(s, attribute=params1)
    # w2.add_attribute(s, attribute=params2)
    # w3.add_attribute(s, attribute=params3)
    #
    # resp = rest_request(s, call_type.post, baseurl=baseurl, apiurl="/api/rest/workgroups",
    #                     payload_params=w1.json_data,
    #                     proxy=False)
    # resp = rest_request(s, call_type.post, baseurl=baseurl, apiurl="/api/rest/workgroups",
    #                     payload_params=w2.json_data,
    #                     proxy=False)
    # resp = rest_request(s, call_type.post, baseurl=baseurl, apiurl="/api/rest/workgroups",
    #                     payload_params=w3.json_data,
    #                     proxy=False)
    #
    # w1.clear()
    # w2.clear()
    # w3.clear()
    #
    # params4 = [{'name': 'a'}, {'name': 'aa'}, {'name': ''}, {'description': 'Workgroup name is aa'}]
    # params5 = [{'name': 'b'}, {'name': 'ba'}, {'description': 'Workgroup name is ba'}]
    # params6 = [{'name': 'c'}, {'name': 'ca'}, {'description': 'Workgroup name is ca'}]
    #
    # w1.add_attribute(s, attribute=params4)
    # w2.add_attribute(s, attribute=params5)
    # w3.add_attribute(s, attribute=params6)
    #
    # resp = rest_request(s, call_type.post, baseurl=baseurl, apiurl="/api/rest/workgroups",
    #                     payload_params=w1.json_data,
    #                     proxy=False)
    # resp = rest_request(s, call_type.post, baseurl=baseurl, apiurl="/api/rest/workgroups",
    #                     payload_params=w2.json_data,
    #                     proxy=False)
    # resp = rest_request(s, call_type.post, baseurl=baseurl, apiurl="/api/rest/workgroups",
    #                     payload_params=w3.json_data,
    #                     proxy=False)
    #
    # w1.clear()
    # w2.clear()
    # w3.clear()
    # # params7 = [{'name': 'a'},{'name':'ab'},{'name':''},{'description': 'Workgroup name is aa'}]
    # params7 = [{'name': 'a'}, {'name': 'ab'}, {'name': ''}, {'description': 'Workgroup name is aa'}]
    # params8 = [{'name': 'b'}, {'name': 'bb'}, {'description': 'Workgroup name is ba'}]
    # params9 = [{'name': 'c'}, {'name': 'cb'}, {'description': 'Workgroup name is ca'}]
    #
    # w1.add_attribute(s, attribute=params7)
    # w2.add_attribute(s, attribute=params8)
    # w3.add_attribute(s, attribute=params9)
    #
    # resp = rest_request(s, call_type.post, baseurl=baseurl, apiurl="/api/rest/workgroups",
    #                     payload_params=w1.json_data,
    #                     proxy=False)
    # resp = rest_request(s, call_type.post, baseurl=baseurl, apiurl="/api/rest/workgroups",
    #                     payload_params=w2.json_data,
    #                     proxy=False)
    # resp = rest_request(s, call_type.post, baseurl=baseurl, apiurl="/api/rest/workgroups",
    #                     payload_params=w3.json_data,
    #                     proxy=False)
    # w1.clear()
    # w2.clear()
    # w3.clear()
    #
    # params10 = [{'name': 'a'}, {'name': 'aa'}, {'name': 'aaa'}, {'name': ''}, {'description': 'Workgroup name is aba'}]
    # params11 = [{'name': 'b'}, {'name': 'ba'}, {'name': 'baa'}, {'description': 'Workgroup name is abb'}]
    # params12 = [{'name': 'c'}, {'name': 'cb'}, {'name': 'cba'}, {'description': 'Workgroup name is abc'}]
    #
    # w1.add_attribute(s, attribute=params10)
    #
    # resp = rest_request(s, call_type.post, baseurl=baseurl, apiurl="/api/rest/workgroups",
    #                     payload_params=w1.json_data,
    #                     proxy=False)
    #
    # w2.add_attribute(s, attribute=params11)
    #
    #
    #
    # resp = rest_request(s, call_type.post, baseurl=baseurl, apiurl="/api/rest/workgroups",
    #                     payload_params=w2.json_data,
    #                     proxy=False)
    #
    # w3.add_attribute(s, attribute=params12)
    # resp = rest_request(s, call_type.post, baseurl=baseurl, apiurl="/api/rest/workgroups",
    #                     payload_params=w3.json_data,
    #                     proxy=False)