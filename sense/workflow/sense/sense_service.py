from sense.workflow.provider.provider import Service
from sense.workflow.base.utils import get_logger
from . import sense_utils
from .sense_constants import SERVICE_INSTANCE_KEYS
from .sense_exceptions import SenseException
from sense.workflow.base.config_models import Config
from typing import Union, Dict
from sense.workflow.base.state_models import ServiceState

logger = get_logger()


class SenseService(Service):
    def __init__(self, *, client, label, name: str, profile: str,
                 edit_template: Union[Config, Dict],
                 manifest_template: Union[Config, Dict],
                 saved_state=Union[ServiceState, Dict]):
        super().__init__(label=label, name=name)
        self._client = client
        self.profile = profile

        if isinstance(edit_template, Config):
            self.edit_template: dict = edit_template.attributes
        else:
            self.edit_template: dict = edit_template

        assert isinstance(self.edit_template, dict)

        if isinstance(manifest_template, Config):
            self.manifest_template: dict = manifest_template.attributes
        else:
            self.manifest_template: dict = manifest_template

        assert isinstance(self.manifest_template, dict)

        self.id = str()
        self.state = str()
        self.intents = list()
        self.manifest = dict()

        if isinstance(saved_state, ServiceState):
            self._saved_state: dict = saved_state.attributes
        else:
            self._saved_state: dict = saved_state

    def create(self):
        self.id = sense_utils.find_instance_by_alias(client=self._client, alias=self.name)

        if not self.id:
            logger.debug(f"Creating {self.name}")
            self.id = sense_utils.create_instance(
                client=self._client,
                alias=self.name,
                profile=self.profile,
                edit_template=self.edit_template)

        status = sense_utils.instance_get_status(client=self._client, si_uuid=self.id)
        logger.info(f"Service instance: {self.name} {self.id} with status={status}")

        if 'CREATE - READY' == status:
            return

        self._saved_state = dict()

        if 'INIT' in status:
            status = sense_utils.wait_for_instance_create(client=self._client, si_uuid=self.id)

        if 'FAILED' in status:
            logger.warning(f"Found instance {self.id} with status={status}. Will try to delete")

            try:
                sense_utils.delete_instance(client=self._client, si_uuid=self.id)
                sense_utils.wait_for_delete_instance(client=self._client, si_uuid=self.id, alias=self.name)
            except Exception as e:
                raise SenseException(f"Got exception while deleting instance {self.id} with status={status}:{e}")

        if 'CANCEL - READY' == status:
            logger.info(f"Reprovisioning {self.name}")
            sense_utils.instance_operate(action='reprovision', client=self._client, si_uuid=self.id)
        elif 'CREATE - READY' not in status:
            logger.debug(f"Provisioning {self.name}")
            sense_utils.instance_operate(client=self._client, si_uuid=self.id)

    def wait_for_create(self):
        si_uuid = self.id
        status = sense_utils.wait_for_instance_operate(client=self._client, si_uuid=si_uuid)

        if status not in ['CREATE - READY', 'REINSTATE - READY', 'MODIFY - READY']:
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

        self.manifest = self._saved_state.get('manifest', dict())

        if self.manifest:
            logger.info(f"Using saved manifest {self.name}: \n{json.dumps(self.manifest, indent=2)}")
            return

        self.manifest = sense_utils.manifest_create(client=self._client,
                                                    si_uuid=si_uuid, template=self.manifest_template)

        logger.info(f"Retrieved manifest {self.name}: \n{json.dumps(self.manifest, indent=2)}")

        if ('terminals' in self.manifest and 'connections' in self.intents[0]['json']['data']
                and 'terminals' in self.intents[0]['json']['data']['connections'][0]):
            adjusted_terminals = list()
            uris = list()

            for terminal in self.intents[0]['json']['data']['connections'][0]['terminals']:
                uris.append(terminal['uri'])

            for uri in uris:
                for terminal in self.manifest['terminals']:
                    if 'port' in terminal and terminal['port'].startswith(uri + ":"):
                        adjusted_terminals.append(terminal)
                        break

            if adjusted_terminals:
                self.manifest['terminals'] = adjusted_terminals
                logger.info(f"Adjusted terminals in manifest {self.name}: \n{json.dumps(self.manifest, indent=2)}")
            else:
                logger.warning(f"Could not adjust terminals in manifest for {self.name}")

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
            sense_utils.wait_for_delete_instance(client=self._client, si_uuid=si_uuid, alias=self.name)
            logger.debug(f"Deleted {self.name} {si_uuid}")
