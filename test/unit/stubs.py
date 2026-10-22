"""Offline stand-in for RequestWrapper: records calls, never touches the network."""
import base64
import json

SENTINEL = object()


def identity_headers(**claims):
    """Unsigned test JWT; production discovery reads claims from the API token."""
    payload = base64.urlsafe_b64encode(json.dumps(claims).encode()).decode().rstrip('=')
    return {'Authorization': 'Bearer header.%s.signature' % payload}


class StubRequestWrapper:
    def __init__(self):
        self.config = {}
        self.calls = []

    def request(self, method, path, **kwargs):
        self.calls.append((method, path, kwargs))
        return SENTINEL
