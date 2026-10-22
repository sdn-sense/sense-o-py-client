import pytest

from sense.client.profile_api import ProfileApi
from test.unit.stubs import StubRequestWrapper, identity_headers


class ProfileChoicesWrapper(StubRequestWrapper):
    def __init__(self, owner='other', roles=None):
        super().__init__()
        self.config['headers'] = identity_headers(
            preferred_username='Alice', email='alice@example.org',
            groups=['/science/team', '/operations/$GROUP_LEAD'],
            realm_access={'roles': roles or ['PROFILE_VIEWER', 'SERVICE_CREATOR']})
        self.profile = {'uuid': 'profile-1', 'name': 'Science Profile', 'owner': owner, 'authorized': True}
        self.licenses = [
            {'principal': 'ALICE', 'allocations': 2, 'readOnly': True},
            {'principal': 'Alice@EXAMPLE.org', 'allocations': 2, 'readOnly': False},
            {'principal': '/science', 'allocations': 3, 'readOnly': False},
            {'principal': '/science/team', 'allocations': 1, 'readOnly': True},
            {'principal': '/operations', 'allocations': 0, 'readOnly': True},
            {'principal': '/SCIENCE', 'allocations': 2, 'readOnly': False},
            {'principal': '/unrelated', 'allocations': 2, 'readOnly': False},
            {'principal': 'PROFILE_VIEWER', 'allocations': 2, 'readOnly': False},
        ]
        self.uses = {'ALICE': ['i1'], '/science': ['i2'], '/science/team': ['i3']}
        self.projects = {
            '/science': [{'id': 2, 'name': 'Preferred', 'externalId': 'PRJ-2'},
                         {'id': 1, 'name': 'Another', 'externalId': None}],
            'ALICE': [{'id': 3, 'name': 'Personal', 'externalId': None}],
        }
        self.denied_path = None

    def request(self, method, path, **kwargs):
        super().request(method, path, **kwargs)
        if path == self.denied_path:
            raise ValueError('Returned code 403: Access denied')
        if path == '/profile/Science Profile':
            return self.profile
        if path == '/profile/profile-1/licenses':
            return self.licenses
        if path == '/profile/profile-1/licenses/uses':
            return self.uses
        if path == '/project/available':
            return self.projects.get(dict(kwargs['query_params'])['subject'], [])
        raise AssertionError('Unexpected request: %s %s' % (method, path))


def test_profile_choices_match_identity_and_report_capacity_and_projects():
    wrapper = ProfileChoicesWrapper()
    result = ProfileApi(req_wrapper=wrapper).profile_submission_options('Science Profile')
    assert result['profile'] == wrapper.profile
    assert result['licenseRequired'] is True
    assert result['defaultPrincipal'] is None
    choices = {choice['principal']: choice for choice in result['principals']}
    assert set(choices) == {'ALICE', 'Alice@EXAMPLE.org', '/science', '/science/team', '/operations'}
    assert choices['ALICE']['readOnly'] is True
    assert choices['ALICE']['selectable'] is True  # read-only limits editing, not creation
    assert choices['ALICE']['used'] == 1
    assert choices['ALICE']['remaining'] == 1
    assert choices['ALICE']['projectRequired'] is False
    assert choices['ALICE']['suggestedProject'] == 'Personal'
    assert choices['/science']['suggestedProject'] == 'PRJ-2'
    assert choices['/science']['projectRequired'] is True
    assert [project['selector'] for project in choices['/science']['projects']] == ['PRJ-2', 'Another']
    assert choices['/science/team']['remaining'] == 0
    assert choices['/science/team']['selectable'] is False
    assert choices['/operations']['selectable'] is False
    assert wrapper.calls[:3] == [
        ('GET', '/profile/Science Profile', {'query_params': []}),
        ('GET', '/profile/profile-1/licenses', {}),
        ('GET', '/profile/profile-1/licenses/uses', {}),
    ]
    assert all(path != '/keycloak/groups' for _, path, _ in wrapper.calls)
    assert all('selector' not in project for projects in wrapper.projects.values() for project in projects)


def test_selected_principal_limits_project_query():
    wrapper = ProfileChoicesWrapper()
    result = ProfileApi(req_wrapper=wrapper).profile_submission_options('Science Profile', principal='/science')
    assert len(result['principals']) == 1
    assert result['principals'][0]['principal'] == '/science'
    assert wrapper.calls[-1] == (
        'GET', '/project/available', {'query_params': [('subject', '/science')]})
    assert len(wrapper.calls) == 4


