from typing import Dict, List

import yaml

from .config_models import Config, ResourceConfig, BaseConfig, ProviderConfig, Dependency, DependencyInfo
from .resource_models import ResolvedDependency
from .constants import Constants


class BaseState:
    def __init__(self, type: str, label: str, attributes: Dict):
        self.type = type
        self.label = label
        self.attributes = attributes


class ResourceState(BaseState):
    def __init__(self, type: str, label: str, attributes: Dict):
        super().__init__(type, label, attributes)
        self.type = type
        self.label = label
        self.attributes = attributes

    @property
    def name(self) -> str:
        return self.attributes['name']

    @property
    def is_service_state(self):
        return self.type == Constants.RES_TYPE_SERVICE


class ServiceState(ResourceState):
    def __init__(self, *, label, attributes):
        super().__init__(Constants.RES_TYPE_SERVICE, label, attributes)


class ProviderState(BaseState):
    def __init__(self, label, attributes, service_states: List[ServiceState],
                 pending,
                 pending_internal, failed: Dict[str, str], creation_details: Dict):
        super().__init__("provider", label, attributes)
        self.service_states = service_states
        self.pending = pending
        self.pending_internal = pending_internal
        self.failed = failed
        self.creation_details = creation_details

    def add_if_not_found(self, resource_state: ResourceState):
        from typing import cast
        assert resource_state.type in [Constants.RES_TYPE_SERVICE]

        def exists(state, states: list):
            temp = next(filter(lambda s: s.label == state.label and s.name == state.name, states), None)

            return temp is not None

        if exists(resource_state, self.states()):
            return

        if resource_state.is_service_state:
            self.service_states.append(cast(ServiceState, resource_state))
        else:
            raise Exception("Unexpected resource state")

    def add(self, resource_state: ResourceState):
        from typing import cast
        assert resource_state.type in [Constants.RES_TYPE_SERVICE]

        def exists(state, states: list):
            temp = next(filter(lambda s: s.label == state.label and s.name == state.name, states), None)

            return temp is not None

        assert not exists(resource_state, self.states())

        if resource_state.is_service_state:
            self.service_states.append(cast(ServiceState, resource_state))

    def add_all(self, resource_states: List[ResourceState]):
        for resource_state in resource_states:
            self.add(resource_state)

    def states(self) -> List[ResourceState]:
        temp = []
        temp.extend(self.service_states)
        return temp

    def number_of_created_resources(self):
        count = 0

        for creation_detail in self.creation_details.values():
            count += creation_detail['created_count']

        return count

    def number_of_failed_resources(self):
        count = 0

        for creation_detail in self.creation_details.values():
            count += creation_detail['failed_count']

        return count

    def number_of_total_resources(self):
        count = 0

        for creation_detail in self.creation_details.values():
            count += creation_detail['total_count']

        return count


def provider_constructor(loader: yaml.SafeLoader, node: yaml.nodes.MappingNode) -> ProviderState:
    return ProviderState(**loader.construct_mapping(node))


def provider_representer(dumper: yaml.SafeDumper, provider_state: ProviderState) -> yaml.nodes.MappingNode:
    return dumper.represent_mapping("!ProviderState", {
        "label": provider_state.label,
        "attributes": provider_state.attributes,
        "service_states": provider_state.service_states,
        "pending": provider_state.pending,
        "pending_internal": provider_state.pending_internal,
        "failed": provider_state.failed,
        "creation_details": provider_state.creation_details
    })


def base_config_constructor(loader: yaml.SafeLoader, node: yaml.nodes.MappingNode) -> BaseConfig:
    return BaseConfig(**loader.construct_mapping(node))


def base_config_representer(dumper: yaml.SafeDumper, base_config: BaseConfig) -> yaml.nodes.MappingNode:
    return dumper.represent_mapping("!BaseConfig", {
        "type": base_config.type,
        "name": base_config.name,
        "attrs": base_config.attributes
    })


def config_constructor(loader: yaml.SafeLoader, node: yaml.nodes.MappingNode) -> Config:
    return Config(**loader.construct_mapping(node))


def config_representer(dumper: yaml.SafeDumper, config: Config) -> yaml.nodes.MappingNode:
    return dumper.represent_mapping("!Config", {
        "type": config.type,
        "name": config.name,
        "attrs": config.attributes
    })


def provider_config_constructor(loader: yaml.SafeLoader, node: yaml.nodes.MappingNode) -> ProviderConfig:
    return ProviderConfig(**loader.construct_mapping(node))


def provider_config_representer(dumper: yaml.SafeDumper, provider_config: ProviderConfig) -> yaml.nodes.MappingNode:
    return dumper.represent_mapping("!ProviderConfig", {
        "type": provider_config.type,
        "name": provider_config.var_name,
        "attrs": provider_config.attributes
    })


def resource_config_constructor(loader: yaml.SafeLoader, node: yaml.nodes.MappingNode) -> ResourceConfig:
    return ResourceConfig(**loader.construct_mapping(node))


def resource_config_representer(dumper: yaml.SafeDumper, resource_config: ResourceConfig) -> yaml.nodes.MappingNode:
    return dumper.represent_mapping("!ResourceConfig", {
        "type": resource_config.type,
        "name": resource_config.var_name,
        "attrs": resource_config.attributes,
        "provider": resource_config.provider
    })


def service_constructor(loader: yaml.SafeLoader, node: yaml.nodes.MappingNode) -> ServiceState:
    return ServiceState(**loader.construct_mapping(node))


def service_representer(dumper: yaml.SafeDumper, service_state: ServiceState) -> yaml.nodes.MappingNode:
    return dumper.represent_mapping("!ServiceState", {
        "label": service_state.label,
        "attributes": service_state.attributes
    })


def named_tuple(self, data):
    if hasattr(data, '_asdict'):
        if isinstance(data, DependencyInfo):
            data = dict(dependency_info=dict(resource=str(data.resource),
                                             attribute=data.attribute))
        elif isinstance(data, Dependency):
            data = dict(dependency=dict(resource=str(data.resource),
                                        key=data.key,
                                        is_external=data.is_external,
                                        attribute=data.attribute))
        elif isinstance(data, ResolvedDependency):
            data = dict(resolved_dependency=dict(resource_label=data.resource_label,
                                                 attribute=data.attr,
                                                 value=str(data.value)))
        else:
            data = data._asdict()

        return self.represent_dict(data)

    return self.represent_list(data)


def init_loader():
    loader = yaml.SafeLoader
    yaml.add_constructor("!ProviderState", provider_constructor, Loader=loader)
    yaml.add_constructor("!ServiceState", service_constructor, Loader=loader)
    yaml.add_constructor("!ResourceConfig", resource_config_constructor, Loader=loader)
    yaml.add_constructor("!ProviderConfig", provider_config_constructor, Loader=loader)
    yaml.add_constructor("!BaseConfig", base_config_constructor, Loader=loader)
    yaml.add_constructor("!Config", config_constructor, Loader=loader)
    return loader


# noinspection PyTypeChecker
def get_dumper():
    safe_dumper = yaml.SafeDumper
    safe_dumper.add_representer(ProviderState, provider_representer)
    safe_dumper.add_representer(ServiceState, service_representer)
    safe_dumper.add_representer(ResourceConfig, resource_config_representer)
    safe_dumper.add_representer(ProviderConfig, provider_config_representer)
    safe_dumper.add_representer(Config, config_representer)
    safe_dumper.add_representer(BaseConfig, base_config_representer)

    safe_dumper.yaml_multi_representers[tuple] = named_tuple
    return safe_dumper
