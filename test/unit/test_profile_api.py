import pytest

from sense.client.profile_api import ProfileApi
from test.unit.stubs import SENTINEL, StubRequestWrapper


@pytest.fixture
def stub():
    return StubRequestWrapper()


@pytest.fixture
def api(stub):
    return ProfileApi(req_wrapper=stub)


def test_profile_describe_sync(api, stub):
    result = api.profile_describe('my-profile')
    assert stub.calls == [('GET', '/profile/my-profile', {'query_params': []})]
    assert result is SENTINEL


def test_profile_describe_async(api, stub):
    result = api.profile_describe('my-profile', async_req=True)
    assert stub.calls == [('GET', '/profile/my-profile', {'query_params': []})]
    assert result is SENTINEL
