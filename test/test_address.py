import os
import unittest
import pytest
import re
import json
import time
import sys

# Append root for proper imports
sys.path.append('')
#

#
from sense.client.address_api import AddressApi
from sense.common import loadJSON
#


class TestAddressApi(unittest.TestCase):

    def setUp(self) -> None:
        self.client = AddressApi()
        self.pool = 'IPv6-Pool-T1'
        self.scope = 'TestScope1'
        # TODO: create test pool update setUp

    def tearDown(self) -> None:
        # TODO: delet test pool update tearDown
        pass

    def test_get_pool(self):
        # - TESTING: GET /address/allocate
        res = self.client.get_allocations(self.pool)
        print(res)

    def test_get_pool_scope(self):
        # - TESTING: GET /address/allocate/{scope}
        res = self.client.get_allocations(self.pool, scope=self.scope)
        print(res)

    def test_allocate_ipv6(self):
        # - TESTING: POST /address/allocate/{pool_name}
        res = self.client.allocate_ipv4_address(self.pool, 'alloc1', batch=3, scope=self.scope)
        print(res)
        res = self.client.allocate_ipv4_address_subnet(self.pool, 'alloc2', batch = 3, netmask='/50', scope=self.scope)
        print(res)
        res = self.client.allocate_ipv4_subnet(self.pool, 'alloc3', netmask='/64', scope=self.scope)
        print(res)


    def test_free_ipv6(self):
        # - TESTING: DELETE /address/allocate/{pool_name}/...
        #res = self.client.free_address(self.pool, name='alloc2', scope=self.scope)
        res = self.client.free_address(self.pool, scope=self.scope, address='2001:48d0:3001:8000::/50')
        print(res)


    def test_affiliate_ipv6(self):
        # - TESTING: POST /address/affiliate/{pool_name}/...
        # res = self.client.affiliate_address(self.pool, 'uri:test:test', scope=self.scope, address='2001:48d0:3001::/50')
        res = self.client.affiliate_address(self.pool, 'uri:test:test2', scope=self.scope, name='2001:48d0:3001::/50')
        print(res)


