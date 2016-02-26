__author__ = 'rkaye'

import sys, json
from getpass import getpass
import requests
import logging
import logging.config
import configparser
from framework.constants import *
from framework.authentication_rest import *
from framework.http_rest import *
from framework.framework_object_rest import framework_object


class File_upload(framework_object):
    def __init__(self,api_version):
        super().__init__(api_version)
        '''
        self.user_data contains the json parameter needed to add this object
        to the CM.
        '''
        self.json_data = {}
        self.file_to_upload = None

    def add_attribute(self,session, attribute):
        '''
        Adds the list of key value pairs specified in attribute to the media_metadata_datp_data dictionary
        for this instance.  Attributes can be added one at a time or in a list
        :param session:  The session used to communicate with the CM for validating object ID's and names
        :param attribute: A list of dictionaries containing the attributes to add.  e.g. [{'name':'foo'},...].
        :return: True if successful.  False otherwise.

        Each key value pair is a single attribute where key is the name of the field and value is the value to be
        entered.  All key value pairs should be run through validate_attribute to make sure that they are valid
        for this data type.

        The format of the attribute field is very important and should be as follows:

        attribute = [{'<field 1>':'<value1>'},{'<field2>':'<value2>'},...{'<field n>':'<value n>'}]
        '''

        # Validate all of the keys in the key value pairs in attribute
        for key_value_pair in attribute:
            if not self.validate_attribute(key_value_pair):
                return False

                # Handle any special attributes here

        if attribute is not None:
            for key_value_pair in attribute:
                self.json_data.update(key_value_pair)
        else:
            return False

        logging.debug('user data is now: ' + json.dumps(self.file_to_upload))
        return True

    def validate_attribute(self,attribute):
        '''
        Validates the dictionary in attribute contains a single valid key value
        pair that can be added to the user data record.  Autheticates keys based on
        Enum in framework.constants
        '''
        valid = [name for name, member in valid_file_upload_attributes.__members__.items()]
        logging.debug('valid keys are:' + str(valid))
        logging.debug('attribute keys are:' + str([key for key in attribute]))
        for key in attribute:
            if key in valid:
                print(True)
            else:
                logging.warning('invalid user attribute: ' + key)
                return False
        return True


    def add_file(self,file_like_object):
        self.file_to_upload = file_like_object

    def handle_imagefilename(self):
        pass

    def initiate_upload(self,session, baseurl, local_file_name, file_upload_path):
        '''
        Wrapper around initiate file upload API at endpoint:
        /api/rest/fileupload/init
        :return: True if status code is 200 and UUID could be retrieved from message. False otherwise
        '''

            # Build JSON parameters for file upload in
        file_upload_parameter_list = {'filename':local_file_name,'filepath':file_upload_path,'uploadType':'media_item'}

        # Begin Media upload.   Start with Init call
        self.last_response = rest_request(session, call_type.post, baseurl=baseurl, apiurl='/api/rest/fileupload/init',
                            query_params = None, payload_params= file_upload_parameter_list,  proxy=False)
        logging.info('Response from init call is: status_code =  {}, response = {}'.format(self.last_response.status_code,self.last_response.text))
        if self.last_response.status_code == 200:
            try:
                logging.debug('UUID from Init call is: {}'.format(self.last_response.json()['uuid']))
                logging.debug('filename from Init call is: {}'.format(self.last_response.json()['filename']))
                return True
            except KeyError:
                logging.debug('Failed to find UUID or file name in response from CM for file upload init. {}'.format(self.last_response.text))
                return False
        else:
            logging.debug('Received incorrect response code after Media file upload init call.  Expected 200, got {}'.format(self.last_response.status_code))
            return False



    def upload_file_part(self,session, baseurl,local_file_name, local_file_path, uuid ):
        '''
        Post a file like object using the UUID of the file upload
        :param session: session object for this sesion
        :param baseurl: baseurl for CM
        :param local_file_name: filename to upload
        :param local_file_path: path to file for upload terminated in a /
        :param uuid: UUID of file upload
        :return:True if file upload is completed (status code is 204) False otherwise
        '''
        # Prep the arguments for the put call
        file = open(local_file_path + local_file_name,'rb')
        file_upload_put_apiurl = '/api/rest/fileupload/part/'+str(uuid)+ '/0'

        #Send the put request to upload the file
        self.last_response = rest_request(session,call_type.put,baseurl = baseurl, apiurl=file_upload_put_apiurl, file_object = file)
        logging.info('Response from file put call is: status_code =  {}, response = {}'.format(self.last_response.status_code,self.last_response.text))
        file.close()
        if self.last_response.status_code == 204:
            logging.info('Successful file upload.  Prepare to commit')
            return True
        else:
            logging.info('Received incorrect response code after file put call on media upload')
            return False



    def upload_finished(self, session, baseurl, uuid, silent = False):
        '''
        Wrapper around Upload Finished at /api/rest/fileupload/complete/{uploadId}
        :return: True if status code = 204, False otherwise
        '''
        # Commit the change
        commit_apiurl = '/api/rest/fileupload/complete/' + str(uuid)
        commit_param = None

        if silent == True:
            commit_param = {str(uuid): {'silent': True}}

        self.last_response  = rest_request(session,call_type.post, baseurl = baseurl, apiurl=commit_apiurl, payload_params= commit_param)
        logging.info('Response  from file complete call is: status_code =  {}, response = {}'.format(self.last_response.status_code,self.last_response.text))
        if self.last_response.status_code == 204:
            logging.info('Correct status code for complete upload received')
            return True
        else:
            logging.info('Incorrect status code for complete upload received')
            return False


