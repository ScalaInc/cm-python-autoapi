__author__ = 'rkaye'
from framework.framework_object_rest import framework_object
from framework.constants import *
from framework.http_rest import rest_request
import logging
import logging.config


class Heartbeats(framework_object):
    '''
    Class that wraps around Heartbeat API calls
    '''

    apiurl = '/api/rest/heartbeats'

    def __init__(self,api_version):
        super().__init__(api_version)
        self.events = []

    def get_current_heartbeat_sequence_of_player(self,
                                                 session,
                                                 baseurl,
                                                 uuid):
        '''
        Return a current heartbeat's sequence of a player. Return 0 if no heartbeat registered.
        :param session: The requests.session variable used to send the API call
        :param baseurl: The base url of the CM under test e.g. http//w.x.y.z:8080/ContentManager
        :param uuid: UUID of the player in question
        :param api_version: API version being tested.  Defaults to constants.DEFAULT_API_VERSION
        :return: True if response is 200, False otherwise
        '''

        get_cur_heartbeat_apirul = self.apiurl + '/sequence/' + uuid
        type_of_call = call_type.get

        resp = rest_request(session, type_of_call=type_of_call, baseurl=baseurl, apiurl=get_cur_heartbeat_apirul)
        logging.debug(
            'Response from get heartbeat sequence call is: status_code expected 200, got = {}, response = {}'.format(
                resp.status_code, resp.text))
        self.json_data = resp.json()
        self.last_response = resp
        if resp.status_code == 200:
            return True
        else:
            return False

    def renew_license(self, session, baseurl, uuid):
        '''
        Return a new license for a particular player. using the
        GET /api/rest/heartbeats/renewLicense/{uuid} API

        Returns Response object from API call
        '''

        renew_license_apiurl = self.apiurl + '/' + str(uuid)
        type_of_call = call_type.get

        resp = rest_request(session, type_of_call=type_of_call, baseurl = baseurl, apiurl = renew_license_apiurl)
        logging.debug('Sent GET /api/rest/heartbeats/renewLicense for player {}. '.format(uuid))
        logging.debug('Response from GET message is: status code = {}, response = {}'.format(resp.status_code, resp.text))
        if resp.status_code == 200:
            return True
        else:
            return False


    def report_heartbeat(self,
                         session,
                         baseurl,
                         uuid,
                         timestamp='2013-06-08 13:00:17',
                         bootTimestamp='2013-11-07 23:22:17',
                         sequence=1,
                         active=True,
                         events = None):
        '''
        Wrapper around the report heartbeat api call located at endpoint
        POST /api/rest/heartbeats

        The 'events' variable is a list of Heartbeat event objects

        :returns True if heartbeat response
        '''

        report_heartbeat_apiurl = '/api/rest/heartbeats'

        # If there are no event objects passed to this method, then use the defaults specified in
        # Heartbeat Events
        if events == None:
            default_event = Heartbeat_event(self.api_version)
            logging.debug('JSON data in default event is: {}'.format(default_event.get_json_data()))
            events_list = [default_event.get_json_data()]
        else:
            events_list = events

        heartbeat_parameters = {'uuid':uuid,
                                'timestamp':timestamp,
                                'sequence':sequence,
                                'active':active,
                                'bootTimestamp':bootTimestamp,
                                'events':events_list}

        logging.debug('Heartbeat Parameters: {}'.format(heartbeat_parameters))

        # Now post the heartbeat event

        self.last_response = rest_request(session, baseurl = baseurl, type_of_call= call_type.post, apiurl = report_heartbeat_apiurl, payload_params = heartbeat_parameters)
        #self.json_data = self.last_response.json()

        if self.last_response.status_code == 200:
            return True
        else:
            return False


class Heartbeat_event(framework_object):
    '''
    Useful for generating heartbeat messages for use in testing.  The event field is a complex field that
    shows up in the heartbeat (list of events).  Most tests will use a default event, which is datafilled
    by the constructor with no arguments.  Any argument can be customized to create a custom event.
    '''

    def __init__(self, api_version,
                 errorNumber='44.3',
                 problemMessage='message',
                 logName='IC',
                 problemNumber=12,
                 dateTime="2014-05-10 23:13:12",
                 lastDateTime='2014-3-10 22:14:10',
                 problemRemainder="remainder",
                 sequence='1',
                 type='error',
                 source='NETIC'):
        super().__init__(api_version)
        self.json_data = {'errorNumber': errorNumber,
                          'problemMessage': problemMessage,
                          'logName': logName,
                          'problemNumber': problemNumber,
                          'dateTime': dateTime,
                          'lastDateTime': lastDateTime,
                          'problemRemainder': problemRemainder,
                          'sequence': sequence,
                          'type': type,
                          'source': source}
        logging.debug('JSON data for heartbeat event is: {}'.format(self.json_data))

    def get_event_json(self):
        return self.json_data
