import json
from types import SimpleNamespace

from sense.client.discover_api import DiscoverApi
from sense.client.profile_api import ProfileApi
from sense.client.workflow_combined_api import WorkflowCombinedApi
from sense.workflow.base.utils import get_logger
from .sense_constants import *
from .sense_exceptions import SenseException

logger = get_logger()


def describe_profile(*, client, uuid: str):
    profile_api = ProfileApi(req_wrapper=client)
    profile_details = profile_api.profile_describe(uuid)
    profile_details = json.loads(json.dumps(profile_details), object_hook=lambda dct: SimpleNamespace(**dct))

    if hasattr(profile_details, "edit"):
        from requests import utils

        for ns in profile_details.edit:
            ns.path = utils.unquote(ns.path)

            if hasattr(ns, 'valid'):
                ns.valid = utils.unquote(ns.valid)

    return profile_details


def get_profile_uuid(*, client, profile):
    profile_api = ProfileApi(req_wrapper=client)

    try:
        profile = profile_api.profile_search_get_with_http_info(search=profile)
        profile_uuid = profile['uuid']
        return profile_uuid
    except Exception as e:
        raise SenseException(f"Exception searching for profile:{e}")


def create_instance(*, client, profile, alias, edit_template):
    profile_uuid = get_profile_uuid(client=client, profile=profile)
    workflow_api = WorkflowCombinedApi(req_wrapper=client)
    workflow_api.instance_new()
    intent = {SENSE_PROFILE_UID: profile_uuid, "alias": alias}
    profile_details = describe_profile(client=client, uuid=profile_uuid)

    logger.debug(f'Profile Details: {profile_details}')

    if hasattr(profile_details, "edit"):
        edit_entries = profile_details.edit
        temp_entries = [e.__dict__ for e in edit_entries]
        logger.info(f'Edit Entries: {json.dumps(temp_entries, indent=2)}')

    options = []

    for k, v in edit_template.items():
        options.append({k: str(v)})

    if options:
        query = dict([("ask", "edit"), ("options", options)])
        intent["queries"] = [query]

    logger.info(f'Intent: {json.dumps(intent, indent=2)}')
    intent = json.dumps(intent)
    logger.info(f"creating instance: {alias}")
    response = workflow_api.instance_create(intent, async_req=True)
    return response['service_uuid']


def instance_operate(*, client, si_uuid, action='provision'):
    import time
    from random import randint

    workflow_api = WorkflowCombinedApi(req_wrapper=client)
    status = workflow_api.instance_get_status(si_uuid=si_uuid)

    if "CREATE - COMMITTING" not in status or 'CANCEL - READY' == status:
        try:
            time.sleep(randint(5, 10))
            workflow_api.instance_operate(action, si_uuid=si_uuid, async_req=True)
        except Exception as e:
            logger.warning(f"exception from instance_operate {e}")


def wait_for_instance_create(*, client, si_uuid):
    import time
    from random import randint

    workflow_api = WorkflowCombinedApi(req_wrapper=client)

    for attempt in range(SENSE_RETRY):
        try:
            status = workflow_api.instance_get_status(si_uuid=si_uuid)
            logger.info(f"Waiting on CREATED COMPILED: status={status}:attempt={attempt} out of {SENSE_RETRY}")

            if status in ['CREATE - COMPILED']:
                break

            if 'FAILED' in status:
                break
        except Exception as e:
            logger.warning(f"exception from  instance_get_status {e}")
            pass

        logger.info(f"Waiting on CREATE COMPILED: going to sleep attempt={attempt}")
        time.sleep(randint(30, 35))

    return workflow_api.instance_get_status(si_uuid=si_uuid)


def wait_for_instance_operate(*, client, si_uuid):
    import time
    from random import randint

    workflow_api = WorkflowCombinedApi(req_wrapper=client)

    for attempt in range(SENSE_RETRY):
        try:
            status = workflow_api.instance_get_status(si_uuid=si_uuid)

            if status in ['CREATE - READY', 'REINSTATE - READY', 'MODIFY - READY']:
                return status

            logger.info(f"Waiting on CREATE/REINSTATE/MODIFY-READY: status={status}:attempt={attempt} out of {SENSE_RETRY}")

            if 'FAILED' in status:
                break
        except Exception as e:
            logger.warning(f"exception from  instance_get_status {e}")
            pass

        logger.info(f"Waiting on CREATE/REINSTATE-READY: going to sleep attempt={attempt}")
        time.sleep(randint(30, 35))

    return workflow_api.instance_get_status(si_uuid=si_uuid)


