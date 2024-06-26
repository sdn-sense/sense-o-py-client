#!/usr/bin/env python3
"""SENSE Worker script to test multiple service instance creation and deletion"""
import argparse
import os
import sys
import json
import time
import pprint
import threading

from yaml import safe_dump as ydump
from sense.client.workflow_combined_api import WorkflowCombinedApi
from sense.common import classwrapper, functionwrapper

@functionwrapper
def argParser():
    """Parse input arguments for the script"""
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--uuid", action="append",
                        help="service profile uuid")
    parser.add_argument("-n", "--name", action="append",
                        help="service instance alias name")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="verbose mode providing extra output")
    parser.add_argument("-c", "--count", action="store", default=1, type=int,
                        help="Count of parallel submissions")
    parser.add_argument("-r", "--repeats", action="store", default=1, type=int,
                        help="Count of repeat cancel/resubmit submissions")
    outargs = parser.parse_args()
    return outargs


def timer_func(func):
    """Decorator function to calculate the execution time of a function"""
    def wrap_func(*args, **kwargs):
        t1 = time.time()
        result = func(*args, **kwargs)
        t2 = time.time()
        print(f'== Function {func.__name__!r} executed in {(t2 - t1):.4f}s')
        print(f'== Function {func.__name__!r} returned: {result}')
        print(f'== Function {func.__name__!r} args: {args}')
        print(f'== Function {func.__name__!r} kwargs: {kwargs}')
        return result
    return wrap_func




