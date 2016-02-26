__author__ = 'richardkaye'
from framework.framework_object_rest import framework_object
from framework.constants import *
from framework.http_rest import rest_request
import logging
import logging.config

class Player_Health(framework_object):
    '''
    Class that encapsulates methods testing /api/rest/playerhealth API
    '''

    def list_player_health(self, session, baseurl,limit = 10, offset = 0 , sort = None, search = None, filters = None, fields = None):
        '''
        Wrapper around the GET /api/rest/playerhealth.  Uses the super class list_objects method
        :param session:
        :param baseurl:
        :param limit:
        :param offset:
        :param sort:
        :param search:
        :param filters:
        :param fields:
        :return:
        '''
        list_player_health_apiurl = '/api/rest/playerhealth'
        return self.list_objects(session = session,
                                 baseurl=baseurl,
                                 apiurl=list_player_health_apiurl,
                                 limit = limit,
                                 offset = offset,
                                 sort = sort,
                                 search = search,
                                 filters = filters,
                                 fields = fields)


    def list_problems(self,session, baseurl, limit = 10, offset = 0, sort = None, search = None, filters = None, fields = None):
        '''
        Wrapper around /api/rest/playerhealth/problems
        Uses super class list_objects method
        :return:
        '''

        list_problems_apiurl = '/aip/rest/playerhealth/problems'

        return self.list_objects(session = session,
                                 baseurl = baseurl,
                                 apiurl = list_problems_apiurl,
                                 limit = limit,
                                 offset = offset,
                                 sort = sort,
                                 filters = filters,
                                 fields = fields
                                 )

    def list_ignored_problems(self,session, baseurl, limit = 10, offset = 0, sort = None, search = None, filters = None, fields = None):
        '''
        Wrapper around /api/rest/playerhealth/ignoreproblems
        Uses super class list_objects method
        :return:
        '''

        list_problems_apiurl = '/aip/rest/playerhealth/ignoreproblems'

        return self.list_objects(session = session,
                                 baseurl = baseurl,
                                 apiurl = list_problems_apiurl,
                                 limit = limit,
                                 offset = offset,
                                 sort = sort,
                                 filters = filters,
                                 fields = fields
                                 )

    def clear_all_problems(self, session, baseurl):
        """
        Wrapper around DELETE /api/rest/playerhealth/clearProblems
        :param session: Authenticated session object on CM
        :param baseurl: Base URL of CM under test
        :return: True if response code is 200.  False otherwise.  Updates self.last_response
        """

        clear_all_problems_apiurl = '/api/rest/playerhealth/clearProblems'
        self.last_response = rest_request(session = session,
                                          baseurl = baseurl,
                                          apiurl = clear_all_problems_apiurl,
                                          type_of_call = call_type.delete)
        logging.debug('Made call to DELETE {}.  Response code = {}. Response = {}'.format(clear_all_problems_apiurl,
                                                                                          self.last_response.status_code,
                                                                                          self.last_response.text))

        if self.last_response.status_code == 200:
            return True
        else:
            return False

    def clear_problem(self, session, baseurl, uuid):
        """
        Wrapper around DELETE /api/rest/playerhealth/clearProblems/{uuid}
        :param session: Authenticated session object on CM
        :param baseurl: Base URL of CM under test
        :return: True if response code is 200.  False otherwise.  Updates self.last_response
        """

        clear_all_problems_apiurl = '/api/rest/playerhealth/clearProblems/' + str(uuid)
        self.last_response = rest_request(session = session,
                                          baseurl = baseurl,
                                          apiurl = clear_all_problems_apiurl,
                                          type_of_call = call_type.delete)
        logging.debug('Made call to DELETE {}.  Response code = {}. Response = {}'.format(clear_all_problems_apiurl,
                                                                                          self.last_response.status_code,
                                                                                          self.last_response.text))

        if self.last_response.status_code == 200:
            return True
        else:
            return False

    def clear_problems_by_problem_number(self, session, baseurl, uuid):
        """
        Wrapper around DELETE /api/rest/playerhealth/clearProblemsByProblemNumber/{uuid}
        :param session: Authenticated session object on CM
        :param baseurl: Base URL of CM under test
        :return: True if response code is 200.  False otherwise.  Updates self.last_response
        """

        clear_all_problems_apiurl = '/api/rest/playerhealth/clearProblemsByProblemNumber/' + str(uuid)
        self.last_response = rest_request(session = session,
                                          baseurl = baseurl,
                                          apiurl = clear_all_problems_apiurl,
                                          type_of_call = call_type.delete)
        logging.debug('Made call to DELETE {}.  Response code = {}. Response = {}'.format(clear_all_problems_apiurl,
                                                                                          self.last_response.status_code,
                                                                                          self.last_response.text))

        if self.last_response.status_code == 200:
            return True
        else:
            return False

    def update_player_health_settings(self, session, baseurl, identifier, key_dict):
        """
        Wrapper around PUT /api/rest/playerhealth/settings/{id}
        :param session: Authenticated Session object
        :param baseurl: base url of CM under test
        :param identifier: ID - not clear what ID this is from API docs...
        :param key_dict: Dictionary containing the keys to update, and their associated value
        :return: True if response code is 200.  False otherwise.  Updates last_response
        """

        # Todo - Find out what the ID parameter is supposed to be and rename it appropriately

        update_player_health_settings_apiurl = '/api/rest/playerhealth/settings/' + str(identifier)

        return self.update_single_object(session = session,
                                         baseurl = baseurl,
                                         apiurl = update_player_health_settings_apiurl,
                                         object_id=identifier,
                                         field_change_dict=key_dict)

