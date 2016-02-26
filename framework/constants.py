from enum import Enum


""" ..py:module:: constants
Holds constant values (final's) and Enums usedby the system
"""

CONFIG_FILE_PATH = './config/testconfig'
PERF_LOG_FILE_PATH = './logs/perflogconfig'
PERF_TEST_RESULTS_FILE_PATH = './logs/perf_test_data.csv'
LOG_FILE_PATH = './config/log_config'
DEFAULT_API_VERSION = 1.0
PERF_YAML_CONFIG_FILE_PATH = './config/perf_test_info.yml'
DEFAULT_HTTP_TIMEOUT = 10


class call_type(Enum):
    '''
    Enum containing valid HTTP call types used by this system.  Currently the following are supported:

    +----------+------------+
    |   Call   |    Enum    |
    |          |    Value   |
    +==========+============+
    |  get     |      1     |
    +----------+------------+
    |  post    |      2     |
    +----------+------------+
    |  put     |      3     |
    +----------+------------+
    |  delete  |      4     |
    +----------+------------+
    '''

    get = 1
    post = 2
    put = 3
    delete = 4


class valid_user_attributes(Enum):
    '''
    Valid attributes for USER objects.  Used by the framework.user_rest module when validating input parameters.
    Only parameters in this list will be put into requests for 'user' objects.

    For example, if I have an attirbute:  {'booga':'<some data value''} it will be rejected by the add method in
    the user_rest module.  However, {'username':'<some data value>'} will be added to the API request to the
    CM when adding a user because 'username' is a member of this Enum
    '''

    username = 1
    password = 2
    firstname = 3
    lastname = 4
    emailaddress = 5
    confirmPassword = 6
    roles = 7

class valid_workgroup_attributes(Enum):
    '''
    Valid attributes for WORKGROUP objects.  Used by the framework.worktroup_rest module when validating input
    parameters.  Only the parameters in this list will be put into requests for 'workgroup' objects.

    For exmaple, if I have a key value pair: {'booga':'<some data value''} it will be rejected by the add method in
    the user_rest module.  However, {'name':'<some data value>'} will be added to the API request to the
    CM when adding a user because 'username' is a member of this Enum
    '''

    name = 1
    description = 2
    children = 3
    userCount = 4
    parentId = 5
    parentName = 6
    owner = 7

class valid_media_metadata_attributes(Enum):
    '''
    Valid attributes for MEDIA_METADATA objects.  Used by the framework.media_metadata_rest module when validating input
    parameters.  Only the parameters in this list will be put into requests for 'workgroup' objects.

    For exmaple, if I have a key value pair: {'booga':'<some data value''} it will be rejected by the add method in
    the user_rest module.  However, {'name':'<some data value>'} will be added to the API request to the
    CM when adding a user because 'username' is a member of this Enum
    '''

    name = 1
    datatype = 2
    valueType = 3
    order = 4
    predefinedValues = 5

class valid_media_category_attributes(Enum):
    '''Valid attributes for MEDIA_Catagory objects.  Used by the framework.media_catagory_rest module when validating input
    parameters.  Only the parameters in this list will be put into requests for 'workgroup' objects.

    For exmaple, if I have a key value pair: {'booga':'<some data value''} it will be rejected by the add method in
    the user_rest module.  However, {'name':'<some data value>'} will be added to the API request to the
    CM when adding a user because 'username' is a member of this Enum
    '''

    name = 1
    description = 2
    parentId = 3
    children = 4

class valid_file_upload_attributes(Enum):
    '''Valid attributes for MEDIA_Catagory objects.  Used by the framework.media_catagory_rest module when validating input
    parameters.  Only the parameters in this list will be put into requests for 'workgroup' objects.

    For exmaple, if I have a key value pair: {'booga':'<some data value''} it will be rejected by the add method in
    the user_rest module.  However, {'name':'<some data value>'} will be added to the API request to the
    CM when adding a user because 'username' is a member of this Enum
    '''

    filename = 1
    filepath = 2
    uploadType = 3

class valid_media_web_attributes(Enum):
    '''Valid attributes for web media objects.  Used by the framework.media_category_rest module when validating input
    parameters.  Only the parameters in this list will be put into requests for 'web media' objects.

    For exmaple, if I have a key value pair: {'booga':'<some data value''} it will be rejected by the add method in
    the user_rest module.  However, {'name':'<some data value>'} will be added to the API request to the
    CM when adding a user because 'username' is a member of this Enum
    '''
    description = 1
    uri = 2
    mediaType = 3
    name = 4


class valid_api_names(Enum):
    '''
    Valid API names - the portion of the URL which follows /api/rest in the API call.
    '''

    categories = 1
    workgroups = 2
    metadata = 3
    media = 4

class uploadType(Enum):
    '''
    Valid upload types for media uploads to the CM
    '''
    media_item = 1
    maint_item = 2

class validate_api_field_results(Enum):
    '''
    Internal Enum used for all validate_api_field methods in all framework objects
    '''
    OK = 1
    KEY_NO_MATCH = 2
    VALUE_NO_MATCH = 3
    KEY_DEPRECATED = 4
    VALUE_DEPRECATED =5

class metadata_data_type(Enum):
    '''
    Values of datatype for metadata objects in the CM system
    '''
    BOOLEAN = 1
    INTEGER = 2
    STRING = 3

class metadata_value_type(Enum):
    '''
    Allowed values of metadata valuetype
    '''
    ANY = 1
    PICKLIST = 2
class playlistItemType(Enum):
    '''
    Type of playlist Item for use with /api/rest/playlists/{id}/playlistItems
    '''
    MEDIA_ITEM = 1
    SUB_PLAYLIST = 2