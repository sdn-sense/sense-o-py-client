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

class FullProfile(object):
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
        'uuid': 'str',
        'name': 'str',
        'json': 'str',
        'owner': 'str',
        'description': 'str',
        'created': 'datetime',
        'last_edited': 'datetime',
        'authorized': 'bool',
        'editable': 'bool',
        'edit_json': 'str',
        'licenses': 'list[ProfileLicense]'
    }

    attribute_map = {
        'uuid': 'uuid',
        'name': 'name',
        'json': 'json',
        'owner': 'owner',
        'description': 'description',
        'created': 'created',
        'last_edited': 'lastEdited',
        'authorized': 'authorized',
        'editable': 'editable',
        'edit_json': 'editJson',
        'licenses': 'licenses'
    }

    def __init__(self, uuid=None, name=None, json=None, owner=None, description=None, created=None, last_edited=None, authorized=None, editable=None, edit_json=None, licenses=None):  # noqa: E501
        """FullProfile - a model defined in Swagger"""  # noqa: E501
        self._uuid = None
        self._name = None
        self._json = None
        self._owner = None
        self._description = None
        self._created = None
        self._last_edited = None
        self._authorized = None
        self._editable = None
        self._edit_json = None
        self._licenses = None
        self.discriminator = None
        self.uuid = uuid
        self.name = name
        self.json = json
        if owner is not None:
            self.owner = owner
        if description is not None:
            self.description = description
        if created is not None:
            self.created = created
        if last_edited is not None:
            self.last_edited = last_edited
        if authorized is not None:
            self.authorized = authorized
        if editable is not None:
            self.editable = editable
        if edit_json is not None:
            self.edit_json = edit_json
        if licenses is not None:
            self.licenses = licenses

    @property
    def uuid(self):
        """Gets the uuid of this FullProfile.  # noqa: E501

        The profile's ID.  # noqa: E501

        :return: The uuid of this FullProfile.  # noqa: E501
        :rtype: str
        """
        return self._uuid

    @uuid.setter
    def uuid(self, uuid):
        """Sets the uuid of this FullProfile.

        The profile's ID.  # noqa: E501

        :param uuid: The uuid of this FullProfile.  # noqa: E501
        :type: str
        """
        if uuid is None:
            raise ValueError("Invalid value for `uuid`, must not be `None`")  # noqa: E501

        self._uuid = uuid

    @property
    def name(self):
        """Gets the name of this FullProfile.  # noqa: E501

        The profile's user-given name.  # noqa: E501

        :return: The name of this FullProfile.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this FullProfile.

        The profile's user-given name.  # noqa: E501

        :param name: The name of this FullProfile.  # noqa: E501
        :type: str
        """
        if name is None:
            raise ValueError("Invalid value for `name`, must not be `None`")  # noqa: E501

        self._name = name

    @property
    def json(self):
        """Gets the json of this FullProfile.  # noqa: E501

        The profile intent itself, stored as a trimmed JSON string.  # noqa: E501

        :return: The json of this FullProfile.  # noqa: E501
        :rtype: str
        """
        return self._json

    @json.setter
    def json(self, json):
        """Sets the json of this FullProfile.

        The profile intent itself, stored as a trimmed JSON string.  # noqa: E501

        :param json: The json of this FullProfile.  # noqa: E501
        :type: str
        """
        if json is None:
            raise ValueError("Invalid value for `json`, must not be `None`")  # noqa: E501

        self._json = json

    @property
    def owner(self):
        """Gets the owner of this FullProfile.  # noqa: E501

        The username of the profile owner.  # noqa: E501

        :return: The owner of this FullProfile.  # noqa: E501
        :rtype: str
        """
        return self._owner

    @owner.setter
    def owner(self, owner):
        """Sets the owner of this FullProfile.

        The username of the profile owner.  # noqa: E501

        :param owner: The owner of this FullProfile.  # noqa: E501
        :type: str
        """

        self._owner = owner

    @property
    def description(self):
        """Gets the description of this FullProfile.  # noqa: E501

        The profile's description.  # noqa: E501

        :return: The description of this FullProfile.  # noqa: E501
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """Sets the description of this FullProfile.

        The profile's description.  # noqa: E501

        :param description: The description of this FullProfile.  # noqa: E501
        :type: str
        """

        self._description = description

    @property
    def created(self):
        """Gets the created of this FullProfile.  # noqa: E501

        The profile's timestamp for creation.  # noqa: E501

        :return: The created of this FullProfile.  # noqa: E501
        :rtype: datetime
        """
        return self._created

    @created.setter
    def created(self, created):
        """Sets the created of this FullProfile.

        The profile's timestamp for creation.  # noqa: E501

        :param created: The created of this FullProfile.  # noqa: E501
        :type: datetime
        """

        self._created = created

    @property
    def last_edited(self):
        """Gets the last_edited of this FullProfile.  # noqa: E501

        The timestamp for when the profile was last edited.  # noqa: E501

        :return: The last_edited of this FullProfile.  # noqa: E501
        :rtype: datetime
        """
        return self._last_edited

    @last_edited.setter
    def last_edited(self, last_edited):
        """Sets the last_edited of this FullProfile.

        The timestamp for when the profile was last edited.  # noqa: E501

        :param last_edited: The last_edited of this FullProfile.  # noqa: E501
        :type: datetime
        """

        self._last_edited = last_edited

    @property
    def authorized(self):
        """Gets the authorized of this FullProfile.  # noqa: E501

        Whether the profile carries an admin's authorization with it.  # noqa: E501

        :return: The authorized of this FullProfile.  # noqa: E501
        :rtype: bool
        """
        return self._authorized

    @authorized.setter
    def authorized(self, authorized):
        """Sets the authorized of this FullProfile.

        Whether the profile carries an admin's authorization with it.  # noqa: E501

        :param authorized: The authorized of this FullProfile.  # noqa: E501
        :type: bool
        """

        self._authorized = authorized

    @property
    def editable(self):
        """Gets the editable of this FullProfile.  # noqa: E501

        Whether the profile can be edited by licensed users.  # noqa: E501

        :return: The editable of this FullProfile.  # noqa: E501
        :rtype: bool
        """
        return self._editable

    @editable.setter
    def editable(self, editable):
        """Sets the editable of this FullProfile.

        Whether the profile can be edited by licensed users.  # noqa: E501

        :param editable: The editable of this FullProfile.  # noqa: E501
        :type: bool
        """

        self._editable = editable

    @property
    def edit_json(self):
        """Gets the edit_json of this FullProfile.  # noqa: E501

        The JSON string for user-configured editable fields.  # noqa: E501

        :return: The edit_json of this FullProfile.  # noqa: E501
        :rtype: str
        """
        return self._edit_json

    @edit_json.setter
    def edit_json(self, edit_json):
        """Sets the edit_json of this FullProfile.

        The JSON string for user-configured editable fields.  # noqa: E501

        :param edit_json: The edit_json of this FullProfile.  # noqa: E501
        :type: str
        """

        self._edit_json = edit_json

    @property
    def licenses(self):
        """Gets the licenses of this FullProfile.  # noqa: E501

        The profile's collection of given licenses.  # noqa: E501

        :return: The licenses of this FullProfile.  # noqa: E501
        :rtype: list[ProfileLicense]
        """
        return self._licenses

    @licenses.setter
    def licenses(self, licenses):
        """Sets the licenses of this FullProfile.

        The profile's collection of given licenses.  # noqa: E501

        :param licenses: The licenses of this FullProfile.  # noqa: E501
        :type: list[ProfileLicense]
        """

        self._licenses = licenses

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
        if issubclass(FullProfile, dict):
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
        if not isinstance(other, FullProfile):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
