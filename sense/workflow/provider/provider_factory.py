from typing import List, Dict

from sense.workflow.base.constants import Constants
from sense.workflow.base.exceptions import ProviderTypeNotSupported, ProviderException
from sense.workflow.provider.provider import Provider


class ProviderFactory:
    def __init__(self):
        self._providers: Dict[str, Provider] = {}

    # noinspection PyBroadException
    def init_provider(self, *, type: str, label: str, name: str, attributes) -> Provider:
        if type not in Constants.PROVIDER_CLASSES:
            raise ProviderTypeNotSupported(type)

        import importlib

        full_name = Constants.PROVIDER_CLASSES.get(type)
        idx = full_name.rindex('.')
        module_name = full_name[:idx]
        class_name = full_name[idx+1:]
        cls = getattr(importlib.import_module(module_name), class_name)
        provider = cls(type=type, label=label, name=name, config=attributes)

        try:
            provider.init()
        except Exception as e:
            raise ProviderException(f"Exception encountered while initializing {label}: {e}")

        self._providers[label] = provider
        return provider

    @property
    def providers(self) -> List[Provider]:
        return list(self._providers.values())

    def has_provider(self, *, label: str) -> bool:
        return label in self._providers

    def get_provider(self, *, label: str) -> Provider:
        return self._providers[label]


default_provider_factory = ProviderFactory()
