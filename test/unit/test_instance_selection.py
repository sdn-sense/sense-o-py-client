import json

import pytest

from sense.client.instance_api import InstanceApi
from sense.client.workflow_combined_api import WorkflowCombinedApi
from sense.client.workflow_phased_api import WorkflowPhasedApi
from test.unit.stubs import SENTINEL, StubRequestWrapper


@pytest.mark.parametrize('api_class', [InstanceApi, WorkflowCombinedApi, WorkflowPhasedApi])
@pytest.mark.parametrize('low_level', [False, True])
@pytest.mark.parametrize('async_req', [False, True])
@pytest.mark.parametrize('selection,expected', [
    ({'group': '/science/team'}, {'principal': '/science/team', 'project': 'existing'}),
    ({'project': 'PRJ-42'}, {'principal': '/existing', 'project': 'PRJ-42'}),
    ({'group': '/science/team', 'project': 'Science'},
     {'principal': '/science/team', 'project': 'Science'}),
    ({'principal': 'alice@example.org'}, {'principal': 'alice@example.org', 'project': 'existing'}),
])
def test_selection_sent_in_intent(api_class, low_level, async_req, selection, expected):
    stub = StubRequestWrapper()
    api = api_class(req_wrapper=stub)
    intent = {'service': 'test', 'principal': '/existing', 'project': 'existing',
              'data': {'value': 'preserved'}}
    original = json.dumps(intent)
    if low_level:
        result = api.instance_si_uuid_post_with_http_info(
            intent, si_uuid='instance-1', async_req=async_req, **selection)
    else:
        api.si_uuid = 'instance-1'
        result = api.instance_create(original, async_req=async_req, **selection)
    assert result is SENTINEL
    method, path, kwargs = stub.calls[0]
    assert (method, path) == ('POST', '/instance/instance-1')
    assert json.loads(kwargs['body_params']) == dict(intent, **expected)
    assert json.dumps(intent) == original
    assert kwargs.get('query_params', []) == []


@pytest.mark.parametrize('api_class', [InstanceApi, WorkflowCombinedApi, WorkflowPhasedApi])
def test_existing_requests_and_uuid_allocation_unchanged(api_class):
    stub = StubRequestWrapper()
    api = api_class(req_wrapper=stub)
    body = '{"service":"test", "principal":"/existing", "project":"Science"}'
    api.instance_create(body, si_uuid='instance-1')
    assert stub.calls[0][2]['body_params'] == body
    api.instance_new()
    assert stub.calls[1] == ('GET', '/instance', {})
    assert api.si_uuid is SENTINEL


@pytest.mark.parametrize('api_class', [InstanceApi, WorkflowCombinedApi, WorkflowPhasedApi])
@pytest.mark.parametrize('selection', [
    {'group': ''}, {'group': '  '}, {'project': ''}, {'project': 42}, {'typo': 'x'},
    {'principal': ''}, {'principal': ' '}, {'principal': 'alice', 'group': '/science'},
])
def test_invalid_selection_never_submitted(api_class, selection):
    stub = StubRequestWrapper()
    api = api_class(req_wrapper=stub)
    with pytest.raises((ValueError, TypeError)):
        api.instance_create('{}', si_uuid='instance-1', **selection)
    assert stub.calls == []


@pytest.mark.parametrize('body', ['[]', 'null', 'invalid-json', []])
def test_selection_requires_object(body):
    stub = StubRequestWrapper()
    with pytest.raises(ValueError):
        InstanceApi(req_wrapper=stub).instance_create(body, si_uuid='i', group='/team')
    assert stub.calls == []


def test_instance_selection_preserves_execution_parameters():
    stub = StubRequestWrapper()
    InstanceApi(req_wrapper=stub).instance_create(
        '{}', si_uuid='i', group='/team', project='Science', sync=False, proceed=True)
    assert stub.calls[0][2]['query_params'] == [('sync', False), ('proceed', True)]
