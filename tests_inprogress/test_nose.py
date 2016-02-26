from nose import with_setup
import requests
import logging
import logging.config
import configparser
from framework.constants import *
from framework.authentication_rest import login, logout, get_auth_token
from framework.http_rest import *


class Base_Nose_Class(object):
    def setup(self):
        print ('setup before each test')

    def teardown(self):
        print('teardown after each test')

    @classmethod
    def setup_class(cls):
        print('only run once per module')

    @classmethod
    def teardown_class(cls):
        print('run only once per module for teardown')

# class test_class(Base_Nose_Class):
#     def test_1(self):
#         print('first test')
#         assert True
#
#     def test_2(self):
#         print('second test')
#         assert True

class test_class(Base_Nose_Class):
    def method(self,batta):
        print (str(batta))
        print('test run number: {}'.format(batta))


    def test_1(self):
        for x in range(1,5):
            print()
            thrust = 'bbbbb'
            print ('test run where x = {}'.format(str(x)))
            yield self.method,thrust
        print('test run complete.')

