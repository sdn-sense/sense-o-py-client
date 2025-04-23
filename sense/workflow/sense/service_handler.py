from typing import List

from sense.workflow.base.config_models import DependencyInfo
from sense.workflow.base.constants import Constants
from sense.workflow.base.utils import get_logger
from sense.workflow.provider.dependency_util import get_values_for_dependency
from .sense_service import SenseService

logger = get_logger()


class ServiceHandler:
    def __init__(self, *, provider):
        self.provider = provider
        self._being_deleted = dict()

    @property
    def client(self):
        return self.provider.client

    @property
    def name(self):
        return self.provider.name

    @property
    def resource_listener(self):
        return self.provider.resource_listener

    @property
    def services(self) -> List[SenseService]:
        services: List[SenseService] = list()

        for serv in self.provider.services:
            if isinstance(serv, SenseService):
                services.append(serv)

        return services

    @staticmethod
    def _load_manifest_template(config_dir, manifest_template) -> dict:
        import json
        from pathlib import Path
        import os
        import yaml

        if not Path(manifest_template).is_absolute():
            manifest_template = os.path.join(config_dir, manifest_template)

        if manifest_template.endswith('.json'):
            with open(manifest_template, 'r') as fp:
                manifest_template = json.load(fp)
        else:
            with open(manifest_template, 'r') as stream:
                manifest_template = yaml.safe_load(stream)

        return manifest_template

    def add_resource(self, *, resource: dict):
        assert Constants.PROFILE in resource
        label = resource[Constants.LABEL]
        profile = resource[Constants.PROFILE]
        assert profile, f"Must have a profile for {label}"
        edit_template = resource.get(Constants.EDIT_TEMPLATE, dict())
        count = resource[Constants.RES_COUNT]
        manifest_template = resource.get("manifest_template", dict())

        if isinstance(manifest_template, str):
            manifest_template = self._load_manifest_template(resource.get(Constants.CONFIG_DIR), manifest_template)

        for idx in range(0, count):
            serv_name = self.provider.resource_name(resource, idx)
            saved_state = next(filter(lambda s: s.attributes['name'] == serv_name, resource[Constants.SAVED_STATES]),
                               dict())
            serv = SenseService(client=self.client, label=label, name=serv_name, profile=profile,
                                edit_template=edit_template,
                                manifest_template=manifest_template,
                                saved_state=saved_state
                                )
            self.provider.services.append(serv)
            self.resource_listener.on_added(source=self.provider, provider=self.provider, resource=serv)

    def create_resource(self, *, resource: dict):
        label = resource[Constants.LABEL]

        if self.provider.modified:
            for serv_name in set(self.provider.existing_map[label]) - set(self.provider.added_map[label]):
                logger.warning(f"{self.name}:Modified count of resource: Deleting {serv_name} ...")
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
                logger.warning(f"Done deleting sense resource:{serv_name}")

        if Constants.PROFILE not in resource:
            return

        serv = next(filter(lambda s: s.label == label, self.services))

        for k, v in serv.edit_template.items():
            if isinstance(v, DependencyInfo):
                values = get_values_for_dependency(resource=resource,
                                                   attribute=Constants.EDIT_TEMPLATE + "." + k)
                serv.edit_template[k] = values[0]

        logger.debug(f"{self.name}: Creating resource with label {label} ....")

        for serv in filter(lambda s: s.label == label, self.services):
            logger.info(f"Creating resource: {serv.name}")
            serv.create()

    def wait_for_create_resource(self, *, resource: dict):
        label = resource[Constants.LABEL]
        for serv_name, serv in self._being_deleted.copy().items():
            if serv.label != label:
                continue

            logger.info(f"{self.name}: Checking modified in wait_for_create_resource: {serv_name} ....")
            self._being_deleted.pop(serv_name)
            serv.wait_for_delete()
            logger.warning(f"Done waiting on deleting sense resource:{serv_name}")
            self.resource_listener.on_deleted(source=self.provider, provider=self.provider, resource=serv)

        for serv in filter(lambda s: s.label == label, self.services):
            logger.debug(f"Waiting on Create resource: {serv.name}")
            serv.wait_for_create()
            logger.debug(f"Resource has been created {serv.name}")
            self.resource_listener.on_created(source=self.provider, provider=self.provider, resource=serv)
            logger.debug(f"Notified Resource has been created: {serv.name}")

    def delete_resource(self, *, resource: dict):
        assert Constants.PROFILE in resource

        label = resource[Constants.LABEL]
        logger.info(f"Deleting resource: {label}")
        edit_template = resource.get("edit_template", dict())
        profile = resource[Constants.PROFILE]
        count = resource[Constants.RES_COUNT]
        manifest_template = resource.get("manifest_template", dict())

        if isinstance(manifest_template, str):
            manifest_template = self._load_manifest_template(resource.get(Constants.CONFIG_DIR), manifest_template)

        services = list()

        for idx in range(0, count):
            serv_name = self.provider.resource_name(resource, idx)
            serv = SenseService(client=self.client,
                                label=label, name=serv_name,
                                profile=profile,
                                edit_template=edit_template,
                                manifest_template=manifest_template)

            serv.delete()
            services.append(serv)

        for serv in services:
            serv.wait_for_delete()
            self.resource_listener.on_deleted(source=self.provider, provider=self.provider, resource=serv)

        logger.info(f"Done Deleting resource: {label}")
