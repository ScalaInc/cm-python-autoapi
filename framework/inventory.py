import sys, json
import requests
import logging
import logging.config
from time import sleep
import configparser
from framework.http_rest import rest_request
from framework.authentication_rest import login
from framework.constants import *


class Inventory:
    '''Base Class for non hierarchical inventory objects.  Do not instantiate this class.'''

    def __init__(self, session):
        self.configuration = configparser.ConfigParser()
        self.configuration.read(CONFIG_FILE_PATH)
        self.baseurl = self.configuration['login']['baseurl']
        self.session = session
        self.data = self.refresh()

    def refresh(self):
        logging.info('about to refresh inventory class for ' + str(type(self)))
        resp = rest_request(self.session, call_type.get, baseurl=self.baseurl, apiurl=self.api_call,
                            query_params=self.params,
                            proxy=False)
        logging.info('refresh response code is: ' + str(resp.status_code))
        if resp.status_code == 200:
            # print(resp.text)
            return resp.text
        else:
            return None

    def id_2_name(self, identifier):
        json_data = json.loads(self.data)
        for item in json_data['list']:
            if item['id'] == identifier:
                return item['name']
        return None

    def name_2_id(self, item_name):
        json_data = json.loads(self.data)
        for item in json_data['list']:
            if item['name'] == item_name:
                return item['id']
        return None

    def get_data(self):
        return self.data

    def get_child_tuple_by_name(self, parent_tuple, search_child_name):
        '''
        Returns the child identified by the name parameter given a parent node specified by parent_tuple
        :param parent_tuple: Tuple of the form (<parent id>, <parent name>)
        :param search_child_name: String containing the name of the child to search for
        :return: If found, the tuple of the form (<child id>, <child name>).  None otherwise
        '''

        self.refresh()
        json_data = json.loads(self.data)
        parent_id, parent_name = parent_tuple
        logging.info('Searching for child node with parent id = {}, parent name = {}, and child name = {}'.format(parent_id,parent_name,search_child_name))
        parent_json = [item for item in json_data['list'] if item['id'] == parent_id]
        logging.info('Exactly {} items found that match the parent id (should be 1)'.format(len(parent_json)))
        # logging.debug('The parent node json object looks like this: {}'.format(json.dumps(parent_json[0])))
        if 'children' in parent_json[0]:
            children_json = parent_json[0]['children']
            for child in children_json:
                found_child_id = child['id']
                found_child_name = child['name']
                if found_child_name == search_child_name:
                    return (found_child_id, found_child_name)
        else:
            return None

    def name_2_ids(self, workgroup_name):
        '''
        Returns the id's of all elements with matching name.  Names are not unique in the hierarchy
        Names are unique on a single level.
        :param workgroup_name: name of element to search for
        :return: list of id's associated with matching workgroups
        '''
        self.refresh()
        json_data = json.loads(self.data)
        # Form a list of the ID's of all elements that match name == workgroup name
        element_id_list = [item['id'] for item in json_data['list'] if item['name'] == workgroup_name]
        return element_id_list

    def get_parent_id(self, identifier):
        '''
        Returns the parent ID of the associated element
        :param identifier: id of the element who's parentId is returned
        :return: the parentId of the element specified by identifier
        '''
        self.refresh()
        json_data = json.loads(self.data)
        for item in json_data['list']:
            if item['id'] == identifier and 'parentId' in item:
                return item['parentId']
        return None

    def get_children_ids(self, identifier):
        '''
        Returns the ids of the children for the element with the specified ID
        :param identifier: The id of the element to check
        :return: A list of ids of the children of the identifier parameter, or None if no children found
        '''
        self.refresh()
        json_data = json.loads(self.data)
        logging.debug('now searching for children of element with id = {}'.format(identifier))
        logging.debug('current refreshed json is: {}'.format(json.dumps(json_data)))
        for element in json_data['list']:
            logging.debug('Current element being examined is: {}'.format(json.dumps(workgroup)))
            if element['id'] == identifier:
                if 'children' in element:
                    children = element['children']
                    logging.debug(
                        'Found the following children IDs in workgroup: {}'.format(
                            children))
                    id_list = [child['id'] for child in children]
                    return id_list
            else:
                logging.debug(
                    'Workgroups_inventory.get_children_ids: Did not find any children on workgroup node {}'.format(
                        element['id']))
        return None

class Roles_inventory(Inventory):
    '''Inventory management object for CM roles'''

    def __init__(self, session):
        self.api_call = '/api/rest/roles'
        self.params = {'limit': '50', 'offset': '0', 'sort': 'name', 'fields': 'id,name'}
        Inventory.__init__(self, session)


class Media_metadata_inventory(Inventory):
    '''Inventory management object for CM Media Metadata'''

    def __init__(self, session):
        self.api_call = '/api/rest/roles'
        self.params = {'limit': '50', 'offset': '0', 'sort': 'name', 'fields': 'id,name'}
        Inventory.__init__(self, session)


class Workgroups_inventory(Inventory):
    '''
    Inventory management for CM Workgroups.
    '''

    def __init__(self, session):
        self.api_call = '/api/rest/workgroups'
        self.params = {'limit': '50', 'offset': '0', 'sort': 'name', 'fields': 'id,name,parentId,children'}
        Inventory.__init__(self, session)



class Category_inventory(Inventory):
    def __init__(self,session):
        self.api_call = '/api/rest/categories'
        self.params = {'limit': '50', 'offset': '0', 'sort': 'name', 'fields': 'id,name,parentId,children'}
        Inventory.__init__(self, session)

if __name__ == '__main__':
    configuration = configparser.ConfigParser()
    configuration.read(CONFIG_FILE_PATH)
    baseurl = configuration['login']['baseurl']
    username = configuration['login']['username']
    password = configuration['login']['password']
    logging.config.fileConfig("config/log_config")
    logging.debug('Read from config file and ready to begin.')
    s = login(username, password, baseurl, 0)

    # Testing Roles
    a = Roles_inventory(s)
    a_json = json.loads(a.get_data())
    logging.debug(json.dumps(a_json))
    logging.debug('Schedule Manager ID = ' + str(a.name_2_id('Schedule Manager')))
    logging.debug('Administrator ID = ' + str(a.name_2_id('Administrator')))
    logging.debug('not a real ID = ' + str(a.name_2_id('Not a real ID')))
    logging.debug('ID 22 name = ' + str(a.id_2_name(22)))

    # Testing workgroups
    a = Workgroups_inventory(s)
    a_json = json.loads(a.get_data())
    logging.debug(json.dumps(a_json))
    list_of_names = [item['name'] for item in a_json['list']]
    list_of_ids = [item['id'] for item in a_json['list']]
    logging.debug('bloop The list of all workgroup ids is: {}'.format(list_of_ids))

    print(json.dumps(list_of_names))
    for name in list_of_names:
        logging.debug('bloop The id of {} is {}'.format(name, a.name_2_ids(name)))
    for identifier in list_of_ids:
        logging.debug('bloop The parent of {} is {}'.format(identifier, a.get_parent_id(identifier)))

    for identifier in list_of_ids:
        logging.debug('bloop identifier is: {}'.format(identifier))
        logging.debug('bloop the children of {} are {}'.format(identifier, a.get_children_ids(identifier)))

