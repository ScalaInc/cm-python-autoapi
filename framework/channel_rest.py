__author__ = 'rkaye'
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

class Channels(framework_object):
    """
    Helper class that builds a channel json object for use in API testing.
    Class methods 'help' programmers by validating data before it can be
    placed into the main data object for the instance.
    """

    def __init__(self, api_version):
        super().__init__(api_version)

    def find_channel_by_id(self, session, baseurl, id, fields = None):
        '''
        Implements the find channel by ID API call located at: GET /api/rest/media/{id}
        :param session:  The session object logged in for this test
        :param baseurl: Base url of the CM under test.  i.e. 'http://192.168.10.135:8080/ContentManager
        :param id: id of Media object to find
        :param fields: Comma separated list of fields that should be reuturned in the response
        :return:True if status code was 200, False otherwise.  Also sets self.last response
        '''
        find_channels_apiurl= '/api/rest/channels/' + str(id)
        query_parameters = {}
        if fields != None:
            query_parameters['fields']= fields

        self.last_response = rest_request(session, type_of_call = call_type.get, baseurl = baseurl, apiurl = find_channels_apiurl, query_params = query_parameters)
        logging.debug('made request at GET {}, and received status code: {} response: {}'.format(find_channels_apiurl,self.last_response.status_code,self.last_response.text))
        if self.last_response.status_code == 200:
            return True
        else:
            return False


    def create_channel(self, session, baseurl, name, frameset_id, type = "AUDIOVISUAL", playDetectedAudioTrack = False, description = 'none'):
        '''
        Implements create channel API call located at POST /api/rest/channels
        :param session: The session object logged in for this test
        :param baseurl: Base url of CM under test.  i.e. 'http://192.168.10.135:8080/ContentManager
        :param name: Name of the channel
        :param frameset_id: frameset id of the frameset selected for this channel
        :param type: Type of channel - defaults to AUDIOVISUAL
        :param description: Description of the channel
        :return: True if status code is 200.  Also adjusts self.last_response
        '''

        create_channel_apiurl = '/api/rest/channels'

        channel_params = {"name":name,"type":type,"playDedicatedAudioTrack":playDetectedAudioTrack,"description": description, "frameset":{"id":frameset_id}}

        self.last_response = rest_request(session, baseurl = baseurl,  type_of_call=call_type.post,apiurl = create_channel_apiurl, payload_params=channel_params)
        logging.info("Made call to POST /api/rest/channels to create channel.  Status code = {}, response = {}".format(self.last_response.status_code,self.last_response.text))
        if self.last_response == 200:
            return True
        else:
            return False

    def delete_channel_by_id(self,session,baseurl,channel_id):

        channel_delete_apiurl = '/api/rest/channels/' + str(channel_id)
        logging.debug('About to call super delete function')
        return self.delete_object_by_id(session,baseurl,apiurl = channel_delete_apiurl,object_id=channel_id)

    def list_channels(self, session, baseurl, limit=10, offset = 0, sort=None, filters = None, fields = None, search = None):

        list_channels_apiurl = '/api/rest/channels'

        return self.list_objects(session = session,
                                 baseurl = baseurl,
                                 apiurl = list_channels_apiurl,
                                 limit = limit,
                                 offset = offset,
                                 sort = sort,
                                 filters = filters,
                                 fields = fields,
                                 search = search
                                 )

    def update_channel(self, session, baseurl, channel_id, channel_json):
        """
        Wrapper around PUT /api/rest/channels/{id}
        :param session: Authenticated session object
        :param baseurl: Base URL of CM under test
        :param channel_id: ID of channel to update
        :param channel_json: JSON object containing hte DTO to send.
        :return:True if response code is 200. False otherwise.  Updates self.last_response.  Uses super class
        """
        update_channel_apiurl = '/api/rest/channels/' + str(channel_id)
        return self.update_single_object(session = session,
                                         baseurl = baseurl,
                                         apiurl = update_channel_apiurl,
                                         object_id=channel_id,
                                         field_change_dict=channel_json
                                         )

    def update_schedules(self,
                         session,
                         baseurl,
                         channel_id,
                         playlist_id,
                         channel_frameset_id,
                         eventTriggers = [],
                         timeTriggers = [],
                         audioDucking = False,
                         color = "#FCAD7D",
                         hasPriorityClassChanged = False,
                         locked = False,
                         name = None, # Name field is playlist name and is not supported today by framework
                         playFullScreen = False,
                         priorityClass = "NORMAL",
                         recurrencePattern = "WEEKLY",
                         startDate = "2014-10-01",
                         startTime = "05:00:00",
                         endTime = "07:30:00",
                         tempName = "N967f7952-e008-3cdb-0a72-a42adcd35eb8", # Not sure what this is - research,
                         weekdays = ["MONDAY"],
                         schedule_id = ""
                         ):


        update_schedule_apiurl = '/api/rest/channels/' + str(channel_id) + '/schedules'

        update_schedule_param = {'frames': [
            {
                "eventTriggers": eventTriggers,
                "id": channel_frameset_id,
                "timeTriggers": timeTriggers,
                "timeslots": [
                    {
                        "audioDucking": audioDucking,
                        "color": color,
                        "endTime": endTime,
                        "hasPriorityClassChanged": hasPriorityClassChanged,
                        "locked": locked,
                        # "name": "Playlist C",
                        "playFullScreen": playFullScreen,
                        "playlist": {
                            "id": playlist_id
                        },
                        "priorityClass": priorityClass,
                        "recurrencePattern": recurrencePattern,
                        "sortOrder": 1,
                        "startDate": startDate,
                        "startTime": startTime,
                        "tempName": tempName,
                        "weekdays": weekdays
                    }
                ]
            }
        ],
                                 "id": schedule_id}

        self.last_response = rest_request(session = session,
                                          baseurl = baseurl,
                                          apiurl = update_schedule_apiurl,
                                          type_of_call= call_type.put,
                                          payload_params=update_schedule_param)
        if self.last_response != None:
            logging.debug('Made call to PUT {}.  Response code = {}, response = {}'.format(update_schedule_apiurl,
                                                                                       self.last_response.status_code,
                                                                                       self.last_response.text))
            if self.last_response.status_code == 200:
                return True

        return False


    def find_timeslots_for_given_input_criteria(self, session, baseurl, channel_id, frame_id, fromDate, toDate, year = None, week = None):
        '''
        Wrapper around GET /api/rest/channels/<channel_id>/frames/<frame_id>

        :param session: Requests.session object logged into the CM under test
        :param baseurl: baseurl for CM under test
        :param channel_id: channel ID to 'get' timeslots on
        :param frame_id: channel frameset id to get the timeslots for.  In a channel record,
        look for:  'frameset'{'frames':[{'id':<channel frameset id>...},{...}] ....
        :param fromDate: Start date for search
        :param toDate: End date for search
        :param year: Only used if the start date is None
        :param week: deprecated
        :return: True if status code is 200, False otherwise.  Updates last_resposnse
        '''
        find_timeslots_apiurl = '/api/rest/channels/' + str(channel_id) + '/frames/' + str(frame_id) + '/timeslots'

        find_timeslot_query_parms = {fromDate:fromDate,'toDate':toDate,'year':year,'week':week}

        self.last_response = rest_request(session = session,
                                          baseurl = baseurl,
                                          apiurl = find_timeslots_apiurl,
                                          type_of_call= call_type.get,
                                          query_params=find_timeslot_query_parms)
        logging.debug('Sent request to GET {}, response code = {}, response = {}'.format(find_timeslots_apiurl,
                                                                                         self.last_response.status_code,
                                                                                         self.last_response.text))
        if self.last_response.status_code == 200:
            return True
        else:
            return False

