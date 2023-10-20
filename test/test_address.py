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
        self.scope = 'TestScope2'
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

    def test_allocate_ipv4(self):
        # - TESTING: POST /address/allocate/{pool_name}
        res = self.client.allocate_ipv4_address(self.pool, 'alloc1', batch=3, scope=self.scope)
        print(res)
        res = self.client.allocate_ipv4_address_subnet(self.pool, 'alloc2', batch = 3, netmask='/50', scope=self.scope)
        print(res)
        res = self.client.allocate_ipv4_subnet(self.pool, 'alloc3', netmask='/64', scope=self.scope)
        print(res)