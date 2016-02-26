import sys, json
import requests
import logging
import logging.config
from time import sleep
import configparser
from framework.constants import *
from framework.authentication_rest import *
from framework.http_rest import *
from framework.inventory import Category_inventory
from framework.framework_object_rest import framework_object
from itertools import chain

__author__ = 'rkaye'


class Category(framework_object):
    def __init__(self, api_version):
        '''
        Constructor for media categories.  Sets the JSON object json_data to empty.
        :return: VOID
        '''
        super().__init__(api_version)

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
        logging.debug('user data is now: ' + json.dumps(self.json_data))
        return True

    def validate_attribute(self, attribute):
        '''
        Validates the dictionary in attribute contains a single valid key value
        pair that can be added to the user data record.  Authenticates keys based on
        Enum in framework.constants
        :param attribute: A list of key value pairs
        :return: True if all key-value pairs are valid.  False if even one key value pair is not valid

        The format of the attribute field is very important and should be as follows:

        attribute = [{'<field 1>':'<value1>'},{'<field2>':'<value2>'},...{'<field n>':'<value n>'}]
        '''
        valid = [name for name, member in valid_media_category_attributes.__members__.items()]
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
        return self.json_data

    def clear(self):
        self.json_data = {}

    def handle_name(self, attribute, session):
        '''
        This method determines the parentId of the element passed as an attribute, and adds the correct 'parentId' kvp
        to the json_data object.  It also adds the 'name' parameter into the json_data.  It then returns
        whatever key value pairs are left to be processed.

        Best explained with an example.

        If the data type is a workgroup hierarchy in the CM is:

        wg1 (id = 1)--->wg2 (id = 5) --> wg3 (id = 8)

        And the attribute added is:
        attribute = [{'name':'wg1'},{'name':'wg2'},{'name':'wg3'},{'name':'blah'},{'description':'this is a workgroup'}]

        The following two key value pairs will be added to the workgroup_data:
        {'name':'blah'} <---as the last wg name in attribute, this is the name of the new workgroup
        {'parentId':8} <---the ID of wg3, which is the parent of blah.

        The method would then return whatever was left in the attribute, in this case [{'description':'this is a workgroup'}]

        If this method fails, it returns None.

        Returns
        :param attribute: Adds the parentId key value pair to self.workgroup_data for this workgroup based on the 'name'
        key value pairs passed in attribute.
        :return: List of dictionaries in attribute, less the 'name' key value pairs or None if parsing fails.
        '''

        current_inventory = Category_inventory(session)
        # First, split off the name attributes into a new list
        name_attribute_list = [item for item in attribute if 'name' in item.keys() and '' not in item.values()]
        logging.debug('length of list of names is: {}'.format(len(name_attribute_list)))

        # Check to see if we're adding a top level workgroup.  If so, no parentId is needed in the JSON request.  Just return
        if len(name_attribute_list) == 1:
            logging.debug(
                'Found case where top level workgroup to be added.  Name list is: {}'.format(name_attribute_list))
            self.json_data['name'] = name_attribute_list[0]['name']
            return [item for item in attribute if 'name' not in item.keys()]

        parent_name = name_attribute_list[0]['name']
        parent_ids = current_inventory.name_2_ids(parent_name)
        parent_id = 0

        # Before I can create the top node tuple, I need to determine which of the ID's I have
        # found is the one which has no parent

        for identifier in parent_ids:
            if current_inventory.get_parent_id(identifier) is None:
                parent_id = identifier

        logging.debug('starting to perform search for parentId: {}'.format(name_attribute_list))
        parent_tuple = (parent_id, parent_name)
        name_attribute_list.pop(0)
        # Walk down the tree according to the names passed in the name_attribute list
        for item in name_attribute_list:
            logging.debug('Starting search for named tuple: {}, with parent of {}'.format(item, parent_tuple))
            child_tuple = current_inventory.get_child_tuple_by_name(parent_tuple, item['name'])
            if child_tuple == None:
                parent_id, parent_name = parent_tuple
                self.json_data['parentId'] = parent_id
                self.json_data['name'] = item['name']
                logging.info('workgroup_data is now: {}'.format(self.json_data))
            else:
                parent_tuple = child_tuple
        return [item for item in attribute if 'name' not in item.keys()]


    def list_categories(self, session, baseurl, limit=10, offset=0, sort='name', filters=None, fields=None,
                        search=None):
        '''
        Wrapper around the GET /api/rest/categories api call.  Uses list_objects from the super class
        :param session:
        :param baseurl:
        :param limit:
        :param offset:
        :param sort:
        :param filters:
        :param fields:
        :param search:
        :return: True if return code is 200
        '''

        list_category_apiurl = '/api/rest/categories'

        return self.list_objects(session=session,
                                 baseurl=baseurl,
                                 apiurl=list_category_apiurl,
                                 limit=limit,
                                 offset=offset,
                                 sort=sort,
                                 filters=filters,
                                 fields=fields,
                                 search=search
        )

    def create_category(self, session, baseurl, name, description, parentId=None, children=None):
        """
        Wrapper around POST /api/rest/categories
        :param session: Authenticated session object
        :param baseurl: Base URL for the CM under test
        :param name: String - name of category to create
        :param description: String - Description of category to create
        :param parentId: ID of parent category - if any
        :param children: List Of ID's of children categories - if any
        :return: True if response code is 200.  False otherwise.  Updates self.last_response
        """
        create_category_params = {'name': name, 'description': description}
        if parentId is not None:
            create_category_params['parentId'] = parentId
        if children is not None:
            create_category_params['children'] = children

        create_category_apiurl = '/api/rest/categories'

        self.last_response = rest_request(session=session,
                                          baseurl=baseurl,
                                          apiurl=create_category_apiurl,
                                          type_of_call=call_type.post,
                                          payload_params=create_category_params)

        logging.debug('Made call to POST {}.  Response code = {}.  Response = {}'.format(create_category_apiurl,
                                                                                         self.last_response.status_code,
                                                                                         self.last_response.text))
        if self.last_response.status_code == 200:
            return True
        else:
            return False

    def delete_category_by_id(self, session, baseurl, category_id):
        """
        Wrapper around Delete
        :param session: Authenticated session on CM under test
        :param baseurl: Baseurl of CM under test
        :param category_id: Category ID to delete
        :return:True if response code is 204.  False otherwise.  Updates last_response
        """
        delete_category_apiurl = '/api/rest/categories/' + str(category_id)
        return self.delete_object_by_id(session = session,
                                        baseurl = baseurl,
                                        apiurl = delete_category_apiurl,
                                        object_id=category_id)

    def update_single_cateogry(self, session, baseurl, category_id, category_object):
        """
        Wrapper around PUT /api/rest/categories/{ID}
        :param session: Authenticated session object
        :param baseurl: Base url for CM under tes
        :param category_id: ID of cateogry to be updated
        :param category_object: JSON object containing change data
        :return:True if response code is 200.  False otherwise.  Upldates self.last_response
        """

        update_single_media_apiurl = '/api/rest/categories/'

        return self.update_single_object(session = session,
                                         baseurl = baseurl,
                                         apiurl = update_single_media_apiurl,
                                         object_id = category_id,
                                         field_change_dict= category_object)


