from sense.workflow.provider.provider import Service
from sense.workflow.base.utils import get_logger
from . import sense_utils
from .sense_constants import SERVICE_INSTANCE_KEYS
from .sense_exceptions import SenseException
from sense.workflow.base.config_models import Config
from typing import Union, Dict

logger = get_logger()


class SenseService(Service):
    def __init__(self, *, client, label, name: str, profile: str,
                 edit_template: Union[Config, Dict],
                 manifest_template: Union[Config, Dict]):
        super().__init__(label=label, name=name)
        self._client = client
        self.profile = profile

        if isinstance(edit_template, Config):
            self.edit_template: dict = edit_template.attributes
        else:
            self.edit_template: dict = edit_template

        if isinstance(manifest_template, Config):
            self.manifest_template: dict = manifest_template.attributes
        else:
            self.manifest_template: dict = manifest_template

        self.id = ''
        self.state = ''
        self.intents = list()
        self.manifest = dict()

    def create(self):
        si_uuid = sense_utils.find_instance_by_alias(client=self._client, alias=self.name)

        if not si_uuid:
            logger.debug(f"Creating {self.name}")
            si_uuid, status = sense_utils.create_instance(
                client=self._client,
                alias=self.name,
                profile=self.profile,
                edit_template=self.edit_template)
        else:
            logger.debug(f"Found {self.name} {si_uuid}")
            assert si_uuid
            status = sense_utils.instance_get_status(client=self._client, si_uuid=si_uuid)
            logger.info(f"Found existing {self.name} {si_uuid} with status={status}")

        if 'FAILED' in status:
            raise SenseException(f"Found instance {si_uuid} with status={status}")

        if 'CREATE - READY' not in status:
            logger.debug(f"Provisioning {self.name}")
            status = sense_utils.instance_operate(client=self._client, si_uuid=si_uuid)

        if 'CREATE - READY' not in status:
            raise Exception(f"Creation failed for {si_uuid} {status}")

        logger.debug(f"Retrieving details {self.name} {status}")
        instance_dict = sense_utils.service_instance_details(client=self._client, si_uuid=si_uuid)

        import json

        logger.info(f"Retrieved details {self.name} {status}: \n{ json.dumps(instance_dict, indent=2)}")

        for key in SERVICE_INSTANCE_KEYS:
            assert key in instance_dict

        self.id = instance_dict['referenceUUID']
        self.state = instance_dict['state']
        self.intents = instance_dict['intents']

        if not self.manifest_template:
            return

        assert isinstance(self.manifest_template, dict)
        self.manifest = sense_utils.manifest_create(client=self._client,
                                                    si_uuid=si_uuid, template=self.manifest_template)
        logger.info(f"Retrieved manifest {self.name}: \n{json.dumps(self.manifest, indent=2)}")

    def delete(self):
        si_uuid = sense_utils.find_instance_by_alias(client=self._client, alias=self.name)

        logger.debug(f"Deleting {self.name} {si_uuid}")

        if si_uuid:
            sense_utils.delete_instance(client=self._client, si_uuid=si_uuid)
            logger.debug(f"Deleted {self.name} {si_uuid}")
