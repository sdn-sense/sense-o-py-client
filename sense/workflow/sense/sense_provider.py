from sense.workflow.base.exceptions import ResourceTypeNotSupported, ProviderException
from sense.workflow.provider.provider import Provider
from sense.workflow.base.utils import get_logger
from sense.workflow.base.constants import Constants
from .sense_exceptions import SenseException
from .sense_constants import *
from .sense_service import SenseService

logger = get_logger()


class SenseProvider(Provider):
    def __init__(self, *, type, label, name, config: dict):
        super().__init__(type=type, label=label, name=name, logger=logger, config=config)
        self.supported_resources = [Constants.RES_TYPE_SERVICE]
        self._handled_modify = False
        self._client = None

    def setup_environment(self):
        for attr in SENSE_CONF_ATTRS:
            if self.config.get(attr.lower()) is None and self.config.get(attr.upper()) is None:
                raise ProviderException(f"{self.name}: Expecting a value for {attr}")

    def _init_client(self):
        if not self.client:
            self.logger.info(f"{self.name}: Initializing sense client")
            from sense.client.requestwrapper import RequestWrapper

            self._client = RequestWrapper(self.config)
            self.logger.info(f"{self.name}: Initialized sense client")

    @property
    def client(self):
        return self._client

    def do_validate_resource(self, *, resource: dict):
        label = resource[Constants.LABEL]
        rtype = resource[Constants.RES_TYPE]

        if rtype not in self.supported_resources:
            raise ResourceTypeNotSupported(f"{rtype} for {label}")

        if Constants.PROFILE not in resource:
            raise SenseException(f"Must have a profile for {label}")

    def do_add_resource(self, *, resource: dict):
        self._init_client()
        creation_details = resource[Constants.RES_CREATION_DETAILS]

        if not creation_details['in_config_file']:
            return

        label = resource[Constants.LABEL]
        assert resource[Constants.RES_TYPE] in self.supported_resources
        net_name = self.resource_name(resource)
        profile = resource[Constants.PROFILE]
        assert profile, f"Must have a profile for {net_name}"
        edit_template = resource.get("edit_template", dict())
        manifest_template = resource.get("manifest_template", str())
        net = SenseService(client=self.client, label=label, name=net_name, profile=profile,
                           edit_template=edit_template,
                           manifest_template=manifest_template)
        self.services.append(net)
        self.resource_listener.on_added(source=self, provider=self, resource=net)

    def do_create_resource(self, *, resource: dict):
        assert self.client
        assert resource[Constants.RES_TYPE] in self.supported_resources
        label = resource[Constants.LABEL]
        self.logger.info(f"{self.name}: Creating resource {label} ....")

        if not self._handled_modify and self.modified:
            self._handled_modify = True
            self.logger.warning(f"{self.name}:Modified state: Deleting sense resources ...")
            net_name = self.resource_name(resource)
            profile = resource[Constants.PROFILE]
            edit_template = resource.get("edit_template", dict())
            manifest_template = resource.get("manifest_template", str())
            net = SenseService(
                client=self.client,
                label=label, name=net_name, profile=profile,
                edit_template=edit_template,
                manifest_template=manifest_template)

            try:
                net.delete()
                self.logger.warning(f"Deleted sense resource:{net_name}")
            except Exception as e:
                self.logger.error(f"Exception deleting sense resource:{net_name}", e)

        for net in [net for net in self._services if net.label == label]:
            self.logger.debug(f"Creating resource: {net.name}")
            net.create()
            self.resource_listener.on_created(source=self, provider=self, resource=net)
            self.logger.debug(f"Created resource: {net.name}")

    def do_delete_resource(self, *, resource: dict):
        self._init_client()
        assert self.client
        assert resource[Constants.RES_TYPE] in self.supported_resources
        label = resource[Constants.LABEL]
        net_name = self.resource_name(resource)
        logger.info(f"Deleting resource: {net_name}")
        edit_template = resource.get("edit_template", dict())
        manifest_template = resource.get("manifest_template", str())
        profile = resource[Constants.PROFILE]
        net = SenseService(client=self.client,
                           label=label, name=net_name,
                           profile=profile,
                           edit_template=edit_template,
                           manifest_template=manifest_template)

        net.delete()
        logger.debug(f"Done Deleting resource: {net_name}")
        self.resource_listener.on_deleted(source=self, provider=self, resource=net)
