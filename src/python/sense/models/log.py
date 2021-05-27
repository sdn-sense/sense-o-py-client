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

class Log(object):
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
        'id': 'str',
        'timestamp': 'str',
        'reference_uuid': 'str',
        'level': 'LogLevel',
        'logger': 'str',
        'message': 'str',
        'event': 'str',
        'exception': 'str',
        'target_id': 'str'
    }

    attribute_map = {
        'id': 'id',
        'timestamp': 'timestamp',
        'reference_uuid': 'referenceUUID',
        'level': 'level',
        'logger': 'logger',
        'message': 'message',
        'event': 'event',
        'exception': 'exception',
        'target_id': 'targetID'
    }

    def __init__(self, id=None, timestamp=None, reference_uuid=None, level=None, logger=None, message=None, event=None, exception=None, target_id=None):  # noqa: E501
        """Log - a model defined in Swagger"""  # noqa: E501
        self._id = None
        self._timestamp = None
        self._reference_uuid = None
        self._level = None
        self._logger = None
        self._message = None
        self._event = None
        self._exception = None
        self._target_id = None
        self.discriminator = None
        self.id = id
        self.timestamp = timestamp
        if reference_uuid is not None:
            self.reference_uuid = reference_uuid
        self.level = level
        if logger is not None:
            self.logger = logger
        self.message = message
        self.event = event
        if exception is not None:
            self.exception = exception
        if target_id is not None:
            self.target_id = target_id

    @property
    def id(self):
        """Gets the id of this Log.  # noqa: E501

        Database ID for the entry.  # noqa: E501

        :return: The id of this Log.  # noqa: E501
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this Log.

        Database ID for the entry.  # noqa: E501

        :param id: The id of this Log.  # noqa: E501
        :type: str
        """
        if id is None:
            raise ValueError("Invalid value for `id`, must not be `None`")  # noqa: E501

        self._id = id

    @property
    def timestamp(self):
        """Gets the timestamp of this Log.  # noqa: E501

        When the log was registered.  # noqa: E501

        :return: The timestamp of this Log.  # noqa: E501
        :rtype: str
        """
        return self._timestamp

    @timestamp.setter
    def timestamp(self, timestamp):
        """Sets the timestamp of this Log.

        When the log was registered.  # noqa: E501

        :param timestamp: The timestamp of this Log.  # noqa: E501
        :type: str
        """
        if timestamp is None:
            raise ValueError("Invalid value for `timestamp`, must not be `None`")  # noqa: E501

        self._timestamp = timestamp

    @property
    def reference_uuid(self):
        """Gets the reference_uuid of this Log.  # noqa: E501

        A service instance UUID that the log is associated with.  # noqa: E501

        :return: The reference_uuid of this Log.  # noqa: E501
        :rtype: str
        """
        return self._reference_uuid

    @reference_uuid.setter
    def reference_uuid(self, reference_uuid):
        """Sets the reference_uuid of this Log.

        A service instance UUID that the log is associated with.  # noqa: E501

        :param reference_uuid: The reference_uuid of this Log.  # noqa: E501
        :type: str
        """

        self._reference_uuid = reference_uuid

    @property
    def level(self):
        """Gets the level of this Log.  # noqa: E501


        :return: The level of this Log.  # noqa: E501
        :rtype: LogLevel
        """
        return self._level

    @level.setter
    def level(self, level):
        """Sets the level of this Log.


        :param level: The level of this Log.  # noqa: E501
        :type: LogLevel
        """
        if level is None:
            raise ValueError("Invalid value for `level`, must not be `None`")  # noqa: E501

        self._level = level

    @property
    def logger(self):
        """Gets the logger of this Log.  # noqa: E501

        Class name of the logger that created this entry.  # noqa: E501

        :return: The logger of this Log.  # noqa: E501
        :rtype: str
        """
        return self._logger

    @logger.setter
    def logger(self, logger):
        """Sets the logger of this Log.

        Class name of the logger that created this entry.  # noqa: E501

        :param logger: The logger of this Log.  # noqa: E501
        :type: str
        """

        self._logger = logger

    @property
    def message(self):
        """Gets the message of this Log.  # noqa: E501

        The main event data.  # noqa: E501

        :return: The message of this Log.  # noqa: E501
        :rtype: str
        """
        return self._message

    @message.setter
    def message(self, message):
        """Sets the message of this Log.

        The main event data.  # noqa: E501

        :param message: The message of this Log.  # noqa: E501
        :type: str
        """
        if message is None:
            raise ValueError("Invalid value for `message`, must not be `None`")  # noqa: E501

        self._message = message

    @property
    def event(self):
        """Gets the event of this Log.  # noqa: E501

        The specific method or signature of that created this entry.  # noqa: E501

        :return: The event of this Log.  # noqa: E501
        :rtype: str
        """
        return self._event

    @event.setter
    def event(self, event):
        """Sets the event of this Log.

        The specific method or signature of that created this entry.  # noqa: E501

        :param event: The event of this Log.  # noqa: E501
        :type: str
        """
        if event is None:
            raise ValueError("Invalid value for `event`, must not be `None`")  # noqa: E501

        self._event = event

    @property
    def exception(self):
        """Gets the exception of this Log.  # noqa: E501

        An exception string, including trace and formatted information.  # noqa: E501

        :return: The exception of this Log.  # noqa: E501
        :rtype: str
        """
        return self._exception

    @exception.setter
    def exception(self, exception):
        """Sets the exception of this Log.

        An exception string, including trace and formatted information.  # noqa: E501

        :param exception: The exception of this Log.  # noqa: E501
        :type: str
        """

        self._exception = exception

    @property
    def target_id(self):
        """Gets the target_id of this Log.  # noqa: E501

        Extra UUID field, for additional tracking or metadata purposes. Specific to the log event.  # noqa: E501

        :return: The target_id of this Log.  # noqa: E501
        :rtype: str
        """
        return self._target_id

    @target_id.setter
    def target_id(self, target_id):
        """Sets the target_id of this Log.

        Extra UUID field, for additional tracking or metadata purposes. Specific to the log event.  # noqa: E501

        :param target_id: The target_id of this Log.  # noqa: E501
        :type: str
        """

        self._target_id = target_id

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
        if issubclass(Log, dict):
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
        if not isinstance(other, Log):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other