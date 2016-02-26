__author__ = 'rkaye'
from framework.http_rest import rest_request
from framework.fileupload_rest import File_upload
import logging
import logging.config
from framework.constants import *
import requests
'''
A module containing utility functions used by tests.  These functions are vetted, and not stored within the
module for a given data type - usually because they use more than one API to accomplish a common task.

All of the methods in this module should throw
'''

class UnexpecteStatusCodeError(Exception):
    def __init__(self, expected_response_code, actual_response_code, apiurl):
        self.message = 'Unexpected status code on call to {}. Expected {} and got {}'.format(apiurl,expected_response_code,actual_response_code)


class Media_utilities:
    '''
    Class which contains media related utility methods and data structures.
    '''

    def __init__(self, session, baseurl):
        self.session = session
        self.baseurl = baseurl


    def upload_media_file(self,local_file_path, local_file_name, file_upload_path, uploadType=uploadType.media_item):
        '''
        Upload the file indicated by local_file_name to the directory on the CM specified by file_upload_path.
        The file is presumed to have an 'uploadType' of 'media'
        '''
        # Build JSON parameters for file upload in
        file_upload_parameter_list = {'filename':local_file_name,'filepath':file_upload_path,'uploadType':uploadType.name}
        file_upload_init_apiurl = '/api/rest/fileupload/init'

        # Begin Media upload.   Start with Init call
        resp = rest_request(self.session, call_type.post, baseurl=self.baseurl, apiurl=file_upload_init_apiurl,
                            query_params = None, payload_params= file_upload_parameter_list,  proxy=False)
        logging.info('Response code from init call is: {}'.format(resp.status_code))
        if resp.status_code != 200:
            logging.error('Received incorrect response code after Media file upload init call.  Expected 200 got {}'.format())
            raise UnexpecteStatusCodeError(200,resp.status_code,file_upload_init_apiurl)

        # Save off the json response to pluck the uuid out of it
        json_init_response = resp.json()
        logging.debug('UUID from Init call is: {}'.format(json_init_response['uuid']))
        logging.debug('filename from Init call is: {}'.format(json_init_response['filename']))

        # Prep the arguments for the put call
        file = open(local_file_path + local_file_name,'rb')
        file_upload_put_apiurl = '/api/rest/fileupload/part/'+json_init_response['uuid'] + '/0'

        #Send the put request to upload the file
        resp = rest_request(self.session,call_type.put,baseurl = self.baseurl, apiurl=file_upload_put_apiurl, file_object = file)
        logging.info('Response from file put call is: status code = {}, resp = {}'.format(resp.status_code, resp.text))
        file.close()
        if resp.status_code != 204:
            logging.error('Received incorrect response code after file put call on media upload. Expected 204, got {}'.format(resp.status_code))
            raise UnexpecteStatusCodeError(204,resp.status_code, file_upload_put_apiurl)

        # Commit the change
        commit_apiurl = '/api/rest/fileupload/complete/' + json_init_response['uuid']
        resp = rest_request(self.session,call_type.post, baseurl = self.baseurl, apiurl=commit_apiurl)
        logging.info('Response from file complete call is: status code = {}, response = {}'.format(resp.status_code,resp.text))
        if resp.status_code != 204:
            logging.error('Received incorrect response code after file commit call on media upload. Expected 204, got {}'.format(resp.status_code))
            raise UnexpecteStatusCodeError(204,resp.status_code, commit_apiurl)