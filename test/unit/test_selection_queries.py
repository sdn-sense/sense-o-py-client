import json

import pytest

from sense.client.group_api import GroupApi
from sense.client.caller_identity import caller_identity, inherited_groups, same_principal
from sense.client.project_api import ProjectApi
from sense.client.requestwrapper import RequestWrapper
from test.unit.stubs import SENTINEL, StubRequestWrapper, identity_headers


def test_group_queries():
    stub = StubRequestWrapper()
    stub.config['headers'] = identity_headers(
        preferred_username='alice', groups=['/science/team', '/other/$GROUP_LEAD', 'PROFILE_MANAGER'])
    api = GroupApi(req_wrapper=stub)
    assert api.group_list() == ['/other', '/science', '/science/team']
    assert stub.calls == []


def test_memberships_keep_escaped_slashes_and_exclude_flags():
    assert inherited_groups(['/science/one~/two/team', '/science/one~/two/$GROUP_LEAD']) == [
        '/science', '/science/one~/two', '/science/one~/two/team']


def test_group_discovery_uses_current_local_token():
    stub = StubRequestWrapper()
    stub.config['headers'] = dict(identity_headers(preferred_username='alice', groups=['/local']),
                                  **{'X-Original-Authorization': 'Bearer foreign-token'})
    api = GroupApi(req_wrapper=stub)
    assert api.group_list() == ['/local']
    stub.config['headers'] = identity_headers(preferred_username='alice', groups=['/refreshed'])
    assert api.group_list() == ['/refreshed']


def test_user_without_group_claim_has_no_memberships():
    stub = StubRequestWrapper()
    stub.config['headers'] = identity_headers(preferred_username='alice')
    assert GroupApi(req_wrapper=stub).group_list() == []
    assert stub.calls == []


@pytest.mark.parametrize('header', [None, 'Bearer opaque-token', 'Bearer h.??.s', 'Basic abc'])
def test_group_discovery_rejects_missing_or_unreadable_identity(header):
    stub = StubRequestWrapper()
    stub.config['headers'] = {'Authorization': header} if header else {}
    with pytest.raises(ValueError, match='(Caller discovery|Cannot read caller identity)'):
        GroupApi(req_wrapper=stub).group_list()
    assert stub.calls == []


@pytest.mark.parametrize('claims', [
    {}, {'preferred_username': 'alice', 'groups': '/science'},
    {'preferred_username': 'alice', 'realm_access': None},
])
def test_identity_requires_expected_claim_shapes(claims):
    stub = StubRequestWrapper()
    stub.config['headers'] = identity_headers(**claims)
    with pytest.raises(ValueError, match='Cannot read caller identity'):
        caller_identity(stub)


@pytest.mark.parametrize('left,right,expected', [
    ('Alice', 'alice', True), ('Alice@EXAMPLE.org', 'alice@example.org', True),
    ('/science/team', '/science/team', True), ('/science/team', '/Science/team', False),
    ('/alice', 'alice', False), ('alice', 'bob', False),
])
def test_same_principal(left, right, expected):
    assert same_principal(left, right) is expected


def test_project_queries():
    stub = StubRequestWrapper()
    api = ProjectApi(req_wrapper=stub)
    assert api.project_available() is SENTINEL
    assert api.project_available(subject='/science/team & lab') is SENTINEL
    assert api.project_list() is SENTINEL
    assert api.project_list(active_only=True) is SENTINEL
    assert api.project_get('12') is SENTINEL
    assert stub.calls == [
        ('GET', '/project/available', {'query_params': []}),
        ('GET', '/project/available', {'query_params': [('subject', '/science/team & lab')]}),
        ('GET', '/project', {'query_params': [('activeOnly', 'false')]}),
        ('GET', '/project', {'query_params': [('activeOnly', 'true')]}),
        ('GET', '/project/12', {}),
    ]


@pytest.mark.parametrize('project_id', [None, '', '../available', True, -1, 0, 1.5])
def test_project_id_validation(project_id):
    stub = StubRequestWrapper()
    with pytest.raises(ValueError):
        ProjectApi(req_wrapper=stub).project_get(project_id)
    assert stub.calls == []


@pytest.mark.parametrize('subject', ['', ' ', 42])
def test_subject_validation(subject):
    stub = StubRequestWrapper()
    with pytest.raises(ValueError):
        ProjectApi(req_wrapper=stub).project_available(subject=subject)
    assert stub.calls == []


@pytest.mark.parametrize('api_class,method', [
    (ProjectApi, 'project_available'),
])
def test_queries_send_auth_and_propagate_access_denial(monkeypatch, api_class, method):
    import requests

    wrapper = RequestWrapper(config={
        'API_ENDPOINT': 'https://example.invalid/restapi',
        'AUTH_ENDPOINT': 'https://example.invalid/token',
        'CLIENT_ID': 'test', 'ACCESS_TOKEN': 'test-access-token',
    })
    calls = []

    def forbidden(url, **kwargs):
        calls.append((url, kwargs))
        response = requests.Response()
        response.status_code = 403
        response.headers['content-type'] = 'application/json'
        response._content = json.dumps({'exception': 'Access denied'}).encode()
        return response

    monkeypatch.setattr(requests, 'get', forbidden)
    with pytest.raises(ValueError, match='403'):
        getattr(api_class(req_wrapper=wrapper), method)()
    assert len(calls) == 1
    assert calls[0][1]['headers']['Authorization'] == 'Bearer test-access-token'
