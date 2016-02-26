import sys, json
from getpass import getpass
import requests
import logging
import logging.config
from time import sleep
import configparser
from framework.framework_object_rest import framework_object
from framework.constants import *
from framework.http_rest import rest_request
from itertools import chain
from framework.media_metadata_rest import Media_meta_data
import time

""" A module that provides an interface into the media api of the CM"""

""" implements POST /api/rest/media """

#
# def media_add(session, baseurl, mname, muri, mmediaType):
#     params = dict(
#         name=mname,
#         uri=muri,
#         mediaType=mmediaType)
#     authurl = baseurl + '/api/rest/media'
#     logger.info('About to send POST to ' + authurl + ' with parameters = ' + str(params))
#     response = session.put(base_url + '/api/rest/media', data=json.dumps(params))
#     logger.info('Response code from put is: ' + str(response.status_code))
#     if response.status_code == 200:
#         return True
#     return False


class http_media_cm():
    """
    Helper class that builds a media (html only) json object for use in API testing.
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

        # Completed validation and special handling of attributes requiring
        #it.  Update internal user_data field
        logging.debug('about to add the following attribute to the system: ' + str(attribute))
        self.user_data = dict(chain(self.user_data.items(), attribute.items()))
        logging.debug('user data is now: ' + json.dumps(self.user_data))

    def validate_attribute(self, attribute):
        '''
        Validates the dictionary in attribute contains a single valid key value
        pair that can be added to the user data record.
        '''
        valid = [name for name, member in valid_media_web_attributes.__members__.items()]
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

class Media(framework_object):

    def __init__(self, api_version):
        super().__init__(api_version)

    def create_media(self,session, baseurl, name, uri, media_type = 'HTML'):
        '''
        Wrapper around POST /api/rest/media
        Create media of type HTML only.  File upload API is used to create media objects on the server.
        :param session: Authenticated session object
        :param baseurl: Base url of CM under test
        :param name: Name of media object to create
        :param uri: URI for the web page
        :param media_type: Only 'HTML' is supported by the framework at this time
        :return: True if status code = 200.  False otherwise
        '''

        create_media_apiurl = '/api/rest/media'
        payload_params = {'name':name, 'uri': uri, 'mediaType':media_type}

        self.last_response = rest_request(session,
                                          type_of_call=call_type.post,
                                          baseurl = baseurl,
                                          apiurl = create_media_apiurl,
                                          payload_params=payload_params
                                          )
        logging.debug('Sent call to POST {}.  Response code = {}.  Response = {}'.format(create_media_apiurl,
                                                                                         self.last_response.status_code,
                                                                                         self.last_response.text))
        if self.last_response.status_code == 200:
            return True
        else:
            return False


    def list_media(self,session,baseurl, limit = 10, offset = 0, sort = 'name', filters = None, fields = None, search = None):
            '''
            Implements GET /api/rest/media
            List all media matching the parameters
            :param session: The session object logged in for this test
            :param limit: Number of items to return in the list (maximum)
            :param offset: First index to perform the search.  Used for paging
            :param sort: Comma separated list of fields to sort by
            :param filters: One or more filters can be applied.  See api docs for filter formats
            :param fields: A comma separated list of fields you want to include on the response object
            :param search:
            :return: True if status code is 200 (and update last_response), false otherwise
            '''

            list_media_apiurl = '/api/rest/media'
            return self.list_objects(session,
                                     baseurl,
                                     apiurl = list_media_apiurl,
                                     limit = limit,
                                     offset = offset,
                                     sort = sort,
                                     filters = filters,
                                     fields = fields,
                                     search = search)

    def find_media_by_id(self, session, baseurl, id, fields = None):
        '''
        Implements the find media by ID API call located at: GET /api/rest/media/{id}
        :param session:  The session object logged in for this test
        :param baseurl: Base url of the CM under test.  i.e. 'http://192.168.10.135:8080/ContentManager
        :param id: id of Media object to find
        :param fields: Comma separated list of fields that should be reuturned in the response
        :return:True if status code was 200, False otherwise.  Also sets self.last response
        '''
        find_media_apiurl= '/api/rest/media/' + str(id)
        query_parameters = {}
        if fields != None:
            query_parameters['fields']= fields

        self.last_response = rest_request(session, type_of_call = call_type.get, baseurl = baseurl, apiurl = find_media_apiurl, query_params = query_parameters)
        logging.debug('made request at GET {}, and received status code: {} response: {}'.format(find_media_apiurl,self.last_response.status_code,self.last_response.text))
        if self.last_response.status_code == 200:
            return True
        else:
            return False

    def delete_media_by_id(self, session, baseurl, id):
        '''
        Implements DELETE /api/rest/media/{id}

        :param session: Session object for this test
        :param baseurl: Baseurl for the CM under test
        :param id: ID of media object to delete
        :return: True if status code is 204, and False otherwise
        '''

        delete_media_apiurl = '/api/rest/media/' + str(id)
        self.last_response = rest_request(session, type_of_call=call_type.delete, baseurl = baseurl, apiurl = delete_media_apiurl)
        if self.last_response.status_code == 204:
            logging.info('Got 204 status code for DELETE /api/rest/media/(id)')
            return True
        else:
            logging.info('Expected 204 status code for DELETE /api/rest/media/(id), bug got {}'.format(self.last_response.status_code))
            return False

    def get_thumbnail_status_by_id(self, session, baseurl, media_id):
        '''
        Wrapper around GET /api/rest/media/thumbnailStatus/{id}
        :param session: Session object authenticated on CM
        :param baseurl: Baseurl of CM under test
        :param media_id: Media id of CM under test
        :return:True if the response code is 200.  False otherwise.  Updates last_response
        '''
        get_thumbnail_apiurl = '/api/rest/media/thumbnailStatus/' + str(media_id)

        self.last_response = rest_request(session = session,
                                          baseurl = baseurl,
                                          apiurl = get_thumbnail_apiurl,
                                          type_of_call = call_type.get)

        logging.debug('Made call to GET {}.  Response code = {}.  Response = {}'.format(get_thumbnail_apiurl,
                                                                                        self.last_response.status_code,
                                                                                        self.last_response.text))

        if self.last_response.status_code == 200:
            return True
        else:
            return False

    def update_single_media(self, session, baseurl, media_id, field_change_dict = None):
        '''
        Implements PUT /api/rest/media/{id}
        Parameters to change is a dictonary of key
        :param session:  Session object logged into the CM under test
        :param baseurl: Base url of CM under test
        :param id: id of media to be modified
        :param modified_key_pairs: The specific dictionary that contains the fields to change
        :return: True if response code is 200, False otherwise
        '''

        update_media_apiurl = '/api/rest/media/' + str(media_id)

        self.last_response = rest_request(session = session,
                                          baseurl = baseurl,
                                          apiurl = update_media_apiurl,
                                          type_of_call = call_type.put,
                                          payload_params=field_change_dict)
        logging.debug('Made call to PUT {}.  Response status code = {}, response = {}'.format(update_media_apiurl,
                                                                                              self.last_response.status_code,
                                                                                              self.last_response.text))
        if self.last_response.status_code == 200:
            return True
        else:
            return False

    def modify_media_metadata_assignment(self,session, baseurl, media_id, metadata_id, metadata_value,api_version_media_metadata):

        metadata_object = Media_meta_data(api_version_media_metadata)
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

        return self.update_single_media(session = session,
                                         baseurl = baseurl,
                                         media_id = media_id,
                                         field_change_dict = changed_metadata_definition), 'Failed to update the media with the new metadata value: {}'.format(self.last_response.text)

    def wait_for_media_upload(self, session, baseurl, max_wait_seconds, media_id):
        '''
        Utility function that makes use of GET /api/rest/media/thumbnailStatus/{id}
        Sends a request to get the thumbnail status for media with id = media_id every second up to max_wait_seconds.
        If the thumbnail is not generated within max_wait_seconds, the method returns False.  As soon as the
        call returns that the thumbnail is ready, this method returns True
        :param session: Session object logged into CM under test
        :param baseurl: Baseurl of CM under test
        :param wait_in_seconds: Maximum wait time in seconds
        :return:True if the 'value' field in the response is 'Done' within max_wait_seconds.  False otherwise.  Updates last_response
        '''
        # Use a new media object so as not to corrupt the last_response  - try this
        media_object = Media(self.api_version)

        for current_wait in range(max_wait_seconds):
            media_object.get_thumbnail_status_by_id(session = session,
                                           baseurl = baseurl,
                                           media_id = media_id)
            if media_object.last_response.json()['value'] == 'Done':
                return True
            logging.debug('loop number {} through wait for media upload'.format(current_wait))
            time.sleep(1)
        logging.error('Failed to produce the thumbnail on media_id {} within {} seconds'.format(media_id,
                                                                                                max_wait_seconds))
        return False