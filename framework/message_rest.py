__author__ = 'rkaye'
from framework.framework_object_rest import framework_object
from framework.constants import *
from framework.http_rest import rest_request
import logging
import logging.config

class Message(framework_object):

    apiurl = '/api/rest/messages'

    def __init__(self,api_version):
        super().__init__(api_version)

    def list_messages(self, session, baseurl, limit = 10, offset = 0, sort = 'name', filters = None, fields = None, search = None):
        """
        Wrapper around GET /api/rest/messages
        Uses super method list_objects
        :param session: Authenticated session object on system
        :param baseurl: base url for system
        :param limit: number of objects to return in the response
        :param offset: used for paging through responses
        :param sort: field to sort by
        :param filters: json string filter
        :param fields: comma separated list of fields to include in the response
        :param search: Search fields not defined
        :return: True if response code is 200.  False otherwise.  Updates self.last_response
        """

        list_messages_apiurl = '/api/rest/messages'
        return self.list_objects(session = session,
                                 baseurl =baseurl,
                                 apiurl = list_messages_apiurl,
                                 limit = limit,
                                 offset = offset,
                                 sort = sort,
                                 filters = filters,
                                 fields = fields,
                                 search = search)

    def update_message(self, session, baseurl, message_id, message_json):
        """
        Wrapper around /api/rest/messages/{id}
        Uses super class framework_object.update_object_by_id
        :param session: Authenticated session object
        :param baseurl: Baseurl of CM under test
        :param message_id: ID of message to update
        :param message_json: JSON object containing update fileds
        :return:
        """
        update_message_apiurl = '/api/rest/messages/' + str(message_id)
        return self.update_single_object(session = session,
                                         baseurl = baseurl,
                                         apiurl = update_message_apiurl,
                                         object_id= message_id,
                                         field_change_dict = message_json)


    def create_message(self, session, baseurl, name, template_id, description = None, fields = None, hasUnapprovedElements = None):
        '''
        Create a message using the template provided in the parameters
        :param session: Authenticated requests.Session object for CM under test
        :param baseurl: Base URL of the CM under test
        :param template_id: the ID of the template under test
        :param fields: list of fields included in the template and their values [{'field1':'value1'},{'field2':'value2'},...{'fieldn':'valuen'}]
        :param hasUnapprovedElements: True if mediaMessageField value is rejected, False otherwise
        :return: True if the status code is 200, false otherewise.  Also sets last_response
        '''
        create_message_apiurl = self.apiurl

        # Format the query parameter object
        create_message_params = {'name':name}
        create_message_params['template'] = {'id':template_id}
        if description is not None:
            create_message_params['description'] = description
        if fields is not None:
            create_message_params['fields'] = fields

        # Now send the request to add the Workgroup and store the response in last_response
        self.last_response = rest_request(session,
                                          baseurl=baseurl,
                                          type_of_call=call_type.post,
                                          apiurl=create_message_apiurl,
                                          payload_params=create_message_params)
        logging.debug('Sent POST /api/rest/messages to create message response code = {}, response = {}'.format(self.last_response.status_code,
                                                                                                                self.last_response.text))
        if self.last_response.status_code == 200:
            return True
        else:
            return False

    @DeprecationWarning
    def delete_message_by_id(self, session, baseurl):
        '''
        Depricated - not implemented
        :return:
        '''
        pass
