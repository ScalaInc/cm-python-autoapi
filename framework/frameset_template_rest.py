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

class Frameset_template(framework_object):
    """
    Helper class that builds a Frameset Template json object for use in API testing.
    Class methods 'help' programmers by validating data before it can be
    placed into the main data object for the instance.
    """

    def __init__(self, api_version):
        super().__init__(api_version)

    def list_all_available_frameset_templates(self,session,baseurl,limit = 10, offset = 0, sort = 'name',filters = None, fields = None, search = None):
        list_framesets_apiurl = '/api/rest/framesetTemplates'

        # Every fricken object has a list api call.  Put it in the framework super class so I don't have to write it again and again.
        # in cases where it must be overridden it can be.
        return self.list_objects(session, baseurl= baseurl, apiurl = list_framesets_apiurl, limit = limit, offset = offset, sort = sort, filters = filters, fields = fields, search = search)

    def create_frameset_template(self, session, baseurl, name, list_of_frames, width, height):
        """
        Create a new frameset template using POST /api/rest/framesetTemplates.  Note: the list of frames takes the form:

            [
            {
            "id": 91,
            "name": "Main",
            "color": "#ccccff",
            "left": 0,
            "top": 0,
            "width": 1080,
            "height": 1740,
            "zOrder": 2,
            "autoscale": "FILL_EXACTLY",
            "hidden": False
            },
            {
            "id": 92,
            "name": "Bottom",
            "color": "#99ccff",
            "left": 0,
            "top": 1740,
            "width": 1080,
            "height": 180,
            "zOrder": 1,
            "autoscale": "FILL_EXACTLY",
            "hidden": False
            }]
        :param session: Authenticated session object
        :param baseurl: Base URL of the CM under test
        :param name: Name of fraemeset template to create
        :param list_of_frames: List of frames of the form shown above.
        :param width: width of the frameset
        :param height: height of the frameset
        :return:
        """

        create_frameset_apiurl = '/api/rest/framesetTemplates'
        create_frameset_parameter = {'name': name,
                                     'frames': list_of_frames,
                                     'width': width,
                                     'height': height}

        self.last_response = rest_request(session=session,
                                          baseurl=baseurl,
                                          apiurl=create_frameset_apiurl,
                                          type_of_call=call_type.post,
                                          payload_params=create_frameset_parameter)
        logging.debug(
            'Sent call to POST {}.  HTTP response code = {}.  JSON response = {}'.format(create_frameset_apiurl,
                                                                                         self.last_response.status_code,
                                                                                         self.last_response.text))
        if self.last_response.status_code == 200:
            return True
        else:
            return False

    def delete_frameset_template_by_id(self, session, baseurl, frameset_id):
        """
        Wrapper around DELETE /api/rest/framesetTemplates/{id}
        :param session: Authenticated session object
        :param baseurl: Baseurl of CM under test
        :param frameset_id: ID of frameset to delete
        :return:True if response code is 204.  False otherwise.  Updates self.last_response
        """
        delete_frameset_apiurl = '/api/rest/framesetTemplates/' + str(frameset_id)
        return self.delete_object_by_id(session=session,
                                        baseurl=baseurl,
                                        apiurl=delete_frameset_apiurl,
                                        object_id=frameset_id)

    def update_frameset_template(self, session, baseurl, frameset_id, field_change_dict):
        """
        Wrapper around PUT /api/rest/framesetTemplates/{id}
        :param session: Authenticated Session object
        :param baseurl: Base URL for the CM under test
        :param frameset_id: frameset to update
        :param field_change_dict: Field change dict for the message
        :return:True if response code is 200.  False otherwise.  Updates self.last_response
        """
        update_frameset_template_apiurl = '/api/rest/framesetTemplates/' + str(frameset_id)
        return self.update_single_object(session = session,
                                         baseurl = baseurl,
                                         apiurl = update_frameset_template_apiurl,
                                         object_id = frameset_id,
                                         field_change_dict=field_change_dict)