@pytest.mark.parametrize('principal', ['/unrelated', '/SCIENCE', 'PROFILE_VIEWER'])
def test_unheld_subject_never_used_for_project_discovery(principal):
    wrapper = ProfileChoicesWrapper()
    with pytest.raises(ValueError, match='not a choice'):
        ProfileApi(req_wrapper=wrapper).profile_submission_options('Science Profile', principal=principal)
    assert len(wrapper.calls) == 3


@pytest.mark.parametrize('principal,expected', [
    ('alice', 'ALICE'), ('alice@example.org', 'Alice@EXAMPLE.org'),
])
def test_selected_personal_principal_ignores_case(principal, expected):
    wrapper = ProfileChoicesWrapper()
    result = ProfileApi(req_wrapper=wrapper).profile_submission_options('Science Profile', principal=principal)
    assert [choice['principal'] for choice in result['principals']] == [expected]


def test_selected_group_principal_requires_exact_path():
    wrapper = ProfileChoicesWrapper()
    with pytest.raises(ValueError, match='not a choice'):
        ProfileApi(req_wrapper=wrapper).profile_submission_options('Science Profile', principal='/Science/team')


@pytest.mark.parametrize('license_record', [
    {'principal': '/science', 'allocations': None, 'readOnly': False},
    {'principal': '/science', 'readOnly': False},
])
def test_license_without_allocations_has_unknown_capacity(license_record):
    wrapper = ProfileChoicesWrapper()
    wrapper.licenses = [license_record]
    result = ProfileApi(req_wrapper=wrapper).profile_submission_options('Science Profile')
    choice = result['principals'][0]
    assert choice['allocations'] is None
    assert choice['used'] == 1
    assert choice['remaining'] is None
    assert choice['selectable'] is True


def test_unlicensed_user_has_no_choices_or_project_queries():
    wrapper = ProfileChoicesWrapper()
    wrapper.licenses = [{'principal': '/unrelated', 'allocations': 10, 'readOnly': False}]
    result = ProfileApi(req_wrapper=wrapper).profile_submission_options('Science Profile')
    assert result['principals'] == []
    assert result['defaultPrincipal'] is None
    assert len(wrapper.calls) == 3


def test_choices_read_identity_after_request_token_refresh():
    wrapper = ProfileChoicesWrapper()
    original_request = wrapper.request

    def refreshed_request(method, path, **kwargs):
        result = original_request(method, path, **kwargs)
        if path.endswith('/licenses/uses'):
            wrapper.config['headers'] = identity_headers(preferred_username='Alice', groups=['/unrelated'])
        return result

    wrapper.request = refreshed_request
    result = ProfileApi(req_wrapper=wrapper).profile_submission_options('Science Profile')
    assert [choice['principal'] for choice in result['principals']] == ['ALICE', '/unrelated']


@pytest.mark.parametrize('owner,roles,source', [
    ('Alice', [], 'owner'), ('other', ['SYSTEM_ADMIN'], 'admin'),
])
def test_owner_and_admin_can_submit_without_delegated_license(owner, roles, source):
    wrapper = ProfileChoicesWrapper(owner=owner, roles=roles)
    wrapper.licenses = []
    result = ProfileApi(req_wrapper=wrapper).profile_submission_options('Science Profile')
    assert result['licenseRequired'] is False
    assert result['defaultPrincipal'] == 'Alice'
    choice = result['principals'][0]
    assert choice['principal'] == 'Alice'
    assert choice['source'] == source
    assert choice['allocations'] is None
    assert choice['selectable'] is True
    assert choice['projectRequired'] is False


@pytest.mark.parametrize('denied_path', [
    '/profile/Science Profile', '/profile/profile-1/licenses',
    '/profile/profile-1/licenses/uses', '/project/available',
])
def test_profile_choice_access_errors_propagate(denied_path):
    wrapper = ProfileChoicesWrapper()
    wrapper.denied_path = denied_path
    with pytest.raises(ValueError, match='403'):
        ProfileApi(req_wrapper=wrapper).profile_submission_options('Science Profile')
    assert wrapper.calls[-1][1] == denied_path


def test_profile_licenses_preserve_response_and_encode_identifier():
    wrapper = StubRequestWrapper()
    api = ProfileApi(req_wrapper=wrapper)
    api.profile_licenses('p/1')
    api.profile_license_uses('p/1')
    assert wrapper.calls == [
        ('GET', '/profile/p%2F1/licenses', {}), ('GET', '/profile/p%2F1/licenses/uses', {}),
    ]


@pytest.mark.parametrize('method', ['profile_licenses', 'profile_license_uses', 'profile_submission_options'])
@pytest.mark.parametrize('search', [None, '', ' '])
def test_profile_queries_require_identifier(method, search):
    wrapper = StubRequestWrapper()
    with pytest.raises(ValueError):
        getattr(ProfileApi(req_wrapper=wrapper), method)(search)
    assert wrapper.calls == []