def delete_instance(*, client, si_uuid):
    # import time
    # import random

    workflow_api = WorkflowCombinedApi(req_wrapper=client)
    status = workflow_api.instance_get_status(si_uuid=si_uuid)

    if 'error' in status:
        raise SenseException("error deleting got " + status)

    if 'FAILED' in status:
        instance_dict = service_instance_details(client=client, si_uuid=si_uuid)
        lastState = instance_dict['lastState']

        if lastState in ['INIT', 'COMPILED']:
            return

        raise SenseException(f'cannot delete instance - contact admin. {status}')

    if "CREATE - COMPILED" in status:
        return

    if "CANCEL" not in status:
        if 'CREATE' not in status and 'REINSTATE' not in status and 'MODIFY' not in status:
            raise ValueError(f"cannot cancel an instance in '{status}' status...")

        # TODO REVISIT THIS. time.sleep(random.randint(5, 30))

        try:
            if 'READY' not in status:
                workflow_api.instance_operate('cancel', si_uuid=si_uuid, async_req=True, force=True)
            else:
                workflow_api.instance_operate('cancel', si_uuid=si_uuid, async_req=True)
        except ValueError as ve:
            status = workflow_api.instance_get_status(si_uuid=si_uuid)

            if "CANCEL" not in status:
                raise ve


def wait_for_delete_instance(*, client, si_uuid, alias):
    import time
    import random

    workflow_api = WorkflowCombinedApi(req_wrapper=client)
    status = workflow_api.instance_get_status(si_uuid=si_uuid)

    if 'error' in status:
        raise SenseException("error deleting got " + status)

    if 'FAILED' in status:
        instance_dict = service_instance_details(client=client, si_uuid=si_uuid)
        lastState = instance_dict['lastState']

        if lastState in ['INIT', 'COMPILED']:
            workflow_api.instance_delete(si_uuid=si_uuid)
            return

        raise SenseException(f'cannot delete instance - contact admin. {status}')
    elif "CREATE - COMPILED" in status:
        time.sleep(random.randint(5, 30))
        workflow_api.instance_delete(si_uuid=si_uuid)
        return

    for attempt in range(SENSE_RETRY):
        # This sleep is here to workaround issue where CANCEL-READY shows up prematurely.
        time.sleep(random.randint(30, 35))

        status = workflow_api.instance_get_status(si_uuid=si_uuid)
        logger.info(f"Waiting on CANCEL-READY for {alias}: status={status}:attempt={attempt} out of {SENSE_RETRY}")

        if 'CANCEL - READY' in status:  # This got triggered very quickly ...
            break

        if 'FAILED' in status:
            break

    if 'CANCEL - READY' in status:
        logger.info(f"Deleting instance: {si_uuid}")
        # TODO REVISIT THIS. time.sleep(random.randint(5, 30))
        ret = workflow_api.instance_delete(si_uuid=si_uuid)
        logger.info(f"Deleted instance: {si_uuid}: ret={ret}")
    else:
        raise SenseException(f'cancel operation disrupted - instance not deleted - contact admin. {status}')


def instance_get_status(*, client, si_uuid):
    workflow_api = WorkflowCombinedApi(req_wrapper=client)
    return workflow_api.instance_get_status(si_uuid=si_uuid)


def service_instance_details(*, client, si_uuid):
    discover_api = DiscoverApi(req_wrapper=client)
    response = discover_api.discover_service_instances_get()
    instances = response['instances']

    for instance in instances:
        temp = SimpleNamespace(**instance)

        if temp.referenceUUID == si_uuid:
            instance['intents'] = []

            for intent in temp.intents:
                intent['json'] = json.loads(intent['json'])
                instance['intents'].append(intent)

            return instance

    raise SenseException('no details found')


# TODO Handle error
# /discover/service/instances?search=test-gcp-vms
def find_instance_by_alias(*, client, alias):
    discover_api = DiscoverApi(req_wrapper=client)
    response = discover_api.discover_service_instances_get(search=alias)
    instances = response['instances']

    if not instances:
        return None

    instance = instances[0]
    return instance['referenceUUID']


def manifest_create(*, client, template, alias=None, si_uuid=None):
    import time
    from json.decoder import JSONDecodeError

    si_uuid = si_uuid or find_instance_by_alias(client=client, alias=alias)
    workflow_api = WorkflowCombinedApi(req_wrapper=client)
    template = json.dumps(template)

    for attempt in range(SENSE_RETRY):
        response = workflow_api.manifest_create(template, si_uuid=si_uuid)

        if isinstance(response, dict) and 'jsonTemplate' in response:
            try:
                details = json.loads(response['jsonTemplate'])
                return details
            except JSONDecodeError:
                logger.warning(f"Could not decode sense manifest from response={response}")

        logger.warning(f"got {response} while retrieving manifest. Will retry ....")
        time.sleep(10)

    raise SenseException(f"Unable to retrieve manifest using {template}")
