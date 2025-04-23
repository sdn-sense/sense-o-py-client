import copy
import logging
from typing import List, Union, Dict

from sense.workflow.base.config import WorkflowConfig
from sense.workflow.base.config_models import ResourceConfig, ProviderConfig
from sense.workflow.base.constants import Constants
from sense.workflow.base.exceptions import ControllerException
from sense.workflow.base.state_models import ResourceState, ProviderState
from sense.workflow.base.utils import get_logger
from sense.workflow.provider.provider import Provider
from sense.workflow.provider.provider_factory import ProviderFactory, default_provider_factory
from sense.workflow.provider.resource_event_listener import ResourceListener


class Controller:
    def __init__(self, *, config: WorkflowConfig, logger: Union[logging.Logger, None] = None):
        import copy

        self.config = copy.deepcopy(config)
        self.logger = logger or get_logger()
        self.provider_factory: Union[ProviderFactory, None] = None
        self.resources: List[ResourceConfig] = []
        self.resource_listener = ControllerResourceListener()

    def init(self, *, session: str,
             provider_factory: ProviderFactory = default_provider_factory,
             provider_states: List[ProviderState]):
        init_provider_map: Dict[str, bool] = dict()

        for provider_config in self.config.get_provider_configs():
            init_provider_map[provider_config.label] = False

        for resource in self.config.get_resource_configs():
            count = resource.attributes.get(Constants.RES_COUNT, 1)
            init_provider_map[resource.provider.label] = init_provider_map[resource.provider.label] or count > 0

        for provider_state in provider_states:
            init_provider_map[provider_state.label] = init_provider_map[provider_state.label] \
                                                      or len(provider_state.states()) > 0

        for provider_config in self.config.get_provider_configs():
            if not init_provider_map[provider_config.label]:
                self.logger.warning(f"Skipping initialization of {provider_config.label}: no resources")
                continue

            name = provider_config.attributes.get('name')
            name = f"{session}-{name}" if name else session
            provider = provider_factory.init_provider(type=provider_config.type,
                                                      label=provider_config.label,
                                                      name=name,
                                                      attributes=provider_config.attributes)
            saved_state = next(filter(lambda s: s.label == provider.label, provider_states), None)
            provider.set_saved_state(saved_state)

        self.resources = self.config.get_resource_configs()

        self.provider_factory = provider_factory
        providers = self.provider_factory.providers
        self.resource_listener.set_providers(providers)

        for provider in providers:
            provider.set_resource_listener(self.resource_listener)

        for resource in self.resources:
            resource_dict = resource.attributes
            resource_dict[Constants.RES_COUNT] = resource_dict.get(Constants.RES_COUNT, 1)
            resource_dict[Constants.RES_NAME_PREFIX] = resource.name
            resource_dict[Constants.CONFIG] = resource_dict.copy()
            resource_dict[Constants.RES_TYPE] = resource.type
            resource_dict[Constants.LABEL] = resource.label
            resource_dict[Constants.EXTERNAL_DEPENDENCIES] = list()
            resource_dict[Constants.RESOLVED_EXTERNAL_DEPENDENCIES] = list()
            resource_dict[Constants.INTERNAL_DEPENDENCIES] = list()
            resource_dict[Constants.RESOLVED_INTERNAL_DEPENDENCIES] = list()
            resource_dict[Constants.SAVED_STATES] = list()

            for dependency in resource.dependencies:
                if dependency.is_external:
                    resource_dict[Constants.EXTERNAL_DEPENDENCIES].append(dependency)
                else:
                    resource_dict[Constants.INTERNAL_DEPENDENCIES].append(dependency)

    def plan(self, provider_states: List[ProviderState]):
        resources = self.resources
        resource_state_map = Controller._build_state_map(provider_states)
        self.logger.info(f"Starting PLAN_PHASE for {len(resources)} resource(s)")
        pf = self.provider_factory
        resources_labels = [r.label for r in resources]
        planned_resources = []

        for resource in resources:
            resource_dict = resource.attributes
            label = resource.provider.label
            provider = pf.get_provider(label=label)
            creation_details = resource_dict[Constants.RES_CREATION_DETAILS] = {}
            creation_details['resources'] = {}
            creation_details['resources'][resource.label] = []
            creation_details['total_count'] = resource_dict[Constants.RES_COUNT]
            creation_details['failed_count'] = 0
            creation_details['created_count'] = 0
            creation_details['in_config_file'] = True
            creation_details['provider_supports_modifiable'] = provider.supports_modify()

            if resource.label in resource_state_map:
                resource_dict = resource.attributes
                resource_dict[Constants.RES_CREATION_DETAILS].update(
                    provider.saved_state.creation_details[resource.label])
                resource_dict[Constants.RES_CREATION_DETAILS]['total_count'] = resource_dict[Constants.RES_COUNT]

            planned_resources.append(resource)

        for state_label, states in resource_state_map.items():
            if state_label not in resources_labels:
                state = states[0]
                resource_dict = state.attributes.copy()
                provider_state = resource_dict.pop(Constants.PROVIDER_STATE)
                provider = pf.get_provider(label=provider_state.label)
                creation_details: Dict = copy.deepcopy(provider_state.creation_details[state_label])
                creation_details['in_config_file'] = False
                creation_details['provider_supports_modifiable'] = provider.supports_modify()
                var_name, _ = tuple(provider_state.label.split('@'))
                provider_config = ProviderConfig(type=provider.type, name=var_name, attrs=provider.config)

                resource_dict = {}
                var_name, _ = tuple(state.label.split('@'))

                if var_name != creation_details['name_prefix']:
                    resource_dict['name'] = creation_details['name_prefix']

                resource_config = ResourceConfig(type=state.type, name=var_name, provider=provider_config,
                                                 attrs=resource_dict)
                resource_dict[Constants.RES_TYPE] = state.type
                resource_dict[Constants.RES_NAME_PREFIX] = creation_details['name_prefix']
                resource_dict[Constants.LABEL] = resource_config.label
                resource_dict[Constants.EXTERNAL_DEPENDENCIES] = list()
                resource_dict[Constants.RESOLVED_EXTERNAL_DEPENDENCIES] = list()
                resource_dict[Constants.INTERNAL_DEPENDENCIES] = list()
                resource_dict[Constants.RESOLVED_INTERNAL_DEPENDENCIES] = list()
                resource_dict[Constants.SAVED_STATES] = list()
                resource_dict[Constants.RES_COUNT] = creation_details['total_count']
                resource_dict[Constants.RES_CREATION_DETAILS] = creation_details
                resource_dict[Constants.CONFIG] = creation_details.pop(Constants.CONFIG)
                planned_resources.append(resource_config)

        self.resources = planned_resources

    def add(self, provider_states: List[ProviderState]):
        resources = self.resources
        self.logger.info(f"Starting ADD_PHASE: Calling ADD ... for {len(resources)} resource(s)")

        exceptions = []
        for resource in resources:
            label = resource.provider.label
            provider = self.provider_factory.get_provider(label=label)

            try:
                provider.validate_resource(resource=resource.attributes)
            except Exception as e:
                exceptions.append(e)
                self.logger.error(e, exc_info=True)

        if exceptions:
            raise ControllerException(exceptions)

        exceptions = []
        resource_state_map = Controller._build_state_map(provider_states)
        for resource in resources:
            label = resource.provider.label
            provider = self.provider_factory.get_provider(label=label)

            if resource.label in resource_state_map:
                resource.attributes[Constants.SAVED_STATES] = resource_state_map[resource.label]

            try:
                provider.add_resource(resource=resource.attributes)
            except Exception as e:
                exceptions.append(e)
                self.logger.error(e, exc_info=True)

        if exceptions:
            raise ControllerException(exceptions)

    def apply(self, provider_states: List[ProviderState]):
        resources = self.resources
        self.logger.info(f"Starting APPLY_PHASE for {len(resources)} resource(s)")
        resource_state_map = Controller._build_state_map(provider_states)
        exceptions = []

        create_and_wait_resource_labels = set()

        for resource in resources:
            resource_dict = resource.attributes

            for dependency in resource_dict[Constants.EXTERNAL_DEPENDENCIES]:
                create_and_wait_resource_labels.add(dependency.resource.label)

            if resource.label in resource_state_map:
                resource.attributes[Constants.SAVED_STATES] = resource_state_map[resource.label]

        for resource in resources:
            if resource.label in create_and_wait_resource_labels:
                provider = self.provider_factory.get_provider(label=resource.provider.label)

                try:
                    provider.create_resource(resource=resource.attributes)
                    provider.wait_for_create_resource(resource=resource.attributes)
                except Exception as e:
                    exceptions.append(e)
                    self.logger.error(e, exc_info=True)

        if exceptions:
            raise ControllerException(exceptions)

        exceptions = []

        for resource in resources:
            if resource.label not in create_and_wait_resource_labels:
                provider = self.provider_factory.get_provider(label=resource.provider.label)

                try:
                    provider.create_resource(resource=resource.attributes)
                except Exception as e:
                    exceptions.append(e)
                    self.logger.error(e, exc_info=True)

        if exceptions:
            raise ControllerException(exceptions)

        exceptions = []

        for resource in resources:
            if resource.label not in create_and_wait_resource_labels:
                provider = self.provider_factory.get_provider(label=resource.provider.label)

                try:
                    provider.wait_for_create_resource(resource=resource.attributes)
                except Exception as e:
                    exceptions.append(e)
                    self.logger.error(e, exc_info=True)

        if exceptions:
            raise ControllerException(exceptions)

    @staticmethod
    def _build_state_map(provider_states: List[ProviderState]) -> Dict[str, List[ResourceState]]:
        resource_state_map = dict()

        for provider_state in provider_states:
            temp_list = provider_state.states()

            for state in temp_list:
                state.attributes[Constants.PROVIDER_STATE] = provider_state

                if state.label in resource_state_map:
                    resource_state_map[state.label].append(state)
                else:
                    resource_state_map[state.label] = [state]

        return resource_state_map

    def destroy(self, *, provider_states: List[ProviderState]):
        exceptions = []
        resource_state_map = Controller._build_state_map(provider_states)
        provider_resource_map = dict()
        failed_resources = []

        for provider_state in provider_states:
            for k in provider_state.failed:
                failed_resources.append(k)

        for provider_state in provider_states:
            key = provider_state.label
            provider_resource_map[key] = list()

        temp = self.resources
        temp.reverse()

        for resource in temp:
            if resource.label in resource_state_map:
                key = resource.provider.label
                external_dependencies = resource.attributes.get(Constants.EXTERNAL_DEPENDENCIES, [])
                external_states = [resource_state_map[ed.resource.label] for ed in external_dependencies]
                resource.attributes[Constants.EXTERNAL_DEPENDENCY_STATES] = sum(external_states, [])
                provider_resource_map[key].append(resource)
                resource.attributes[Constants.SAVED_STATES] = resource_state_map[resource.label]

        remaining_resources = list()
        skip_resources = set()

        for resource in temp:
            if resource.label not in resource_state_map and resource.label not in failed_resources:
                continue

            provider_label = resource.provider.label
            provider = self.provider_factory.get_provider(label=provider_label)
            external_states = resource.attributes.get(Constants.EXTERNAL_DEPENDENCY_STATES, list())

            if resource.label in skip_resources:
                self.logger.warning(f"Skipping deleting resource: {resource} with {provider_label}")
                remaining_resources.append(resource)
                skip_resources.update([external_state.label for external_state in external_states])
                continue

            try:
                provider.delete_resource(resource=resource.attributes)
            except Exception as e:
                self.logger.warning(f"Exception occurred while deleting resource: {e} using {provider_label}",
                                    exc_info=True)
                remaining_resources.append(resource)
                skip_resources.update([external_state.label for external_state in external_states])
                exceptions.append(e)

        if not remaining_resources:
            provider_states.clear()
            return

        provider_states_copy = provider_states.copy()
        provider_states.clear()

        for provider_state in provider_states_copy:
            provider_state.service_states.clear()

            if self.provider_factory.has_provider(label=provider_state.label):
                provider = self.provider_factory.get_provider(label=provider_state.label)
                provider_state.failed = provider.failed

                for remaining_resource in [r for r in remaining_resources if r.provider.label == provider_state.label]:
                    if remaining_resource.label in resource_state_map:
                        resource_states = resource_state_map[remaining_resource.label]
                        provider_state.add_all(resource_states)

                if provider_state.states() or provider_state.failed:
                    provider_states.append(provider_state)

        if exceptions:
            raise ControllerException(exceptions)

    def get_states(self) -> List[ProviderState]:
        provider_states = []

        for provider in self.provider_factory.providers:
            provider_state = provider.get_state()
            provider_states.append(provider_state)

        return provider_states


class ControllerResourceListener(ResourceListener):
    def __init__(self):
        self.providers = list()

    def set_providers(self, providers: list):
        self.providers = providers

    def on_added(self, *, source, provider: Provider, resource: object):
        for temp_provider in self.providers:
            temp_provider.on_added(source=self, provider=provider, resource=resource)

    def on_created(self, *, source, provider: Provider, resource: object):
        for temp_provider in self.providers:
            if temp_provider == provider:
                temp_provider.on_created(source=self, provider=provider, resource=resource)
                break

        for temp_provider in self.providers:
            if temp_provider != provider:
                temp_provider.on_created(source=self, provider=provider, resource=resource)

    def on_deleted(self, *, source, provider: Provider, resource: object):
        for temp_provider in self.providers:
            temp_provider.on_deleted(source=self, provider=provider, resource=resource)
