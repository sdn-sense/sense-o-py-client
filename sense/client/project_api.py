"""Queries for SENSE-O projects and caller-scoped attribution choices."""
from sense.client.requestwrapper import RequestWrapper
from sense.common import classwrapper, require_text


@classwrapper
class ProjectApi:
    def __init__(self, req_wrapper=None):
        self.client = req_wrapper if req_wrapper is not None else RequestWrapper()

    def project_list(self, active_only=False):
        """List the project catalog; this is not a list of allowed selections."""
        return self.client.request(
            'GET', '/project',
            query_params=[('activeOnly', 'true' if active_only else 'false')])

    def project_available(self, subject=None):
        """List active projects offered for the caller or a selected group.

        The server checks that the caller holds the requested subject and
        returns no projects for subjects outside the caller's access.
        """
        query_params = []
        if subject is not None:
            require_text(subject, 'subject')
            query_params.append(('subject', subject))
        return self.client.request('GET', '/project/available', query_params=query_params)

    def project_get(self, project_id):
        """Get a project by its local numeric ID (not an intent selector)."""
        if (isinstance(project_id, bool) or
                not isinstance(project_id, (int, str)) or
                not str(project_id).isdigit() or int(project_id) <= 0):
            raise ValueError('project_id must be a positive integer')
        return self.client.request('GET', '/project/%s' % int(project_id))
