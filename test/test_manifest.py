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
        template = loadJSON("requests/manifest-2.json")
        self.client.si_uuid = "9d327176-1516-4061-a0d0-660ae866d141"
        res = self.client.manifest_create(json.dumps(template))
        print()
        print(res)
        assert res

if __name__ == '__main__':
    unittest.main()
