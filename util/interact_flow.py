#!/usr/bin/env python3
import argparse
import re
import json
import time
import jsonpath_ng

from sense.client.workflow_combined_api import WorkflowCombinedApi
from sense.client.profile_api import ProfileApi
from sense.client.discover_api import DiscoverApi
from sense.client.address_api import AddressApi

SENSE_REQ_PROFILE = """
{
  "service_profile_uuid": "04ca4de9-9813-4176-8e8f-a521be453c4b",
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

    # Step 1: fill the profile template with query statements
    # 1a. populate editable fields
    # 2b. ask other than "total-block-maximum-bandwidth"
    # ...
    intent = json.loads(SENSE_REQ_PROFILE)
    if args.name:
        intent['alias'] = args.name[0]
    if args.uuid:
        intent["service_profile_uuid"] = args.uuid
    if args.time:
        jsonpath_expr = jsonpath_ng.parse("$..end-before")
        for match in jsonpath_expr.find(intent):
            path = match.full_path
            path.update(intent, "+" + args.time[0])

    print(intent)

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
        workflowApi.instance_delete()
        raise
    # print(f"computed service instance:\\m{response}")
    orig_intent_uuid = response['intent_uuid']
    # 2c. extract maximum bandwidth
    jsonpath_expr = jsonpath_ng.parse('$.queries[*].results[*].bandwidth')
    max_avail_bw = None
    for match in jsonpath_expr.find(response):
        max_avail_bw = int(match.value)
        break
    if not max_avail_bw:
        raise ValueError('cannot extract bandwidth value from query results')
    print(f"found a path with maximum available bw at {int(max_avail_bw / 1000000)} Mbps")

    # Step 3: finalize the orchestration computation with desired parameter input
    #   3a. Modify/reuse the SENSE_REQ_PROFILE template (or make new):
    #   For example, set the bandwidth to 80% of the max_avail_bw in mbps; get rid of the other queries.
    # TODO: add/edit schedule time fields
    intent["queries"] = [{
        "ask": "edit",
        "options": [
            {
                "data.connections[0].bandwidth.capacity": f"{int(max_avail_bw / 1000000)}"
            }
        ]
    }]
    # 3b. compute with the new intent
    print(f"trying to provision bw at {int(max_avail_bw / 1000000)} Mbps")
    try:
        response = workflowApi.instance_create(json.dumps(intent))
    except ValueError:
        # We may try this a few more times with varying parameters before abort
        # IMPORTANT: some SENSE Site RMs may require bandwidth divisible by 1G (or 1000 Mbps). If is possible that a
        # request with bw smaller than the maximum available still got rejected.
        workflowApi.instance_delete()
        raise
    last_intent_uuid = response['intent_uuid']
    # 3c. provision using the last intent (default).
    # If we have tried a few more intents, more than more would work, we can pick an intent to provision, for example:
    #   workflowApi.instance_operate('provision', sync='true', intent=other_intent_uuid)
    workflowApi.instance_operate('provision', sync='true')

    # Step 4: Check provisioning status
    # 4a.  Upon sync='true' the above provision call will return after "CREATE - COMMITTED"
    orch_status = workflowApi.instance_get_status(si_uuid=workflowApi.si_uuid)
    print(f'provision status={orch_status}')
    # 4b. keep polling until "CREATE - READY" (up to 10 minutes)
    conf_status = 'PENDING'
    for i in range(20):
        time.sleep(30)
        orch_status = workflowApi.instance_get_status(si_uuid=workflowApi.si_uuid)
        if 'READY' in orch_status:
            # 4c. we may also want to check data-plane configuration status
            conf_status = workflowApi.instance_get_status(si_uuid=workflowApi.si_uuid, status='configstate')
            if conf_status in ['UNKNOWN', 'EXPIRED']:
                print(f'Warning! configuration status="{conf_status}"')
            elif conf_status == 'STABLE':
                break
            else:
                print(f'polling: configuration status="{conf_status}"')
    if 'READY' not in orch_status:
        raise ValueError(
            f'SENSE service instance {workflowApi.si_uuid} failed to verify - contact admin for control plane issues')
    if conf_status != 'STABLE':
        raise ValueError(
            f'SENSE service instance {workflowApi.si_uuid} failed to activate - contact admin for data plane issues')
    print(f'SENSE service instance orchestration status="{orch_status}" configuration status="{conf_status}"')

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
    print(f"trying to modify bw to {int(max_avail_bw * 0.5 / 1000000)} Mbps")
    try:
        response = workflowApi.instance_modify(json.dumps(intent), sync='true')
    except ValueError:
        # TODO: handle error (more modify or cancel)
        raise
    print(f"modified service instance: {response}")

    # 5b. handle errors: this modify will fail as 1200M does not satisfy the constraint of 1G bw granularity
    print(f"trying to modify bw to 1200 Mbps")
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
        workflowApi.instance_operate('cancel', force='true', sync='true')
        raise

    # Step 6:  de-provision / cancel
    status = workflowApi.instance_get_status()
    if 'FAILED' in status:
        # 6a. need to force cancel
        workflowApi.instance_operate('cancel', force='true', sync='true')
    elif 'READY' in status:
        # 6b. normal cancel
        workflowApi.instance_operate('cancel', sync='true')
    else:
        print(f"Warning! Cannot cancel service instance in '{status}' status")
    status = workflowApi.instance_get_status()
    print(f"canceled service instance in '{status}' status")



###########################################
# Cosmetic: Colorful Terminal Logging     #
###########################################
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    GREY = '\033[90m'

def format_message(level, message, color):
    return f"{Colors.BOLD}{color}[{level}] {Colors.RESET}{message}"
def log_info(message):
    print(format_message("INFO", message, Colors.BLUE))
def log_success(message):
    print(format_message("SUCCESS", message, Colors.GREEN))
def log_warning(message):
    print(format_message("WARNING", message, Colors.YELLOW))
def log_error(message):
    print(format_message("ERROR", message, Colors.RED))
def log_debug(message):
    print(format_message("DEBUG", message, Colors.CYAN))
def log_critical(message):
    print(format_message("CRITICAL", message, Colors.MAGENTA))
def log_custom(message, color=Colors.WHITE, prefix="LOG"):
    print(format_message(prefix, message, color))
def divider(char="=", length=50, color=Colors.WHITE):
    """Prints a colored divider line."""
    print(f"{color}{char * length}{Colors.RESET}")
def section_header(title, char="=", length=50, color=Colors.WHITE):
    """Prints a centered section header with a divider."""
    padding = (length - len(title) - 2) // 2  # For centering the title
    line = f"{char * padding} {title.upper()} {char * padding}"
    if len(line) < length:
        line += char  # Adjust for odd lengths
    print(f"{color}{line}{Colors.RESET}")

"""
# Example usage
    log_info("This is an informational message.")
    log_success("Operation completed successfully!")
    log_warning("This is a warning. Proceed with caution.")
    log_error("An error occurred while processing the data.")
    log_debug("Debugging variable x: 42")
    log_critical("Critical failure! System shutting down.")
    log_custom("This is a custom log with a star!", color=Colors.YELLOW, prefix="★ CUSTOM ★")

    divider()
    section_header("Starting Process")
    divider("~", 50, color=Colors.BLUE)
    section_header("Process Complete", char="*", color=Colors.GREEN)
"""
