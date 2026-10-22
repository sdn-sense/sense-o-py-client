import pytest

from sense.client.workflow_phased_api import WorkflowPhasedApi
from test.unit.stubs import SENTINEL, StubRequestWrapper

ACTIONS = ['propagate', 'commit', 'release', 'reinstate', 'verify']


@pytest.fixture
def stub():
    return StubRequestWrapper()


@pytest.fixture
def api(stub):
    return WorkflowPhasedApi(req_wrapper=stub)


@pytest.mark.parametrize('action', ACTIONS)
@pytest.mark.parametrize('kwargs,expected', [
    ({}, []),
    ({'sync': True}, [('sync', True)]),
    ({'sync': 'true', 'force': True, 'intent': 'last'},
     [('sync', 'true'), ('force', True), ('intent', 'last')]),
])
def test_instance_operate_request(api, stub, action, kwargs, expected):
    result = api.instance_operate(action, si_uuid='abc-123', **kwargs)
    assert stub.calls == [
        ('PUT', f'/instance/abc-123/{action}', {'query_params': expected})]
    assert result is SENTINEL


@pytest.mark.parametrize('action', ACTIONS)
def test_instance_operate_unknown_kwarg(api, stub, action):
    with pytest.raises(TypeError):
        api.instance_operate(action, si_uuid='abc-123', bogus=1)
    assert stub.calls == []


def test_instance_operate_disallowed_action(api, stub):
    with pytest.raises(ValueError):
        api.instance_operate('cancel', si_uuid='abc-123')
    assert stub.calls == []
