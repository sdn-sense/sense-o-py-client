# coding: utf-8
"""
    SENSE-O Northbound Intent API

    StackV SENSE-O Northbound REST API Documentation  # noqa: E501

    OpenAPI spec version: 2.0.2
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

from __future__ import absolute_import
import six
from sense.client.requestwrapper import RequestWrapper


class WorkflowCombinedApi(object):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    Ref: https://github.com/swagger-api/swagger-codegen
    """

    def __init__(self, req_wrapper=None):
        if req_wrapper is None:
            self.client = RequestWrapper()
        else:
            self.client = req_wrapper
        self.si_uuid = None

        self._allowed_actions = ['provision', 'cancel', 'reprovision']

    def instance_new(self, **kwargs):  # noqa: E501
        """Generate new service instance UUID  # noqa: E501

        Retrieves UUID for new instance from backend.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.instance_new(async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :return: str
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            data = self.instance_get_with_http_info(**kwargs)
            self.si_uuid = data
            return data  # noqa: E501
        else:
            (data) = self.instance_get_with_http_info(**kwargs)  # noqa: E501
            self.si_uuid = data
            return data

    def instance_get_with_http_info(self, **kwargs):  # noqa: E501
        """Generate new service instance UUID  # noqa: E501

        Retrieves UUID for new instance from backend.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.instance_get_with_http_info(async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :return: str
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError("Got an unexpected keyword argument '%s'"
                                " to method instance_get" % key)
            params[key] = val
        del params['kwargs']

        return self.client.request('GET', '/instance')

    # TODO: check action types and only allow for combined ops
    def instance_operate(self, action, **kwargs):  # noqa: E501
        """Operate on a service instance  # noqa: E501

        Request an operation for specified service instance.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.instance_operate(si_uuid, action, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str si_uuid: service instance UUID (required)
        :param Operation action: Service operation requested
            * `provision` - Composite service to propagate, commit and verify instance.
            * `cancel` - Composite service to cancel, propagate, commit and verify instance.
            * `reprovision` - Composite service to reinstate, propagate, commit and verify instance.
        :param bool sync: Whether to perform the operation in a synchronous/blocking mode.
        :param bool force: Whether to force the operation on a failed instance.
        :param str intent: Intent UUID string or 'last'.
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """
        if self.si_uuid:
            kwargs['si_uuid'] = self.si_uuid
        if not kwargs['si_uuid']:
            raise ValueError("Missing the required parameter `si_uuid`")

        if action not in self._allowed_actions:
            raise ValueError(
                f'operate action must of one of {self._allowed_actions}')

        if kwargs.get('async_req'):
            return self.instance_si_uuid_action_put_with_http_info(
                action, **kwargs)  # noqa: E501
        else:
            (data) = self.instance_si_uuid_action_put_with_http_info(
                action, **kwargs)  # noqa: E501
            return data

    def instance_si_uuid_action_put_with_http_info(self, action,
                                                   **kwargs):  # noqa: E501
        """Operate on a service instance  # noqa: E501

        Request an operation for specified service instance.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.instance_si_uuid_action_put_with_http_info(si_uuid, action, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str si_uuid: service instance UUID (required)
        :param Operation action: Service operation requested   * `cancel` - Composite service to cancel, propagate, commit and verify instance.   * `release` - Composite service to cancel and propagate in 2-phase commit process.   * `verify` - Begin service verification process. (required)
        :param bool sync: Whether to perform the operation in a synchronous/blocking mode.
        :param bool force: Whether to force the operation on a failed instance.
        :param str intent: Intent UUID string or 'last'.
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['si_uuid', 'action', 'sync', 'force', 'intent']
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError("Got an unexpected keyword argument '%s'"
                                " to method instance_si_uuid_action_put" % key)
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'si_uuid' is set
        if ('si_uuid' not in params or params['si_uuid'] is None):
            raise ValueError(
                "Missing the required parameter `si_uuid` when calling `instance_si_uuid_action_put`"
            )  # noqa: E501
        # verify the required parameter 'action' is set
        if ('action' not in params or params['action'] is None):
            raise ValueError(
                "Missing the required parameter `action` when calling `instance_si_uuid_action_put`"
            )  # noqa: E501

        query_params = []
        if 'sync' in params:
            query_params.append(('sync', params['sync']))
        if 'force' in params:
            query_params.append(('force', params['force']))
        if 'intent' in params:
            query_params.append(('intent', params['intent']))

        return self.client.request('PUT',
                                   '/instance/' + kwargs['si_uuid'] + '/' + action,
                                   query_params=query_params)

    def instance_delete(self, **kwargs):  # noqa: E501
        """Delete a service instance  # noqa: E501

        Deletes the specified service instance.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.instance_delete(si_uuid, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str si_uuid: service instance UUID (required)
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """
        if self.si_uuid:
            kwargs['si_uuid'] = self.si_uuid
        if not kwargs['si_uuid']:
            raise ValueError("Missing the required parameter `si_uuid`")

        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.instance_si_uuid_delete_with_http_info(**kwargs)  # noqa: E501
        else:
            (data) = self.instance_si_uuid_delete_with_http_info(**kwargs)  # noqa: E501
            return data

    def instance_si_uuid_delete_with_http_info(self,
                                               **kwargs):  # noqa: E501
        """Delete a service instance  # noqa: E501

        Deletes the specified service instance.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.instance_si_uuid_delete_with_http_info(si_uuid, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str si_uuid: service instance UUID (required)
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['si_uuid']  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError("Got an unexpected keyword argument '%s'"
                                " to method instance_si_uuid_delete" % key)
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'si_uuid' is set
        if ('si_uuid' not in params or params['si_uuid'] is None):
            raise ValueError(
                "Missing the required parameter `si_uuid` when calling `instance_si_uuid_delete`"
            )  # noqa: E501
        try:
            return self.client.request('DELETE', '/instance/' + kwargs['si_uuid'])
        except ValueError:
            return self.client.request('DELETE', '/service/' + kwargs['si_uuid'])

    def instance_create(self, intent, **kwargs):  # noqa: E501
        """Create new service instance and/or add new intent  # noqa: E501

        Creates a new service instance with the given UUID and intent specification or add new intent to existing service instance  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.instance_create(body, si_uuid, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param ServiceIntent body: Service instance creation request object. (required)
        :param str si_uuid: Service instance UUID. (required)
        :return: ServiceIntentResponse
                 If the method is called asynchronously,
                 returns the request thread.
        """
        if self.si_uuid:
            kwargs['si_uuid'] = self.si_uuid
        if not kwargs['si_uuid']:
            raise ValueError("Missing the required parameter `si_uuid`")

        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.instance_si_uuid_post_with_http_info(
                intent, **kwargs)  # noqa: E501
        else:
            (data) = self.instance_si_uuid_post_with_http_info(
                intent, **kwargs)  # noqa: E501
            return data

    def instance_si_uuid_post_with_http_info(self, body,
                                             **kwargs):  # noqa: E501
        """Create new service instance and/or add new intent  # noqa: E501

        Creates a new service instance with the given UUID and intent specification or add new intent to existing service instance  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.instance_si_uuid_post_with_http_info(body, si_uuid, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param ServiceIntent body: Service instance creation request object. (required)
        :param str si_uuid: Service instance UUID. (required)
        :return: ServiceIntentResponse
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['body', 'si_uuid']  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError("Got an unexpected keyword argument '%s'"
                                " to method instance_si_uuid_post" % key)
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'body' is set
        if ('body' not in params or params['body'] is None):
            raise ValueError(
                "Missing the required parameter `body` when calling `instance_si_uuid_post`"
            )  # noqa: E501
        # verify the required parameter 'si_uuid' is set
        if ('si_uuid' not in params or params['si_uuid'] is None):
            raise ValueError(
                "Missing the required parameter `si_uuid` when calling `instance_si_uuid_post`"
            )  # noqa: E501

        path_params = {}
        if 'si_uuid' in params:
            path_params['siUUID'] = params['si_uuid']  # noqa: E501

        query_params = []
        # proceed is false and sync is true by default

        # Authentication setting
        auth_settings = ['oAuth2Keycloak']  # noqa: E501
        return self.client.request('POST',
                                   '/instance/' + kwargs['si_uuid'],
                                   body_params=body)


    def instance_modify(self, intent, **kwargs):  # noqa: E501
        """Create new service instance and/or add new intent  # noqa: E501

        Creates a new service instance with the given UUID and intent specification or add new intent to existing service instance  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.instance_create(body, si_uuid, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param ServiceIntent body: Service instance creation request object. (required)
        :param str si_uuid: Service instance UUID. (required)
        :return: ServiceIntentResponse
                 If the method is called asynchronously,
                 returns the request thread.
        """
        if self.si_uuid:
            kwargs['si_uuid'] = self.si_uuid
        if not kwargs['si_uuid']:
            raise ValueError("Missing the required parameter `si_uuid`")

        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.instance_modify_si_uuid_post_with_http_info(
                intent, **kwargs)  # noqa: E501
        else:
            (data) = self.instance_modify_si_uuid_post_with_http_info(
                intent, **kwargs)  # noqa: E501
            return data

    def instance_modify_si_uuid_post_with_http_info(self, body,
                                             **kwargs):  # noqa: E501
        """Create new service instance and/or add new intent  # noqa: E501

        Creates a new service instance with the given UUID and intent specification or add new intent to existing service instance  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.instance_modify_si_uuid_post_with_http_info(body, si_uuid, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param ServiceIntent body: Service instance creation request object. (required)
        :param str si_uuid: Service instance UUID. (required)
        :return: ServiceIntentResponse
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['body', 'si_uuid', 'sync']  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError("Got an unexpected keyword argument '%s'"
                                " to method instance_modify_si_uuid_post" % key)
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'body' is set
        if ('body' not in params or params['body'] is None):
            raise ValueError(
                "Missing the required parameter `body` when calling `instance_modify_si_uuid_post`"
            )  # noqa: E501
        # verify the required parameter 'si_uuid' is set
        if ('si_uuid' not in params or params['si_uuid'] is None):
            raise ValueError(
                "Missing the required parameter `si_uuid` when calling `instance_modify_si_uuid_post`"
            )  # noqa: E501

        path_params = {}
        if 'si_uuid' in params:
            path_params['siUUID'] = params['si_uuid']  # noqa: E501

        query_params = []
        if 'sync' in params:
            query_params.append(('sync', params['sync']))

        # Authentication setting
        auth_settings = ['oAuth2Keycloak']  # noqa: E501
        return self.client.request('POST',
                                   '/instance/' + kwargs['si_uuid'] + '/modify',
                                   body_params=body, query_params=query_params)


    def instance_get_status(self, **kwargs):  # noqa: E501
        """Get instance status  # noqa: E501
        Retrieves the full instance status.  # noqa: E501
        This method makes a synchronous HTTP request by default.
        :param async_req bool
        :param str si_uuid: Service instance UUID. (required)
        :return: str
                 If the method is called asynchronously,
                 returns the request thread.
        """
        if self.si_uuid:
            kwargs['si_uuid'] = self.si_uuid
        if not kwargs.get('si_uuid'):
            raise ValueError("Missing the required parameter `si_uuid`")

        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.instance_si_uuid_status_get_with_http_info(**kwargs)  # noqa: E501
        else:
            (data) = self.instance_si_uuid_status_get_with_http_info(
                **kwargs)  # noqa: E501
            return data

    def instance_si_uuid_status_get_with_http_info(self, **kwargs):  # noqa: E501
        """Get instance status  # noqa: E501
        Retrieves the full instance status.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.instance_si_uuid_status_get_with_http_info(si_uuid, async_req=True)
        >>> result = thread.get()
        :param async_req bool
        :param str si_uuid: Service instance UUID. (required)
        :return: str
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['si_uuid']  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError("Got an unexpected keyword argument '%s'"
                                " to method instance_si_uuid_status_get" % key)
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'si_uuid' is set
        if ('si_uuid' not in params or params['si_uuid'] is None):
            raise ValueError(
                "Missing the required parameter `si_uuid` when calling `instance_si_uuid_status_get`"
            )  # noqa: E501

        return self.client.request('GET', f'/instance/{kwargs.get("si_uuid")}/status')

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
        if not kwargs['si_uuid']:
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
        >>> thread = api.intent_instance_si_uuid_get_with_http_info(async_req=True)
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
        for key, val in six.iteritems(params['kwargs']):
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

    def profile_list(self, **kwargs):
        """Get skimmed profile data  # noqa: E501

        Retrieves the list of profiles the user is permitted to use without any JSON data.  # noqa: E501
        This method makes a synchronous HTTP request by default.
        :param async_req bool
        :return: list[SlimProfile]
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.profile_get_with_http_info(**kwargs)  # noqa: E501
        else:
            (data) = self.profile_get_with_http_info(**kwargs)  # noqa: E501
            return data

    def profile_get_with_http_info(self, **kwargs):
        """Get skimmed profile data  # noqa: E501

        Retrieves the list of profiles the user is permitted to use without any JSON data.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.profile_get_with_http_info(async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :return: list[SlimProfile]
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError("Got an unexpected keyword argument '%s'"
                                " to method profile_get" % key)
            params[key] = val
        del params['kwargs']

        return self.client.request('GET', '/profile')

    def profile_describe(self, uuid, **kwargs):  # noqa: E501
        """Get single profile  # noqa: E501

        Retrieves the specified profile.  # noqa: E501
        This method makes a synchronous HTTP request by default.
        :param async_req bool
        :param str uuid: Profile UUID. (required)
        :return: FullProfile
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.profile_uuid_get_with_http_info(uuid,
                                                        **kwargs)  # noqa: E501
        else:
            (data) = self.profile_uuid_get_with_http_info(
                uuid, **kwargs)  # noqa: E501
            return data

    def profile_uuid_get_with_http_info(self, uuid, **kwargs):  # noqa: E501
        """Get single profile  # noqa: E501

        Retrieves the specified profile.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.profile_uuid_get_with_http_info(uuid, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str uuid: Profile UUID. (required)
        :return: FullProfile
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['uuid']  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError("Got an unexpected keyword argument '%s'"
                                " to method profile_uuid_get" % key)
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'uuid' is set
        if ('uuid' not in params or params['uuid'] is None):
            raise ValueError(
                "Missing the required parameter `uuid` when calling `profile_uuid_get`"
            )  # noqa: E501

        return self.client.request('GET', '/profile/' + uuid)

    def manifest_create(self, template, **kwargs):  # noqa: E501
        """Create new service instance and/or add new intent  # noqa: E501

        Creates a new service instance with the given UUID and intent specification or add new intent to existing service instance  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.instance_create(body, si_uuid, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param ServiceIntent body: Service instance creation request object. (required)
        :param str si_uuid: Service instance UUID. (required)
        :return: ServiceIntentResponse
                 If the method is called asynchronously,
                 returns the request thread.
        """
        if self.si_uuid:
            kwargs['si_uuid'] = self.si_uuid
        if not kwargs['si_uuid']:
            raise ValueError("Missing the required parameter `si_uuid`")

        kwargs['_return_http_data_only'] = True

        # manfiest in json form; insert into XML body
        body_xml = f'<serviceManifest> <serviceUUID></serviceUUID><jsonTemplate>{template}</jsonTemplate></serviceManifest>'
        if kwargs.get('async_req'):
            return self.instance_si_uuid_manifest_post_with_http_info(
                body_xml, **kwargs)  # noqa: E501
        else:
            (data) = self.instance_si_uuid_manifest_post_with_http_info(
                body_xml, **kwargs)  # noqa: E501
            return data

    def instance_si_uuid_manifest_post_with_http_info(self, body,
                                                    **kwargs):  # noqa: E501
        """Create new service instance and/or add new intent  # noqa: E501

        Creates a new service instance with the given UUID and intent specification or add new intent to existing service instance  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.instance_si_uuid_manifest_post_with_http_info(body, si_uuid, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param ServiceIntent body: Service instance creation request object. (required)
        :param str si_uuid: Service instance UUID. (required)
        :return: ServiceIntentResponse
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['body', 'si_uuid', 'sync']  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method instance_si_uuid_post_with_http_info" %
                    key)
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'body' is set
        if ('body' not in params or params['body'] is None):
            raise ValueError(
                "Missing the required parameter `body` when calling `instance_modify`"
            )  # noqa: E501
        # verify the required parameter 'si_uuid' is set
        if ('si_uuid' not in params or params['si_uuid'] is None):
            raise ValueError(
                "Missing the required parameter `si_uuid` when calling `instance_modify`"
            )  # noqa: E501

        path_params = {}
        if 'si_uuid' in params:
            path_params['siUUID'] = params['si_uuid']  # noqa: E501

        query_params = []
        if 'sync' in params:
            query_params.append(('sync', params['sync']))
        # sync is true by default

        # Authentication setting
        auth_settings = ['oAuth2Keycloak']  # noqa: E501
        self.client.config['headers']['Content-type'] = 'application/xml'
        return self.client.request('POST',
                                   f'/service/manifest/{kwargs["si_uuid"]}',
                                   body_params=body,
                                   query_params=query_params)
