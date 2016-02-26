__author__ = 'richardkaye'
from framework.framework_object_rest import framework_object

class License(framework_object):
    """
    Helper class that builds a License json object for use in API testing.
    Class methods 'help' programmers by validating data before it can be
    placed into the main data object for the instance.
    """

    def __init__(self, api_version):
        super().__init__(api_version)

