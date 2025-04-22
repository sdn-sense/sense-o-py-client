class Constants:
    PROVIDER_STATE = 'provider_state'
    LABELS = 'labels'

    RES_TYPE = 'res_type'
    CONFIG = 'config'
    RES_NAME_PREFIX = "name_prefix"
    CREDENTIAL_FILE = 'credential_file'
    PROFILE = "profile"
    CONFIG_DIR = "config_dir"

    POOL = 'pool'
    ADDR_TYPE = "addr_type"
    NET_MASK = 'netmask'

    SENSE_EXTENSION = "sense"
    PROVIDER = 'provider'
    LABEL = 'label'
    RES_COUNT = 'count'

    PROVIDER_CLASSES = {
        "sense": "sense.workflow.sense.sense_provider.SenseProvider"
    }

    EDIT_TEMPLATE = 'edit_template'
    CONFIG_SUPPORTED_TYPES = [EDIT_TEMPLATE, 'manifest_template']
    RES_TYPE_SERVICE = "service"
    RES_SUPPORTED_TYPES = [RES_TYPE_SERVICE]
    RES_RESTRICTED_TYPES = []

    EXTERNAL_DEPENDENCIES = "external_dependencies"
    RESOLVED_EXTERNAL_DEPENDENCIES = "resolved_external_dependencies"

    INTERNAL_DEPENDENCIES = "internal_dependencies"
    RESOLVED_INTERNAL_DEPENDENCIES = "resolved_internal_dependencies"

    SAVED_STATES = "saved_states"
    RES_CREATION_DETAILS = "creation_details"
    EXTERNAL_DEPENDENCY_STATES = "external_dependency_states"

    LOGGING = "logging"
    PROPERTY_CONF_LOG_FILE = 'log-file'
    PROPERTY_CONF_LOG_LEVEL = 'log-level'
    PROPERTY_CONF_LOG_RETAIN = 'log-retain'
    PROPERTY_CONF_LOG_SIZE = 'log-size'
    PROPERTY_CONF_LOGGER = "logger"
