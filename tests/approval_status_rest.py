__author__ = 'rkaye'
from framework.http_rest import rest_request
from framework.inventory import Roles_inventory
from itertools import chain
from framework.constants import call_type
from framework.framework_object_rest import framework_object
class Approval_status(framework_object):
    def __init__(self, api_version):
        '''
        Constructor for Approval_status object.
        :param api_version: version of Approval_status api
        :return:
        '''
        super().__init__(api_version)

    def list_all_approver_users_for_media(self, media_id):
        """
        Wrapper around GET /api/rest/approvalStatus/{id}/mediaApprovers
        :param media_id: ID of media to return list of approvers for
        :return:
        """
        pass

    def list_all_approver_users_for_message(self, message_id):
        pass

    def list_possible_approval_status_values(self):
        pass

    def current_approval_state_for_a_media_or_message(self, media_or_message_id):
        pass