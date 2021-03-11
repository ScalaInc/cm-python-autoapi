__author__ = 'rkaye'


from framework.framework_object_rest import framework_object
from framework.templates_rest import Templates
from framework.constants import *
from framework.http_rest import rest_request
import logging
import logging.config

class Playlist(framework_object):
    '''
    Class that encapsulates all of the methods used in testing player API
    '''
    apiurl = '/api/rest/players'

    def __init__(self,api_version):
        '''
        Constructor initializes api version
        :return: VOID
        '''
        super().__init__(api_version)

    def create_playlist(self, session, baseurl, name, description = None,playlist_type = "MEDIA_PLAYLIST", healthy = True, enable_smart_playlist=False):
        '''
        Wrapper around POST /api/rest/playlists - create playlist
        :param session: CM session logged into CM under test
        :param baseurl:
        :param name:
        :param description:
        :return: True if return code is 200.  False otherwise
        '''
        create_playlist_apiurl = '/api/rest/playlists'
        create_playlist_parameters = {}

        if description != None:
            create_playlist_parameters['description'] = description
        create_playlist_parameters['name'] = name
        create_playlist_parameters['playlistType']=playlist_type
        create_playlist_parameters['healthy'] = healthy
        create_playlist_parameters['enableSmartPlaylist']=enable_smart_playlist

        self.last_response = rest_request(session,
                                          baseurl = baseurl,
                                          apiurl=create_playlist_apiurl,
                                          type_of_call=call_type.post,
                                          payload_params=create_playlist_parameters)

        logging.debug('Call to POST {} returned status code of {} and response of {}'.format(create_playlist_apiurl,
                                                                                             self.last_response.status_code,
                                                                                             self.last_response.text))
        if self.last_response.status_code == 200:
            return True
        else:
            return False
    def add_media_to_normal_playlist(self,session, baseurl, playlist_id, media_id):
        '''
        Wrapper around PUT /api/rest/playlists/<id>/playlistItems/<id>
        :param session: CM session logged into CM under test
        :param baseurl: base url of CM under test
        :param playlist_id: id of playlist to add the media item to
        :param media_id: id of media item to add
        :return:true if status code is 200.  False otherwise
        '''
        add_media_to_playlist_apiurl = '/api/rest/playlists/' + str(playlist_id) + '/playlistItems/' + str(media_id)

        self.last_response = rest_request(session = session,
                                          baseurl = baseurl,
                                          apiurl= add_media_to_playlist_apiurl,
                                          type_of_call=call_type.put)

        logging.debug('Call to PUT {} returned status code = {}, response = {}'.format(add_media_to_playlist_apiurl,
                                                                                       self.last_response.status_code,
                                                                                       self.last_response.text))
        if self.last_response.status_code == 200:
            return True
        else:
            return False

    def add_subplaylist_to_playlist(self,session,baseurl,playlist_id,name,subplaylistId):
        '''
        A wrapper around PUT /api/rest/playlists/<id>

        This wrapper only provides the ability to add a subplaylist to a playlist.  Note: the name of the
        playlist is required, not hte name of the subplaylist.

        This method was created to save some time with this very common function.  Ultimately a more involved wrapper
        will have to be written for the PUT /api/rest/playlists/<id> endpoint
        :param session: Session object logged into CM
        :param baseurl: base url of CM under test
        :param playlist_id: id of the playlist that will accept the new subPlaylist
        :param name: name of the playlist
        :param subplaylistId: id of the subplaylist
        :return:True if status code is 200.  False otherwise
        '''

        add_subplaylist_apiurl = '/api/rest/playlists/' + str(playlist_id)

        add_subplaylist_parameters = {}
        add_subplaylist_parameters['name'] = name
        add_subplaylist_parameters['playlistItems']= [{'subplaylist':{'id':subplaylistId}}]

        self.last_response = rest_request(session = session,
                                          baseurl = baseurl,
                                          apiurl= add_subplaylist_apiurl,
                                          type_of_call= call_type.put,
                                          payload_params=add_subplaylist_parameters)
        logging.debug('Response to PUT {} is status code: {} response {}'.format(add_subplaylist_apiurl,
                                                                                 self.last_response.status_code,
                                                                                 self.last_response.text))
        if self.last_response.status_code == 200:
            return True
        else:
            return False
    def list_playlists(self,session,baseurl,limit = 10, offset = 0, sort ='name', filters = None, fields = None, search = None):
        '''
        Wrapper aroudn /api/rest/playlists/all
        Uses super method list_objects

        :param session: Session object logged into CM under test
        :param baseurl: base url of the system under test
        :param limit: number of responses per page of response
        :param offset: page offset
        :param sort: sort by field
        :param filters: filters for the list
        :param fields: fields used by the list
        :param search: search keywords for the list
        :return:  True if status code is 200, False otherwise
        '''

        list_all_playlists_apiurl = '/api/rest/playlists/all'

        self.list_objects(session = session,
                          baseurl = baseurl,
                          apiurl = list_all_playlists_apiurl,
                          limit = limit,
                          offset = offset,
                          sort = sort,
                          search = search,
                          filters = filters,
                          fields = fields)
        logging.debug('Response to GET {} is status code = {}, response = {}'.format(list_all_playlists_apiurl,
                                                                                     self.last_response.status_code,
                                                                                     self.last_response.text))

        if self.last_response.status_code == 200:
            return True
        else:
            return False

    def list_playlists_for_landing_page(self, session, baseurl, limit = 10, offset = 0, sort = 'name', filters = None, fields = None, search = None):
        '''
        Wrapper around /api/rest/playlists
        Uses super method list_objects

        :param session: Session object logged into CM under test
        :param baseurl: base url of the system under test
        :param limit: number of responses per page of response
        :param offset: page offset
        :param sort: sort by field
        :param filters: filters for the list
        :param fields: fields used by the list
        :param search: search keywords for the list
        :return:  True if status code is 200, False otherwise
        '''

        list_all_playlists_apiurl = '/api/rest/playlists'

        self.list_objects(session = session,
                          baseurl = baseurl,
                          apiurl = list_all_playlists_apiurl,
                          limit = limit,
                          offset = offset,
                          sort = sort,
                          search = search,
                          filters = filters,
                          fields = fields)
        logging.debug('Response to GET {} is status code = {}, response = {}'.format(list_all_playlists_apiurl,
                                                                                     self.last_response.status_code,
                                                                                     self.last_response.text))

        if self.last_response.status_code == 200:
            return True
        else:
            return False
    def list_playlist_types(self,session, baseurl):
        '''
        Wrapper around /api/rest/plalists/types
        :param session: Session object logged into the CM under test
        :param baseurl: Base url of the system under test
        :return:True if the response status code is 200, False otherwise
        '''

        list_playlist_types_apiurl = '/api/rest/playlists/types'

        self.last_response = rest_request(session=session,
                                          baseurl = baseurl,
                                          apiurl = list_playlist_types_apiurl,
                                          type_of_call=call_type.get)

        logging.debug("Made call to GET {}.  Response status code = {}, response = {}".format(list_playlist_types_apiurl,
                                                                                              self.last_response.status_code,
                                                                                              self.last_response.text))
        if self.last_response.status_code == 200:
            return True
        else:
            return False


    def delete_playlist_by_id(self, session, baseurl, playlist_id):
        '''
        wrapper around DELETE /api/rest/playlist/<id>
        :param session: Logged in session to the CM under test
        :param baseurl: baseurl for the system under test
        :param playlist_id: id of playlist to be deleted
        :return:True if resposne is 204, False otherwise.  Updates last_response
        '''
        delete_playlist_apiurl = '/api/rest/playlists/' + str(playlist_id)

        return self.delete_object_by_id(session = session,
                                        baseurl = baseurl,
                                        apiurl= delete_playlist_apiurl,
                                        object_id=playlist_id)

    def find_normal_playlist_by_id(self, session, baseurl, playlist_id, fields=None):
        '''
        Wrapper around GET /api/rest/playlists/<id>

        uses super class find_object_by_id
        :param session: Logged in session to the CM under test
        :param baseurl: baseurl for the system under test
        :param playlist_id: Id of player to retur
        :return: True if status code is 200, false otherwise.  Updates last response
        '''

        find_normal_playlist_apiurl = '/api/rest/playlists/' + str(playlist_id)

        return self.find_object_by_id(session = session,
                                      baseurl = baseurl,
                                      apiurl = find_normal_playlist_apiurl,
                                      object_id= playlist_id,
                                      fields = fields)

    def list_all_available_playlist_items(self, session, baseurl, playlist_id,fields = None):
        '''
        Wrapper around GET /aip/rest/playlists/<playlist_id>/items

        :param session: Logged in session to the CM under test
        :param baseurl: baseurl for the system under test
        :param playlist_id: ID of playlist to retrieve items for
        :param fields: limit the resposne by comma separated list of fields.  This is a string.  e.g. 'id,media'
        :return:  True if status code is 200, False otherwise.  Updates self.last_response
        '''
        list_all_items_apiurl = '/api/rest/playlists/' +str(playlist_id) + '/items'

        params = {}
        if fields != None:
            params['fields'] = fields

        self.last_response = rest_request(session = session,
                                          baseurl = baseurl,
                                          apiurl = list_all_items_apiurl,
                                          type_of_call= call_type.get,
                                          query_params = params
                                          )
        logging.debug('Made call to GET {}.  Response code = {}, Response = {}'.format(list_all_items_apiurl,
                                                                                       self.last_response.status_code,
                                                                                       self.last_response.text))
        if self.last_response.status_code == 200:
            return True
        else:
            return False

    def duplicate_playlist(self, session, baseurl, playlist_id, new_playlist_name, new_playlist_description):
        '''
        Wrapper around /api/rest/playlists/{id}/duplicate
        :param session: Authenticated Requests.session object
        :param baseurl: base url for system under test
        :param playlist_id: Playlist to duplicate
        :return: True if response code is 200.  False otherwise.  Updates last_response
        '''

        duplicate_playlist_apiurl = '/api/rest/playlists/' + str(playlist_id)+ '/duplicate'
        duplicate_playlist_paramaters = {'name':new_playlist_name,
                                         'description':new_playlist_description}

        self.last_response = rest_request(session = session,
                                          baseurl = baseurl,
                                          apiurl = duplicate_playlist_apiurl,
                                          type_of_call = call_type.post,
                                          payload_params=duplicate_playlist_paramaters)
        logging.debug('Made call to POST {}. Response code = {}, Response = {}'.format(duplicate_playlist_apiurl,
                                                                                       self.last_response.status_code,
                                                                                       self.last_response.text))
        if self.last_response.status_code == 200:
            return True
        else:
            return False



    def update_playlist(self,session, baseurl, playlist_id, field_change_dict = None):
        '''
        Wrapper around PUT /api/rest/playlists/{id}
        :param session: Authenticated Session object
        :param baseurl: Baseurl for system under test
        :param playlist_id: ID of playlist to update
        :param field_change_dict: Dictionary containing the representation of the playlist to send to the server
        :return: True if status code == 200, False otherwise.  Updates last_response
        '''

        update_playlist_apiurl = '/api/rest/playlists/' + str(playlist_id)

        return self.update_single_object(session = session,
                                         baseurl = baseurl,
                                         apiurl= update_playlist_apiurl,
                                         object_id= playlist_id,
                                         field_change_dict=field_change_dict)

    def get_playlist_usage(self,session, baseurl, playlist_ids):
        '''
        Wrapper around GET /api/rest/playlists/usage
        :param session: Authenticated Session object
        :param baseurl: Baseurl for system under test
        :param playlist_id: Comma Separated list of IDs of playlists to report usage on
        :return: True if response code is 200, False otherwise.  Updates last_response
        '''

        get_playlist_usage_apiurl = '/api/rest/playlists/usage'
        get_playlist_usage_params = {'ids':playlist_ids}

        self.last_response = rest_request(session = session,
                                          baseurl = baseurl,
                                          apiurl = get_playlist_usage_apiurl,
                                          type_of_call=call_type.get,
                                          query_params= get_playlist_usage_params)

        logging.debug('Sent call to GET {}, response code: {}, response {}'.format(get_playlist_usage_apiurl,
                                                                                   self.last_response.status_code,
                                                                                   self.last_response.text))
        if self.last_response.status_code == 200:
            return True
        else:
            return False

    def list_available_thumbnails_for_playlist_items(self, session, baseurl, playlist_id):
        '''
        Wrapper around /api/rest/;playlists/
        :param session: Authenticated Session object
        :param baseurl: Baseurl for system under test
        :param playlist_id: Playlist ID to return the available thumbnails
        :return:True if status code is 200.  False otherwise.
        '''

        list_available_playlist_apiurl = '/api/rest/playlists/' + str(playlist_id) + '/items/thumbnails'

        self.last_response = rest_request(session = session,
                                          baseurl = baseurl,
                                          apiurl = list_available_playlist_apiurl,
                                          type_of_call= call_type.get)

        logging.debug('Made call to GET {}.  Response code: {} Response {}'.format(list_available_playlist_apiurl,
                                                                                   self.last_response.status_code,
                                                                                   self.last_response.text))
        if self.last_response.status_code == 200:
            return True
        else:
            return False

    def list_transitions(self, session, baseurl):
        '''
        Wrapper around /api/rest/playlists/transition
        :param session:  Logged in session object for system under tst
        :param baseurl:  baseurl of system under test
        :return:  True if status code is 200.  False otherwise.  Updates last response
        '''

        list_transitions_apiurl = '/api/rest/playlists/transition'

        self.last_response = rest_request(session = session,
                                          baseurl = baseurl,
                                          apiurl = list_transitions_apiurl,
                                          type_of_call = call_type.get)

        logging.debug('Made call to GET {}.  Response code: {}, Response: {}'.format(list_transitions_apiurl,
                                                                                     self.last_response.status_code,
                                                                                     self.last_response.text))

        if self.last_response.status_code == 200:
            return True
        else:
            return False

    def list_transitions_by_group(self,session, baseurl):
        '''
        Wrapper around /api/rest/playlists/listTransitions
        List Transitions by Group
        :param session: Logged in session object for system under test
        :param baseurl: baseurl of system under test
        :return:  True of status code is 200.  False otherwise.  Updates last response
        '''
        list_transitions_apiurl = '/api/rest/playlists/listTransitions'

        self.last_response = rest_request(session = session,
                                          baseurl = baseurl,
                                          apiurl = list_transitions_apiurl,
                                          type_of_call = call_type.get)

        logging.debug('Made call to GET {}.  Response code: {}, Response: {}'.format(list_transitions_apiurl,
                                                                                     self.last_response.status_code,
                                                                                     self.last_response.text))

        if self.last_response.status_code == 200:
            return True
        else:
            return False

    def multi_update_playlists(self, session, baseurl, uuid, item_to_change, value):
        '''
        Wrapper around PUT /api/rest/playlists/multi/<uuid>
        :param session: session authenticated on CM under test
        :param baseurl: baseurl of system under test
        :param uuid: UUID of storage object containing list of ID's to change
        :param item_to_change: The playlist field to be updated in the call.  Valid values are-
        description, controlledByAdManager,pickPolicy,shuffleNotRepeatType,shuffleNotRepeatWithin,categories,workgroups,playlistItems
        :return:True if response code is 200. False otherwise.  Updates last_response
        '''

        multi_update_apiurl = '/api/rest/playlists/multi/' + str(uuid)
        multi_update_param = {'id':uuid,'uuid':uuid,'item':{item_to_change:value}}

        '''
        Note:  The multi update param variable should take this form in 1.0 of the playlist api
        # {
        #   id:"29cbbb57-e2de-4a91-8e26-4cf7f8f889ab",
        #   uuid : "29cbbb57-e2de-4a91-8e26-4cf7f8f889ab",
        #   item: {description:'blah'}
        # }
        '''
        self.last_response = rest_request(session = session,
                                          baseurl = baseurl,
                                          apiurl = multi_update_apiurl,
                                          type_of_call = call_type.put,
                                          payload_params=multi_update_param)
        logging.debug('Made call to PUT {}.  Response code = {}, Response = {}'.format(multi_update_apiurl,
                                                                                       self.last_response.status_code,
                                                                                       self.last_response.text))

        if self.last_response.status_code == 200:
            return True
        else:
            return False

    def find_playlist_with_given_name(self, session, baseurl, name):
        '''
        Wrapper around get /api/rest/playlists/findByName/(name)

        :param session: Authenticated session object for the test CM
        :param baseurl: Base url of the system under test
        :param name: Name of playlist to find
        :return:True if response code is 200.  False otherwise.  Updates last response
        '''

        find_playlist_by_name_apiurl = '/api/rest/playlists/findByName/' + str(name)

        self.last_response = rest_request(session = session,
                                          baseurl = baseurl,
                                          apiurl = find_playlist_by_name_apiurl,
                                          type_of_call=call_type.get)

        logging.debug('Made call to GET {}.  Response code = {}.  Response = {}'.format(find_playlist_by_name_apiurl,
                                                                                        self.last_response.status_code,
                                                                                        self.last_response.text))

        if self.last_response.status_code == 200:
            return True
        else:
            return False

    def update_partial_playlist(self, session, baseurl, playlist_id, playlist):
        """
        PUT /api/rest/playlists/<id>/partial
        Rapidly update a playlist.  This API call is not advertised in the api docs - it was created for dot2dot as
        part of the fix for CM-9707.  The public PUT playlists will delete all playlist items if the playlistItems
        data structure is omitted.  This call changes only the fields provided as arguments and leaves playlistItems
        unaffected
        :param session: authenticated session object
        :param baseurl:
        :param playlist_id: ID of playlist
        :param playlist: A DTO containing the playlist modifications
        :return: True if response code is 200, false otherwise
        """

        partial_update_playlist_apiurl = '/api/rest/playlists/' + str(playlist_id) + '/partial'

        self.last_response = rest_request(session=session,
                                          baseurl=baseurl,
                                          apiurl=partial_update_playlist_apiurl,
                                          type_of_call=call_type.put,
                                          payload_params=playlist)

        logging.debug('Made call to PUT {}.  Response code = {}.  Response = {}'.format(partial_update_playlist_apiurl,
                                                                                        self.last_response.status_code,
                                                                                        self.last_response.text))

        if self.last_response.status_code == 200:
            return True
        else:
            return False

    def append_playlistItem(self, session, baseurl, playlist_id, playlist_item_dto):
        """
        Wrapper around /api/rest/playlists/<id>/playlistItems
        :param session: Authenticated session object
        :param baseurl: Basurl of CM under test
        :param playlist_id: ID of playlist to append to
        :param playlist_item_dto: playlist dto
        Example media append request body:
        {
          "playlistItemType":"MEDIA_ITEM",
          "media": { "id": 1234 },
          "startValidDate": "...",
          "endValidDate": "...",
          "conditions": [...],
          "timeSchedules": [...],
          ...
        }

        Example subplaylist append request body:
        {
          "playlistItemType":"SUB_PLAYLIST",
          "subplaylist": { "id": 5678 },
          "startValidDate": "...",
          "endValidDate": "...",
          "conditions": [...],
          "timeSchedules": [...],
          ...
        }
        :return:
        """
        append_playlist_apiurl = '/api/rest/playlists/' + str(playlist_id) + '/playlistItems/' + str(playlist_item_dto)

        # if 'playlistItemType' not in playlist_item_dto:
        # logging.debug("Invalid playlist dto item provided to append to playlist call: {}".format(playlist_item_dto))
        # return False
        #
        # if playlist_item_dto['playlistItemType'] == 'MEDIA_ITEM':
        #     # Check that the playlist
        #
        # elif playlist_item_dto['playlistItemType'] == "SUB_PLAYLIST":




        self.last_response = rest_request(session=session,
                                          baseurl=baseurl,
                                          apiurl=append_playlist_apiurl,
                                          type_of_call=call_type.put)

        try:
            logging.debug('Made call to POST {}.  Response code = {}.  Response = {}'.format(append_playlist_apiurl,
                                                                                        self.last_response.status_code,
                                                                                  self.last_response.text))
        except AttributeError:
            logging.debug('APPENDTIME Response did not have status code or status text for append playlist')
            return False

        if self.last_response.status_code == 200:
            return True
        else:
            return False

    def getDefaultPlaylistItem(self,playlist_item_type, item_id, player_id, player_group_id,start_date, end_date):#,startValidDate,endValidDate,conditions,timeSchedules):
        """
        Utility method used to return a playlist item for the append methods.  Initial version just returns a
        'standard' dto - later versions will add complexity
        """
        dto = {}
        if playlist_item_type is playlistItemType.MEDIA_ITEM:
            dto = {
                "playlistItemType":"MEDIA_ITEM",
                "media": { "id": item_id },
                "startValidDate": start_date,
                "endValidDate":  end_date,
                "useValidRange": True,
                "conditions": [{'comparator': 'IS', 'hasChanged': True, 'type':'PLAYER_GROUP', 'value': player_group_id},
                               {'comparator': 'IS', 'hasChanged': True, 'type':'PLAYER_NAME', 'value': player_id},
                               {'comparator': 'IS', 'hasChanged': True, 'type':'CHANNEL_DISPLAY', 'value': "Display 1"}],
                "timeSchedules": [{'days': ["SUNDAY", "THURSDAY", "FRIDAY", "SATURDAY"],
                                   'endTime': "12:00",
                                   'hasChanged': True,
                                   'showRemove': True,
                                   'startTime': "00:00"},
                                  {'days': ["SUNDAY", "MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY"],
                                   'endTime': "24:00",
                                   'hasChanged': True,
                                   'showRemove': True,
                                   'startTime': "12:01"}]
            }
        elif playlist_item_type is playlistItemType.SUB_PLAYLIST:
            dto = {
                "playlistItemType":"SUB_PLAYLIST",
                "subplaylist": {"id": item_id},
                "startValidDate": start_date,
                "endValidDate": end_date,
                "useValidRange": True,
                "conditions": [{'comparator': 'IS', 'hasChanged': True, 'type':'PLAYER_GROUP', 'value': player_group_id},
                               {'comparator': 'IS', 'hasChanged': True, 'type':'PLAYER_NAME', 'value': player_id},
                               {'comparator': 'IS', 'hasChanged': True, 'type':'CHANNEL_DISPLAY', 'value': "Display 1"}],
                "timeSchedules": [{'days': ["SUNDAY", "THURSDAY", "FRIDAY", "SATURDAY"],
                                   'endTime': "12:00",
                                   'hasChanged': True,
                                   'showRemove': True,
                                   'startTime': "00:00"},
                                  {'days': ["SUNDAY", "MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY"],
                                   'endTime': "24:00",
                                   'hasChanged': True,
                                   'showRemove': True,
                                   'startTime': "12:01"}]
            }
        return dto

    def delete_media_from_normal_playlist(self, session, baseurl, playlist_id, playlist_item_id):
        """
        Wrapper around DELETE /api/rest/playlists/{id}/playlistItems/{playlistItemId}
        Which was created as part of Jira ticket CM-9704
        :param session: Authenticated session on CM under etst
        :param baseurl: Baseurl of CM under test
        :param playlist_id:
        :param playlist_item_id:
        :return:
        """
        delete_media_apiurl = '/api/rest/playlists/' + str(playlist_id) + '/playlistItems/' + str(playlist_item_id)



        self.last_response = rest_request(session = session,
                                          baseurl = baseurl,
                                          apiurl = delete_media_apiurl,
                                          type_of_call = call_type.delete)
        logging.debug('Made call to PUT {}.  Response code = {}, Response = {}'.format(delete_media_apiurl,
                                                                                       self.last_response.status_code,
                                                                                       self.last_response.text))

        if self.last_response.status_code == 204:
            return True
        else:
            return False