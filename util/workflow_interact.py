#!/usr/bin/env python3
# A script intended to show an example of how a client should interact with SENSE-O in a realistic workflow.

import argparse
import sys
import json
import time
import jsonpath_ng
import logger

from sense.client.workflow_combined_api import WorkflowCombinedApi
from sense.client.address_api import AddressApi
from sense.client.discover_api import DiscoverApi


SENSE_REQ_PROFILE = """
{
  "service_profile_uuid": "061a29bd-c803-4271-8551-1df656ada4be",
  "queries": [
    {
      "ask": "edit",
      "options": [
        {
          "data.connections[0].bandwidth.capacity": "0"
        }
      ]
    },
    {
      "ask": "total-block-maximum-bandwidth",
      "options": [
        {
            "name": "Connection 1",
            "start": "now",
            "end-before": "+1h"
        }
      ]
    }
  ]
}
"""

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    operations = parser.add_mutually_exclusive_group()
    parser.add_argument("-u", "--uuid", action="append",
                        help="service profile uuid")
    parser.add_argument("-n", "--name", action="append",
                        help="service instance")
    parser.add_argument("-t", "--time", action="append",
                        help="bandwidth lifetime")
    args = parser.parse_args()

    # TODO: Step 0: AddressAPI and DiscoverAPI queries to prepare workflow specific params

    # Step 1: fill the profile template with query statements
    # 1a. populate editable fields
    # 2b. ask other than "total-block-maximum-bandwidth"
    # ...
    intent = json.loads(SENSE_REQ_PROFILE)
    if args.name:
        intent['alias'] = args.name[0]
    if args.uuid:
        intent["service_profile_uuid"] = args.uuid[0]
    if args.time:
        jsonpath_expr = jsonpath_ng.parse("$..end-before")
        for match in jsonpath_expr.find(intent):
            path = match.full_path
            path.update(intent, "+" + args.time[0])
    logger.section_header("Interactive SENSE Workflow")
    logger.debug(f"start with intent #1: {json.dumps(intent)}")
    logger.divider()

    # Step 2: query for a max. bandwidth path for next CONST_BW_LIFETIME (hours)
    workflowApi = WorkflowCombinedApi()
    # 2a. create a new instance. `workflowApi.si_uuid` is a session ID to access the instance context until deleted.
    workflowApi.instance_new()
    try:
        # 2b. Perform the first orchestration computation of a feasible path and also query for the maximum possible
        #     bandwidth reservable on the path for the given period of time.
        response = workflowApi.instance_create(json.dumps(intent))
    except ValueError:
        # 2c. Handle the error. The instance does not have to be deleted. If you are not finished with this workflow,
        #     we recommend you use the same instance (with `workflowApi.si_uuid`) for continuing negotiation.
        """ Alternatively we can update some params and try recompute.
        jsonpath_expr = jsonpath_ng.parse("$..end-before")
        for match in jsonpath_expr.find(intent):
            path = match.full_path
            path.update(intent, "+24h") 
            response = workflowApi.instance_create(json.dumps(intent))
            ... 
        """
        # TODO: Provide an iterative function that calls with a sequence of modifying criteria. Upon failed computation
        #       attempt, a next attempt will be made following the sequence until success or sequence exhausted.
        logger.error("failed to compile intent #1")
        workflowApi.instance_delete()
        logger.info("instance deleted w/o provisioning")
        sys.exit()
    # print(f"computed service instance:\\m{response}")
    orig_intent_uuid = response['intent_uuid']
    # 2c. extract maximum bandwidth
    jsonpath_expr = jsonpath_ng.parse('$.queries[*].results[*].bandwidth')
    max_avail_bw = None
    for match in jsonpath_expr.find(response):
        max_avail_bw = int(match.value)
        break
    if not max_avail_bw:
        logger.error('cannot extract bandwidth value from query results')
        logger.info(f"service instance {workflowApi.si_uuid} - end of workflow")
        sys.exit()

    logger.info(f"found a path with maximum available bw at {int(max_avail_bw / 1000000)} Mbps")
    logger.divider()

    # Step 3: finalize the orchestration computation with desired parameter input
    #   3a. Modify/reuse the SENSE_REQ_PROFILE template (or make new):
    #   For example, set the bandwidth to 80% of the max_avail_bw in mbps; get rid of the other queries.
    # TODO: edit schedule time fields (service profile also has to add schedule statements)
    # use_bw = int(max_avail_bw / 1000000)
    use_bw = 2000
    intent["queries"] = [{
        "ask": "edit",
        "options": [
            {
                "data.connections[0].bandwidth.capacity": f"{use_bw}"
            }
        ]
    }]
    # 3b. compute with the new intent
    logger.info(f"trying to provision bw at {use_bw} Mbps with updated intent #2")
    logger.debug(f"proceed with intent #2: {intent}")
    try:
        response = workflowApi.instance_create(json.dumps(intent))
    except ValueError:
        # We may try this a few more times with varying parameters before abort
        # IMPORTANT: some SENSE Site RMs may require bandwidth divisible by 1G (or 1000 Mbps). If is possible that a
        # request with bw smaller than the maximum available still got rejected.
        logger.error("failed to compile intent #2")
        workflowApi.instance_delete()
        logger.info("instance deleted w/o provisioning")
        sys.exit()
    last_intent_uuid = response['intent_uuid']
    # 3c. provision using the last intent (default).
    # If we have tried a few more intents, more than more would work, we can pick an intent to provision, for example:
    #   workflowApi.instance_operate('provision', sync='true', intent=other_intent_uuid)
    workflowApi.instance_operate('provision', sync='true')
    # 4c.  Upon sync='true' the above provision call will return after "CREATE - COMMITTED"
    orch_status = workflowApi.instance_get_status(si_uuid=workflowApi.si_uuid)
    logger.debug(f'provision status={orch_status}')

    logger.divider()

    # Step 4: Check provisioning status
    # 4a. keep polling until "CREATE - READY" (up to 10 minutes)
    conf_status = 'PENDING'
    for i in range(20):
        time.sleep(30)
        orch_status = workflowApi.instance_get_status(si_uuid=workflowApi.si_uuid)
        if 'READY' in orch_status:
            # 4c. we may also want to check data-plane configuration status
            conf_status = workflowApi.instance_get_status(si_uuid=workflowApi.si_uuid, status='configstate')
            if conf_status in ['UNKNOWN', 'EXPIRED']:
                logger.warning(f'instance configuration status="{conf_status}"')
            elif conf_status == 'STABLE':
                break
            else:
                logger.debug(f'polling instance: configuration status="{conf_status}"')
    if 'READY' not in orch_status:
        logger.error(
            f'SENSE service instance {workflowApi.si_uuid} failed to verify - contact admin for control plane issues')
        sys.exit()
    if conf_status != 'STABLE':
        logger.error(
            f'SENSE service instance {workflowApi.si_uuid} failed to activate - contact admin for data plane issues')
        sys.exit()
    logger.success(f'SENSE service instance orchestration status="{orch_status}" configuration status="{conf_status}"')
    logger.divider()

    # Step 5: modify
    # 5a. change intent - example: use full available bandwidth
    intent["queries"] = [{
        "ask": "edit",
        "options": [
            {
                "data.connections[0].bandwidth.capacity": f"{int(max_avail_bw * 0.5 / 1000000)}"
            }
        ]
    }]
    logger.info(f"trying to modify bw to {int(max_avail_bw * 0.5 / 1000000)} Mbps")
    logger.debug(f"proceed with intent #3: {intent}")
    try:
        response = workflowApi.instance_modify(json.dumps(intent), sync='true')
    except ValueError:
        # TODO: handle error (more modify or cancel)
        logger.error(
            f'SENSE service instance {workflowApi.si_uuid} failed to modify - exit')
        sys.exit()
    logger.success(f"modified service instance: {response}")

    # 5b. handle errors: this modify will fail as 1200M does not satisfy the constraint of 1G bw granularity
    logger.warning(f"trying to modify bw to 1200 Mbps")
    intent["queries"] = [{
        "ask": "edit",
        "options": [
            {
                "data.connections[0].bandwidth.capacity": "1200"
            }
        ]
    }]
    try:
        response = workflowApi.instance_modify(json.dumps(intent), sync='true')
    except ValueError:
        # 5c. force-cancel the failed modify (or more modify...)
        logger.error(f'SENSE service instance {workflowApi.si_uuid} failed to modify - force cancel')
        workflowApi.instance_operate('cancel', force='true', sync='true')
        logger.info(f"service instance {workflowApi.si_uuid} - end of workflow")
        sys.exit()
    logger.divider()
    # Step 6:  de-provision / cancel
    status = workflowApi.instance_get_status()
    if 'FAILED' in status:
        # 6a. need to force cancel
        workflowApi.instance_operate('cancel', force='true', sync='true')
    elif 'READY' in status and 'CANCEL' not in status:
        # 6b. normal cancel
        workflowApi.instance_operate('cancel', sync='true')
    else:
        logger.warning(f"Cannot cancel service instance in '{status}' status")
    status = workflowApi.instance_get_status()
    logger.success(f"canceled service instance in '{status}' status")
    logger.section_header("End of Workflow")



