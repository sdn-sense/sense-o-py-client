#!/usr/bin/env python3
# coding: utf-8
import json

from sense.client.requestwrapper import RequestWrapper
from sense.common import classwrapper


@classwrapper
class FacilitySpaceApi:
    """Client for FacilitySpaceResource endpoints."""

    def __init__(self, req_wrapper=None):
        self.client = req_wrapper if req_wrapper is not None else RequestWrapper()

    def facility_space_get(self, uuid, **kwargs):
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.facility_space_get_with_http_info(uuid, **kwargs)
        return self.facility_space_get_with_http_info(uuid, **kwargs)

    def facility_space_get_with_http_info(self, uuid, **kwargs):
        all_params = ['uuid', 'async_req', '_return_http_data_only', '_preload_content', '_request_timeout']
        params = locals()
        for key, val in params['kwargs'].items():
            if key not in all_params:
                raise TypeError(f"Got an unexpected keyword argument '{key}' to method facility_space_get")
            params[key] = val
        del params['kwargs']

        if 'uuid' not in params or params['uuid'] is None:
            raise ValueError("Missing the required parameter `uuid` when calling `facility_space_get`")

        return self.client.request('GET', f'/facilityspace/{uuid}')

    def facility_space_jobs_get(self, uuid, **kwargs):
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.facility_space_jobs_get_with_http_info(uuid, **kwargs)
        return self.facility_space_jobs_get_with_http_info(uuid, **kwargs)

    def facility_space_jobs_get_with_http_info(self, uuid, **kwargs):
        all_params = ['uuid', 'async_req', '_return_http_data_only', '_preload_content', '_request_timeout']
        params = locals()
        for key, val in params['kwargs'].items():
            if key not in all_params:
                raise TypeError(f"Got an unexpected keyword argument '{key}' to method facility_space_jobs_get")
            params[key] = val
        del params['kwargs']

        if 'uuid' not in params or params['uuid'] is None:
            raise ValueError("Missing the required parameter `uuid` when calling `facility_space_jobs_get`")

        return self.client.request('GET', f'/facilityspace/{uuid}/jobs')

    def facility_space_job_get(self, uuid, job_id, **kwargs):
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.facility_space_job_get_with_http_info(uuid, job_id, **kwargs)
        return self.facility_space_job_get_with_http_info(uuid, job_id, **kwargs)

    def facility_space_job_get_with_http_info(self, uuid, job_id, **kwargs):
        all_params = ['uuid', 'job_id', 'async_req', '_return_http_data_only', '_preload_content', '_request_timeout']
        params = locals()
        for key, val in params['kwargs'].items():
            if key not in all_params:
                raise TypeError(f"Got an unexpected keyword argument '{key}' to method facility_space_job_get")
            params[key] = val
        del params['kwargs']

        if 'uuid' not in params or params['uuid'] is None:
            raise ValueError("Missing the required parameter `uuid` when calling `facility_space_job_get`")
        if 'job_id' not in params or params['job_id'] is None:
            raise ValueError("Missing the required parameter `job_id` when calling `facility_space_job_get`")

        return self.client.request('GET', f'/facilityspace/{uuid}/job/{job_id}')

    def facility_space_job_action(self, uuid, job_id, action, **kwargs):
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.facility_space_job_action_with_http_info(uuid, job_id, action, **kwargs)
        return self.facility_space_job_action_with_http_info(uuid, job_id, action, **kwargs)

    def facility_space_job_action_with_http_info(self, uuid, job_id, action, **kwargs):
        all_params = ['uuid', 'job_id', 'action', 'async_req', '_return_http_data_only', '_preload_content', '_request_timeout']
        params = locals()
        for key, val in params['kwargs'].items():
            if key not in all_params:
                raise TypeError(f"Got an unexpected keyword argument '{key}' to method facility_space_job_action")
            params[key] = val
        del params['kwargs']

        if 'uuid' not in params or params['uuid'] is None:
            raise ValueError("Missing the required parameter `uuid` when calling `facility_space_job_action`")
        if 'job_id' not in params or params['job_id'] is None:
            raise ValueError("Missing the required parameter `job_id` when calling `facility_space_job_action`")
        if 'action' not in params or params['action'] is None:
            raise ValueError("Missing the required parameter `action` when calling `facility_space_job_action`")

        return self.client.request('PUT', f'/facilityspace/{uuid}/job/{job_id}/{action}')

    def facility_space_job_patch(self, uuid, job_id, patch_json, **kwargs):
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.facility_space_job_patch_with_http_info(uuid, job_id, patch_json, **kwargs)
        return self.facility_space_job_patch_with_http_info(uuid, job_id, patch_json, **kwargs)

    def facility_space_job_patch_with_http_info(self, uuid, job_id, patch_json, **kwargs):
        all_params = ['uuid', 'job_id', 'patch_json', 'async_req', '_return_http_data_only', '_preload_content', '_request_timeout']
        params = locals()
        for key, val in params['kwargs'].items():
            if key not in all_params:
                raise TypeError(f"Got an unexpected keyword argument '{key}' to method facility_space_job_patch")
            params[key] = val
        del params['kwargs']

        if 'uuid' not in params or params['uuid'] is None:
            raise ValueError("Missing the required parameter `uuid` when calling `facility_space_job_patch`")
        if 'job_id' not in params or params['job_id'] is None:
            raise ValueError("Missing the required parameter `job_id` when calling `facility_space_job_patch`")
        if patch_json is None:
            raise ValueError("Missing the required parameter `patch_json` when calling `facility_space_job_patch`")

        body = patch_json if isinstance(patch_json, str) else json.dumps(patch_json)
        return self.client.request('PATCH', f'/facilityspace/{uuid}/job/{job_id}', body_params=body)
