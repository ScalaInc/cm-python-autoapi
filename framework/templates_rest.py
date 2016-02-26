__author__ = 'richardkaye'
from framework.framework_object_rest import framework_object
from framework.constants import *
from framework.http_rest import rest_request
import time
import logging
import logging.config


class Templates(framework_object):
    '''
    Class that wraps around Template API calls
    '''

    apiurl = '/api/rest/templates'

    def __init__(self, api_version):
        super().__init__(api_version)

    def find_tempalte_by_id(self, session, baseurl, id):
        '''
        GET /api/rest/templates/{id}
        :return: True if status code is 200.  False otherwise.  Stores responses in self.last_response
        '''
        find_template_id_apiurl = '/api/rest/templates/' + str(id)
        self.last_response = rest_request(session, type_of_call=call_type.get, baseurl=baseurl,
                                          apiurl=find_template_id_apiurl)
        logging.info('Response from /api/rest/templates/(id) is: status_code = {}, response = {}'.format(
            self.last_response.status_code, self.last_response.text))
        if self.last_response.status_code == 200:
            return True
        else:
            return False

    def delete_template_by_id(self, session, baseurl, id):
        '''
         DELETE /api/rest/templates/{id} (Depricated)

         Deletes the template with the given  ID
        :param session: Authenticated CM session
        :param baseurl: baseurl for the CM
        :param id: ID of template to be deleted
        :return: True if the response code is 204, False otherwise
        '''
        delete_apiurl = Templates.apiurl + '/' + str(id)

        self.last_response = rest_request(session, baseurl=baseurl, type_of_call=call_type.delete, apiurl=delete_apiurl)
        logging.debug('Sent DELETE /api/rest/templates/{} response code = {}, response = {}'.format(str(id),
                                                                                                    self.last_response.status_code,
                                                                                                    self.last_response.text))
        if self.last_response == 204:
            return True
        else:
            return False

    def template_faceted_search(self, session, baseurl, limit=None, offset=None, sort=None, filters=None,
                                facets=None, ):
        pass

    def list_templates(self, session, baseurl, limit=None, offset=None, sort=None, filters=None, fields=None,
                       search=None):
        '''
        GET /api/rest/templates

        Lists templates according to the following parameters
        :param session: Authenticated CM session
        :param baseurl: baseurl for CM
        :param limit: Max number of return elemets - used in paging
        :param offset: Paging offset
        :param sort: Sort by field
        :param filters: Filter for returned data objects
        :param fields: Fields returned in search
        :param search: Old style (non faceted) search mechanism
        :return: True if the respones is code 200, false otherwise.  Also resets 'last response'
        '''

        list_apiurl = Templates.apiurl

        list_query_params = {}

        # Build the Query parameters based on the values of parameters

        if limit != None:
            list_query_params['limit'] = limit
        if offset != None:
            list_query_params['offset'] = offset
        if sort != None:
            list_query_params['sort'] = sort
        if filters != None:
            list_query_params['filters'] = filters
        if fields != None:
            list_query_params['fields'] = fields
        if search != None:
            list_query_params['search'] = search


        # Send the request
        self.last_response = rest_request(session, baseurl=baseurl, type_of_call=call_type.get, apiurl=list_apiurl,
                                          query_params=list_query_params)
        logging.debug(
            'Sent GET /api/rest/templates/ response code = {}, response = {}'.format(self.last_response.status_code,
                                                                                     self.last_response.text))
        if self.last_response.status_code == 200:
            return True
        else:
            return False

    def list_templates_in_use(self, session, baseurl, limit=None, offset=None, sort=None, filters=None, fields=None,
                              search=None):
        '''
        GET /api/rest/templates/inuse

        Lists templates in use according to the following parameters
        :param session: Authenticated CM session
        :param baseurl: baseurl for CM
        :param limit: Max number of return elemets - used in paging
        :param offset: Paging offset
        :param sort: Sort by field
        :param filters: Filter for returned data objects
        :param fields: Fields returned in search
        :param search: Old style (non faceted) search mechanism
        :return: True if the response+ is code 200, false otherwise.  Also resets 'last response'
        '''

        list_inuse_apiurl = Templates.apiurl + '/inuse'

        list_query_params = {}

        if limit != None:
            list_query_params['limit'] = limit
        if offset != None:
            list_query_params['offset'] = offset
        if sort != None:
            list_query_params['sort'] = sort
        if filters != None:
            list_query_params['filters'] = filters
        if fields != None:
            list_query_params['fields'] = fields
        if search != None:
            list_query_params['search'] = search

        # Send the request
        self.last_response = rest_request(session, baseurl=baseurl, type_of_call=call_type.get,
                                          apiurl=list_inuse_apiurl, query_params=list_query_params)
        logging.debug('Sent GET /api/rest/templates/inuse response code = {}, response = {}'.format(
            self.last_response.status_code, self.last_response.text))
        if self.last_response.status_code == 200:
            return True
        else:
            return False

    def get_thumbnail_status_by_uuid(self, session, baseurl, uuid):
        '''
        Wrapper around GET /api/rest/templates/{uuid}/thumbnailStatus
        :param session: Session object authenticated on CM
        :param baseurl: Baseurl of CM under test
        :param uuid: Universal ID of the template under test
        :return:
        '''

        get_thumbnail_status_apirul = '/api/rest/templates/' + str(uuid) + '/thumbnailStatus'
        self.last_response = rest_request(session = session,
                                  baseurl = baseurl,
                                  apiurl = get_thumbnail_status_apirul,
                                  type_of_call = call_type.get)

        logging.debug('Made call to GET {}.  Response code = {}.  Response = {}'.format(get_thumbnail_status_apirul,
                                                                                        self.last_response.status_code,
                                                                                        self.last_response.text))

        if self.last_response.status_code == 200:
            return True
        else:
            return False

    def wait_for_template_upload(self, session, baseurl, max_wait_seconds, template_uuid):
        '''
        Utility function that makes use of GET /api/rest/templates/{uuid}/thumbnailStatus
        Sends a request to get the thumbnail status for template with uuid = template_uuid every second up to max_wait_seconds.
        If the thumbnail is not generated within max_wait_seconds, the method returns False.  As soon as the
        call returns that the thumbnail is ready, this method returns True
        :param session: Session object logged into CM under test
        :param baseurl: Baseurl of CM under test
        :param wait_in_seconds: Maximum wait time in seconds
        :param template_uuid: The UUID of the template being 'waited' for
        :return:True if the 'value' field in the response is 'Done' within max_wait_seconds.  False otherwise.  Updates last_response
        '''

        for current_wait in range(max_wait_seconds):
            if self.get_thumbnail_status_by_uuid(session = session,
                                           baseurl = baseurl,
                                           uuid= template_uuid):
                return True
            time.sleep(1)
        return False
    # def validate_api_field(self, key_value_pair):
    #     '''
    #     Validates that self.last_response.json() has the key and value pair indicated in the argument.
    #     The argument is a dict of the form: {<key>:<value>}.  If the value is None, then only the existence
    #     of the key is checked.
    #
    #     Internally, the result of this comparison maps to the following truth table:
    #
    #     Argument to validate    Is Key Present?     Does Value Match    Internal Response                           Return Value
    #     <key>:None              Yes                 Not Checked         validate_api_field_results.OK               True
    #     <key>:None              No                  Not Checked         validate_api_field_results.KEY_NO_MATCH     False
    #     <key>:<value>           YES                 YES                 validate_api_filed_results.OK               True
    #     <key>:<value>           No                  N/A                 validate_api_field_results.KEY_NO_MATCH     False
    #     <key>:<value>           Yes                 No                  validate_api_field_results.VALUE_NO_MATCH   False
    #     <key>:<value>           Deprecated          N/A                 validate_api_field_results.KEY_DEPRECATED   True*
    #     <key>:<value>           Yes                 Deprecated          validate_api_field_results.VALUE_DEPRECATED True*
    #
    #     * Note that the method returns True if the key or the value is deprecated.  This way as the API changes,
    #     this method can be changed to adjust without modifying test cases.  Using the class api_version attribute, this method can have
    #     logic added to it that identifies fields that are deprecated or changed.
    #
    #     The test case never has to adapt except that it has a big honking list of valid
    #     fields.  This method is smart enough to recognize if a key:value pair is correct for the API version
    #      that the Templates object was instantiated with.
    #
    #      However, since the logic for depricated fields may be complex, and dependant on
    #
    #
    #     :param key_value_pair:
    #     :return: See the description
    #     '''
    #
    #     value = list(key_value_pair.values())[0]
    #     key = list(key_value_pair.keys())[0]
    #
    #     logging.info('Checking if key {} and value {} is in last json response or Deprecated.'.format(key,value))
    #
    #     # Return true if the key or key:value pair is not valid for this API version
    #     if self.is_key_deprecated(key):
    #         result = validate_api_field_results.KEY_DEPRECATED
    #         logging.info('Result of check is: {}.  Key is not from this api version'.format(result.name))
    #         return True
    #     elif self.is_value_deprecated(key,value):
    #         result = validate_api_field_results.VALUE_DEPRECATED
    #         logging.info('Result of check is: {}.  Value is not from this api version'.format(result.name))
    #         return True
    #     # Return False if key is not present in last response json object
    #     elif key not in self.last_response.json():
    #         result = validate_api_field_results.KEY_NO_MATCH
    #         logging.info('Result of check is: {}.  Key is not valid'.format(result.name))
    #         return False
    #     # The key must be in the last response json object, if value is not checked return True
    #     elif value == None:
    #         result = validate_api_field_results.OK
    #         logging.info('Result of check is: {}.  Key valid, value is None'.format(result.name))
    #         return True
    #     # The value is present in the arguments and is not None.  Return true if the value matches last_Response.json
    #     elif value == self.last_response.json()[key]:
    #         result = validate_api_field_results.OK
    #         logging.info('Result of check is: {}. Key is valid, value matches'.format(result.name))
    #         return True
    #     # The value is present and does not match the value found in last_response.json().  Return False
    #     else:
    #         result = validate_api_field_results.VALUE_NO_MATCH
    #         logging.info('Result of check is: {}. Key is valid, value does not match'.format(result.name))
    #         logging.info('Expected value of {}, got value of {}'.format(value,self.last_response.json()[key]))
    #         return False
    #
    #
    # def is_key_deprecated(self,key):
    #     #Logic goes here to determine if the given key is valid for the current self.api_version
    #     return False
    #
    # def is_value_deprecated(self,key, value):
    #     #Logic goes here to determine if the given key:value pair is valid for the current self.api_version
    #     return False