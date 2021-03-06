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

class LoggingConfiguration(object):
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
        'loggers': 'LoggingConfigurationLoggers',
        'filter': 'str',
        'main_rows': 'float',
        'main_usage': 'float',
        'archived_rows': 'float',
        'archived_usage': 'float'
    }

    attribute_map = {
        'loggers': 'loggers',
        'filter': 'filter',
        'main_rows': 'mainRows',
        'main_usage': 'mainUsage',
        'archived_rows': 'archivedRows',
        'archived_usage': 'archivedUsage'
    }

    def __init__(self, loggers=None, filter=None, main_rows=None, main_usage=None, archived_rows=None, archived_usage=None):  # noqa: E501
        """LoggingConfiguration - a model defined in Swagger"""  # noqa: E501
        self._loggers = None
        self._filter = None
        self._main_rows = None
        self._main_usage = None
        self._archived_rows = None
        self._archived_usage = None
        self.discriminator = None
        self.loggers = loggers
        if filter is not None:
            self.filter = filter
        if main_rows is not None:
            self.main_rows = main_rows
        if main_usage is not None:
            self.main_usage = main_usage
        if archived_rows is not None:
            self.archived_rows = archived_rows
        if archived_usage is not None:
            self.archived_usage = archived_usage

    @property
    def loggers(self):
        """Gets the loggers of this LoggingConfiguration.  # noqa: E501


        :return: The loggers of this LoggingConfiguration.  # noqa: E501
        :rtype: LoggingConfigurationLoggers
        """
        return self._loggers

    @loggers.setter
    def loggers(self, loggers):
        """Sets the loggers of this LoggingConfiguration.


        :param loggers: The loggers of this LoggingConfiguration.  # noqa: E501
        :type: LoggingConfigurationLoggers
        """
        if loggers is None:
            raise ValueError("Invalid value for `loggers`, must not be `None`")  # noqa: E501

        self._loggers = loggers

    @property
    def filter(self):
        """Gets the filter of this LoggingConfiguration.  # noqa: E501

        Filter configuration string, for dropping matching messages from logging.  # noqa: E501

        :return: The filter of this LoggingConfiguration.  # noqa: E501
        :rtype: str
        """
        return self._filter

    @filter.setter
    def filter(self, filter):
        """Sets the filter of this LoggingConfiguration.

        Filter configuration string, for dropping matching messages from logging.  # noqa: E501

        :param filter: The filter of this LoggingConfiguration.  # noqa: E501
        :type: str
        """

        self._filter = filter

    @property
    def main_rows(self):
        """Gets the main_rows of this LoggingConfiguration.  # noqa: E501

        Number of rows present in the main logging table.  # noqa: E501

        :return: The main_rows of this LoggingConfiguration.  # noqa: E501
        :rtype: float
        """
        return self._main_rows

    @main_rows.setter
    def main_rows(self, main_rows):
        """Sets the main_rows of this LoggingConfiguration.

        Number of rows present in the main logging table.  # noqa: E501

        :param main_rows: The main_rows of this LoggingConfiguration.  # noqa: E501
        :type: float
        """

        self._main_rows = main_rows

    @property
    def main_usage(self):
        """Gets the main_usage of this LoggingConfiguration.  # noqa: E501

        Bytes usage in the main logging table.  # noqa: E501

        :return: The main_usage of this LoggingConfiguration.  # noqa: E501
        :rtype: float
        """
        return self._main_usage

    @main_usage.setter
    def main_usage(self, main_usage):
        """Sets the main_usage of this LoggingConfiguration.

        Bytes usage in the main logging table.  # noqa: E501

        :param main_usage: The main_usage of this LoggingConfiguration.  # noqa: E501
        :type: float
        """

        self._main_usage = main_usage

    @property
    def archived_rows(self):
        """Gets the archived_rows of this LoggingConfiguration.  # noqa: E501

        Number of rows present in the archived logging table.  # noqa: E501

        :return: The archived_rows of this LoggingConfiguration.  # noqa: E501
        :rtype: float
        """
        return self._archived_rows

    @archived_rows.setter
    def archived_rows(self, archived_rows):
        """Sets the archived_rows of this LoggingConfiguration.

        Number of rows present in the archived logging table.  # noqa: E501

        :param archived_rows: The archived_rows of this LoggingConfiguration.  # noqa: E501
        :type: float
        """

        self._archived_rows = archived_rows

    @property
    def archived_usage(self):
        """Gets the archived_usage of this LoggingConfiguration.  # noqa: E501

        Bytes usage in the archived logging table.  # noqa: E501

        :return: The archived_usage of this LoggingConfiguration.  # noqa: E501
        :rtype: float
        """
        return self._archived_usage

    @archived_usage.setter
    def archived_usage(self, archived_usage):
        """Sets the archived_usage of this LoggingConfiguration.

        Bytes usage in the archived logging table.  # noqa: E501

        :param archived_usage: The archived_usage of this LoggingConfiguration.  # noqa: E501
        :type: float
        """

        self._archived_usage = archived_usage

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
        if issubclass(LoggingConfiguration, dict):
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
        if not isinstance(other, LoggingConfiguration):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
