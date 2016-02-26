__author__ = 'rkaye'
from framework.framework_object_rest import framework_object
from framework.player_metadata_rest import Player_meta_data
from framework.constants import *
from framework.http_rest import rest_request
import logging
import json
import logging.config

class Reports(framework_object):
    '''
    Class that encapsulates all of the methods used in testing Reports API
    '''
    apiurl = '/api/rest/players'

    def __init__(self, api_version):
        '''
        Constructor initializes api version
        :return: VOID
        '''
        super().__init__(api_version)

    def create_report(self, session, baseurl, name, description, periodStart, periodEnd, templateFiliename):
        """
        Wrapper around POST /api/rest/reports
            channelAndFrameIds: [{frameId: 1, channelId: 1}, {frameId: 2, channelId: 1}]
            includeScalaScriptEvent: true
            language: 0
            mediaCategoryIds: []
            mediaItemIds: []
            mediaMetadataValues: []
            name: "Report (2015-01-23 13:46:37 GMT-0500)"
            ownerWorkgroupIds: []
            periodStart: "2015-01-15"
            periodStop: "2015-01-22"
            playerGroupIds: []
            playerIds: [1]
            playerMetadataValues: []
            templateFilename: "PLAYER_DETAIL"
            viewWorkgroupIds: []
        :param session: Authenticated session on the CM
        :param baseurl: Baseurl of CM under test
        :param name: Name of report
        :param description: Description of report
        :param periodStart: Start period in YYYY-MM-DD format
        :param periodEnd: End period in YYYY-MM-DD format
        :param templateFiliename: Type of report enum
        :return: True if status_code == 200.  False otherwise.  Updates self.last_request
        """

        create_report_apiurl = '/api/rest/reports'
        create_report_param = {'name': name,
                               'description': description,
                               'periodStart': periodStart,
                               'periodEnd': periodEnd,
                               'templateFilename': templateFiliename

        }

        self.last_response = rest_request(session = session,
                                          baseurl = baseurl,
                                          apiurl = create_report_apiurl,
                                          type_of_call= call_type.post,
                                          payload_params=create_report_param)

        logging.debug('Made call to POST {}.  Response code = {}, Response = {}'.format(create_report_apiurl,
                                                                                        self.last_response.status_code,
                                                                                        self.last_response.text))

        if self.last_response.status_code == 200:
            return True
        else:
            return False




