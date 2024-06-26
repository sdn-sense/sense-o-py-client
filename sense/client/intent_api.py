#!/usr/bin/env python3
# coding: utf-8
"""
    SENSE-O Northbound Intent API

    StackV SENSE-O Northbound REST API Documentation  # noqa: E501

    OpenAPI spec version: 2.0.2

    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""
from sense.client.requestwrapper import RequestWrapper
from sense.common import classwrapper

@classwrapper
class IntentApi():
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    Ref: https://github.com/swagger-api/swagger-codegen
    """
    def __init__(self, req_wrapper=None):
        if req_wrapper is None:
            self.client = RequestWrapper()
        else:
            self.client = req_wrapper
        if 'SI_UUID' in self.client.config:
            self.si_uuid = self.client.config['SI_UUID']
        else:
            self.si_uuid = None

    def instance_get_intents(self, **kwargs):  # noqa: E501
        """Retrieve intents by service instance  # noqa: E501

        Queries all service intents belonging to given instance UUID.  # noqa: E501
        This method makes a synchronous HTTP request by default.
        :param async_req bool
        :param str si_uuid: Intent UUID. (required)
        :return: list[IntentExpanded]
                 If the method is called asynchronously,
                 returns the request thread.
        """
        if self.si_uuid:
            kwargs['si_uuid'] = self.si_uuid
        if not kwargs['si_uuid'] :
            raise ValueError("Missing the required parameter `si_uuid`")

        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.intent_instance_si_uuid_get_with_http_info(**kwargs)  # noqa: E501
        else:
            (data) = self.intent_instance_si_uuid_get_with_http_info(**kwargs)  # noqa: E501
            return data

    def intent_instance_si_uuid_get_with_http_info(self,
                                                   **kwargs):  # noqa: E501
        """Retrieve intents by service instance  # noqa: E501

        Queries all service intents belonging to given instance UUID.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.intent_instance_si_uuid_get_with_http_info(si_uuid, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str si_uuid: Intent UUID. (required)
        :return: list[IntentExpanded]
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['si_uuid']  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in params['kwargs'].items():
            if key not in all_params:
                raise TypeError("Got an unexpected keyword argument '%s'"
                                " to method intent_instance_si_uuid_get" % key)
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'si_uuid' is set
        if ('si_uuid' not in params or params['si_uuid'] is None):
            raise ValueError(
                "Missing the required parameter `si_uuid` when calling `intent_instance_si_uuid_get`"
            )  # noqa: E501

        return self.client.request('GET', '/intent/instance/' + kwargs['si_uuid'])

    def intent_describe(self, uuid, **kwargs):  # noqa: E501
        """Retrieve intent by UUID  # noqa: E501

        Queries service intent with given ID.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.intent_describe(uuid, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str uuid: Intent UUID. (required)
        :return: Intent
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.intent_uuid_get_with_http_info(uuid,
                                                       **kwargs)  # noqa: E501
        else:
            (data) = self.intent_uuid_get_with_http_info(
                uuid, **kwargs)  # noqa: E501
            return data

    def intent_uuid_get_with_http_info(self, uuid, **kwargs):  # noqa: E501
        """Retrieve intent by UUID  # noqa: E501

        Queries service intent with given ID.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.intent_uuid_get_with_http_info(uuid, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str uuid: Intent UUID. (required)
        :return: Intent
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['uuid']  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in params['kwargs'].items():
            if key not in all_params:
                raise TypeError("Got an unexpected keyword argument '%s'"
                                " to method intent_uuid_get" % key)
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'uuid' is set
        if ('uuid' not in params or params['uuid'] is None):
            raise ValueError(
                "Missing the required parameter `uuid` when calling `intent_uuid_get`"
            )  # noqa: E501

        collection_formats = {}

        path_params = {}
        if 'uuid' in params:
            path_params['uuid'] = params['uuid']  # noqa: E501

        # Authentication setting
        auth_settings = ['oAuth2Keycloak']  # noqa: E501

        return self.client.request('GET', '/intent/' + uuid)
