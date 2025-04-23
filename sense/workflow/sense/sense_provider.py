from sense.workflow.base.constants import Constants
from sense.workflow.base.exceptions import ResourceTypeNotSupported, ProviderException
from sense.workflow.base.utils import get_logger
from sense.workflow.provider.provider import Provider
from .sense_constants import *
from .sense_exceptions import SenseException

logger = get_logger()


class SenseProvider(Provider):
    def __init__(self, *, type, label, name, config: dict):
        super().__init__(type=type, label=label, name=name, logger=logger, config=config)
        self.supported_resources = [Constants.RES_TYPE_SERVICE]
        self._client = None
        self.service_handler = None
        self.address_handler = None

    def setup_environment(self):
        for attr in SENSE_CONF_ATTRS:
            if self.config.get(attr.lower()) is None and self.config.get(attr.upper()) is None:
                raise ProviderException(f"{self.name}: Expecting a value for {attr}")

    def _init_client(self):
        if not self.client:
            self.logger.debug(f"{self.name}: Initializing sense client {self.label}")
            from sense.client.requestwrapper import RequestWrapper

            self._client = RequestWrapper(self.config)
            self.logger.info(f"{self.name}: Initialized sense client {self.label}")

    @property
    def client(self):
        return self._client

    def supports_modify(self):
        return True

    def do_validate_resource(self, *, resource: dict):
        label = resource[Constants.LABEL]
        rtype = resource[Constants.RES_TYPE]

        if rtype not in self.supported_resources:
            raise ResourceTypeNotSupported(f"{rtype} for {label}")

        if Constants.PROFILE not in resource and Constants.POOL not in resource:
            raise SenseException(f"Must have a profile or pool for {label}")

    def _get_handler(self, resource):
        def handler_from_dict(adict: dict):
            from .service_handler import ServiceHandler
            from .address_handler import AddressHandler

            if Constants.PROFILE in adict:
                self.service_handler = self.service_handler or ServiceHandler(provider=self)
                return self.service_handler
            elif Constants.POOL in adict:
                self.address_handler = self.address_handler or AddressHandler(provider=self)
                return self.address_handler
            else:
                return None

        handler = handler_from_dict(resource)

        if handler is None:
            if resource[Constants.SAVED_STATES]:
                handler = handler_from_dict(resource[Constants.SAVED_STATES][0].attributes)

        if handler is None:
            raise SenseException(f'unkown resource {resource}')

        return handler

    def do_add_resource(self, *, resource: dict):
        assert resource[Constants.RES_TYPE] in self.supported_resources
        self._init_client()

        handler = self._get_handler(resource)
        handler.add_resource(resource=resource)

    def do_create_resource(self, *, resource: dict):
        assert resource[Constants.RES_TYPE] in self.supported_resources
        self._init_client()
        handler = self._get_handler(resource)
        handler.create_resource(resource=resource)

    def do_wait_for_create_resource(self, *, resource: dict):
        assert resource[Constants.RES_TYPE] in self.supported_resources
        self._init_client()
        handler = self._get_handler(resource)
        handler.wait_for_create_resource(resource=resource)

    def do_delete_resource(self, *, resource: dict):
        assert resource[Constants.RES_TYPE] in self.supported_resources
        self._init_client()
        handler = self._get_handler(resource)
        handler.delete_resource(resource=resource)
