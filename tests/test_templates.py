__author__ = 'richardkaye'

from nose import with_setup
from nose.tools import nottest
import logging
import logging.config
import configparser
from framework.constants import CONFIG_FILE_PATH, LOG_FILE_PATH
from framework.authentication_rest import login, logout, get_auth_token
from framework.http_rest import *
from framework.player_rest import Player
from framework.fileupload_rest import File_upload
from framework.templates_rest import Templates
from framework.media_rest import Media
from framework.message_rest import Message
import datetime

import inspect

print(CONFIG_FILE_PATH)
config = configparser.ConfigParser()
config.read(CONFIG_FILE_PATH)
baseurl = config['login']['baseurl']
logging.config.fileConfig(LOG_FILE_PATH)
logging.debug('Logging config file path is: {}'.format(CONFIG_FILE_PATH))
session = requests.Session()
namespace = config['test']['namespace']
api_version = config['api_info']['api_version']
api_version_templates = config['api_info']['api_version_templates']
api_version_fileupload = config['api_info']['api_version_fileupload']
api_version_media = config['api_info']['api_version_media']
api_version_messages = config['api_info']['api_version_messages']
template_id = 0
media_id = 0


def this_function_name():
    return inspect.stack()[1][3]


def t_setup():
    '''
    In order to test this case, new templates must be created and the session must be logged in.
    '''

    # Begin by initiating a new login session for this test case.
    global config, session, media_id, baseurl, namespace, player_id, api_version,template_id
    logging.info('Beginning test setup')
    baseurl = config['login']['baseurl']
    username = config['login']['username']
    password = config['login']['password']
    logging.debug('Read login info from config file and ready to begin.')
    logging.info('Initializing session for next test case.')
    media_path = config['path']['media']
    # INITIALIZE SESSION OBJECT
    session = login(username, password, baseurl)
    assert session is not None

    template_id = None
    player_id = None
    cur_datetime = datetime.datetime.now()
    #path = namespace + "test_templates" + cur_datetime.strftime("%Y%m%d_T%H%M%S")
    path = namespace
    # Create a template for use in this test suite

    # Init upload
    file_up = File_upload(api_version_fileupload)
    file_up.initiate_upload(session, baseurl=baseurl, local_file_name=config['template_items']['templatefile_3'],
                               file_upload_path=path)

    # Upload File
    uuid = file_up.get_response_key('uuid')
    template_id = file_up.get_response_key('mediaId')
    file_up.upload_file_part(session, baseurl=baseurl, local_file_name=config['template_items']['templatefile_3'],
                                local_file_path=config['path']['templates'], uuid=uuid)

    # Commit Upload
    file_up.upload_finished(session, baseurl=baseurl, uuid=uuid)

    # Wait for template to upload and thumbnail to generate before moving on


    # Create Media object for use in this test suite

    # Init Upload
    file_up2 = File_upload(api_version_fileupload)
    file_up2.initiate_upload(session, baseurl = baseurl, local_file_name = config['media_items']['mediafile_1'],
                            file_upload_path = path)

    # Upload file
    media_uuid = file_up2.get_response_key('uuid')
    media_id = file_up2.get_response_key('mediaId')
    logging.debug('About to upload media using uuid = {}, and mediaID = {}'.format(media_uuid, media_id))
    file_up2.upload_file_part(session, baseurl = baseurl, local_file_name=config['media_items']['mediafile_1'],
                              local_file_path=config['path']['media'], uuid=media_uuid)

    # Commit Upload
    file_up2.upload_finished(session, baseurl = baseurl, uuid = media_uuid, silent = True)

    # Verify that thumbnail is completed before moving on.  Wait 20 seconds
    media_object = Media(api_version_media)
    media_object.wait_for_media_upload(session = session,
                                       baseurl = baseurl,
                                       max_wait_seconds = 20,
                                       media_id = media_id)

    # Create a Message with the newly created template and Media item
    test_message = Message(api_version_messages)
    test_message_fields = [{'name':'photo','value':media_id},{'name':'caption','value':namespace + ' Booga booga booga'}]
    message_create_response = test_message.create_message(session, baseurl = baseurl, name = namespace + '_Test Message',
                                                          template_id = template_id,description = namespace + ' Test Description',
                                                          fields = test_message_fields)


def t_teardown():
    '''
    The templates created in the setup must be deleted, and the session logged off.
    :return:
    '''
    global session, player_id, api_version_templates,template_id, api_version_media, media_id

    # Delete the templates used in this test case
    template = Templates(api_version_templates)
    template.delete_template_by_id(session, baseurl = baseurl, id = template_id)

    media = Media(api_version_media)
    media.delete_media_by_id(session,baseurl = baseurl, id =media_id)

    assert logout(session, config['login']['baseurl']), 'Failed to Log out of server at end of test case'