if __name__ == '__main__':
    import os

    print(os.getcwd())
    configuration = configparser.ConfigParser()
    configuration.read(CONFIG_FILE_PATH)
    baseurl = configuration['login']['baseurl']
    username = configuration['login']['username']
    password = configuration['login']['password']
    logging.config.fileConfig("config/log_config")
    logging.debug('Read from config file and ready to begin.')
    s = login(username, password, baseurl, 0)
    w1 = Category()
    w2 = Category()
    w3 = Category()

    api_call = '/api/rest/categories'

    params1 = [{'name': 'a'}, {'description': 'Category name is a'}]
    params2 = [{'name': 'b'}, {'description': 'Category name is b'}]
    params3 = [{'name': 'c'}, {'description': 'Category name is c'}]

    w1.add_attribute(s, attribute=params1)
    w2.add_attribute(s, attribute=params2)
    w3.add_attribute(s, attribute=params3)

    resp = rest_request(s, call_type.post, baseurl=baseurl, apiurl=api_call,
                        payload_params=w1.json_data,
                        proxy=False)
    resp = rest_request(s, call_type.post, baseurl=baseurl, apiurl=api_call,
                        payload_params=w2.json_data,
                        proxy=False)
    resp = rest_request(s, call_type.post, baseurl=baseurl, apiurl=api_call,
                        payload_params=w3.json_data,
                        proxy=False)

    w1.clear()
    w2.clear()
    w3.clear()

    params4 = [{'name': 'a'}, {'name': 'aa'}, {'name': ''}, {'description': 'Category name is is aa'}]
    params5 = [{'name': 'b'}, {'name': 'ba'}, {'description': 'Category name is ba'}]
    params6 = [{'name': 'c'}, {'name': 'ca'}, {'description': 'Category name is ca'}]

    w1.add_attribute(s, attribute=params4)
    w2.add_attribute(s, attribute=params5)
    w3.add_attribute(s, attribute=params6)

    resp = rest_request(s, call_type.post, baseurl=baseurl, apiurl=api_call,
                        payload_params=w1.json_data,
                        proxy=False)
    resp = rest_request(s, call_type.post, baseurl=baseurl, apiurl=api_call,
                        payload_params=w2.json_data,
                        proxy=False)
    resp = rest_request(s, call_type.post, baseurl=baseurl, apiurl=api_call,
                        payload_params=w3.json_data,
                        proxy=False)

    w1.clear()
    w2.clear()
    w3.clear()
    # params7 = [{'name': 'a'},{'name':'ab'},{'name':''},{'description': 'Workgroup name is aa'}]
    params7 = [{'name': 'a'}, {'name': 'ab'}, {'name': ''}, {'description': 'Category name is aa'}]
    params8 = [{'name': 'b'}, {'name': 'bb'}, {'description': 'Category name is ba'}]
    params9 = [{'name': 'c'}, {'name': 'cb'}, {'description': 'Category name is ca'}]

    w1.add_attribute(s, attribute=params7)
    w2.add_attribute(s, attribute=params8)
    w3.add_attribute(s, attribute=params9)

    resp = rest_request(s, call_type.post, baseurl=baseurl, apiurl=api_call,
                        payload_params=w1.json_data,
                        proxy=False)
    resp = rest_request(s, call_type.post, baseurl=baseurl, apiurl=api_call,
                        payload_params=w2.json_data,
                        proxy=False)
    resp = rest_request(s, call_type.post, baseurl=baseurl, apiurl=api_call,
                        payload_params=w3.json_data,
                        proxy=False)
    w1.clear()
    w2.clear()
    w3.clear()

    params10 = [{'name': 'a'}, {'name': 'aa'}, {'name': 'aaa'}, {'name': ''}, {'description': 'Workgroup name is aba'}]
    params11 = [{'name': 'b'}, {'name': 'ba'}, {'name': 'baa'}, {'description': 'Workgroup name is abb'}]
    params12 = [{'name': 'c'}, {'name': 'cb'}, {'name': 'cba'}, {'description': 'Workgroup name is abc'}]

    w1.add_attribute(s, attribute=params10)

    resp = rest_request(s, call_type.post, baseurl=baseurl, apiurl=api_call,
                        payload_params=w1.json_data,
                        proxy=False)

    w2.add_attribute(s, attribute=params11)

    resp = rest_request(s, call_type.post, baseurl=baseurl, apiurl=api_call,
                        payload_params=w2.json_data,
                        proxy=False)

    w3.add_attribute(s, attribute=params12)
    resp = rest_request(s, call_type.post, baseurl=baseurl, apiurl=api_call,
                        payload_params=w3.json_data,
                        proxy=False)