"""Translate instance selection options into the SENSE-O intent contract."""
import json

from sense.common import require_text


def select_instance_scope(body, group=None, project=None, principal=None):
    """
    Return a serialized intent copy with explicit selections overriding intent fields.
    """
    if group is not None and principal is not None:
        raise ValueError('Specify either principal or group, not both')
    if group is None and project is None and principal is None:
        return body
    for name, value in [('group', group), ('principal', principal), ('project', project)]:
        if value is not None:
            require_text(value, name)
    intent = json.loads(body) if isinstance(body, str) else body
    if not isinstance(intent, dict):
        raise ValueError('Instance selection requires a JSON object intent')
    intent = dict(intent)
    selected_principal = principal if principal is not None else group
    if selected_principal is not None:
        intent['principal'] = selected_principal
    if project is not None:
        intent['project'] = project
    return json.dumps(intent)
