__author__ = 'rkaye'
import logging
import logging.config
import requests
import json
from framework.constants import validate_api_field_results
from framework.constants import call_type
from framework.http_rest import rest_request
import time

class framework_object():
    '''
    Base class for all other data objects used by framework - media, players etc.
    '''
    def __init__(self,api_version):
        self.json_data = {}
        self.last_response = requests.Response()
        self.api_version = api_version
        logging.info('Created framework object with API version: {}'.format(api_version))

    def get_json_data(self):
        '''
        Is loaded with json data for new requests prior to sending them to the server.  JSON representation
        of responses are also stored here
        :return:
        '''
        return self.json_data

    def get_last_response(self):
        return self.last_response

    def get_id(self):
        '''
        Returns the 'id' field of the json object in the last response
        :return: The id (integer).  If the ID does not exist in the response this will return None
        '''
        try:
            identifier = self.last_response.json()['id']
            return identifier
        except KeyError as e:
            logging.error('Did not find key id in last response.  Last response: {}'.format(self.last_response.text))
            return None

    def get_response_key(self,key):
        '''
        Examines self.last_response, and then returns the top value associated with the
        key specified   Returns None if that key cannot be parsed.
        :return: The value associated with the specified key, or None if the key is not found
        '''
        try:
            value = self.last_response.json()[key]
            return value
        except KeyError as e:
            logging.error('Did not find key {} in last response.  Last response: {}'.format(key,self.last_response.text))
            return None

    def validate_api_field(self, key_value_pair):
        '''
        Validates that self.last_response.json() has the key and value pair indicated in the argument.
        The argument is a dict of the form: {<key>:<value>}.  If the value is None, then only the existence
        of the key is checked.

        Internally, the result of this comparison maps to the following truth table:

        Argument to validate    Is Key Present?     Does Value Match    Internal Response                           Return Value
        <key>:None              Yes                 Not Checked         validate_api_field_results.OK               True
        <key>:None              No                  Not Checked         validate_api_field_results.KEY_NO_MATCH     False
        <key>:<value>           YES                 YES                 validate_api_filed_results.OK               True
        <key>:<value>           No                  N/A                 validate_api_field_results.KEY_NO_MATCH     False
        <key>:<value>           Yes                 No                  validate_api_field_results.VALUE_NO_MATCH   False
        <key>:<value>           Deprecated          N/A                 validate_api_field_results.KEY_DEPRECATED   True*
        <key>:<value>           Yes                 Deprecated          validate_api_field_results.VALUE_DEPRECATED True*

        * Note that the method returns True if the key or the value is deprecated.  This way as the API changes,
        this method can be changed to adjust without modifying test cases.  Using the class api_version attribute, this method can have
        logic added to it that identifies fields that are deprecated or changed.

        The test case never has to adapt except that it has a big honking list of valid
        fields.  This method is smart enough to recognize if a key:value pair is correct for the API version
         that the Templates object was instantiated with.

         However, the logic for individual child classes may be quite


        :param key_value_pair:
        :return: See the description
        '''

        value = list(key_value_pair.values())[0]
        key = list(key_value_pair.keys())[0]

        logging.info('Checking if key {} and value {} is in last json response or Deprecated.'.format(key,value))

        # Return true if the key or key:value pair is not valid for this API version
        if self.is_key_deprecated(key):
            result = validate_api_field_results.KEY_DEPRECATED
            logging.info('Result of check is: {}.  Key is not from this api version'.format(result.name))
            return True
        elif self.is_value_deprecated(key, value):
            result = validate_api_field_results.VALUE_DEPRECATED
            logging.info('Result of check is: {}.  Value is not from this api version'.format(result.name))
            return True
        # Return False if key is not present in last response json object
        elif key not in self.last_response.json():
            result = validate_api_field_results.KEY_NO_MATCH
            logging.info('Result of check is: {}.  Key is not valid'.format(result.name))
            return False
        # The key must be in the last response json object, if value is not checked return True
        elif value == None:
            result = validate_api_field_results.OK
            logging.info('Result of check is: {}.  Key valid, value is None'.format(result.name))
            return True
        # The value is present in the arguments and is not None.  Return true if the value matches last_Response.json
        elif value == self.last_response.json()[key]:
            result = validate_api_field_results.OK
            logging.info('Result of check is: {}. Key is valid, value matches'.format(result.name))
            return True
        # The value is present and does not match the value found in last_response.json().  Return False
        else:
            result = validate_api_field_results.VALUE_NO_MATCH
            logging.info('Result of check is: {}. Key is valid, value does not match'.format(result.name))
            logging.info('Expected value of {}, got value of {}'.format(value,self.last_response.json()[key]))
            return False


    def is_key_deprecated(self,key):
        #Logic goes here to determine if the given key is valid for the current self.api_version
        return False

    def is_value_deprecated(self,key, value):
        #Logic goes here to determine if the given key:value pair is valid for the current self.api_version
        return False

    def list_objects(self,session, baseurl, apiurl, limit, offset, sort=None, search=None, filters=None, fields=None):

        query_parameters = {'limit':limit, 'offset':offset}
        if sort != None:
            query_parameters['sort'] = sort
        if filters != None:
            query_parameters['filters'] = filters
        if fields != None:
            query_parameters['fields'] = fields
        if search != None:
            query_parameters['search'] = search

        self.last_response = rest_request(session, type_of_call=call_type.get,  baseurl=baseurl, apiurl = apiurl, query_params=query_parameters)
        try:
            logging.debug('made request at GET {} with query params = {}.  Status code = {}, response = {}'.format(apiurl,query_parameters,self.last_response.status_code, self.last_response.text))
            if self.last_response.status_code == 200:
                logging.info('Status code for GET {} api call was 200'.format(apiurl))
                return True
            else:
                logging.info('Status code for GET {} call was not 200.  It was {}'.format(apiurl, self.last_response.status_code))
                return False
        except AttributeError:
            logging.debug('Did not get valid response from server - attribute error thrown')
            return False

    def delete_object_by_id(self,session,baseurl,apiurl,object_id, max_wait = 20):
        """
        Base method for most of the delete object by ID api calls.

        When a delete API call is sent to the CM, the CM does not necessarily delete the resource before responding to the
        call.  In stead, the object is 'marked for deletion' - usually by modifying it's description to be something along the
        lines of: 'This object has been deleted.'  A background task then eventually deletes the object from the CM.  The
        response to the request is immediate.

        This means that objects deleted in the teardown section of a test suite may not be deleted in time for the setup of the
        next test in the suite.

        This method takes the CM's behavior into account.

        First this method checks for an http response code of 204 - the expected response for delete.  If the response is anything but
        204, the method returns False.

        Then this method polls for up to max_wait seconds.  Each second it performs a 'GET' on the object that was
        deleted.  If the response is 404 not found, this resource has been deleted and this method returns True.
        If the response has a status code of 200, the method waits one second and tries again.  If max_wait seconds
        elapse and the resource has not been deleted, then this method returns False.

        If max_wait is 0, the method polls exactly once.  These poles do NOT update the last_response variable for
        this object.  The last_response is the response to the actual delete message. However, the http polling requests
        are logged in the framework log file - along with their responses.

        :param session: Authenticated Session object on CM
        :param baseurl: Base url of the CM under test
        :param apiurl: API url of api resource to delete
        :param object_id: Id of object to delete
        :param lazy: True if the delete should block for up to max_wait seconds for the object to actually delete from the CM
        :param max_wait: Number of seconds to poll for the object to be deleted
        :return: True if object is deleted within max_wait seconds.  False otherwise
        """


        if apiurl[-1].isdigit():
            pass
        elif apiurl[-1] == '/':
            apiurl = apiurl + str(object_id)
        else:
            logging.error('find_object_by_id requires apiurl to end in object ID or a /')
            return False

        self.last_response = rest_request(session,type_of_call=call_type.delete, baseurl = baseurl, apiurl = apiurl)
        logging.debug('made request at DELETE {}.  Status code = {}, response = {}'.format(apiurl, self.last_response.status_code,self.last_response.text))
        if self.last_response.status_code == 204:
            logging.info('Status code for DELETE {} was 204.'.format(apiurl))
        else:
            logging.info('Status code for DELETE {} was not 204.  It was {}'.format(apiurl, self.last_response.status_code))
            return False

        # Now poll for the object to be actually deleted
        fo = framework_object(self.api_version)
        for current_wait in range(max_wait):
            logging.debug('LazyDelete, about to pole for delete completion')
            fo.find_object_by_id(session = session, baseurl = baseurl, apiurl = apiurl, object_id= object_id)

            # Note: Some deletes return 500 when deletes fail, others return 400's.  Must check for not = to 204
            if fo.last_response.status_code != 204: # We will return true if the object is not found
                logging.debug('LazyDelete, Object not found after delete call.  Delete returns True')
                return True
            logging.debug('LazyDelete, loop number {} through wait for delete'.format(current_wait))
            time.sleep(1)
        logging.error('LazyDelete, Failed to delete object at {} with id {} within {} seconds'.format(apiurl, object_id, max_wait))
        return False


    def find_object_by_id(self,session, baseurl, apiurl, object_id, fields = None):
        '''
        Sets self.last_response.  A general method for GETing objects given an ID.
        Accepts apiurl as:  /api/rest/blah/4
                            /api/rest/blah/
                            but not
                            /api/rest/blahblahblah
        :param session: Session object authenticated with CM under test
        :param baseurl: BAse url for CM
        :param apiurl: api url as described above
        :param object_id: ID of object to be returned
        :return:
        '''

        if apiurl[-1].isdigit():
            pass
        elif apiurl[-1] == '/':
            apiurl = apiurl + str(object_id)
        else:
            logging.error('find_object_by_id requires apiurl to end in object ID or a /')
            return False

        query_params = None
        if fields is not None:
            query_params = {'fields':fields}

        self.last_response = rest_request(session,
                                          type_of_call=call_type.get,
                                          baseurl=baseurl,
                                          apiurl=apiurl,
                                          query_params=query_params)
        logging.debug('Made request at GET {}.  Status code = {}, response = {}'.format(apiurl,
                                                                                        self.last_response.status_code,
                                                                                        self.last_response.text))
        if self.last_response.status_code == 200:
            logging.info('Status code for GET {} was 200'.format(apiurl))
            return True
        else:
            logging.info('Status code for GET {} was not 200. It was {}'.format(apiurl,
                                                                                self.last_response.status_code))

            return False

    def update_single_object(self, session, baseurl, apiurl, object_id, field_change_dict = None):
        '''
        Implements PUT apiurl/<id>
        Parameters to change is a dictonary of key
        :param session:  Session object logged into the CM under test
        :param baseurl: Base url of CM under test
        :param id: id of media to be modified
        :param modified_key_pairs: The specific dictionary that contains the fields to change
        :return: True if response code is 200, False otherwise
        '''
        if apiurl[-1].isdigit():
            pass
        elif apiurl[-1] == '/':
            apiurl = apiurl + str(object_id)
        else:
            logging.error('find_object_by_id requires apiurl to end in object ID or a /')
            return False

        self.last_response = rest_request(session = session,
                                          baseurl = baseurl,
                                          apiurl = apiurl,
                                          type_of_call = call_type.put,
                                          payload_params=field_change_dict)
        logging.debug('Made call to PUT {}.  Response status code = {}, response = {}'.format(apiurl,
                                                                                              self.last_response.status_code,
                                                                                              self.last_response.text))
        if self.last_response.status_code == 200:
            return True
        else:
            return False

    def faceted_search_on_object(self,
                                 session,
                                 baseurl,
                                 apiurl,
                                 limit = 10,
                                 offset = 0,
                                 sort = 'name',
                                 filters = None,
                                 facets = None,
                                 fields = None,
                                 search = None):
        '''
        Implements faceted search for all objects.  Pass in the apiurl from specific resource objects
        :param session: Logged in session object
        :param baseurl: baseurl of CM under test
        :param apiurl: apiurl of specific faceted search call (e.g. players, media etc.)
        :param limit: Number of resources to return in the response
        :param offset: offset used in paging
        :param sort: name of the field to sort results on
        :param filters: filters - if any - to apply to the result
        :param facets: comma separated list of facets to include in response object.  Must be URL encoded
        :param fields: comman separated list of fields to include in response objects
        :param search: String to search for in the name field of the resources in the response
        :return: True if respones code is 200.  False otherwise.  Updates last_response
        '''
        query_parameters = {'limit':limit, 'offset':offset}
        if sort != None:
            query_parameters['sort'] = sort
        if filters != None:
            query_parameters['filters'] = filters
        if facets != None:
            query_parameters['facets'] = facets
        if fields != None:
            query_parameters['fields'] = fields
        if search != None:
            query_parameters['search'] = search

        self.last_response = rest_request(session, type_of_call=call_type.get,  baseurl=baseurl, apiurl = apiurl, query_params=query_parameters)
        logging.debug('made request at GET {} with query params = {}.  Status code = {}, response = {}'.format(apiurl,query_parameters,self.last_response.status_code, self.last_response.text))
        # if self.lsat_response.status_code
        # if self.last_response.status_code == 200:
        #     logging.info('Status code for GET {} api call was 200'.format(apiurl))
        #     return True
        # else:
        #     return False
        try:
            logging.debug('made request at GET {} with query params = {}.  Status code = {}, response = {}'.format(apiurl,query_parameters,self.last_response.status_code, self.last_response.text))
            if self.last_response.status_code == 200:
                logging.info('Status code for GET {} api call was 200'.format(apiurl))
                return True
            else:
                logging.info('Status code for GET {} call was not 200.  It was {}'.format(apiurl, self.last_response.status_code))
                return False
        except AttributeError:
            logging.debug('Did not get valid response from server - attribute error thrown')
            return False

    def get_status_code(self):
        """
        Utility function returns last_response.status_code
        :return:self.last_response.status_code
        """

        return self.last_response.status_code