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
        self._client = None
        self._being_deleted = dict()

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

    def supports_modify(self):
        return True

    def do_validate_resource(self, *, resource: dict):
        label = resource[Constants.LABEL]
        rtype = resource[Constants.RES_TYPE]

        if rtype not in self.supported_resources:
            raise ResourceTypeNotSupported(f"{rtype} for {label}")

        if Constants.PROFILE not in resource:
            raise SenseException(f"Must have a profile for {label}")

    def do_add_resource(self, *, resource: dict):
        self._init_client()
        label = resource[Constants.LABEL]
        assert resource[Constants.RES_TYPE] in self.supported_resources
        profile = resource[Constants.PROFILE]
        assert profile, f"Must have a profile for {label}"
        edit_template = resource.get("edit_template", dict())
        manifest_template = resource.get("manifest_template", dict())
        count = resource[Constants.RES_COUNT]

        for idx in range(0, count):
            serv_name = self.resource_name(resource, idx)
            serv = SenseService(client=self.client, label=label, name=serv_name, profile=profile,
                                edit_template=edit_template,
                                manifest_template=manifest_template)
            self.services.append(serv)
            self.resource_listener.on_added(source=self, provider=self, resource=serv)

    def do_create_resource(self, *, resource: dict):
        assert resource[Constants.RES_TYPE] in self.supported_resources
        label = resource[Constants.LABEL]
        self._init_client()
        self.logger.info(f"{self.name}: Creating resource {label} ....")

        if self.modified:
            for serv_name in set(self.existing_map[label]) - set(self.added_map[label]):
                self.logger.warning(f"{self.name}:Modified count of resource: Deleting {serv_name} ...")
                saved_state = next(filter(lambda s: s.attributes['name'] == serv_name,
                                          resource[Constants.SAVED_STATES]))
                profile = saved_state.attributes[Constants.PROFILE]
                edit_template = saved_state.attributes["edit_template"]
                manifest_template = saved_state.attributes["manifest_template"]
                serv = SenseService(
                    client=self.client,
                    label=label, name=serv_name, profile=profile,
                    edit_template=edit_template,
                    manifest_template=manifest_template)

                serv.delete()
                self._being_deleted[serv_name] = serv
                self.logger.warning(f"Done deleting sense resource:{serv_name}")

        for serv in filter(lambda s: s.label == label, self.services):
            self.logger.debug(f"Creating resource: {serv.name}")
            serv.create()

    def do_wait_for_create_resource(self, *, resource: dict):
        assert resource[Constants.RES_TYPE] in self.supported_resources
        label = resource[Constants.LABEL]
        self._init_client()
        self.logger.info(f"{self.name}: Waiting on Create resource {label} ....")

        if self.modified:
            for serv_name in set(self.existing_map[label]) - set(self.added_map[label]):
                serv = self._being_deleted.pop(serv_name)
                serv.wait_for_delete()
                self.logger.warning(f"Done waiting on deleting sense resource:{serv_name}")
                self.resource_listener.on_deleted(source=self, provider=self, resource=serv)

        for serv in filter(lambda s: s.label == label, self.services):
            self.logger.debug(f"Waiting on Create resource: {serv.name}")
            serv.wait_for_create()
            self.logger.debug(f"Resource has been created {serv.name}")
            self.resource_listener.on_created(source=self, provider=self, resource=serv)
            self.logger.debug(f"Notified Resource has been created: {serv.name}")

    def do_delete_resource(self, *, resource: dict):
        self._init_client()
        assert self.client
        assert resource[Constants.RES_TYPE] in self.supported_resources
        label = resource[Constants.LABEL]
        logger.info(f"Deleting resource: {label}")
        edit_template = resource.get("edit_template", dict())
        manifest_template = resource.get("manifest_template", dict())
        profile = resource[Constants.PROFILE]
        count = resource[Constants.RES_COUNT]
        services = list()

        for idx in range(0, count):
            serv_name = self.resource_name(resource, idx)
            serv = SenseService(client=self.client,
                                label=label, name=serv_name,
                                profile=profile,
                                edit_template=edit_template,
                                manifest_template=manifest_template)

            serv.delete()
            services.append(serv)

        for serv in services:
            serv.wait_for_delete()
            self.resource_listener.on_deleted(source=self, provider=self, resource=serv)

        logger.info(f"Done Deleting resource: {label}")
