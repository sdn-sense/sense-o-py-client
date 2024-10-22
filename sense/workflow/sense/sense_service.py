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

        self.id = str()
        self.state = str()
        self.intents = list()
        self.manifest = dict()

    def create(self):
        si_uuid = sense_utils.find_instance_by_alias(client=self._client, alias=self.name)

        if not si_uuid:
            logger.debug(f"Creating {self.name}")
            si_uuid = sense_utils.create_instance(
                client=self._client,
                alias=self.name,
                profile=self.profile,
                edit_template=self.edit_template)

        status = sense_utils.instance_get_status(client=self._client, si_uuid=si_uuid)
        logger.info(f"Service instance: {self.name} {si_uuid} with status={status}")

        self.id = si_uuid

        if 'INIT' in status:
            status = sense_utils.wait_for_instance_create(client=self._client, si_uuid=si_uuid)

        if 'FAILED' in status:
            raise SenseException(f"Found instance {si_uuid} with status={status}")

        if 'CANCEL - READY' == status:
            logger.info(f"Reprovisioning {self.name}")
            sense_utils.instance_operate(action='reprovision', client=self._client, si_uuid=si_uuid)
        elif 'CREATE - READY' not in status:
            logger.debug(f"Provisioning {self.name}")
            sense_utils.instance_operate(client=self._client, si_uuid=si_uuid)

    def wait_for_create(self):
        si_uuid = self.id
        status = sense_utils.wait_for_instance_operate(client=self._client, si_uuid=si_uuid)

        if status not in ['CREATE - READY', 'REINSTATE - READY']:
            raise SenseException(f"Creation failed for {si_uuid} {status}")

        logger.debug(f"Retrieving details {self.name} {status}")
        instance_dict = sense_utils.service_instance_details(client=self._client, si_uuid=si_uuid)

        import json

        logger.debug(f"Retrieved details {self.name} {status}: \n{ json.dumps(instance_dict, indent=2)}")

        for key in SERVICE_INSTANCE_KEYS:
            assert key in instance_dict

        assert self.id == instance_dict['referenceUUID']
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

    def wait_for_delete(self):
        si_uuid = sense_utils.find_instance_by_alias(client=self._client, alias=self.name)

        logger.debug(f"Deleting {self.name} {si_uuid}")

        if si_uuid:
            sense_utils.wait_for_delete_instance(client=self._client, si_uuid=si_uuid)
            logger.debug(f"Deleted {self.name} {si_uuid}")
