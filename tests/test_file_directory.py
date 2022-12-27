__author__ = 'rkaye'
from nose import with_setup
from nose.tools import nottest
import logging
import logging.config
from framework.file_directory_rest import FileDirectory
from framework.authentication_rest import login, logout
from framework.common_functions_rest import *
from framework.http_rest import *
import inspect
import time
import datetime
from framework.authentication_api_rest import Auth_api
from nose_parameterized import parameterized

print(CONFIG_FILE_PATH)
config = configparser.ConfigParser()
config.read(CONFIG_FILE_PATH)
baseurl = config['login']['baseurl']
logging.config.fileConfig(LOG_FILE_PATH)
logging.debug('Logging config file path is: {}'.format(CONFIG_FILE_PATH))
session = requests.Session()
category_id = 0
media_id_list = []
user_id_list = []
number_of_cases_run = 0
namespace = config['test']['namespace']

#
# def this_function_name():
#     return inspect.stack()[1][3]
#
# def upload_file(local_file_name, file_upload_path):
#     global session
#
#     # Build JSON parameters for file upload in
#     file_upload_parameter_list = [{'filename':local_file_name},{'filepath':file_upload_path},{'uploadType':'media_item'}]
#     fupl = File_upload()
#     fupl.add_attribute(session,file_upload_parameter_list)
#
#
#     # Begin Media upload.   Start with Init call
#     resp = rest_request(session, call_type.post, baseurl=config['login']['baseurl'], apiurl='/api/rest/fileupload/init',
#                         query_params = None, payload_params= fupl.json_data,  proxy=False)
#     logging.info('Response code from init call is: {}'.format(resp.status_code))
#     assert resp.status_code == 200, 'Received incorrect response code after Media file upload init call.'
#
#     # Save off the json response to pluck the uuid out of it
#     json_init_response = resp.json()
#     logging.debug('UUID from Init call is: {}'.format(json_init_response['uuid']))
#     logging.debug('filename from Init call is: {}'.format(json_init_response['filename']))
#
#     # Prep the arguments for the put call
#     file = open(config['path']['media'] + local_file_name,'rb')
#     file_upload_put_apiurl = '/api/rest/fileupload/part/'+json_init_response['uuid'] + '/0'
#
#     #Send the put request to upload the file
#     resp = rest_request(session,call_type.put,baseurl = config['login']['baseurl'], apiurl=file_upload_put_apiurl, file_object = file)
#     logging.info('Response code from file put call is: {}'.format(resp.status_code))
#     file.close()
#     assert resp.status_code == 204, 'Received incorrect response code after file put call on media upload'
#
#     # Commit the change
#     apiurl = '/api/rest/fileupload/complete/' + json_init_response['uuid']
#     resp = rest_request(session,call_type.post, baseurl = config['login']['baseurl'], apiurl=apiurl)
#     logging.info('Response code from file complete call is: {}'.format(resp.status_code))
#     assert resp.status_code == 204, 'Received incorrect response code after media upload complete call.'
#
# def t_setup():
#     '''
#     In order to test this case, a new user must be created and the session must be logged in as this new user.
#     That user must create a media and then approve it.
#     '''
#
#     # Begin by initiating a new login session for this test case.
#     global config, session, media_id_list, user_id_list, baseurl, number_of_cases_run, namespace
#     logging.info('Beginning test setup')
#     baseurl = config['login']['baseurl']
#     username = config['login']['username']
#     password = config['login']['password']
#     logging.debug('Read login info from config file and ready to begin.')
#     logging.info('Initilizing session for next test case.')
#     media_path = config['path']['media']
#     # INITIALIZE SESSION OBJECT
#     session = login(username, password, baseurl)
#     assert session is not None
#     media_id_list = []
#     user_id_list = []
#
#
# def t_teardown(upload_media=False):
#     '''
#     This method logs off from the CM.  It is intended to be run after each test case in this test suite.
#     Decorate each test case with:  **@with_setup(setup, teardown)**
#
#     if the upload_media flag is set to True, then the teardown module will attempt to delete the media objects created in
#     setup_t
#     '''
#     global session
#     logging.info('Beginning test teardown')
#     response = logout(session, config['login']['baseurl'])
#     assert response
#
# @with_setup(t_setup, t_teardown)
# def test_endpoint_create_directory():
#     '''
#     Use POST /api/rest/directory to create a directory - name utilizes date and time to assure uniqueness
#     Use upload file() to upload a file to the path created
#     Use GET /api/rest/directory/{path} to validate that the file arrived in the correct location
#     :return:
#     '''
#     global session, config, baseurl, namespace
#     # First - create a unique name for the directory using the number of seconds since 1970
#     current_time_since_epoch = time.time()
#     local_file_name = config['media_items']['mediafile_1']
#     base_directory = 'test_auto'
#     test_directory = namespace + '_' + this_function_name() + '_' + str(current_time_since_epoch)
#     directory_name = base_directory + '/' + test_directory
#     create_directory_parameters = {'path':directory_name}
#     create_directory_apiurl = '/api/rest/directory'
#
#     # Make the call to create the directory
#     resp = rest_request(session, type_of_call=call_type.post, baseurl = baseurl, apiurl=create_directory_apiurl, payload_params= create_directory_parameters )
#     logging.debug('Response from add directory post: status code = {}, response = {}'.format(resp.status_code, resp.text))
#     assert resp.status_code == 200, 'POST to create new directory with name {} returned unexpected status code.  Expected 200, received {}'.format(directory_name, resp.status_code)
#
#     # Upload a new media file to the newly created directory
# #    upload_file(local_file_name= local_file_name,file_upload_path=directory_name)
#     media_util = Media_utilities(session, baseurl)
#     media_util.upload_media_file(local_file_path = config['path']['media'],local_file_name=local_file_name,file_upload_path = directory_name)
#
#     # Use the GET /api/rest/directory/{PATH} call to pull back the directory listing and verify the file upload is there
#     list_directory_apiurl = '/api/rest/directory/' + base_directory
#     resp = rest_request(session, type_of_call=call_type.get, baseurl = baseurl, apiurl = list_directory_apiurl)
#     logging.debug('Response from list directory GET is: status code = {}, response = {}'.format(resp.status_code, resp.text))
#     found_test_directory = False
#     for directory in resp.json()['list']:
#         found_test_directory = True if directory['name'] == test_directory or found_test_directory is True else False
#         logging.debug('Have I found the test directory yet? {}'.format(found_test_directory))
#         logging.debug('Searching for directory: {}'.format(test_directory))
#         logging.debug('Currently searching: {}'.format(directory['name']))
#     assert found_test_directory, 'Did Not find test directory after adding it.'
#