if __name__=='__main__':
    configuration = configparser.ConfigParser()
    configuration.read(CONFIG_FILE_PATH)
    baseurl = configuration['login']['baseurl']
    username = configuration['login']['username']
    password = configuration['login']['password']
    logging.config.fileConfig("config/log_config")
    logging.debug('Read from config file and ready to begin.')
    s = login(username, password, baseurl, 0)
    file = open('media/01.jpg','rb')

    print('testing first media upload')

#    params = {'filename':'01.jpg','filepath':'','uploadType':'media_item'}
    params = {'filename':'01.jpg','uploadType':'media_item'}
    resp = rest_request(s, call_type.post, baseurl=baseurl, apiurl='/api/rest/fileupload/init', query_params = None, payload_params=params,  proxy=False)
    print (resp.text)

    json_response = json.loads(resp.text)

    print ('uuid = {}'.format(json_response['uuid']))

    headers =  {}#{'Content-Disposition': 'attachment; filename="01.jpg"','Accept-Language':'en-US;q=0.5','X-Requested-With':'XMLHttpRequest'}
    url = baseurl + '/api/rest/fileupload/part/'+json_response['uuid'] + '/0'
    print ('url is: {}'.format(url))
    resp = s.put(url,data = file,headers = headers)
    print (resp.text)
    url = baseurl + '/api/rest/fileupload/complete/' + json_response['uuid']
    resp = s.post(url)
    file.close()

    print('testing second media upload')

    file2 = open('media/The_Sandman_008.jpg','rb')
    params = {'filename':'The_Sandman_009.jpg','filepath':'','uploadType':'media_item'}
    resp = rest_request(s, call_type.post, baseurl=baseurl, apiurl='/api/rest/fileupload/init', query_params = None, payload_params=params,  proxy=False)
    json_response = json.loads(resp.text)
    print (resp.text)

    headers = {}#{'Content-Disposition': 'attachment; filename="The-Sandman-008.jpg"','Accept-Language':'en-US;q=0.5','X-Requested-With':'XMLHttpRequest'}

    apiurl =  '/api/rest/fileupload/part/'+json_response['uuid'] + '/0'
    resp = rest_request(s, call_type.put, baseurl = baseurl, apiurl = apiurl, query_params = None, file_object = file2,headers = headers, proxy = False)
    print ('response from second added media object is: {}'.format(resp.status_code))
    url = baseurl + '/api/rest/fileupload/complete/' + json_response['uuid']
    resp = s.post(url)

    print('testing third media upload - very large TIFF file')

    file3 = open('media/hs-2006-10-a-full_tif.tif','rb')
    params = {'filename':'hs-2006-10-a-full_tif.tif','filepath':'','uploadType':'media_item'}
    resp = rest_request(s, call_type.post, baseurl=baseurl, apiurl='/api/rest/fileupload/init', query_params = None, payload_params=params,  proxy=False)
    json_response = json.loads(resp.text)
    print (resp.text)

    headers = {}# {'Content-Disposition': 'attachment; filename="hs-2006-10-a-full_tif.tif"','Accept-Language':'en-US;q=0.5','X-Requested-With':'XMLHttpRequest'}

    apiurl =  '/api/rest/fileupload/part/'+json_response['uuid'] + '/0'
    resp = rest_request(s, call_type.put, baseurl = baseurl, apiurl = apiurl, query_params = None, file_object = file3,headers = headers, proxy = False)
    print ('response from third added media object is: {}'.format(resp.status_code))
    url = baseurl + '/api/rest/fileupload/complete/' + json_response['uuid']
    print
    resp = s.post(url)