@with_setup(t_setup, t_teardown)
def test_find_template_by_id():
    global session, baseurl, template_id, api_version_templates
    test_template = Templates(api_version_templates)

    assert test_template.find_tempalte_by_id(session, baseurl = baseurl, id = template_id)
    assert 'name' in test_template.last_response.json()

@with_setup(t_setup,t_teardown)
def delete_template_media_api():
    '''
    Verifies that the Delete /api/rest/media/(id) API can be used to delete a template
    Note:  The Delete /api/rest/templates/(id) API is deprecated

    Note 2: This test case does not depend on the t_teardown to delete the template it creates.
     If the add fails, then the delete will not go through.  The result will
    :return:
    '''
    global api_version_templates, session, baseurl,namespace, api_version_media

    global session, baseurl, template_id, api_version

    # Create a new template for this testcase.
    file_up = File_upload(api_version_fileupload)
    file_up.initiate_upload(session, baseurl=baseurl, local_file_name=config['template_items']['templatefile_3'],
                               file_upload_path=namespace + this_function_name())
    uuid = file_up.get_response_key('uuid')
    this_test_template_id = file_up.get_response_key('mediaId')
    file_up.upload_file_part(session, baseurl=baseurl,
                             local_file_name=config['template_items']['templatefile_3'],
                             local_file_path=config['path']['templates'], uuid=uuid)
    file_up.upload_finished(session, baseurl = baseurl, uuid = uuid)

    # Create a new Message using the template generated for this test case

    test_message = Message(api_version_messages)

    media = Media(api_version_media)

    # Note:  The delete templates api is depricated,
    assert media.delete_media_by_id(session, baseurl = baseurl, id = this_test_template_id),'Failed to delete template using DELETE /api/rest/media/{}'.format(this_test_template_id)

    # Since this test case has already deleted the template it created...... No more work need be done to clean up.

@nottest
@with_setup(t_setup,t_teardown)
def test_endpoint_template_faceted_search():
    pass

@with_setup(t_setup, t_teardown)
def test_endpoint_find_template_by_id():
    global api_version, session, baseurl, namespace, template_id
    test_template = Templates(api_version_templates)

    assert(test_template.find_tempalte_by_id(session, baseurl=baseurl,id=template_id)), 'Could not find template {} by id'.format(template_id)

@nottest
@with_setup(t_setup,t_teardown)
def test_endpoint_template_generate_thumbnail():
    pass

@nottest
@with_setup(t_setup,t_teardown)
def test_endpoint_get_thumbnail_status():
    pass

@with_setup(t_setup, t_teardown)
def test_endpoint_list_templates_in_use():
    global api_version_templates,session,baseurl,namespace,template_id
    test_template = Templates(api_version_templates)

    # Perform the list and validate the response return code is correct
    assert(test_template.list_templates_in_use(session, baseurl = baseurl))
    assert test_template.get_response_key('count') >= 1, 'Found zero templates in use even though setup creates one.'

@nottest
@with_setup(t_setup,t_teardown)
def test_template_upload():
    '''
    This is a test to make sure that all of the templates in the 'templates' directory can be added to the CM
    It is not intended for these tests to run against the build.  This test is only for testing the tests.
    :return:
    '''
    global api_version_templates, session, baseurl, namespace, template_id
    test_template_id_list = []

    # Create the template files
    for template_file_number in [1,3,4,5]:
        file_up = File_upload(api_version_fileupload)
        assert file_up.initiate_upload(session, baseurl=baseurl, local_file_name=config['template_items']['templatefile_' + str(template_file_number)],
                                   file_upload_path=namespace + this_function_name()), 'Failed to initiate session for upload'
        uuid = file_up.get_response_key('uuid')
        test_template_id_list.append(file_up.get_response_key('mediaId'))
        assert file_up.upload_file_part(session, baseurl=baseurl,
                                 local_file_name=config['template_items']['templatefile_' + str(template_file_number)],
                                 local_file_path=config['path']['templates'], uuid=uuid), 'failed to upload file part'
        assert file_up.upload_finished(session, baseurl = baseurl, uuid = uuid), 'Failed to commit changed template file'

    logging.debug('List of template IDs is: {}'.format(test_template_id_list))


@with_setup(t_setup, t_teardown)
def test_endpoint_list_templates():
    global api_version_templates, session, baseurl, namespace, template_id
    test_template = Templates(api_version_templates)

    # Perf
    # orm the list and validate that the return code is correct
    assert(test_template.list_templates(session, baseurl = baseurl))
