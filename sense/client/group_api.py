"""Endpoints for inspecting the current caller's group memberships."""
from sense.client.caller_identity import caller_identity
from sense.client.requestwrapper import RequestWrapper
from sense.common import classwrapper


@classwrapper
class GroupApi:
    def __init__(self, req_wrapper=None):
        self.client = req_wrapper if req_wrapper is not None else RequestWrapper()

    def group_list(self):
        """List own and inherited group paths from the API access token.

        Membership alone does not establish a license for a particular profile.
        """
        return caller_identity(self.client)['groups']
