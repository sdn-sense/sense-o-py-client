from sense.workflow.provider.api.provider import Provider
from sense.workflow.provider.api.resource_event_listener import ResourceListener
from sense.workflow.base.exceptions import ControllerException
from sense.workflow.base.constants import Constants
from sense.workflow.base.config_models import Config


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


def populate_layer3_config(*, networks: list):
    for network in networks:
        layer3 = network.attributes.get(Constants.RES_LAYER3)

        if not layer3:
            continue

        if Constants.RES_SUBNET not in layer3.attributes:
            raise ControllerException(f"network {network.label} must have a subnet in its layer3 config")

        subnet = layer3.attributes[Constants.RES_SUBNET]

        try:
            addr = subnet[:subnet.rindex("/")]
            prefix = addr[:addr.rindex(".")]

            if Constants.RES_NET_GATEWAY not in layer3.attributes:
                layer3.attributes[Constants.RES_NET_GATEWAY] = prefix + ".1"

            if Constants.RES_LAYER3_DHCP_START not in layer3.attributes:
                layer3.attributes[Constants.RES_LAYER3_DHCP_START] = prefix + ".2"

            if Constants.RES_LAYER3_DHCP_END not in layer3.attributes:
                layer3.attributes[Constants.RES_LAYER3_DHCP_END] = prefix + ".254"
        except:
            raise ControllerException(f"Error parsing {subnet} for layer3 config in network {network.label}")


def partition_layer3_config(*, networks: list):
    from ipaddress import IPv4Address
    if len(networks) <= 1:
        return

    layer3 = networks[0].attributes.get(Constants.RES_LAYER3)

    if not layer3.attributes.get(Constants.RES_LAYER3_DHCP_START):
        return

    if "/" in layer3.attributes.get(Constants.RES_LAYER3_DHCP_START):
        return

    if "/" in layer3.attributes.get(Constants.RES_LAYER3_DHCP_END):
        return

    layer3 = networks[0].attributes.get(Constants.RES_LAYER3)
    dhcp_start = int(IPv4Address(layer3.attributes.get(Constants.RES_LAYER3_DHCP_START)))
    last = dhcp_end = int(IPv4Address(layer3.attributes.get(Constants.RES_LAYER3_DHCP_END)))
    interval = int((dhcp_end - dhcp_start) / len(networks))

    for index, network in enumerate(networks):
        layer3_config = Config(layer3.type, f"{layer3.name}-{index}", layer3.attributes.copy())
        dhcp_end = dhcp_start + interval

        if dhcp_end > last:
            dhcp_end = last

        layer3_config.attributes[Constants.RES_LAYER3_DHCP_START] = str(IPv4Address(dhcp_start))
        layer3_config.attributes[Constants.RES_LAYER3_DHCP_END] = str(IPv4Address(dhcp_end))
        network.attributes[Constants.RES_LAYER3] = layer3_config
        dhcp_start = dhcp_end + 1
