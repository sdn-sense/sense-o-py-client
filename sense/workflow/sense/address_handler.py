from sense.workflow.base.constants import Constants
from sense.workflow.base.utils import get_logger
from .sense_exceptions import SenseException
from ...client.address_api import AddressApi
from sense.workflow.provider.provider import Service

logger = get_logger()


class AddressService(Service):
    def __init__(self, *, client, label, name: str, pool: str, addr_type, scope=None, batch=None, netmask=None):
        super().__init__(label=label, name=name)
        self._client = client
        self.pool = pool
        self.addr_type = addr_type or 'IPv4'
        self.scope = scope or 'default'

        if self.addr_type == 'IPv4':
            self.netmask = netmask or '/32'
        else:
            self.netmask = netmask or '/128'

        self.batch = batch or 'subnet'
        self.address = str()
        self.hosts = list()

    def allocate_address(self):
        address_api = AddressApi(req_wrapper=self._client)
        response = address_api.allocate_address(self.pool, self.addr_type,
                                                self.name, scope=self.scope,
                                                batch=self.batch,
                                                netmask=self.netmask)
        try:
            if len(response) == 0 or "ERROR" in response:
                raise SenseException(f'Address allocate failed for {self.label}')

            from ipaddress import IPv4Network

            self.address = response

            if self.addr_type == 'IPv4':
                netmask = '/32'
            else:
                netmask = '/128'

            self.hosts = [str(host) + netmask for host in IPv4Network(response).hosts()]
        except ValueError as ve:
            raise SenseException(ve)

    # sense_util.py --address free,pool=AES-POOL,address='10.251.85.2/32'
    def free_address(self):
        address_api = AddressApi(req_wrapper=self._client)

        try:
            if self.address:
                response = address_api.free_address(self.pool, scope=self.scope, address=self.address)
            else:
                response = address_api.free_address(self.pool, scope=self.scope, name=self.name)

            if "ERROR" in response:
                raise SenseException(f'Address free failed with option {self.label}')
        except ValueError as ve:
            if "has no allocation matching" not in str(ve):
                raise SenseException(ve)


class AddressHandler:
    def __init__(self, *, provider):
        self.provider = provider

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
    def services(self):
        services = []

        for serv in self.provider.services:
            if isinstance(serv, AddressService):
                services.append(serv)

        return services

    def add_resource(self, *, resource: dict):
        assert Constants.POOL in resource
        assert resource[Constants.RES_COUNT] == 1
        label = resource[Constants.LABEL]
        pool = resource[Constants.POOL]
        addr_type = resource[Constants.ADDR_TYPE]
        assert addr_type in ['IPv4', 'IPv6']
        serv_name = self.provider.resource_name(resource, 0)
        netmask = resource.get(Constants.NET_MASK)
        serv = AddressService(label=label, name=serv_name, client=self.client, pool=pool,
                              netmask=netmask, addr_type=addr_type)
        self.provider.services.append(serv)
        self.resource_listener.on_added(source=self.provider, provider=self.provider, resource=serv)

    def create_resource(self, *, resource: dict):
        assert resource[Constants.RES_COUNT] == 1
        label = resource[Constants.LABEL]

        if self.provider.modified:
            for serv_name in set(self.provider.existing_map[label]) - set(self.provider.added_map[label]):
                serv_name = self.provider.resource_name(resource, 0)
                saved_state = next(filter(lambda s: s.attributes['name'] == serv_name,
                                          resource[Constants.SAVED_STATES]))
                pool = saved_state.attributes[Constants.POOL]
                addr_type = saved_state.attributes[Constants.ADDR_TYPE]
                netmask = saved_state.attributes.get(Constants.NET_MASK)
                serv = AddressService(label=label, name=serv_name, client=self.client, pool=pool,
                                      netmask=netmask, addr_type=addr_type)

                if 'address' in saved_state.attributes and saved_state.attributes['address']:
                    serv.address = saved_state.attributes['address']
                    serv.hosts = saved_state.attributes.get('hosts')
                    logger.info(f'Deleting resource {serv_name} using {serv.address}')
                    serv.free_address()

                self.resource_listener.on_deleted(source=self.provider, provider=self.provider, resource=serv)

        for serv in filter(lambda s: s.label == label, self.services):
            if serv.name in self.provider.existing_map[label]:
                saved_state = next(filter(lambda s: s.attributes['name'] == serv.name,
                                          resource[Constants.SAVED_STATES]), None)

                if saved_state:
                    serv.address = saved_state.attributes['address']
                    serv.hosts = saved_state.attributes['hosts']
                    logger.info(f"Resource: {serv.name} already exists:address={serv.address}")
                    continue

            if Constants.POOL not in resource:
                raise SenseException(f"should not happen. No pool ... {serv.name}")

            logger.info(f"Allocating resource: {serv.name}:{serv.address}")
            serv.allocate_address()

    def wait_for_create_resource(self, *, resource: dict):
        assert resource[Constants.RES_COUNT] == 1
        label = resource[Constants.LABEL]

        for serv in filter(lambda s: s.label == label, self.services):
            logger.debug(f'Resource {serv.name} has been created')
            self.resource_listener.on_created(source=self.provider, provider=self.provider, resource=serv)
            logger.info(f'Notified Resource {serv.name} has been created')

    def delete_resource(self, *, resource: dict):
        assert Constants.POOL in resource
        assert resource[Constants.RES_COUNT] == 1
        label = resource[Constants.LABEL]
        pool = resource[Constants.POOL]
        addr_type = resource[Constants.ADDR_TYPE]
        netmask = resource.get(Constants.NET_MASK)
        serv_name = self.provider.resource_name(resource, 0)
        serv = AddressService(label=label, name=serv_name, client=self.client, pool=pool,
                              netmask=netmask, addr_type=addr_type)
        saved_state = next(filter(lambda s: s.attributes['name'] == serv.name,
                                  resource[Constants.SAVED_STATES]), None)

        if saved_state:
            serv.address = saved_state.attributes['address']

        logger.info(f'Deleting resource {serv_name} using {serv.address}')
        serv.free_address()
        self.resource_listener.on_deleted(source=self.provider, provider=self.provider, resource=serv)
