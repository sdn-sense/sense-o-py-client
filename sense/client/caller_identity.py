"""Identity/principal utility flows."""
import base64
import binascii
import json


def inherited_groups(groups):
    """Expand full group paths using StackV's hierarchy and flag conventions."""
    result = set()
    for group in groups:
        if not isinstance(group, str) or not group.startswith('/'):
            continue
        while group:
            separator = group.rfind('/')
            while separator > 0 and group[separator - 1] == '~':
                separator = group.rfind('/', 0, separator - 1)
            leaf = group[separator + 1:]
            if leaf != '$GROUP_LEAD':
                result.add(group)
            group = group[:separator] if separator >= 0 else ''
    return sorted(result)


def caller_identity(client):
    """Decode the current API Authorization JWT, without treating it as proof."""
    authorization = client.config.get('headers', {}).get('Authorization', '')
    scheme, _, token = authorization.partition(' ')
    if scheme.lower() != 'bearer' or not token:
        raise ValueError('Caller discovery requires an authenticated JWT access token')
    try:
        parts = token.split('.')
        if len(parts) != 3:
            raise ValueError('Not a JWT')
        claims = json.loads(base64.urlsafe_b64decode(parts[1] + '=' * (-len(parts[1]) % 4)))
        username = claims.get('preferred_username')
        email = claims.get('email')
        groups = claims.get('groups', [])
        roles = claims.get('realm_access', {}).get('roles', [])
        if (not isinstance(username, str) or not username.strip() or
                (email is not None and not isinstance(email, str)) or
                not isinstance(groups, list) or not isinstance(roles, list)):
            raise ValueError('Invalid identity claims')
    except (ValueError, TypeError, AttributeError, binascii.Error) as exc:
        raise ValueError('Cannot read caller identity from the API access token') from exc
    return {'username': username, 'email': email, 'groups': inherited_groups(groups), 'roles': roles}


def is_personal_principal(subject, identity):
    return any(isinstance(value, str) and subject.lower() == value.lower()
               for value in [identity['username'], identity.get('email')])


def same_principal(left, right):
    if left.startswith('/') or right.startswith('/'):
        return left == right
    return left.lower() == right.lower()


def matches_principal(subject, identity):
    return is_personal_principal(subject, identity) or subject in identity['groups']
