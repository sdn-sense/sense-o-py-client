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

class ConnectionSchedule(object):
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
        'duration': 'str',
        'start': 'str',
        'end': 'str'
    }

    attribute_map = {
        'duration': 'duration',
        'start': 'start',
        'end': 'end'
    }

    def __init__(self, duration=None, start=None, end=None):  # noqa: E501
        """ConnectionSchedule - a model defined in Swagger"""  # noqa: E501
        self._duration = None
        self._start = None
        self._end = None
        self.discriminator = None
        if duration is not None:
            self.duration = duration
        if start is not None:
            self.start = start
        if end is not None:
            self.end = end

    @property
    def duration(self):
        """Gets the duration of this ConnectionSchedule.  # noqa: E501

        Duration of the connection.  # noqa: E501

        :return: The duration of this ConnectionSchedule.  # noqa: E501
        :rtype: str
        """
        return self._duration

    @duration.setter
    def duration(self, duration):
        """Sets the duration of this ConnectionSchedule.

        Duration of the connection.  # noqa: E501

        :param duration: The duration of this ConnectionSchedule.  # noqa: E501
        :type: str
        """

        self._duration = duration

    @property
    def start(self):
        """Gets the start of this ConnectionSchedule.  # noqa: E501

        Start of the scheduling window.  # noqa: E501

        :return: The start of this ConnectionSchedule.  # noqa: E501
        :rtype: str
        """
        return self._start

    @start.setter
    def start(self, start):
        """Sets the start of this ConnectionSchedule.

        Start of the scheduling window.  # noqa: E501

        :param start: The start of this ConnectionSchedule.  # noqa: E501
        :type: str
        """

        self._start = start

    @property
    def end(self):
        """Gets the end of this ConnectionSchedule.  # noqa: E501

        End of the scheduling window.  # noqa: E501

        :return: The end of this ConnectionSchedule.  # noqa: E501
        :rtype: str
        """
        return self._end

    @end.setter
    def end(self, end):
        """Sets the end of this ConnectionSchedule.

        End of the scheduling window.  # noqa: E501

        :param end: The end of this ConnectionSchedule.  # noqa: E501
        :type: str
        """

        self._end = end

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
        if issubclass(ConnectionSchedule, dict):
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
        if not isinstance(other, ConnectionSchedule):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other