api_version_authentication = config['api_info']['api_version_authentication']
api_version_media = config['api_info']['api_version_media']
api_version_fileupload = config['api_info']['api_version_fileupload']
api_version_file_directory = config['api_info']['api_version_file_directory']

class test_file_directory():
    @classmethod
    def setup_class(cls):
        pass

    @classmethod
    def teardown_class(cls):
        pass

    def setup(self):
        # Login to perform teardown
        logging.info('Beginning test setup')
        self.baseurl = config['login']['baseurl']
        self.username = config['login']['username']
        self.password = config['login']['password']
        self.api_auth_object = Auth_api(api_version_authentication)
        logging.debug('Read login info from config file and ready to begin.')
        logging.info('Initializing session for test module setup.')

        self.test_session = self.api_auth_object.login(self.username, self.password, self.baseurl)

        # Create instance variables used in cleaning up test
        self.media_id_list = []
        self.directory_path_list = []

        # cur_datetime = datetime.datetime.now()
        # path = namespace + "player_metadata_" + cur_datetime.strftime("%Y%m%d_T%H%M%S")
        # media_object = Media(api_version_media)
        # for media_item in [config['media_items']['mediafile_1'],config['media_items']['mediafile_2'],config['media_items']['mediafile_3']]:
        #     # Create a media item for use in this test suite
        #     file_up = File_upload(api_version_fileupload)
        #
        #     # Initiate Upload of media item
        #     file_up.initiate_upload(session = self.test_session,baseurl=self.baseurl, local_file_name= media_item, file_upload_path= path)
        #
        #     uuid = file_up.get_response_key('uuid')
        #     media_id = file_up.get_response_key('mediaId')
        #     self.media_id_list.append(media_id)
        #
        #     # Upload file part
        #     file_up.upload_file_part(session=self.test_session, baseurl=self.baseurl, local_file_name=media_item,
        #                              local_file_path=config['path']['media'], uuid=uuid)
        #
        #     # Commit Upload
        #     file_up.upload_finished(session=self.test_session, baseurl=self.baseurl, uuid=uuid)
        #
        #     # Wait for Thumbnail to be available.
        #     media_object.wait_for_media_upload(session = self.test_session,
        #                                        baseurl = self.baseurl,
        #                                        max_wait_seconds = 20,
        #                                        media_id = media_id)
        #
        # logging.debug('media_id_list is = {}'.format(self.media_id_list))

    def teardown(self):
        # Delete all of the directories in the deletion list
        file_directory_object = FileDirectory(api_version_file_directory)
        for directory_path in self.directory_path_list:
            assert file_directory_object.delete_directory(session=self.test_session,
                                                          baseurl=self.baseurl,
                                                          file_path=directory_path), 'Directory cleanup failed'
        # logout of session created for setup

        self.api_auth_object.logout()

    # def test_create_level_1_directory(self):
    #     """
    #     Endpoint test for POST /api/rest/directory.  This test creates a first level directory under the top level
    #     content directory.
    #     :return:
    #     """
    #     create_directory_path = 'fofofofo'
    #     file_directory_object = FileDirectory(api_version_file_directory)
    #
    #     assert file_directory_object.create_directory(session = self.test_session,
    #                                                   baseurl = self.baseurl,
    #                                                   file_path = create_directory_path), 'Create directory returned incorrect response code'
    #
    #     assert file_directory_object.list_content_directory(session = self.test_session,
    #                                                         baseurl = self.baseurl,
    #                                                         bar_file_path= "|"), 'List File directories did not return 200 status code'
    #
    #     found_directory = False
    #     for directory in file_directory_object.last_response.json()['list']:
    #         if directory['name'] == create_directory_path:
    #             found_directory=True
    #     assert found_directory,'Failed to find directory after creating it'
    #
    #     # Now append the directory to the cleanup list
    #     self.directory_path_list.append(create_directory_path)

    @parameterized([
        ('first/second/third'),
        ('first/second/third/fourth/fifth/sixth'),
        ('first/%%%'),
        ('---/abc')
    ])
    def test_create_directory(self, create_path):
        """
        Parameterized test which adds directories verifies they exist, and then adds them to the delete que
        :param create_path:
        :param list_path: The list directory api uses virtical bars to replace the '/' directory dividers to facilitate URL
        encoding.  This parametner should have a vertical bar separated list of directories, down to the n-1 directory
        (Don't include the last directory in the list).  For example
        :param top_level: The top level directory created by this test
        :return:
        """

        # Generate the strings I need for this test case:
        bottom_level_generated = create_path.split('/')[-1]
        top_level_generated = create_path.split('/')[0]
        list_path_generated = '|' + '|'.join(create_path.split('/')[0:-1])

        file_directory_object = FileDirectory(api_version_file_directory)

        assert file_directory_object.create_directory(session=self.test_session,
                                                      baseurl=self.baseurl,
                                                      file_path=create_path), 'Create directory returned incorrect response code'

        # Add the top level directory to the directory path list for cleanup during teardown
        self.directory_path_list.append(top_level_generated)

        assert file_directory_object.list_content_directory(session=self.test_session,
                                                            baseurl=self.baseurl,
                                                            bar_file_path=list_path_generated), 'List Directory did not return correct result'

        logging.debug('Response name is: {}'.format(file_directory_object.last_response.json()['list'][0]['name']))
        logging.debug('Final level of directory is: {}'.format(bottom_level_generated))

        assert file_directory_object.last_response.json()['list'][0]['name'] == bottom_level_generated, 'Did not find bottom level directory {} after createing {}'.format(bottom_level_generated, create_path)

    @parameterized([
        ('first/second/third'),
        ('first/second/third/fourth/fifth/sixth'),
        ('first/%%%'),
        ('---/abc')
    ])
    def test_delete_directory(self, directory_path):
        """
        Testing the delete functionality of the API
        :param directory_path: string containing the directory path of the directory to delete
        :return:
        """
        # Generate the strings I need for this test case:
        bottom_level_generated = directory_path.split('/')[-1]
        top_level_generated = directory_path.split('/')[0]
        list_path_generated = '|' + '|'.join(directory_path.split('/')[0:-1])

        file_directory_object = FileDirectory(api_version_file_directory)

        assert file_directory_object.create_directory(session=self.test_session,
                                                      baseurl=self.baseurl,
                                                      file_path=directory_path), 'Create directory returned incorrect response code'

        # Add the top level directory to the directory path list for cleanup during teardown
        self.directory_path_list.append(top_level_generated)

        assert file_directory_object.delete_directory(session = self.test_session,
                                                      baseurl = self.baseurl,
                                                      file_path = directory_path), 'Delete directory did not return correct response code'

        assert file_directory_object.list_content_directory(session=self.test_session,
                                                            baseurl = self.baseurl,
                                                            bar_file_path=list_path_generated)

        assert file_directory_object.last_response.json() == {}, 'Did not find empty dict after listing empty directory'

    @parameterized([
        ('')
    ])
    def test_list_directory(self, directory_path):
        """
        Testing the list directory API
        :param directory_path:
        :return:
        """

        # Generate the strings I need for this test case:
        bottom_level_generated = directory_path.split('/')[-1]
        top_level_generated = directory_path.split('/')[0]
        list_path_generated = '|' + '|'.join(directory_path.split('/')[0:-1])

        file_directory_object = FileDirectory(api_version_file_directory)
        assert file_directory_object.list_content_directory(session=self.test_session,
                                                            baseurl = self.baseurl,
                                                            bar_file_path=list_path_generated),'List directory did not return correct status code.'