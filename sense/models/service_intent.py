# coding: utf-8

"""
    SENSE-O Northbound Intent API

    StackV SENSE-O Northbound REST API Documentation  # noqa: E501

    OpenAPI spec version: 2.0.2
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

import pprint
import re  # noqa: F401

import six

class ServiceIntent(object):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'service': 'str',
        'options': 'list[str]',
        'profile_id': 'str',
        'queries': 'list[ServiceIntentQueries]',
        'data': 'OneOfServiceIntentData',
        'alias': 'str'
    }

    attribute_map = {
        'service': 'service',
        'options': 'options',
        'profile_id': 'profileID',
        'queries': 'queries',
        'data': 'data',
        'alias': 'alias'
    }

    def __init__(self, service=None, options=None, profile_id=None, queries=None, data=None, alias=None):  # noqa: E501
        """ServiceIntent - a model defined in Swagger"""  # noqa: E501
        self._service = None
        self._options = None
        self._profile_id = None
        self._queries = None
        self._data = None
        self._alias = None
        self.discriminator = None
        self.service = service
        if options is not None:
            self.options = options
        if profile_id is not None:
            self.profile_id = profile_id
        if queries is not None:
            self.queries = queries
        if data is not None:
            self.data = data
        self.alias = alias

    @property
    def service(self):
        """Gets the service of this ServiceIntent.  # noqa: E501

        The type of service being created.  # noqa: E501

        :return: The service of this ServiceIntent.  # noqa: E501
        :rtype: str
        """
        return self._service

    @service.setter
    def service(self, service):
        """Sets the service of this ServiceIntent.

        The type of service being created.  # noqa: E501

        :param service: The service of this ServiceIntent.  # noqa: E501
        :type: str
        """
        if service is None:
            raise ValueError("Invalid value for `service`, must not be `None`")  # noqa: E501

        self._service = service

    @property
    def options(self):
        """Gets the options of this ServiceIntent.  # noqa: E501

        Array of option flags.  # noqa: E501

        :return: The options of this ServiceIntent.  # noqa: E501
        :rtype: list[str]
        """
        return self._options

    @options.setter
    def options(self, options):
        """Sets the options of this ServiceIntent.

        Array of option flags.  # noqa: E501

        :param options: The options of this ServiceIntent.  # noqa: E501
        :type: list[str]
        """

        self._options = options

    @property
    def profile_id(self):
        """Gets the profile_id of this ServiceIntent.  # noqa: E501

        Optional link to a profile via UUID.  # noqa: E501

        :return: The profile_id of this ServiceIntent.  # noqa: E501
        :rtype: str
        """
        return self._profile_id

    @profile_id.setter
    def profile_id(self, profile_id):
        """Sets the profile_id of this ServiceIntent.

        Optional link to a profile via UUID.  # noqa: E501

        :param profile_id: The profile_id of this ServiceIntent.  # noqa: E501
        :type: str
        """

        self._profile_id = profile_id

    @property
    def queries(self):
        """Gets the queries of this ServiceIntent.  # noqa: E501


        :return: The queries of this ServiceIntent.  # noqa: E501
        :rtype: list[ServiceIntentQueries]
        """
        return self._queries

    @queries.setter
    def queries(self, queries):
        """Sets the queries of this ServiceIntent.


        :param queries: The queries of this ServiceIntent.  # noqa: E501
        :type: list[ServiceIntentQueries]
        """

        self._queries = queries

    @property
    def data(self):
        """Gets the data of this ServiceIntent.  # noqa: E501


        :return: The data of this ServiceIntent.  # noqa: E501
        :rtype: OneOfServiceIntentData
        """
        return self._data

    @data.setter
    def data(self, data):
        """Sets the data of this ServiceIntent.


        :param data: The data of this ServiceIntent.  # noqa: E501
        :type: OneOfServiceIntentData
        """

        self._data = data

    @property
    def alias(self):
        """Gets the alias of this ServiceIntent.  # noqa: E501

        Alias to give to the created service instance.  # noqa: E501

        :return: The alias of this ServiceIntent.  # noqa: E501
        :rtype: str
        """
        return self._alias

    @alias.setter
    def alias(self, alias):
        """Sets the alias of this ServiceIntent.

        Alias to give to the created service instance.  # noqa: E501

        :param alias: The alias of this ServiceIntent.  # noqa: E501
        :type: str
        """
        if alias is None:
            raise ValueError("Invalid value for `alias`, must not be `None`")  # noqa: E501

        self._alias = alias

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.swagger_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value
        if issubclass(ServiceIntent, dict):
            for key, value in self.items():
                result[key] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, ServiceIntent):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
