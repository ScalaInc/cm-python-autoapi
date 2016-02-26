import logging
import logging.config
import configparser
from framework.constants import *
from framework.authentication_api_rest import Auth_api
import datetime
from nose.plugins.attrib import attr


config = configparser.ConfigParser()
config.read(CONFIG_FILE_PATH)
baseurl = config['login']['baseurl']
logging.config.fileConfig(LOG_FILE_PATH)
logging.debug('Logging config file path is: {}'.format(CONFIG_FILE_PATH))

api_version_auth = config['api_info']['api_version_authentication']




user_list = [{'name':'All Roles 1','password':'scala'},
             {'name':'All Roles 2','password':'scala'},
             {'name':'All Roles 3','password':'scala'},
             {'name':'All Roles 4','password':'scala'},
             {'name':'Administrator System Roll','password':'scala'},
             {'name':'Graphic Designer','password':'scala'},
             {'name':'Message Editor','password':'scala'},
             {'name':'Message Manager','password':'scala'},
             {'name':'Player User','password':'scala'},
             {'name':'Schedule Manager','password':'scala'}]


auth_object_list = []
for user in user_list:
    auth_object = Auth_api(api_version_auth)
    session = auth_object.login(username=user['name'],
                                baseurl=baseurl,
                                password=user['password'])
    auth_object_list.append(auth_object)

for auth in auth_object_list:
    auth.logout()