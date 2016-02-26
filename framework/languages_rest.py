__author__ = 'rkaye'

from framework.framework_object_rest import framework_object
from framework.http_rest import rest_request
from framework.constants import *
import logging
import logging.config

class Languages(framework_object):
    def __init__(self, api_version):
        super().__init__(api_version)

    def find_language_by_id(self, session, baseurl, id, fields = None):
        '''
        Implements the find language by ID api call  located at GET /api/rest/languages/{id}

         Updates last response
        :param session: The session object logged in for this test
        :param baseurl:  Base url of the CM under test.  i.e. 'http://192.168.10.135:8080/ContentManager
        :param id: id of Media object to find
        :param fields: Comma separated list of fields that should be reuturned in the response
        :return: True if status code in response is 200, False otherwise
        '''

        find_language_apiurl = '/api/rest/languages/' + str(id)

        query_parameters = {}

        if fields !=None:
            query_parameters['fields'] = fields

        return self.find_object_by_id(session, baseurl, find_language_apiurl, object_id=id)

    def list_languages(self,session,baseurl, limit = 10, offset = 0, sort = 'name', filters = None, fields = None, search = None):
        '''
        Implements list language api call located at GET /api/rest/languages

        Updates last response
        :param session: The session object logged in for this test
        :param baseurl:  Base url of the CM under test.  i.e. 'http://192.168.10.135:8080/ContentManager
        :param limit: Max number of languages in the return
        :param offset: Page offeset into total number of assets
        :param sort: sort by field name
        :param filters: filters to be applied to the return values
        :param fields: comma separated list of fields to be returned in the response
        :param search: search term compared to names of languages to retur
        :return: True if status code is 200, False otherwise
        '''

        list_languages_apiurl = '/api/rest/languages'

        return self.list_objects(session = session,
                                 baseurl = baseurl,
                                 apiurl = list_languages_apiurl,
                                 limit = limit,
                                 offset = offset,
                                 sort = sort,
                                 filters = filters,
                                 fields = fields,
                                 search = search)

    def find_language_by_iso_code(self,session, baseurl, isocode, fields = None):
        '''
        Implements find language by ISO code located at:
        GET /api/rest/languages/isocode/{isocode}

        Updates last response
        :param session: The session object logged in for this test
        :param baseurl: Base url of the CM under test.  i.e. 'http://192.168.10.135:8080/ContentManager
        :param isocode: ISO 639-1 language code to search for
        :param fields: comma separated list of fields to
        :return: True if status code is 200, False otherwise
        '''

        find_by_iso_apiurl = '/api/rest/languages/isocode/' + str(isocode)

        query_fields = {}

        if fields !=None:
            query_fields['fields'] = fields

        self.last_response = rest_request(session = session,
                                          baseurl = baseurl,
                                          apiurl = find_by_iso_apiurl,
                                          type_of_call = call_type.get,
                                          query_params= query_fields
                                          )

        logging.debug ('Made call to GET {}.  Response code = {}.  Response = {}'.format(find_by_iso_apiurl,
                                                                                         self.last_response.status_code,
                                                                                         self.last_response.text))
        if self.last_response.status_code == 200:
            return True
        else:
            return False