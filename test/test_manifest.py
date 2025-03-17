import os
import unittest
import pytest
import re
import json
import string
import random
import sys

from sense.client.workflow_combined_api import WorkflowCombinedApi

# Append root for proper imports
sys.path.append('')
#

#
from sense.client.intent_api import IntentApi
from sense.client.instance_api import InstanceApi
from sense.common import loadJSON


#


class TestManifestApi(unittest.TestCase):
    def setUp(self) -> None:
        self.client = WorkflowCombinedApi()

    def test_manifest_create(self):
        #
        # TESTING: - /service/manifest/{siUUID}
        template = loadJSON("requests/manifest-1.json")
        self.client.si_uuid = "56be2b77-4e15-4f70-aee5-2f281f03581a"
        res = self.client.manifest_create(json.dumps(template))
        print()
        print(res)
        assert res

if __name__ == '__main__':
    unittest.main()
