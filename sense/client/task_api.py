#!/usr/bin/env python3
# coding: utf-8
from sense.client.requestwrapper import RequestWrapper
from sense.common import classwrapper


@classwrapper
class TaskApi():

    def __init__(self, req_wrapper=None):
        if req_wrapper is None:
            self.client = RequestWrapper()
        else:
            self.client = req_wrapper
        if 'SI_UUID' in self.client.config:
            self.si_uuid = self.client.config['SI_UUID']
        else:
            self.si_uuid = None

    def get_tasks(self, **kwargs):
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.get_tasks_with_http_info(**kwargs)  # noqa: E501
        else:
            (data) = self.get_tasks_with_http_info(**kwargs)  # noqa: E501
            return data

    def get_tasks_with_http_info(self, **kwargs):
        all_params = ['async_req', '_return_http_data_only', '_preload_content', '_request_timeout', 'assigned']
        params = locals()
        for key, val in params['kwargs'].items():
            if key not in all_params:
                raise TypeError("Got an unexpected keyword argument '%s'"
                                " to method task_query" % key)
            params[key] = val
        del params['kwargs']

        return self.client.request('GET', f'/task/assigned/{kwargs["assigned"]}')

    def get_tasks_agent_status(self, **kwargs):
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.get_tasks_agent_status_with_http_info(**kwargs)  # noqa: E501
        else:
            (data) = self.get_tasks_agent_status_with_http_info(**kwargs)  # noqa: E501
            return data

    def get_tasks_agent_status_with_http_info(self, **kwargs):
        all_params = ['async_req', '_return_http_data_only', '_preload_content', '_request_timeout', 'assigned', 'status']
        params = locals()
        for key, val in params['kwargs'].items():
            if key not in all_params:
                raise TypeError("Got an unexpected keyword argument '%s'"
                                " to method task_query" % key)
            params[key] = val
        del params['kwargs']

        return self.client.request('GET', f'/task/assigned/{kwargs["assigned"]}/status/{kwargs["status"]}')

    def get_task(self, **kwargs):
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.get_task_with_http_info(**kwargs)  # noqa: E501
        else:
            (data) = self.get_task_with_http_info(**kwargs)  # noqa: E501
            return data

    def get_task_with_http_info(self, **kwargs):
        all_params = ['async_req', '_return_http_data_only', '_preload_content', '_request_timeout', 'uuid']
        params = locals()
        for key, val in params['kwargs'].items():
            if key not in all_params:
                raise TypeError("Got an unexpected keyword argument '%s'"
                                " to method task_get" % key)
            params[key] = val
        del params['kwargs']

        return self.client.request('GET', f'/task/uuid/{kwargs["uuid"]}')

    def update_task(self, data, **kwargs):
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.update_task_with_http_info(data, **kwargs)  # noqa: E501
        else:
            (data) = self.update_task_with_http_info(data, **kwargs)  # noqa: E501
            return data

    def update_task_with_http_info(self, data, **kwargs):
        all_params = ['async_req', '_return_http_data_only', '_preload_content', '_request_timeout', 'uuid', 'state']
        params = locals()
        for key, val in params['kwargs'].items():
            if key not in all_params:
                raise TypeError("Got an unexpected keyword argument '%s'"
                                " to method task_update" % key)
            params[key] = val
        del params['kwargs']

        return self.client.request('PUT', f'/task/uuid/{kwargs["uuid"]}/{kwargs["state"]}', body_params=data)

    def delete_task(self, **kwargs):
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.delete_task_with_http_info(**kwargs)  # noqa: E501
        else:
            (data) = self.delete_task_with_http_info(**kwargs)  # noqa: E501
            return data

    def delete_task_with_http_info(self, **kwargs):
        all_params = ['async_req', '_return_http_data_only', '_preload_content', '_request_timeout', 'uuid']
        params = locals()
        for key, val in params['kwargs'].items():
            if key not in all_params:
                raise TypeError("Got an unexpected keyword argument '%s'"
                                " to method profile_get" % key)
            params[key] = val
        del params['kwargs']

        return self.client.request('DELETE', f'/task/uuid/{kwargs["uuid"]}')
