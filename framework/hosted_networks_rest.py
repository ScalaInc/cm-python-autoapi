__author__ = 'rkaye'
from framework.framework_object_rest import framework_object
from framework.http_rest import rest_request
from framework.constants import call_type
import logging


class Hosted_Networks(framework_object):
    def __init__(self, api_version):
        super().__init__(api_version)

    def update_hosted_network(self, session, baseurl, network_id, description=None, active=None):

        update_hosted_network_apiurl = "/api/rest/hostednetworks/" + str(network_id)

        update_hosted_network_param = {}

        if description != None:
            update_hosted_network_param['description'] = description
        if active != None:
            update_hosted_network_param['active'] = active

        self.last_response = rest_request(session=session,
                                          baseurl=baseurl,
                                          type_of_call=call_type.put,
                                          apiurl=update_hosted_network_apiurl,
                                          payload_params=update_hosted_network_param
        )
        logging.debug('Sent call to PUT /api/rest/hostednetworks/(id).  Response code = {}, response = {}'.format(
            self.last_response.status_code, self.last_response.text))
        if self.last_response.status_code == 200:
            logging.info('Status for PUT {} was 200'.format(update_hosted_network_apiurl))
            return True
        else:
            logging.info('Status for PUT {} was {} - expected 200'.format(update_hosted_network_apiurl,
                                                                          self.last_response.status_code))
            return False

    def list_hosted_networks(self, session, baseurl, limit=10, offset=0, sort='name', filters=None, fields=None,
                             search=None):
        """
        Wrapper around GET /api/rest/hostednetworks
        :param session: Authenticated session object
        :param baseurl: Base url of CM under test
        :param limit: number of objects to reutrn in DTO
        :param offset: Offset used in paging through responses
        :param sort: Sort by field - string
        :param filters: Filters (if any) to apply to therequest
        :param fields: Comma separated list of fields to return
        :param search: String to serach on in the 'name' field of the hosted network
        :return: True if status code is 200.  False otherwise.  Updates self.last_response
        """
        list_hn_apiurl = '/api/rest/hostednetworks'

        return self.list_objects(session=session,
                                 baseurl=baseurl,
                                 apiurl=list_hn_apiurl,
                                 limit=limit,
                                 offset=offset,
                                 sort=sort,
                                 filters=filters,
                                 fields=fields,
                                 search=search)

    def delete_hosted_network_by_id(self, session, baseurl, network_id):
        """
        Wrapper around DELETE /api/rest/hostednetworks/{id}
        :param session: Authenticated session object
        :param baseurl: Baseurl for CM under test
        :param network_id: ID of network to delete
        :return: True if response is 200.  False otherwise.  Updates self.last_response
        """
        delete_nw_apiurl = '/api/rest/hostednetworks/' + str(network_id)
        return self.delete_object_by_id(session = session,
                                        baseurl = baseurl,
                                        apiurl = delete_nw_apiurl,
                                        object_id=network_id)