@classwrapper
class SENSEWorker():
    """SENSE Worker class"""

    def __init__(self, parserArgs, workerid=0):
        self.args = parserArgs
        self.workflowApi = WorkflowCombinedApi()
        self.states = {'create': 'CREATE - READY',
                       'cancel': 'CANCEL - READY',
                       'reprovision': 'REINSTATE - READY'}
        self.timeouts = {'create': 1200,
                         'cancel': 1200,
                         'reprovision': 1200}
        self.timings = {}
        self.starttime = 0
        self.workerid = workerid

    def _logTiming(self, status, call, configstatus, timestamp):
        """Log the timing of the function"""
        self.timings.setdefault(call, {})
        if status not in self.timings[call]:
            self.timings[call][status] = {'entertime': 0, 'configStatus': {}}
            self.timings[call][status]['entertime'] = self.starttime - timestamp
        if configstatus not in self.timings[call][status]['configStatus']:
            self.timings[call][status]['configStatus'][configstatus] = self.starttime - timestamp

    def _validateState(self, status, call, incr=None):
        """Validate the state of the service instance creation"""
        states = []
        print(f"({self.workerid}-{incr}) status={status.get('state')}")
        print(f"({self.workerid}-{incr}) configStatus={status.get('configState')}")
        callt = call if incr is None else f"{call}{incr}"
        self._logTiming(status.get('state'), callt, status.get('configState'), int(time.time()))
        # If state in failed, raise exception
        if status.get('state') == 'CREATE - FAILED':
            raise ValueError(f'({self.workerid}) create failed. Please check')
        if status.get('state') == self.states[call]:
            states.append(True)
        if status.get('configState') == 'STABLE':
            states.append(True)
        else:
            states.append(False)
        if not states:
            return False
        return all(states)

    @timer_func
    def create(self):
        """Create a service instance in SENSE-0"""
        self.starttime = int(time.time())
        self._logTiming('CREATE', 'create', 'create', int(time.time()))
        intent = {'service_profile_uuid': self.args.uuid[0]}
        if args.name:
            intent['alias'] = self.args.name[0]
        self.workflowApi.instance_new()
        try:
            response = self.workflowApi.instance_create(json.dumps(intent))
            print(f"({self.workerid}) creating service instance: {response}")
        except ValueError:
            #self.workflowApi.instance_delete()
            raise
        self.workflowApi.instance_operate('provision', async_req=True, sync=False)
        status = {'state': 'CREATE - PENDING', 'configState': 'UNKNOWN'}
        while not self._validateState(status, 'create'):
            time.sleep(1)
            status = self.workflowApi.instance_get_status(si_uuid=response['service_uuid'], verbose=True)
            self.timeouts['create'] -= 1
            if self.timeouts['create'] <= 0:
                raise ValueError(f'({self.workerid}) create timeout. Please check {response}')
        status = self.workflowApi.instance_get_status(si_uuid=response['service_uuid'], verbose=True)
        print(f'({self.workerid}) Final submit status:')
        self._validateState(status, 'create')
        print(f'({self.workerid}) provision complete')
        return response

    @timer_func
    def _cancelwrap(self, si_uuid, force):
        """Wrap the cancel function"""
        try:
            self.workflowApi.instance_operate('cancel', si_uuid=si_uuid, force=force)
        except ValueError as ex:
            print(f"({self.workerid}) Error: {ex}")
            # Check status and return
            status = self.workflowApi.instance_get_status(si_uuid=si_uuid, verbose=True)
            print(f'({self.workerid}) Final cancel status: {status}')
            # TIMEOUT!!! OR VALUE ERROR? CANCEL FAILED - NEED TO CHECK WHAT IS THE STATUS
            # ENABLE PDB TO BREAK!
            import pdb; pdb.set_trace()
            print(status)

    @timer_func
    def cancel(self, response, incr):
        """Cancel a service instance in SENSE-0"""
        self.starttime = int(time.time())
        self._logTiming('CREATE', f'cancel{incr}', 'create', int(time.time()))
        status = self.workflowApi.instance_get_status(si_uuid=response['service_uuid'])
        if 'error' in status:
            raise ValueError(status)
        if 'CREATE' not in status and 'REINSTATE' not in status and 'MODIFY' not in status:
            raise ValueError(f"({self.workerid}) cannot cancel an instance in '{status}' status...")
        if 'READY' not in status:
            self._cancelwrap(response['service_uuid'], 'true')
        else:
            self._cancelwrap(response['service_uuid'], 'false')
        status = {'state': 'CANCEL - PENDING', 'configState': 'UNKNOWN'}
        while not self._validateState(status, 'cancel', incr):
            time.sleep(1)
            status = self.workflowApi.instance_get_status(si_uuid=response['service_uuid'], verbose=True)
            self.timeouts['cancel'] -= 1
            if self.timeouts['cancel'] <= 0:
                raise ValueError(f'({self.workerid}) cancel timeout. Please check {response}')
        status = self.workflowApi.instance_get_status(si_uuid=response['service_uuid'], verbose=True)
        print(f'({self.workerid}-{incr}) Final cancel status:')
        self._validateState(status, 'cancel', incr)
        print(f'({self.workerid}-{incr}) cancel complete')

    @timer_func
    def reprovision(self, response, incr):
        """Reprovision a service instance in SENSE-0"""
        self.starttime = int(time.time())
        self._logTiming('CREATE', f'reprovision{incr}', 'create', int(time.time()))
        status = self.workflowApi.instance_get_status(si_uuid=response['service_uuid'])
        if 'error' in status:
            raise ValueError(status)
        if 'CANCEL' not in status:
            raise ValueError(f"({self.workerid}) cannot reprovision an instance in '{status}' status...")
        if 'READY' not in status:
            self.workflowApi.instance_operate('reprovision', si_uuid=response['service_uuid'], sync='true', force='true')
        else:
            self.workflowApi.instance_operate('reprovision', si_uuid=response['service_uuid'], sync='true')
        status = {'state': 'REPROVISION - PENDING', 'configState': 'UNKNOWN'}
        while not self._validateState(status, 'reprovision', incr):
            time.sleep(1)
            status = self.workflowApi.instance_get_status(si_uuid=response['service_uuid'], verbose=True)
            self.timeouts['reprovision'] -= 1
            if self.timeouts['reprovision'] <= 0:
                raise ValueError(f'({self.workerid}) reprovision timeout. Please check {response}')
        print(f'({self.workerid}-{incr}) Final reprovision status:')
        self._validateState(status, 'reprovision', incr)
        print(f'({self.workerid}-{incr}) reprovision complete')

    def startwork(self, repeat=0):
        """Start loop work"""
        try:
            response = self.create()
            for repc in range(repeat):
                self.cancel(response, repc)
                self.reprovision(response, repc)
            self.cancel(response, repeat)
        except:
            print(f"({self.workerid}) Error: {sys.exc_info()}")
        print(f"({self.workerid}) Final timings:")
        pprint.pprint(self.timings)
        # Write timings into yaml file
        os.makedirs('timings', exist_ok=True)
        with open(f'timings/timings-{self.workerid}.yaml', 'w', encoding="utf-8") as fd:
            fd.write(ydump(self.timings))
        sys.exit(0)



if __name__ == "__main__":
    args = argParser()
    if args.verbose:
        print("Verbose mode enabled")
    if args.uuid:
        print(f"UUIDs provided: {args.uuid}")
    if args.name:
        print(f"Names provided: {args.name}")
    if args.count:
        print(f"Count of parallel submissions: {args.count}")
    if args.repeats:
        print(f"Count of repeat cancel/resubmit submissions: {args.repeats}")
    # Start multiple trheads based on passed config parameters
    threads = []
    if args.count == 1:
        print("Starting single thread")
        worker = SENSEWorker(args)
        worker.startwork(args.repeats+1)
    elif args.count > 1:
        print("Starting multiple threads")
        for i in range(args.count):
            worker = SENSEWorker(args, i)
            thworker = threading.Thread(target=worker.startwork, args=(args.repeats+1,))
            threads.append(thworker)
            thworker.start()
        print('join all threads and wait for finish')
        for t in threads:
            t.join()
        print('all threads finished')
