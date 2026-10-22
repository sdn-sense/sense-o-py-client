import json
from pathlib import Path
import runpy
import sys
from unittest.mock import MagicMock

import pytest

import sense.client.group_api
import sense.client.profile_api
import sense.client.project_api
import sense.client.workflow_combined_api

CLI = Path(__file__).resolve().parents[2] / 'util' / 'sense_util.py'


@pytest.fixture
def cli(monkeypatch):
    workflow = MagicMock()
    workflow.si_uuid = 'instance-1'
    workflow.instance_create.return_value = {'service_uuid': 'instance-1'}
    workflow.instance_get_status.return_value = 'CREATE - READY'
    factory = MagicMock(return_value=workflow)
    monkeypatch.setattr(sense.client.workflow_combined_api, 'WorkflowCombinedApi', factory)
    groups = MagicMock()
    groups.group_list.return_value = ['/science/team']
    monkeypatch.setattr(sense.client.group_api, 'GroupApi', MagicMock(return_value=groups))
    projects = MagicMock()
    projects.project_available.return_value = [{'name': 'Science', 'externalId': 'PRJ-42'}]
    monkeypatch.setattr(sense.client.project_api, 'ProjectApi', MagicMock(return_value=projects))
    profiles = MagicMock()
    profiles.profile_submission_options.return_value = {'principals': [{'principal': '/science/team'}]}
    monkeypatch.setattr(sense.client.profile_api, 'ProfileApi', MagicMock(return_value=profiles))

    def run(*args):
        monkeypatch.setattr(sys, 'argv', [str(CLI), *args])
        runpy.run_path(str(CLI), run_name='__main__')

    return run, workflow, factory, groups, projects


@pytest.mark.parametrize('operation', ['--create', '--compute'])
@pytest.mark.parametrize('source', ['file', 'file-with-uuid', 'profile'])
def test_all_creation_paths(cli, tmp_path, capsys, operation, source):
    run, workflow, _, _, _ = cli
    args = [operation, '--group', '/science/team', '--project', 'PRJ-42']
    intent = {'service_profile_uuid': 'profile-1'}
    if source.startswith('file'):
        intent = {'service': 'test', 'principal': '/old', 'project': 'old', 'data': {'x': 1}}
        path = tmp_path / 'intent.json'
        path.write_text(json.dumps(intent))
        args += ['-f', str(path)]
    if source != 'file':
        args += ['-u', 'profile-1' if source == 'profile' else 'existing-instance']
    run(*args, '-n', 'Selected instance')
    body = json.loads(workflow.instance_create.call_args[0][0])
    assert body == dict(intent, principal='/science/team', project='PRJ-42', alias='Selected instance')
    assert workflow.instance_new.call_count == (0 if source == 'file-with-uuid' else 1)
    assert workflow.instance_operate.call_count == (1 if operation == '--create' else 0)
    assert capsys.readouterr().err == ''


@pytest.mark.parametrize('extra,warning_count', [
    ([], 2), (['--group', '/science/team'], 1), (['--project', 'PRJ-42'], 1),
    (['--use-defaults'], 0),
])
def test_default_warnings_on_stderr(cli, capsys, extra, warning_count):
    run, workflow, _, _, _ = cli
    run('--compute', '-u', 'profile-1', *extra)
    captured = capsys.readouterr()
    assert captured.err.count('Warning:') == warning_count
    assert 'Warning:' not in captured.out
    body = json.loads(workflow.instance_create.call_args[0][0])
    if not extra or extra == ['--use-defaults']:
        assert body == {'service_profile_uuid': 'profile-1'}


def test_intent_selections_suppress_default_warnings(cli, tmp_path, capsys):
    run, workflow, _, _, _ = cli
    intent = {'principal': '/science/team', 'project': 'Science'}
    path = tmp_path / 'intent.json'
    path.write_text(json.dumps(intent))
    run('--compute', '-f', str(path))
    assert json.loads(workflow.instance_create.call_args[0][0]) == intent
    assert capsys.readouterr().err == ''


def test_own_groups_and_project_picker(cli, capsys):
    run, _, factory, groups, projects = cli
    run('--groups', '--json')
    groups.group_list.assert_called_once_with()
    assert json.loads(capsys.readouterr().out) == ['/science/team']
    run('--projects', '--group', '/science/team', '--json')
    projects.project_available.assert_called_once_with(subject='/science/team')
    run('--projects')
    projects.project_available.assert_called_with(subject=None)
    factory.assert_not_called()


@pytest.mark.parametrize('selector', [['-u', 'profile-1'], ['-n', 'Science Profile']])
def test_profile_options_query(cli, capsys, selector):
    run, _, factory, _, _ = cli
    run('--profile-options', *selector, '--principal', '/science/team', '--json')
    profiles = sense.client.profile_api.ProfileApi.return_value
    profiles.profile_submission_options.assert_called_once_with(selector[1], principal='/science/team')
    assert json.loads(capsys.readouterr().out) == {'principals': [{'principal': '/science/team'}]}
    factory.assert_not_called()


def test_personal_principal_override(cli, capsys):
    run, workflow, _, _, _ = cli
    run('--compute', '-u', 'profile-1', '--principal', 'alice@example.org', '--project', 'Science')
    assert json.loads(workflow.instance_create.call_args[0][0])['principal'] == 'alice@example.org'
    assert capsys.readouterr().err == ''


@pytest.mark.parametrize('args', [
    ['--status', '--group', '/team'], ['--projects', '--project', 'Science'],
    ['--groups', '--use-defaults'], ['--create', '-u', 'p', '--group', ' '],
    ['--compute', '-u', 'p', '--project', ''], ['--create'],
    ['--profile-options'], ['--profile-options', '-u', 'p', '-n', 'name'],
    ['--create', '-u', 'p', '--principal', 'alice', '--group', '/science'],
])
def test_invalid_selection_usage_rejected_before_client_creation(cli, args):
    run, _, factory, _, _ = cli
    with pytest.raises(SystemExit) as error:
        run(*args)
    assert error.value.code == 2
    factory.assert_not_called()
