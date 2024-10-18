from sense.workflow.base.exceptions import ResourceTypeNotSupported, ProviderException
from sense.workflow.provider.api.provider import Provider
from sense.workflow.base.utils import get_logger
from sense.workflow.base.constants import Constants
from .sense_exceptions import SenseException
from .sense_constants import *

logger = get_logger()


class SenseProvider(Provider):
    def __init__(self, *, type, label, name, config: dict):
        super().__init__(type=type, label=label, name=name, logger=logger, config=config)
        self.supported_resources = [Constants.RES_TYPE_SERVICE]
        self.initialized = False
        self._handled_modify = False

    def setup_environment(self):
        for attr in SENSE_CONF_ATTRS:
            if self.config.get(attr.lower()) is None and self.config.get(attr.upper()) is None:
                raise ProviderException(f"{self.name}: Expecting a value for {attr}")

        pkey = self.config[SENSE_SLICE_PRIVATE_KEY_LOCATION]

        from  sense.workflow.base.utils import can_read, is_private_key, absolute_path

        pkey = absolute_path(pkey)

        if not can_read(pkey) or not is_private_key(pkey):
            raise ProviderException(f"{self.name}: unable to read/parse ssh key in {pkey}")

        self.config[SENSE_SLICE_PRIVATE_KEY_LOCATION] = pkey

    @property
    def private_key_file_location(self):
        from .sense_constants import SENSE_SLICE_PRIVATE_KEY_LOCATION

        return self.config.get(SENSE_SLICE_PRIVATE_KEY_LOCATION)

    def _init_client(self):
        if not self.initialized:
            self.logger.info(f"{self.name}: Initializing sense client")
            from .sense_client import init_client

            init_client(self.config)
            self.logger.info(f"{self.name}: Initialized sense client")
            self.initialized = True

    def do_add_resource(self, *, resource: dict):
        self._init_client()

        creation_details = resource[Constants.RES_CREATION_DETAILS]

        if not creation_details['in_config_file']:
            return

        label = resource.get(Constants.LABEL)
        rtype = resource.get(Constants.RES_TYPE)

        if rtype not in self.supported_resources:
            raise ResourceTypeNotSupported(f"{rtype} for {label}")

        interfaces = list()

        net_name = self.resource_name(resource)
        profile = resource[Constants.PROFILE]

        if not profile:
            raise SenseException(f"Must have a profile for {net_name}")

        layer3 = resource.get(Constants.RES_LAYER3)
        peering = resource.get(Constants.RES_PEERING)
        bandwidth = resource.get(Constants.RES_BANDWIDTH)

        from .sense_service import SenseService

        net = SenseService(label=label, name=net_name, profile=profile,
                           bandwidth=bandwidth, layer3=layer3, peering=peering, interfaces=interfaces)

        self.services.append(net)
        self.resource_listener.on_added(source=self, provider=self, resource=net)

    def do_create_resource(self, *, resource: dict):
        assert self.initialized
        rtype = resource.get(Constants.RES_TYPE)
        assert rtype in self.supported_resources
        label = resource.get(Constants.LABEL)
        self.logger.info(f"{self.name}: Creating resource {label} ....")

        if not self._handled_modify and self.modified:
            assert rtype == Constants.RES_TYPE_SERVICE, "sense expects network to be created first"
            self._handled_modify = True

            self.logger.warning(f"{self.name}:Modified state: Deleting sense resources ...")

            from .sense_service import SenseService

            net_name = self.resource_name(resource)
            net = SenseService(label=label, name=net_name, bandwidth=None, profile=None, layer3=None, interfaces=None,
                               peering=None)

            try:
                net.delete()
                self.logger.warning(f"Deleted sense resources ....")
            except Exception as e:
                self.logger.error(f"Exception deleting cloudlab resources ....", e)

        label = resource.get(Constants.LABEL)

        for net in [net for net in self._services if net.label == label]:
            self.logger.debug(f"Creating network: {vars(net)}")
            net.create()

            if self.resource_listener:
                self.resource_listener.on_created(source=self, provider=self, resource=net)

            self.logger.debug(f"Created network: {vars(net)}")

    def do_delete_resource(self, *, resource: dict):
        self._init_client()
        rtype = resource.get(Constants.RES_TYPE)
        assert rtype in self.supported_resources
        label = resource.get(Constants.LABEL)

        net_name = self.resource_name(resource)

        logger.debug(f"Deleting network: {net_name}")

        from .sense_service import SenseService

        net = SenseService(label=label, name=net_name, bandwidth=None, profile=None, layer3=None, interfaces=None,
                           peering=None)

        net.delete()
        logger.debug(f"Done Deleting network: {net_name}")

        if self.resource_listener:
            self.resource_listener.on_deleted(source=self, provider=self, resource=net)
