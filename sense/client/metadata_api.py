#!/usr/bin/env python3
# coding: utf-8
from sense.client.requestwrapper import RequestWrapper
from sense.common import classwrapper


@classwrapper
class MetadataApi():

    def __init__(self, req_wrapper=None):
        if req_wrapper is None:
            self.client = RequestWrapper()
        else:
            self.client = req_wrapper
        if 'SI_UUID' in self.client.config:
            self.si_uuid = self.client.config['SI_UUID']
        else:
            self.si_uuid = None

    def get_metadata(self, **kwargs):
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.get_metadata_with_http_info(**kwargs)  # noqa: E501
        else:
            (data) = self.get_metadata_with_http_info(**kwargs)  # noqa: E501
            return data

    def get_metadata_with_http_info(self, **kwargs):
        all_params = ['async_req', '_return_http_data_only', '_preload_content', '_request_timeout', 'domain', 'name']
        params = locals()
        for key, val in params['kwargs'].items():
            if key not in all_params:
                raise TypeError("Got an unexpected keyword argument '%s'"
                                " to method profile_get" % key)
            params[key] = val
        del params['kwargs']

        return self.client.request('GET', f'/meta/{kwargs["domain"]}/{kwargs["name"]}')

    def post_metadata(self, data, **kwargs):
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.post_metadata_with_http_info(data, **kwargs)  # noqa: E501
        else:
            (data) = self.post_metadata_with_http_info(data, **kwargs)  # noqa: E501
            return data

    def post_metadata_with_http_info(self, data, **kwargs):
        all_params = ['async_req', '_return_http_data_only', '_preload_content', '_request_timeout', 'domain', 'name']
        params = locals()
        for key, val in params['kwargs'].items():
            if key not in all_params:
                raise TypeError("Got an unexpected keyword argument '%s'"
                                " to method profile_get" % key)
            params[key] = val
        del params['kwargs']

        return self.client.request('POST', f'/meta/{kwargs["domain"]}/{kwargs["name"]}', body_params=data)

    def update_metadata(self, data, **kwargs):
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.update_metadata_with_http_info(data, **kwargs)  # noqa: E501
        else:
            (data) = self.update_metadata_with_http_info(data, **kwargs)  # noqa: E501
            return data

    def update_metadata_with_http_info(self, data, **kwargs):
        all_params = ['async_req', '_return_http_data_only', '_preload_content', '_request_timeout', 'domain', 'name']
        params = locals()
        for key, val in params['kwargs'].items():
            if key not in all_params:
                raise TypeError("Got an unexpected keyword argument '%s'"
                                " to method profile_get" % key)
            params[key] = val
        del params['kwargs']

        return self.client.request('PUT', f'/meta/{kwargs["domain"]}/{kwargs["name"]}/update', body_params=data)

    def get_metadata_policies(self, **kwargs):
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.get_metadata_policies_with_http_info(**kwargs)  # noqa: E501
        else:
            (data) = self.get_metadata_policies_with_http_info(**kwargs)  # noqa: E501
            return data

    def get_metadata_policies_with_http_info(self, **kwargs):
        all_params = ['async_req', '_return_http_data_only', '_preload_content', '_request_timeout', 'domain', 'name']
        params = locals()
        for key, val in params['kwargs'].items():
            if key not in all_params:
                raise TypeError("Got an unexpected keyword argument '%s'"
                                " to method profile_get" % key)
            params[key] = val
        del params['kwargs']

        return self.client.request('GET', f'/meta/{kwargs["domain"]}/{kwargs["name"]}/policy')

    def update_metadata_policy(self, data, **kwargs):
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.update_metadata_policy_with_http_info(data, **kwargs)  # noqa: E501
        else:
            (data) = self.update_metadata_policy_with_http_info(data, **kwargs)  # noqa: E501
            return data

    def update_metadata_policy_with_http_info(self, data, **kwargs):
        all_params = ['async_req', '_return_http_data_only', '_preload_content', '_request_timeout', 'domain', 'name']
        params = locals()
        for key, val in params['kwargs'].items():
            if key not in all_params:
                raise TypeError("Got an unexpected keyword argument '%s'"
                                " to method profile_get" % key)
            params[key] = val
        del params['kwargs']

        return self.client.request('POST', f'/meta/{kwargs["domain"]}/{kwargs["name"]}/policy', body_params=data)

    def delete_metadata_policy(self, **kwargs):
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.delete_metadata_policy_with_http_info(**kwargs)  # noqa: E501
        else:
            (data) = self.delete_metadata_policy_with_http_info(**kwargs)  # noqa: E501
            return data

    def delete_metadata_policy_with_http_info(self, **kwargs):
        all_params = ['async_req', '_return_http_data_only', '_preload_content', '_request_timeout', 'domain', 'name',
                      'policy']
        params = locals()
        for key, val in params['kwargs'].items():
            if key not in all_params:
                raise TypeError("Got an unexpected keyword argument '%s'"
                                " to method profile_get" % key)
            params[key] = val
        del params['kwargs']

        return self.client.request('DELETE',
                                   f'/meta/{kwargs["domain"]}/{kwargs["name"]}/policy/name/{kwargs["policy"]}')
