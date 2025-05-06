import logging
from argparse import ArgumentParser, RawDescriptionHelpFormatter

from .constants import Constants


def create_parser(usage='%(prog)s [options]',
                  description='',
                  formatter_class=None):
    formatter_class = formatter_class or RawDescriptionHelpFormatter
    return ArgumentParser(usage=usage, description=description, formatter_class=formatter_class)


def build_parser(*, manage_workflow, manage_sessions):
    description = (
        'Sense Workflow Tool'
        '\n'
        '\n'
        'Examples:'
        '\n'
        "      sense_workflow.py workflow --var-file vars.yml --session my_session -validate"
        '\n'
        "      sense_workflow.py workflow --config-dir . --session my_session -validate"
    )

    parser = create_parser(description=description)
    subparsers = parser.add_subparsers()
    workflow_parser = subparsers.add_parser('workflow', help='Manage sense workflows')
    workflow_parser.add_argument('-c', '--config-dir', type=str, default='.',
                                 help='config directory with .sense files. Defaults to current directory.',
                                 required=False)
    workflow_parser.add_argument('-v', '--var-file', type=str, default='',
                                 help="Yaml file with key-value pairs to override the variables' default values",
                                 required=False)
    workflow_parser.add_argument('-s', '--session', type=str, default='',
                                 help='friendly session name to help track a workflow', required=True)
    workflow_parser.add_argument('-p', '--policy-file', type=str, default='',
                                 help="Yaml stitching policy file",
                                 required=False)
    workflow_parser.add_argument('-validate', action='store_true', default=False,
                                 help='assembles and validates all .sense files  in the config directory')
    workflow_parser.add_argument('-plan', action='store_true', default=False, help='shows plan')
    workflow_parser.add_argument('-apply', action='store_true', default=False, help='create resources')
    workflow_parser.add_argument('-show', action='store_true', default=False, help='display resource.')
    workflow_parser.add_argument('-summary', action='store_true', default=False,
                                 help='display summary. used with -show')
    workflow_parser.add_argument('-json', action='store_true', default=False,
                                 help='use json output. relevant when used with -show or -plan')
    workflow_parser.add_argument('-destroy', action='store_true', default=False, help='delete resources')
    workflow_parser.set_defaults(dispatch_func=manage_workflow)

    sessions_parser = subparsers.add_parser('sessions', help='Manage sense sessions ')
    sessions_parser.add_argument('-show', action='store_true', default=False, help='display sessions')
    sessions_parser.add_argument('-json', action='store_true', default=False, help='use json format')
    sessions_parser.set_defaults(dispatch_func=manage_sessions)
    return parser


def get_log_level():
    import os
    return os.environ.get('SENSE_LOG_LEVEL', "INFO")


def get_log_location():
    import os
    return os.environ.get('SENSE_LOG_LOCATION', "/tmp/sense.log")


def get_formatter():
    fmt = "%(asctime)s [%(filename)s:%(lineno)d] [%(levelname)s] %(message)s"
    return logging.Formatter(fmt)


_LOGGER = None


def get_logger():
    global _LOGGER

    if not _LOGGER:
        _LOGGER = init_logger()

    return _LOGGER


def init_logger():
    from logging.handlers import RotatingFileHandler

    log_config = {'log-file': get_log_location(),
                  'log-level': get_log_level(),
                  'log-retain': 5,
                  'log-size': 5000000,
                  'logger': 'sense'}

    logger = logging.getLogger(str(log_config.get(Constants.PROPERTY_CONF_LOGGER, __name__)))
    log_level = log_config.get(Constants.PROPERTY_CONF_LOG_LEVEL, "INFO")
    logger.setLevel(log_level)

    formatter = get_formatter()
    file_handler = RotatingFileHandler(log_config.get(Constants.PROPERTY_CONF_LOG_FILE),
                                       backupCount=int(log_config.get(Constants.PROPERTY_CONF_LOG_RETAIN)),
                                       maxBytes=int(log_config.get(Constants.PROPERTY_CONF_LOG_SIZE)))

    file_handler.setFormatter(formatter)
    logger.propagate = False
    logger.addHandler(file_handler)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    global _LOGGER

    _LOGGER = logger
    return logger


def absolute_path(path):
    from pathlib import Path
    import os

    path = Path(path).expanduser().absolute()

    return os.path.realpath(str(path))


def load_as_ns_from_yaml(*, dir_path=None, content=None):
    import yaml
    import json
    from types import SimpleNamespace

    objs = []

    if dir_path:
        from pathlib import Path
        import os

        dir_path = Path(dir_path).expanduser().absolute()

        if not os.path.isdir(dir_path):
            raise Exception(f'Expected a directory {dir_path}')

        configs = [conf for conf in os.listdir(dir_path) if conf.endswith(Constants.SENSE_EXTENSION)]

        if not configs:
            raise Exception(f'No {Constants.SENSE_EXTENSION} config files found in  {dir_path}')

        for config in configs:
            file_name = os.path.join(dir_path, config)

            with open(file_name, 'r') as stream:
                obj = yaml.safe_load(stream)
                obj = json.loads(json.dumps(obj), object_hook=lambda dct: SimpleNamespace(**dct))
                objs.append(obj)
    else:
        obj = yaml.safe_load(content)
        obj = json.loads(json.dumps(obj), object_hook=lambda dct: SimpleNamespace(**dct))
        objs.append(obj)

    return objs


def load_yaml_from_file(file_name):
    import yaml
    from pathlib import Path

    path = Path(file_name).expanduser().absolute()

    with open(str(path), 'r') as stream:
        return yaml.safe_load(stream)


def load_vars(var_file):
    import yaml
    import os

    if not os.path.isfile(var_file):
        raise Exception(f'The supplied var-file {var_file} is invalid')

    with open(var_file, 'r') as stream:
        return yaml.safe_load(stream)


def get_base_dir(friendly_name):
    from pathlib import Path
    import os

    base_dir = os.path.join(str(Path.home()), '.sense', 'sessions', friendly_name)
    os.makedirs(base_dir, exist_ok=True)
    return base_dir


def dump_sessions(to_json: bool):
    from .state_utils import load_meta_data
    from pathlib import Path
    import os
    import sys

    base_dir = os.path.join(str(Path.home()), '.sense', 'sessions')
    os.makedirs(base_dir, exist_ok=True)
    sessions = os.listdir(base_dir)
    sessions = [dict(session=s,
                     config_dir=load_meta_data(s, 'config_dir')) for s in sessions]

    if to_json:
        import json

        sys.stdout.write(json.dumps(sessions, default=lambda o: o.__dict__, indent=3))
    else:
        import yaml

        sys.stdout.write(yaml.dump(sessions))

    return sessions


def get_counters(*, states):
    services = pending = failed = 0

    for state in states:
        pending += len(state.pending)
        pending += len(state.pending_internal)
        services += len(state.service_states)

        for key, detail in state.creation_details.items():
            failed += detail['failed_count']

    return services, pending, failed


# noinspection PyBroadException
def can_read(path: str):
    from pathlib import Path

    path = str(Path(path).expanduser().absolute())

    try:
        with open(path, 'r') as f:
            f.read()
        return True
    except Exception:
        return False


# noinspection PyBroadException
def can_read_json(path: str):
    try:
        with open(path, 'r') as fp:
            import json

            json.load(fp)

        return True
    except Exception:
        return False

