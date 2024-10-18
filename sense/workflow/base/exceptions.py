class ParseConfigException(Exception):
    pass


class ResourceTypeNotSupported(Exception):
    pass


class ProviderTypeNotSupported(Exception):
    pass


class ConfigTypeNotSupported(Exception):
    pass


class StateException(Exception):
    pass


class ControllerException(Exception):
    pass


class ProviderException(Exception):
    pass
