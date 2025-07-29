# -*- coding: utf-8 -*-
#
# This file is a part of the LinkAhead Project.
#
# Copyright (C) 2018 Research Group Biomedical Physics,
# Max-Planck-Institute for Dynamics and Self-Organization Göttingen
# Copyright (C) 2020-2024 IndiScale GmbH <info@indiscale.com>
# Copyright (C) 2020-2023 Florian Spreckelsen <f.spreckelsen@indiscale.com>
# Copyright (C) 2020-2022 Timm Fitschen <t.fitschen@indiscale.com>
# Copyright (C) 2024 Joscha Schmiedt <joscha@schmiedt.dev>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
#

"""
Collection of the central classes of the LinkAhead client, namely the Entity class
and all of its subclasses and the Container class which is used to carry out
transactions.

All additional classes are either important for the entities or the
transactions.
"""

from __future__ import annotations  # Can be removed with 3.10.

import re
import sys
import warnings
from builtins import str
from copy import deepcopy
from datetime import date, datetime
from functools import cmp_to_key
from hashlib import sha512
from os import listdir
from os.path import isdir
from random import randint
from tempfile import NamedTemporaryFile
from typing import TYPE_CHECKING, Any, Final, Literal, Optional, TextIO, Union

if TYPE_CHECKING:
    from io import BufferedWriter
    from os import PathLike
    from tempfile import _TemporaryFileWrapper

    from .datatype import DATATYPE
    QueryDict = dict[str, Optional[str]]

from warnings import warn

from lxml import etree

from ..configuration import get_config
from ..connection.connection import get_connection
from ..connection.encode import MultipartParam, multipart_encode
from ..exceptions import (AmbiguousEntityError, AuthorizationError,
                          ConsistencyError, EmptyUniqueQueryError,
                          EntityDoesNotExistError, EntityError,
                          EntityHasNoAclError, EntityHasNoDatatypeError,
                          HTTPURITooLongError, LinkAheadConnectionError,
                          LinkAheadException, MismatchingEntitiesError,
                          PagingConsistencyError, QueryNotUniqueError,
                          TransactionError, UniqueNamesError,
                          UnqualifiedParentsError, UnqualifiedPropertiesError)
from .datatype import (BOOLEAN, DATETIME, DOUBLE, INTEGER, TEXT,
                       get_list_datatype, is_list_datatype, is_reference)
from .state import State
from .timezone import TimeZone
from .utils import uuid, xml2str
from .versioning import Version

_ENTITY_URI_SEGMENT = "Entity"

OBLIGATORY: Final = "OBLIGATORY"
SUGGESTED: Final = "SUGGESTED"
RECOMMENDED: Final = "RECOMMENDED"
FIX: Final = "FIX"
ALL: Final = "ALL"
NONE: Final = "NONE"

if TYPE_CHECKING:
    INHERITANCE = Literal["OBLIGATORY", "SUGGESTED", "RECOMMENDED", "ALL", "NONE", "FIX"]
    IMPORTANCE = Literal["OBLIGATORY", "RECOMMENDED", "SUGGESTED", "FIX", "NONE"]
    ROLE = Literal["Entity", "Record", "RecordType", "Property", "File"]

SPECIAL_ATTRIBUTES = ["name", "role", "datatype", "description", "file",
                      "id", "path", "checksum", "size", "value", "unit"]


class Entity:

    """Entity is a generic LinkAhead object.

    The majority of all methods of the derived classes (e.g. Record,
    RecordType, Property ...) are defined here, e.g. add_property,
    add_parent, retrieve ... Each entity may have some attributes (id,
    name, description, ...), a set of properties, a set of parent
    entities and a set of messages which are generated through the
    processing in the client library or the server, or which can be used
    by the user to control several server-side plug-ins.
    """

    def __init__(
        self,
        name: Optional[str] = None,
        id: Optional[int] = None,
        description: Optional[str] = None,  # @ReservedAssignment
        datatype: Optional[DATATYPE] = None,
        value=None,
        role=None,
    ):

        self.__role: Optional[ROLE] = role
        self._checksum: Optional[str] = None
        self._size = None
        self._upload = None
        # If an entity is used (e.g. as parent), it is wrapped instead of being used directly.
        # see Entity._wrap()
        self._wrapped_entity: Optional[Entity] = None
        self._version: Optional[Version] = None
        self._cuid: Optional[str] = None
        self._flags: dict[str, str] = dict()
        self.__value = None
        self.__datatype: Optional[DATATYPE] = None
        self.datatype: Optional[DATATYPE] = datatype
        self.value = value
        self.messages = Messages()
        self.properties = PropertyList()
        self.parents = ParentList()
        self.path: Optional[str] = None
        self.file: Optional[File] = None
        self.unit: Optional[str] = None
        self.acl: Optional[ACL] = None
        self.permissions: Optional[Permissions] = None
        self.is_valid = lambda: False
        self.is_deleted = lambda: False
        self.name = name
        self.description = description
        self.id: Optional[int] = id
        self.state: Optional[State] = None

    def copy(self) -> Entity:
        """
        Return a copy of entity.

        FIXME: This method doesn't have a deep keyword argument.
        If deep == True return a deep copy, recursively copying all sub entities.

        Standard properties are copied using add_property.
        Special attributes, as defined by the global variable SPECIAL_ATTRIBUTES and additionaly
        the "value" are copied using setattr.
        """
        new: Union[File, Property, RecordType, Record, Entity]
        if self.role == "File":
            new = File()
        elif self.role == "Property":
            new = Property()
        elif self.role == "RecordType":
            new = RecordType()
        elif self.role == "Record":
            new = Record()
        elif self.role == "Entity":
            new = Entity()
        else:
            raise RuntimeError("Unkonwn role.")

        # Copy special attributes:
        # TODO: this might rise an exception when copying
        #       special file attributes like checksum and size.
        for attribute in SPECIAL_ATTRIBUTES:
            val = getattr(self, attribute)
            if val is not None:
                setattr(new, attribute, val)

        # Copy parents:
        for p in self.parents:
            new.add_parent(p)

        # Copy properties:
        for p in self.properties:
            new.add_property(p, importance=self.get_importance(p))

        return new

    @property
    def version(self):
        if self._version is not None or self._wrapped_entity is None:
            return self._version

        return self._wrapped_entity.version

    @version.setter
    def version(self, version: Optional[Version]):
        self._version = version

    @property
    def role(self):
        return self.__role

    @role.setter
    def role(self, role):
        if role is not None and role.lower() == "entity":
            self.__role = None
        else:
            self.__role = role

    @property
    def size(self):
        if self._size is not None:
            return int(self._size)

        if self._wrapped_entity is None:
            return None

        return self._wrapped_entity.size

    @property
    def id(self) -> Any:
        if self.__id is not None:
            return self.__id

        if self._wrapped_entity is None:
            return None

        return self._wrapped_entity.id

    @id.setter
    def id(self, new_id) -> None:
        if new_id is not None:
            if not isinstance(new_id, int):
                new_id = int(new_id)
            self.__id: Optional[int] = new_id
        else:
            self.__id = None

    @property
    def name(self):
        if self.__name is not None or self._wrapped_entity is None:
            return self.__name

        return self._wrapped_entity.name

    @name.setter
    def name(self, new_name):
        self.__name = new_name

    @property
    def datatype(self):
        if self.__datatype is not None or self._wrapped_entity is None:
            return self.__datatype

        return self._wrapped_entity.datatype

    @datatype.setter
    def datatype(self, new_type):
        # re-parse value
        self.__value = _parse_value(new_type, self.__value)
        self.__datatype = new_type

    @property
    def description(self):
        if self.__description is not None or self._wrapped_entity is None:
            return self.__description

        return self._wrapped_entity.description

    @description.setter
    def description(self, new_description):
        self.__description = new_description

    @property
    def checksum(self):
        return self._checksum

    @property
    def unit(self):
        if self.__unit is not None or self._wrapped_entity is None:
            return self.__unit

        return self._wrapped_entity.unit

    @unit.setter
    def unit(self, new_unit):
        self.__unit = new_unit

    @property
    def value(self):
        if self.__value is not None or self._wrapped_entity is None:
            return self.__value

        return self._wrapped_entity.value

    @value.setter
    def value(self, new_value):
        self.__value = _parse_value(self.datatype, new_value)

    @property
    def path(self):
        if self.__path is not None or self._wrapped_entity is None:
            return self.__path

        return self._wrapped_entity.path

    @path.setter
    def path(self, new_path):
        self.__path = new_path

    @property
    def thumbnail(self):
        if self.__thumbnail is not None or self._wrapped_entity is None:
            return self.__thumbnail

        return self._wrapped_entity.thumbnail

    @thumbnail.setter
    def thumbnail(self, new_thumbnail):
        self.__thumbnail = new_thumbnail

    @property
    def file(self):
        if self.__file is not None or self._wrapped_entity is None:
            return self.__file

        return self._wrapped_entity.file

    @file.setter
    def file(self, new_file):
        self.__file = new_file

    # FIXME Add test.
    @property   # getter for _cuid
    def cuid(self):
        # Set if None?
        return self._cuid

    # FIXME Add test.
    @property   # getter for _flags
    def flags(self):
        return self._flags.copy()   # for dict[str, str] shallow copy is enough

    def grant(
        self,
        realm: Optional[str] = None,
        username: Optional[str] = None,
        role: Optional[str] = None,
        permission: Optional[str] = None,
        priority: bool = False,
        revoke_denial: bool = True,
    ):
        """Grant a permission to a user or role for this entity.

        You must specify either only the username and the realm, or only the
        role.

        By default a previously existing denial rule would be revoked, because
        otherwise this grant wouldn't have any effect. However, for keeping
        contradicting rules pass revoke_denial=False.

        Parameters
        ----------
        permission: str
            The permission to be granted.
        username : str, optional
            The username. Exactly one is required, either the `username` or the
            `role`.
        realm: str, optional
            The user's realm. Required when username is not None.
        role: str, optional
            The role (as in Role-Based Access Control). Exactly one is
            required, either the `username` or the `role`.
        priority: bool, default False
            Whether this permission is granted with priority over non-priority
            rules.
        revoke_denial: bool, default True
            Whether a contradicting denial (with same priority flag) in this
            ACL will be revoked.
        """
        # @review Florian Spreckelsen 2022-03-17

        if self.acl is None:
            raise EntityHasNoAclError("This entity does not have an ACL (yet).")

        self.acl.grant(realm=realm, username=username, role=role,
                       permission=permission, priority=priority,
                       revoke_denial=revoke_denial)

    def deny(
        self,
        realm: Optional[str] = None,
        username: Optional[str] = None,
        role: Optional[str] = None,
        permission: Optional[str] = None,
        priority: bool = False,
        revoke_grant: bool = True,
    ):
        """Deny a permission to a user or role for this entity.

        You must specify either only the username and the realm, or only the
        role.

        By default a previously existing grant rule would be revoked, because
        otherwise this denial would override the grant rules anyways. However,
        for keeping contradicting rules pass revoke_grant=False.

        Parameters
        ----------
        permission: str
            The permission to be denied.
        username : str, optional
            The username. Exactly one is required, either the `username` or the
            `role`.
        realm: str, optional
            The user's realm. Required when username is not None.
        role: str, optional
            The role (as in Role-Based Access Control). Exactly one is
            required, either the `username` or the `role`.
        priority: bool, default False
            Whether this permission is denied with priority over non-priority
            rules.
        revoke_grant: bool, default True
            Whether a contradicting grant (with same priority flag) in this
            ACL will be revoked.
        """
        # @review Florian Spreckelsen 2022-03-17
        if self.acl is None:
            raise EntityHasNoAclError(
                "This entity does not have an ACL (yet).")

        self.acl.deny(realm=realm, username=username, role=role,
                      permission=permission, priority=priority,
                      revoke_grant=revoke_grant)

    def revoke_denial(self, realm=None, username=None,
                      role=None, permission=None, priority=False):
        if self.acl is None:
            raise EntityHasNoAclError("This entity does not have an ACL (yet).")
        self.acl.revoke_denial(
            realm=realm,
            username=username,
            role=role,
            permission=permission,
            priority=priority)

    def revoke_grant(self, realm=None, username=None,
                     role=None, permission=None, priority=False):
        if self.acl is None:
            raise EntityHasNoAclError("This entity does not have an ACL (yet).")
        self.acl.revoke_grant(
            realm=realm,
            username=username,
            role=role,
            permission=permission,
            priority=priority)

    def is_permitted(self, permission: Permission, role: Optional[str] = None):
        if role is None and self.permissions is not None:
            # pylint: disable=unsupported-membership-test
            return permission in self.permissions

        if self.acl is None:
            raise EntityHasNoAclError(
                "This entity does not have an ACL (yet).")
        return self.acl.is_permitted(role=role, permission=permission)

    def get_all_messages(self) -> Messages:
        ret = Messages()
        ret.append(self.messages)

        for p in self.properties:
            ret.extend(p.get_all_messages())

        for p in self.parents:
            ret.extend(p.get_all_messages())

        return ret

    def clear_server_messages(self):
        self.messages.clear_server_messages()

        for p in self.properties:
            p.clear_server_messages()

        for p in self.parents:
            p.clear_server_messages()

        return self

    def get_versionid(self):
        """Returns the concatenation of ID and version"""
        return str(self.id)+"@"+str(self.version.id)

    def get_importance(self, property):  # @ReservedAssignment
        """Get the importance of a given property regarding this entity."""

        if self.properties is not None:
            return self.properties.get_importance(property)

    def remove_property(self, property):  # @ReservedAssignment
        self.properties.remove(property)

        return self

    def remove_value_from_property(self, property_name: str, value: Any,
                                   remove_if_empty_afterwards: Optional[bool] = True):
        """Remove a value from a property given by name.

        Do nothing if this entity does not have a property of this
        ``property_name`` or if the property value is different of the given
        ``value``. By default, the property is removed from this entity if it
        becomes empty (i.e., value=None) through removal of the value. This
        behavior can be changed by setting ``remove_if_empty_afterwards`` to
        ``False`` in which case the property remains.

        Notes
        -----
        If the property value is a list and the value to be removed occurs more
        than once in this list, only its first occurrance is deleted (similar
        to the behavior of Python's ``list.remove()``.)

        If the property was empty (prop.value == None) before, the property is
        not removed afterwards even if ``remove_if_empty_afterwards`` is set to
        ``True``.  Rationale: the property being empty is not an effect of
        calling this function.

        Parameters
        ----------
        property_name : str
            Name of the property from which the ``value`` will be removed.

        value
            Value that is to be removed.

        remove_if_empty_afterwards : bool, optional
            Whether the property shall be removed from this entity if it is
            emptied by removing the ``value``. Default is ``True``.

        Returns
        -------
        self
            This entity.

        """

        property = self.get_property(property_name)
        if property is None:
            return self

        if property.value is None:
            remove_if_empty_afterwards = False

        empty_afterwards = False
        if isinstance(property.value, list):
            if value in property.value:
                property.value.remove(value)
                if property.value == []:
                    property.value = None
                    empty_afterwards = True
        elif property.value == value:
            property.value = None
            empty_afterwards = True

        if remove_if_empty_afterwards and empty_afterwards:
            self.remove_property(property_name)

        return self

    def remove_parent(self, parent):
        self.parents.remove(parent)

        return self

    def add_property(
        self,
        property: Union[int, str, Entity, None] = None,
        value: Union[
            int,
            str,
            bool,
            datetime,
            Entity,
            list[int],
            list[str],
            list[bool],
            list[Entity],
            None,
        ] = None,
        id: Optional[int] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        datatype: Optional[DATATYPE] = None,
        unit: Optional[str] = None,
        importance: Optional[IMPORTANCE] = None,
        inheritance: Optional[INHERITANCE] = None,
    ) -> Entity:  # @ReservedAssignment
        """Add a property to this entity.

        The first parameter is meant to identify the property entity either via
        its id or name, or by providing the corresponding ``Entity`` Python
        object. The second parameter is the value of the new property. Any other
        named parameter may be passed by means of the keywwords. Accepted
        keywords are: id, name, description, importance, inheritance, datatype,
        and unit.

        Notes
        -----
        If you want to add a property to an already existing entity, the
        property ``id`` of that property needs to be specified before you send
        the updated entity to the server.

        Parameters
        ----------
        property : int, str, Entity, optional
            An identifier for the property to be added, either its name, its id,
            or the corresponding Entity Python object. If ``None``, either the
            `name` or the `id` argument have to be specified explicitly. Default
            is ``None``.
        value : int, str, bool, datetime, Entity, or list of these types, optional
            The value of the new property. In case of a reference to another
            entity, this value may be the referenced entities id or the
            ``Entity`` as a Python object. Default is None.
        id : int, optional
            Id of the property, by default None
        name : str, optional
            Name of the property, by default None
        description : str, optional
            Description of the property, by default None
        datatype : str, optional
            Datatype of the property, by default None
        unit : str, optional
            Unit of the property, by default None
        importance :str, optional
            Importance of the property, by default None
        inheritance : str, optional
            Inheritance of the property, by default None

        Returns
        -------
        Entity
            This Entity object to which the new property has been added.

        Warns
        -----
        UserWarning
            If the first parameter is None then id or name must be defined and not be None.
        UserWarning
            If the first parameter is an integer then it is interpreted as the id and id must be
            undefined or None.
        UserWarning
            If the first parameter is not None and neither an instance of Entity nor an integer it
            is interpreted as the name and name must be undefined or None.

        Raises
        ------
        ValueError:
            If you try to add an ``Entity`` object with File or Record role (or,
            equivalently, a ``File`` or ``Record`` object) as a property, a
            ``ValueError`` is raised.

        Examples
        --------
        Add a simple integer property with the name ``TestProp`` and the value
        27 to a Record:

        >>> import linkahead as db
        >>> rec = db.Record(name="TestRec").add_parent(name="TestType")
        >>> rec.add_property("TestProp", value=27)  # specified by name, you could equally use the
        >>>                                         # property's id if it is known

        You can also use the Python object:

        >>> prop = db.Property(name="TestProp", datatype=db.INTEGER)
        >>> rec.add_property(prop, value=27)  # specified via the Python object

        In case of updating an existing Record, the Property needs to be
        specified by id:

        >>> rec = db.Record(name="TestRec").retrieve()
        >>> prop2 = db.Property(name="OtherTestProp").retrieve()
        >>> rec.add_property(id=prop2.id, value="My new value")
        >>> rec.update()

        Let's look at the more advanced example of adding a list of integers as
        value of the above integer ``TestProp``:

        >>> rec.add_property("TestProp", value=[27,28,29], datatype=db.LIST(db.INTEGER))

        Note that since `TestProp` is a scalar integer Property, the datatype
        `LIST<INTEGER>` has to be specified explicitly.

        Finally, we can also add reference properties, specified by the RecordType of the referenced
        entity.

        >>> ref_rec = db.Record(name="ReferencedRecord").add_parent(name="OtherRT")
        >>> rec.add_property(name="OtherRT", value=ref_rec)  # or value=ref_rec.id if ref_rec has
        >>>                                                  # one set by the server

        See more on adding properties and inserting data in
        https://docs.indiscale.com/caosdb-pylib/tutorials/Data-Insertion.html.

        """

        pid = id
        abstract_property = None

        if isinstance(property, Entity):
            if property.role is not None and property.role.lower() in ["record", "file"]:
                raise ValueError("The property parameter is a {0}. This "
                                 "is very unusual and probably not what you "
                                 "want. Otherwise, construct a property from "
                                 "a {0} using the Property class and add "
                                 "that to this entity.".format(property.role))
            abstract_property = property
        elif isinstance(property, int):
            if pid is not None:
                raise UserWarning(
                    "The first parameter was an integer which would normally be interpreted as the"
                    " id of the property which is to be added. But you have also specified a"
                    " parameter 'id' in the method call. This is ambiguous and cannot be processed."
                )
            pid = property
            id = pid
        elif property is not None:
            if name is not None:
                raise UserWarning(
                    "The first parameter was neither an instance of Entity nor an integer."
                    " Therefore the string representation of your first parameter would normally be"
                    " interpreted name of the property which is to be added. But you have also"
                    " specified a parameter 'name' in the method call. This is ambiguous and cannot"
                    " be processed.")
            name = str(property)

        if property is None and name is None and pid is None:
            raise UserWarning(
                "This method expects you to pass at least an entity, a name or an id.")

        new_property = Property(name=name, id=id, description=description, datatype=datatype,
                                value=value, unit=unit)

        if abstract_property is not None:
            new_property._wrap(abstract_property)

            # FIXME: this really necessary?

            if new_property.datatype is None and isinstance(
                    property, (RecordType, Record, File)):
                new_property.datatype = property
        new_property.value = value

        self.properties.append(
            property=new_property, importance=importance, inheritance=inheritance)

        return self

    def add_message(self, msg=None, type=None, code=None,  # @ReservedAssignment
                    description=None, body=None):
        """Add a message (msg) to this entity. If and only if no msg is given
        this method will created a new message from the parameters type, code,
        description, and body.

        @param msg: The message to be added to this entity.
        @param type: The type of the message to be added.
        @param code: The code of the message to be added.
        @param description: The description of the message to be added.
        @param body: The body of the message to be added.
        """

        if msg is not None:
            pass
        else:
            msg = Message(description=description, type=type, code=code,
                          body=body)
        self.messages.append(msg)

        return self

    def add_parent(
        self,
        parent: Union[Entity, int, str, None] = None,
        id: Optional[int] = None,
        name: Optional[str] = None,
        inheritance: INHERITANCE = "NONE",
    ):  # @ReservedAssignment
        """Add a parent to this entity.

        Parameters
        ----------
        parent : Entity or int or str or None
            The parent entity, either specified by the Entity object
            itself, or its id or its name. Default is None.
        id : int
            Integer id of the parent entity. Ignored if `parent`
            is not None.
        name : str
            Name of the parent entity. Ignored if `parent is not
            none`.
        inheritance : str, INHERITANCE
            One of ``obligatory``, ``recommended``, ``suggested``, or ``all``. Specifies the
            minimum importance which parent properties need to have to be inherited by this
            entity. If no `inheritance` is given, no properties will be inherited by the child.
            This parameter is case-insensitive.

        Notes
        -----
        Note that the behaviour of the `inheritance` argument currently has not
        yet been specified when assigning parents to Records, it only works for
        inheritance of RecordTypes (and Properties). For more information, it is
        recommended to look into the :ref:`data insertion
        tutorial<tutorial-inheritance-properties>`.

        Raises
        ------
        UserWarning
            If neither a `parent` parameter, nor the `id`, nor `name`
            parameter is passed to this method.

        """

        pid = id
        parent_entity = None

        if isinstance(parent, Entity):
            parent_entity = parent
        elif isinstance(parent, int):
            pid = parent
        elif parent is not None:
            name = str(parent)

        if pid is None and name is None and parent_entity is None:
            raise UserWarning(
                "This method expects you to pass at least an entity, a name or an id.")

        addp = Parent(id=pid, name=name, inheritance=inheritance)

        if parent_entity is not None:
            addp._wrap(parent_entity)
        self.parents.append(addp)

        return self

    def has_parent(self, parent: Entity, recursive: bool = True, retrieve: bool = True,
                   check_name: bool = True, check_id: bool = False):
        """Check if this entity has a given parent.

        If 'check_name' and 'check_id' are both False, test for identity
        on the Python level. Otherwise use the name and/or ID for the
        check. Note that, if checked, name or ID should not be None,
        lest the check fail.

        Parameters
        ----------

        parent: Entity
          Check for this parent.

        recursive: bool, optional
          Whether to check recursively.

        check_name: bool, optional
          Whether to use the name for ancestry check.

        check_id: bool, optional
          Whether to use the ID for ancestry check.

        retrieve: bool, optional
          If False, do not retrieve parents from the server.

        Returns
        -------
        out: bool
          True if ``parent`` is a true parent, False otherwise.
        """

        if recursive:
            parents = self.get_parents_recursively(retrieve=retrieve)
        else:
            if retrieve:
                parents = [pp.retrieve()._wrapped_entity for pp in self.parents]
            else:
                parents = [pp._wrapped_entity for pp in self.parents]

        if not (check_name or check_id):
            return parent in parents

        name_result = (
            not check_name or
            (parent.name is not None and
             parent.name in [pp.name for pp in parents]))
        id_result = (
            not check_id or
            (parent.id is not None and
             parent.id in [pp.id for pp in parents]))

        return name_result and id_result

    def get_parents(self):
        """Get all parents of this entity.

        @return: ParentList(list)
        """

        return self.parents

    def get_parents_recursively(self, retrieve: bool = True) -> list[Entity]:
        """Get all ancestors of this entity.

        Parameters
        ----------

        retrieve: bool, optional
          If False, do not retrieve parents from the server.

        Returns
        -------
        out: list[Entity]
          The parents of this Entity
        """

        all_parents: list[Entity] = []
        self._get_parent_recursively(all_parents, retrieve=retrieve)

        return all_parents

    def _get_parent_recursively(self, all_parents: list[Entity], retrieve: bool = True):
        """Get all ancestors with a little helper.

        As a side effect of this method, the ancestors are added to
        all_parents.

        @param all_parents: list, The added parents so far.

        @return: None, but see side effects.
        """

        for parent in self.parents:
            # TODO:
            # Comment on _wrap and _wrapped_entity
            # Currently, I (henrik) do not why the wrapping is necessary (and it is not
            # documented). However, the following illustrates, why I think, it is a bad idea.
            # First you add a parent with rec.add_parent(parent), but then you cannot access
            # attributes of parent when you use rec.parents[0] for example becasue you do not get
            # the same object but a wrapping object and you need to know that you only get the
            # original by accessing the private (!) _wrapped_entity object.
            w_parent = parent._wrapped_entity
            if retrieve:
                parent.retrieve()
                for next_parent in parent.parents:
                    w_parent.add_parent(next_parent)

            if (w_parent.id, w_parent.name) not in [
                    (all_p.id, all_p.name) for all_p in all_parents]:
                all_parents.append(w_parent)
                w_parent._get_parent_recursively(all_parents, retrieve=retrieve)

    def get_parent(self, key: Union[int, Entity, str]) -> Union[Entity, None]:
        """Return the first parent matching the key or None if no match exists.

        Parameters
        ---------
        key : int or Enity or str
            The id, Entity, or name of the parent that should be
            returned. If an Entity is given, its id or its name is
            used to find a matching parent.

        Returns
        -------
        parent : Entity
            The first parent of this entity that matches the given id,
            entity, or name.

        """

        if isinstance(key, int):
            for p in self.parents:
                if p.id is not None and int(p.id) == int(key):
                    return p
        elif isinstance(key, Entity):
            if key.id is not None:
                # first try by id
                found = self.get_parent(int(key.id))

                if found is not None:
                    return found
            # otherwise by name

            return self.get_parent(key.name)
        else:
            for p in self.parents:
                if (p.name is not None
                        and str(p.name).lower() == str(key).lower()):

                    return p

        return None

    def get_properties(self):
        """Get all properties of this entity.

        @return: PropertyList(list)
        """

        return self.properties

    def get_property(self, pattern: Union[int, str, Entity]) -> Union[Property, None]:
        """ Return the first matching property or None.

        Parameters
        ----------
        pattern : str or int or Entity
            The name or id to look for (case-insensitive) or an Entity where
            the name or id is used to match the properites of this instance.

        Returns
        -------
        property : Property
            The first Property of this Entity with a matching name or id.

        """
        # entity given

        if (hasattr(pattern, "name") or hasattr(pattern, "id")):
            # only return if a result was found, otherwise use id

            if (hasattr(pattern, "name") and pattern.name is not None
                    and self.get_property(pattern.name) is not None):

                return self.get_property(pattern.name)

            if hasattr(pattern, "id") and pattern.id is not None:
                return self.get_property(pattern.id)

        # int given
        elif isinstance(pattern, int):
            for p in self.properties:
                if p.id is not None and int(p.id) == int(pattern):
                    return p
        # str given
        elif isinstance(pattern, str):
            for p in self.properties:
                if (p.name is not None
                        and str(p.name).lower() == str(pattern).lower()):

                    return p
        else:
            raise ValueError(
                "`pattern` argument should be an Entity, int or str.")

        return None

    def _get_value_for_selector(
        self, selector: Union[str, list[str], tuple[str]]
    ) -> Any:
        """return the value described by the selector

        A selector is a list or a tuple of strings describing a path in an
        entity tree with self as root. The last selector may be a special one
        like unit or name.

        See also get_property_values()
        """
        SPECIAL_SELECTORS = ["unit", "value", "description", "id", "name"]

        if isinstance(selector, str):
            selector = [selector]
        elif isinstance(selector, tuple):
            selector = list(selector)

        ref = self

        # there are some special selectors which can be applied to the
        # final element; if such a special selector exists we split it
        # from the list

        if selector[-1].lower() in SPECIAL_SELECTORS:
            special_selector = selector[-1]
            selector = selector[:-1]
        else:
            special_selector = None

        # iterating through the entity tree according to the selector
        prop: Optional[Property] = None
        for subselector in selector:
            # selector does not match the structure, we cannot get a
            # property of non-entity

            if not isinstance(ref, Entity):
                return None

            prop = ref.get_property(subselector)

            # selector does not match the structure, we did not get a
            # property

            if prop is None:
                return None

            # if the property is a reference, we are interested in the
            # corresponding entities attributes

            if isinstance(prop.value, Entity):
                ref = prop.value

            # otherwise in the attributes of the property
            else:
                ref = prop

        # if we saved a special selector before, apply it
        if special_selector is None:
            if prop is None:
                return None
            else:
                return prop.value
        else:
            return getattr(ref, special_selector.lower())

    def get_property_values(self, *selectors) -> tuple:
        """ Return a tuple with the values described by the given selectors.

        This represents an entity's properties as if it was a row of a table
        with the given columns.

        If the elements of the selectors parameter are tuples, they will return
        the properties of the referenced entity, if present. E.g. ("window",
        "height") will return the value of the height property of the
        referenced window entity.

        The tuple's values correspond to the order of selectors parameter.

        The tuple contains None for all values that are not available in the
        entity. That does not necessarily mean, that the values are not stored
        in the database (e.g. if a single entity was retrieved without
        referenced entities).

        Parameters
        ----------
        *selectors : str or tuple of str
            Each selector is a list or tuple of property names, e.g. `"height",
            "width"`.

        Returns
        -------
        row : tuple
            A row-like representation of the entity's properties.
        """
        row: tuple = tuple()

        for selector in selectors:
            val = self._get_value_for_selector(selector)

            if isinstance(val, Entity):
                val = val.id if val.id is not None else val.name
            row += (val,)

        return row

    def get_messages(self):
        """Get all messages of this entity.

        @return: Messages(list)
        """

        return self.messages

    def get_warnings(self):
        """Get all warning messages of this entity.

        @return Messages(list): Warning messages.
        """
        ret = Messages()

        for m in self.messages:
            if m.type.lower() == "warning":
                ret.append(m)

        return ret

    def get_errors(self):
        """Get all error messages of this entity.

        @return Messages(list): Error messages.
        """
        ret = Messages()

        for m in self.messages:
            if m.type.lower() == "error":
                ret.append(m)

        if self._wrapped_entity is not None:
            ret.extend(self._wrapped_entity.get_errors())

        return ret

    def get_errors_deep(self, roots=None) -> list[tuple[str, list[Entity]]]:
        """Get all error messages of this entity and all sub-entities /
        parents / properties.

        @return A list of tuples. Tuple index 0 contains the error message
                and tuple index 1 contains the tree.
        """
        roots = [] if roots is None else roots
        result_list = list()
        ret_self = self.get_errors()
        result_list.extend([
            (m, roots) for m in ret_self])

        for parent in self.get_parents():
            result_list.extend(
                parent.get_errors_deep(
                    roots + [parent]))

        return result_list

    def has_errors(self):
        '''
        @return True: if and only if this entities has any error messages.
        '''

        for m in self.messages:
            if m.type.lower() == "error":
                return True

        return False

    def to_xml(
        self,
        xml: Optional[etree._Element] = None,
        add_properties: INHERITANCE = "ALL",
        local_serialization: bool = False,
        visited_entities: Optional[list] = None
    ) -> etree._Element:
        """Generate an xml representation of this entity. If the parameter xml
        is given, all attributes, parents, properties, and messages of this
        entity will be added to it instead of creating a new element.

        Raise an error if xml is not a lxml.etree.Element

        Parameters
        ----------
        xml : etree._Element, optional
            an xml element to which all attributes, parents,
            properties, and messages are to be added. Default is None.
        visited_entities : list, optional
            list of enties that are being printed for recursion check,
            should never be set manually. Default is None.
        add_properties : INHERITANCE, optional
            FIXME: Add documentation for the add_properties
            parameter. Default is "ALL".
        local_serialization : bool, optional
            FIXME: Add documentation for the local_serialization
            parameter. Default is False.

        Returns
        -------
        xml : etree._Element
            xml representation of this entity.
        """

        if xml is None:
            # use role as xml tag name, fall-back to "Entity"
            elem_tag = "Entity" if self.role is None else self.role
            xml = etree.Element(elem_tag)
        assert isinstance(xml, etree._Element)

        if visited_entities is None:
            visited_entities = []
        if self in visited_entities:
            xml.text = xml2str(etree.Comment("Recursive reference"))
            return xml
        visited_entities.append(self)

        # unwrap wrapped entity
        if self._wrapped_entity is not None:
            xml = self._wrapped_entity.to_xml(xml, add_properties,
                                              visited_entities=visited_entities.copy())

        if self.id is not None:
            xml.set("id", str(self.id))

        if self._cuid is not None:
            xml.set("cuid", str(self._cuid))

        if self.name is not None:
            xml.set("name", str(self.name))

        if self.description is not None:
            xml.set("description", str(self.description))

        if self.version is not None:
            # If this ever causes problems, we might add
            # visited_entities support here since it does have some
            # recursion with predecessors / successors. But should be
            # fine for now, since it is always set by the server.
            xml.append(self.version.to_xml())

        if self.value is not None:
            if isinstance(self.value, Entity):
                if self.value.id is not None:
                    xml.text = str(self.value.id)
                elif self.value.name is not None:
                    xml.text = str(self.value.name)
                else:
                    dt_str = xml2str(self.value.to_xml(visited_entities=visited_entities.copy()))
                    xml.text = dt_str
            elif isinstance(self.value, list):
                for v in self.value:
                    v_elem = etree.Element("Value")

                    if isinstance(v, Entity):
                        if v.id is not None:
                            v_elem.text = str(v.id)
                        elif v.name is not None:
                            v_elem.text = str(v.name)
                        else:
                            dt_str = xml2str(v.to_xml(visited_entities=visited_entities.copy()))
                            v_elem.text = dt_str
                    elif v == "":
                        v_elem.append(etree.Element("EmptyString"))
                    elif v is None:
                        pass
                    else:
                        v_elem.text = str(v)
                    xml.append(v_elem)
            elif self.value == "":
                xml.append(etree.Element("EmptyString"))
            elif str(self.value) == "nan":
                xml.text = "NaN"
            else:
                xml.text = str(self.value)

        if self.datatype is not None:
            if isinstance(self.datatype, Entity):
                if self.datatype.id is not None:
                    xml.set("datatype", str(self.datatype.id))
                elif self.datatype.name is not None:
                    xml.set("datatype", str(self.datatype.name))
                else:
                    dt_str = xml2str(self.datatype.to_xml(visited_entities=visited_entities.copy()))
                    # Todo: Use for pretty-printing with calls from _repr_ only?
                    # dt_str = dt_str.replace('<', 'ᐸ').replace('>', 'ᐳ').replace(' ', '⠀').replace(
                    # '"', '\'').replace('\n', '')
                    xml.set("datatype", dt_str)
            else:
                xml.set("datatype", str(self.datatype))

        if self.path is not None:
            xml.set("path", self.path)

        if self.file is not None and local_serialization:
            xml.set("file", self.file)

        if self._checksum is not None:
            xml.set("checksum", self._checksum)

        if self.size is not None:
            xml.set("size", str(self.size))

        if self.unit is not None:
            xml.set("unit", str(self.unit))

        if self.messages is not None:
            self.messages.to_xml(xml)

        if self.parents is not None:
            self.parents.to_xml(xml, visited_entities=visited_entities.copy())

        if self.properties is not None:
            self.properties.to_xml(xml, add_properties,
                                   visited_entities=visited_entities.copy())

        if len(self._flags) > 0:
            flagattr = ""

            for key in self._flags.keys():
                flag = self._flags[key]

                if flag is not None and flag != "":
                    flagattr += str(key) + ":" + str(flag) + ","
                else:
                    flagattr += str(key) + ","
            xml.set("flag", flagattr)

        if self.acl is not None:
            xml.append(self.acl.to_xml())

        if self.state is not None:
            xml.append(self.state.to_xml())

        return xml

    @staticmethod
    def _from_xml(entity, elem):
        """Parse a single string representation of an xml element to an entity.

        @param entity: the entity
        @param elem: the xml element
        """

        if isinstance(entity, Entity):
            entity.role = elem.tag
        entity._cuid = elem.get("cuid")
        entity.id = elem.get("id")  # @ReservedAssignment
        entity.name = elem.get("name")
        entity.description = elem.get("description")
        entity.path = elem.get("path")
        entity._checksum = elem.get("checksum")
        entity._size = elem.get("size")
        entity.datatype = elem.get("datatype")  # @ReservedAssignment
        entity.unit = elem.get("unit")
        entity.file = elem.get("file")

        if hasattr(entity, "affiliation"):
            entity.affiliation = elem.get("affiliation")

        vals = list()

        for celem in elem:

            child = _parse_single_xml_element(celem)

            if isinstance(child, Property):
                entity.properties.append(property=child,
                                         importance=celem.get("importance"),
                                         inheritance=None)
            elif isinstance(child, Parent):
                entity.add_parent(child)
            elif isinstance(child, ACL):
                entity.acl = child
            elif isinstance(child, Permissions):
                entity.permissions = child
            elif isinstance(child, Message):
                entity.add_message(child)
            elif isinstance(child, Version):
                entity.version = child
            elif isinstance(child, State):
                entity.state = child
            elif child is None or hasattr(child, "encode"):
                vals.append(child)
            elif isinstance(child, Entity):
                vals.append(child)
            else:
                raise TypeError(
                    'Child was neither a Property, nor a Parent, nor a Message.\
                    Was ' + str(type(child)) + "\n" + str(child))

        # add VALUE
        value = None

        if vals:
            # The value[s] have been inside a <Value> tag.
            value = vals
        elif elem.text is not None and elem.text.strip() != "":
            value = elem.text.strip()

        try:
            entity.value = value
        except ValueError:
            # circumvent the parsing.
            entity.__value = value

        return entity

    def __repr__(self):
        return xml2str(self.to_xml())

    def retrieve_acl(self):
        self.acl = Entity(name=self.name, id=self.id).retrieve(
            flags={"ACL": None}).acl

    def update_acl(self, **kwargs):
        """Update this entity's ACL on the server.

        A typical workflow is to first edit ``self.acl`` and then call this
        method.

        Note
        ----
        This overwrites any existing ACL, so you may want to run
        ``retrieve_acl`` before updating the ACL in this entity.

        Parameters
        ----------
        **kwargs : dict
            Keyword arguments that are passed through to the
            ``Entity.update`` method.  Useful for e.g. ``unique=False`` in the
            case of naming collisions.

        Returns
        -------
        e : Entity
            This entity after the update of the ACL.

        """
        if self.id is None:
            c = Container().retrieve(query=self.name, sync=False)

            if len(c) == 1:
                e = c[0]
            elif len(c) == 0:
                ee = EntityDoesNotExistError(
                    "The entity to be updated does not exist on the server.",
                    entity=self
                )
                raise TransactionError(ee)
            else:
                ae = AmbiguousEntityError(
                    "Could not determine the desired Entity which is to be updated by its name.",
                    entity=self
                )
                raise TransactionError(ae)
        else:
            e = Container().retrieve(query=self.id, sync=False)[0]
        if self.acl is None:
            raise EntityHasNoAclError("This entity does not have an ACL yet. Please set one first.")
        e.acl = ACL(self.acl.to_xml())
        e.update(**kwargs)

        return e

    def delete(self, raise_exception_on_error=True):
        return Container().append(self).delete(
            raise_exception_on_error=raise_exception_on_error)[0]

    def retrieve(self, unique=True, raise_exception_on_error=True, flags=None):
        """Retrieve this entity identified via its id if present and via its
        name otherwise. Any locally already existing attributes (name,
        description, ...) will be preserved. Any such properties and parents
        will be synchronized as well. They will not be overridden. This method
        returns a Container containing the this entity.

        Note: If only a name is given this could lead to ambiguities. Usually
        this would raise a LinkAheadException. Set the flag 'unique' to False if
        this Exception should be suppressed.  If unique is False this method
        returns a Container object which carries the returned entities. They are
        distinct from this one. This entity will no be changed somehow.

        @param unique=True: flag to suppress the ambiguity exception.

        @return
        Container with the returned entities or single entity if and only
        if unique was True and no exception was raised.

        """

        if unique:
            c = Container().append(self).retrieve(
                unique=unique, raise_exception_on_error=raise_exception_on_error, flags=flags)

            if len(c) == 1:
                c[0].messages.extend(c.messages)

                return c[0]

            raise QueryNotUniqueError("This retrieval was not unique!!!")

        return Container().append(self).retrieve(
            unique=unique, raise_exception_on_error=raise_exception_on_error, flags=flags)

    def insert(
        self,
        raise_exception_on_error=True,
        unique=True,
        sync=True,
        strict=False,
        flags: Optional[dict] = None,
    ):
        """Insert this entity into a LinkAhead server. A successful insertion will
        generate a new persistent ID for this entity. This entity can be
        identified, retrieved, updated, and deleted via this ID until it has
        been deleted.

        If the insertion fails, a LinkAheadException will be raised. The server will have returned
        at least one error-message describing the reason why it failed in that case (call
        <this_entity>.get_all_messages() in order to get these error-messages).

        Some insertions might cause warning-messages on the server-side, but the entities are
        inserted anyway. Set the flag 'strict' to True in order to force the server to take all
        warnings as errors.  This prevents the server from inserting this entity if any warning
        occurs.

        Parameters
        ----------
        strict : bool, optional
            Flag for strict mode. Default is False.
        raise_exception_on_error : bool, optional
            Flag to raise an exception when an error occurs. Default is True.
        unique : bool, optional
            Flag to only allow insertion of elements with unique names. Default
            is True.
        flags : dict, optional
            A dictionary of flags to be send with the insertion. Default is
            None.

        """

        return Container().append(self).insert(
            strict=strict,
            raise_exception_on_error=raise_exception_on_error,
            unique=unique,
            sync=sync,
            flags=flags)[0]

    def update(self, strict=False, raise_exception_on_error=True,
               unique=True, flags=None, sync=True):
        """Update this entity.

        There are two possible work-flows to perform this update:
        First:
            1) retrieve an entity
            2) do changes
            3) call update method

        Second:
            1) construct entity with id
            2) call update method.

        For slight changes the second one it is more comfortable. Furthermore, it is possible to
        stay off-line until calling the update method. The name, description, unit, datatype, path,
        and value of an entity may be changed. Additionally, properties, parents and messages may be
        added.

        However, the first one is more powerful: It is possible to delete and change properties,
        parents and attributes, which is not possible via the second one for internal reasons (which
        are reasons of definiteness).

        If the update fails, a LinkAheadException will be raised. The server will have returned at
        least one error message describing the reason why it failed in that case (call
        <this_entity>.get_all_messages() in order to get these error-messages).

        Some updates might cause warning messages on the server-side, but the updates are performed
        anyway. Set flag 'strict' to True in order to force the server to take all warnings as
        errors.  This prevents the server from updating this entity if any warnings occur.

        @param strict=False: Flag for strict mode.
        """

        return Container().append(self).update(
            strict=strict,
            sync=sync,
            raise_exception_on_error=raise_exception_on_error,
            unique=unique,
            flags=flags)[0]

    def _wrap(self, entity):
        """
        When entity shall be used as parent or property it is not added to the corresponding list
        (such as the parent list) directly, but another Entity object is created and the original
        Entity is wrapped using this function
        TODO: document here and in dev docs why this is done.
        """
        self._wrapped_entity = entity

        return self

    def set_flag(self, key, value=None):
        self._flags[key] = value

        return self


def _parse_value(datatype, value):
    """Parse the value (from XML input) according to the given datatype
    """

    # Simple values
    if value is None:
        return value

    if datatype is None:
        return value

    if datatype == DOUBLE:
        return float(value)

    if datatype == INTEGER:
        if isinstance(value, int):
            return value
        elif isinstance(value, float) and value.is_integer():
            return int(value)
        else:
            return int(str(value))

    if datatype == BOOLEAN:
        if str(value).lower() == "true":
            return True
        elif str(value).lower() == "false":
            return False
        else:
            raise ValueError("Boolean value was {}.".format(value))

    # Datetime and text are returned as-is
    if datatype in [DATETIME, TEXT]:
        if isinstance(value, str):
            return value

    if datatype == DATETIME and (isinstance(value, date) or isinstance(value, datetime)):
        return value

    # deal with collections
    if isinstance(datatype, str):
        matcher = re.compile(r"^(?P<col>[^<]+)<(?P<dt>[^>]+)>$")
        m = matcher.match(datatype)

        if m:
            col = m.group("col")
            dt = m.group("dt")

            if col == "LIST":
                ret = list()
            else:
                return value

            if hasattr(value, "__iter__") and not isinstance(value, str):
                for v in value:
                    ret.append(_parse_value(dt, v))
            else:
                # put a single value into a list since the datatype says so.
                ret.append(_parse_value(dt, value))

            return ret

    # This is for a special case, where the xml parser could not differentiate
    # between single values and lists with one element.
    if hasattr(value, "__len__") and not isinstance(value, str) and len(value) == 1:
        return _parse_value(datatype, value[0])

    # deal with references
    if isinstance(value, Entity):
        return value

    if isinstance(value, str) and "@" in value:
        # probably this is a versioned reference

        return str(value)
    else:
        # for unversioned references
        try:
            return int(value)
        except ValueError:
            # reference via name

            return str(value)
        except TypeError as te:
            # deal with invalid XML: List of values without appropriate datatype
            if isinstance(value, list):
                raise TypeError(
                    "Invalid datatype: List valued properties must be announced by "
                    "the datatype.\n" + f"Datatype: {datatype}\nvalue: {value}")
            else:
                # Everything else that's not related to wrong list assignments
                raise te


def _log_request(request, xml_body=None):
    if Container._debug() > 0:
        print("\n" + request)

        if xml_body is not None:
            print("======== Request body ========\n")
            print(xml2str(xml_body))
            print("\n==============================\n")


def _log_response(body):
    if Container._debug() > 0:
        print("\n======== Response body ========\n")
        print(body.decode())
        print("\n===============================\n")


class QueryTemplate():

    def __init__(
        self,
        id: Optional[int] = None,
        name: Optional[str] = None,
        query: Optional[str] = None,
        description: Optional[str] = None,
    ):  # @ReservedAssignment

        self.id = (int(id) if id is not None else None)
        self.role = "QueryTemplate"
        self.name = name
        self.description = description
        self.query = query
        self._cuid = None
        self.value = None
        self.datatype = None
        self.messages = Messages()
        self.properties = None
        self.parents = None
        self.path = None
        self.file = None
        self._checksum = None
        self._size = None
        self._upload = None
        self.unit = None
        self.acl: Optional[ACL] = None
        self.permissions: Optional[Permissions] = None
        self.is_valid = lambda: False
        self.is_deleted = lambda: False
        self.version = None
        self.state = None

    def retrieve(
        self,
        raise_exception_on_error: bool = True,
        unique: bool = True,
        sync: bool = True,
        flags: Optional[QueryDict] = None,
    ) -> Container:

        return Container().append(self).retrieve(
            raise_exception_on_error=raise_exception_on_error,
            unique=unique,
            sync=sync,
            flags=flags)[0]

    def insert(
        self,
        strict: bool = True,
        raise_exception_on_error: bool = True,
        unique: bool = True,
        sync: bool = True,
        flags: Optional[QueryDict] = None,
    ) -> Container:

        return Container().append(self).insert(
            strict=strict,
            raise_exception_on_error=raise_exception_on_error,
            unique=unique,
            sync=sync,
            flags=flags)[0]

    def update(
        self,
        strict: bool = True,
        raise_exception_on_error: bool = True,
        unique: bool = True,
        sync: bool = True,
        flags: Optional[QueryDict] = None,
    ) -> Container:

        return Container().append(self).update(
            strict=strict,
            raise_exception_on_error=raise_exception_on_error,
            unique=unique,
            sync=sync,
            flags=flags)[0]

    def delete(self, raise_exception_on_error=True):
        return Container().append(self).delete(
            raise_exception_on_error=raise_exception_on_error)[0]

    def __repr__(self):
        return xml2str(self.to_xml())

    def to_xml(self, xml: Optional[etree._Element] = None) -> etree._Element:
        if xml is None:
            xml = etree.Element("QueryTemplate")

        if self.name is not None:
            xml.set("name", self.name)

        if self.id is not None:
            xml.set("id", str(self.id))

        if self.description is not None:
            xml.set("description", self.description)

        if self.version is not None:
            xml.append(self.version.to_xml())

        if self.query is not None:
            queryElem = etree.Element("Query")
            queryElem.text = self.query
            xml.append(queryElem)

        if self.messages is not None:
            self.messages.to_xml(xml)

        if self.acl is not None:
            xml.append(self.acl.to_xml())

        return xml

    @staticmethod
    def _from_xml(xml: etree._Element):
        if str(xml.tag).lower() == "querytemplate":
            q = QueryTemplate(name=xml.get("name"),
                              description=xml.get("description"), query=None)

            for e in xml:
                if str(e.tag).lower() == "query":
                    q.query = e.text
                else:
                    child = _parse_single_xml_element(e)
                    if child is None:
                        continue
                    if isinstance(child, Message):
                        q.messages.append(child)
                    elif isinstance(child, ACL):
                        q.acl = child
                    elif isinstance(child, Version):
                        q.version = child  # type: ignore
                    elif isinstance(child, Permissions):
                        q.permissions = child
            id = xml.get("id")
            q.id = int(id) if id is not None else None

            return q
        else:
            return None

    def clear_server_messages(self):
        self.messages.clear_server_messages()

    def get_parents(self):
        return []

    def get_properties(self):
        return []

    def has_id(self):
        return self.id is not None

    def get_errors(self):
        ret = Messages()

        for m in self.messages:
            if str(m.type).lower() == "error":
                ret.append(m)

        return ret

    def get_messages(self):
        return self.messages

    def has_errors(self):
        return len(self.get_errors()) > 0


class Parent(Entity):
    """The parent entities."""

    @property
    def affiliation(self):
        if self.__affiliation is not None or self._wrapped_entity is None:
            return self.__affiliation
        elif hasattr(self._wrapped_entity, "affiliation"):
            return self._wrapped_entity.affiliation

        return

    @affiliation.setter
    def affiliation(self, affiliation):
        self.__affiliation = affiliation

    def __init__(
        self,
        id: Optional[int] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        inheritance: Optional[INHERITANCE] = None,
    ):  # @ReservedAssignment
        Entity.__init__(self, id=id, name=name, description=description)

        if inheritance is not None:
            self.set_flag("inheritance", inheritance)
        self.__affiliation = None

    def to_xml(
        self,
        xml: Optional[etree._Element] = None,
        add_properties: INHERITANCE = "NONE",
        local_serialization: bool = False,
        visited_entities: Optional[Union[list, None]] = None,
    ):
        if xml is None:
            xml = etree.Element("Parent")

        if visited_entities is None:
            visited_entities = []

        return super().to_xml(xml=xml, add_properties=add_properties,
                              visited_entities=visited_entities)


class _EntityWrapper(object):
    pass


class _ConcreteProperty(_EntityWrapper):
    pass


class Property(Entity):

    """LinkAhead's Property object."""

    def add_property(self, property=None, value=None, id=None, name=None, description=None,
                     datatype=None,
                     unit=None, importance=FIX, inheritance=FIX):  # @ReservedAssignment
        """See ``Entity.add_property``."""

        return super().add_property(
            property=property, id=id, name=name, description=description, datatype=datatype,
            value=value, unit=unit, importance=importance, inheritance=inheritance)

    def add_parent(self, parent=None, id=None, name=None, inheritance=FIX):
        """Add a parent Entity to this Property.

        Parameters
        ----------
        parent : Entity or int or str or None
            The parent entity, either specified by the Entity object
            itself, or its id or its name. Default is None.
        id : int
            Integer id of the parent entity. Ignored if `parent`
            is not None.
        name : str
            Name of the parent entity. Ignored if `parent is not
            none`.
        inheritance : str, default: FIX
            One of ``obligatory``, ``recommended``, ``suggested``, or ``fix``. Specifies the
            minimum importance which parent properties need to have to be inherited by this
            entity. If no `inheritance` is given, no properties will be inherited by the child.
            This parameter is case-insensitive.

        See Also
        --------
        Entity.add_parent

        """

        return super(Property, self).add_parent(parent=parent, id=id, name=name,
                                                inheritance=inheritance)

    def __init__(
        self,
        name: Optional[str] = None,
        id: Optional[int] = None,
        description: Optional[str] = None,
        datatype: Union[DATATYPE, None] = None,
        value=None,
        unit: Optional[str] = None,
    ):
        Entity.__init__(self, id=id, name=name, description=description,
                        datatype=datatype, value=value, role="Property")
        self.unit = unit

    def to_xml(
        self,
        xml: Optional[etree._Element] = None,
        add_properties: INHERITANCE = "ALL",
        local_serialization: bool = False,
        visited_entities: Optional[Union[list, None]] = None,
    ):
        if xml is None:
            xml = etree.Element("Property")

        if visited_entities is None:
            visited_entities = []

        return super(Property, self).to_xml(
            xml=xml,
            add_properties=add_properties,
            local_serialization=local_serialization,
            visited_entities=visited_entities,
        )

    def is_reference(self, server_retrieval: bool = False) -> Optional[bool]:
        """Returns whether this Property is a reference

        Parameters
        ----------
        server_retrieval : bool, optional
            If True and the datatype is not set, the Property is retrieved from the server, by
            default False

        Returns
        -------
        bool, NoneType
            Returns whether this Property is a reference or None if a server call is needed to
            check correctly, but server_retrieval is set to False.

        """

        if self.datatype is None:

            if not self.is_valid():
                # this is a workaround to prevent side effects
                # since retrieve currently changes the object

                if server_retrieval:
                    tmp_prop = deepcopy(self)
                    """
                    remove role to avoid unnessecary ValueError while
                    retrieving the Entity.
                    """
                    tmp_prop.role = None
                    tmp_prop.retrieve()

                    return tmp_prop.is_reference()
                else:
                    return None
            else:
                # a valid property without datatype has to be an RT

                return True
        else:
            return is_reference(self.datatype)


class Message(object):

    def __init__(
        self,
        type: Optional[str] = None,
        code: Optional[int] = None,
        description: Optional[str] = None,
        body: Union[str, etree._Attrib, None] = None,
    ):  # @ReservedAssignment
        self.description = description
        self.type = type if type is not None else "Info"
        self.code = int(code) if code is not None else None
        self.body = body

    def to_xml(self, xml: Optional[etree._Element] = None) -> etree._Element:
        if xml is None:
            xml = etree.Element(str(self.type))

        if self.code is not None:
            xml.set("code", str(self.code))

        if self.description:
            xml.set("description", str(self.description))

        if self.body:
            xml.text = str(self.body)

        return xml

    def __repr__(self):
        return xml2str(self.to_xml())

    def __eq__(self, obj):
        if isinstance(obj, Message):
            return (self.type == obj.type and self.code == obj.code
                    and self.description == obj.description)

        return False

    def get_code(self) -> Optional[int]:
        warn(("get_code is deprecated and will be removed in future. "
              "Use self.code instead."), DeprecationWarning)
        return int(self.code) if self.code is not None else None


class RecordType(Entity):

    """This class represents LinkAhead's RecordType entities."""

    def add_property(self, property=None, value=None, id=None, name=None, description=None,
                     datatype=None,
                     unit=None, importance=RECOMMENDED, inheritance=FIX):  # @ReservedAssignment
        """See ``Entity.add_property``."""

        return super().add_property(
            property=property, id=id, name=name, description=description, datatype=datatype,
            value=value, unit=unit, importance=importance, inheritance=inheritance)

    def add_parent(
        self,
        parent: Union[Entity, int, str, None] = None,
        id: Optional[int] = None,
        name: Optional[str] = None,
        inheritance: INHERITANCE = "OBLIGATORY",
    ):
        """Add a parent to this RecordType

        Parameters
        ----------
        parent : Entity or int or str or None, optional
            The parent entity, either specified by the Entity object
            itself, or its id or its name. Default is None.
        Parameters
        ----------
        parent : Entity or int or str or None
            The parent entity, either specified by the Entity object
            itself, or its id or its name. Default is None.
        id : int
            Integer id of the parent entity. Ignored if `parent`
            is not None.
        name : str
            Name of the parent entity. Ignored if `parent is not
            none`.
        inheritance : INHERITANCE, default OBLIGATORY
            One of ``obligatory``, ``recommended``, ``suggested``, or ``all``. Specifies the
            minimum importance which parent properties need to have to be inherited by this
            entity. If no `inheritance` is given, no properties will be inherited by the child.
            This parameter is case-insensitive.

        See Also
        --------
        Entity.add_parent

        """

        return super().add_parent(parent=parent, id=id, name=name, inheritance=inheritance)

    def __init__(
        self,
        name: Optional[str] = None,
        id: Optional[int] = None,
        description: Optional[str] = None,
        datatype: Optional[DATATYPE] = None,
    ):  # @ReservedAssignment
        Entity.__init__(self, name=name, id=id, description=description,
                        datatype=datatype, role="RecordType")

    def to_xml(
        self,
        xml: Optional[etree._Element] = None,
        add_properties: INHERITANCE = "ALL",
        local_serialization: bool = False,
        visited_entities: Optional[Union[list, None]] = None,
    ) -> etree._Element:
        if xml is None:
            xml = etree.Element("RecordType")

        if visited_entities is None:
            visited_entities = []

        return Entity.to_xml(
            self,
            xml=xml,
            add_properties=add_properties,
            local_serialization=local_serialization,
            visited_entities=visited_entities,
        )


class Record(Entity):

    """This class represents LinkAhead's Record entities."""

    def add_property(self, property=None, value=None, id=None, name=None, description=None,
                     datatype=None,
                     unit=None, importance=FIX, inheritance=FIX):  # @ReservedAssignment
        """See ``Entity.add_property``."""

        return super().add_property(
            property=property, id=id, name=name, description=description, datatype=datatype,
            value=value, unit=unit, importance=importance, inheritance=inheritance)

    def __init__(
        self,
        name: Optional[str] = None,
        id: Optional[int] = None,
        description: Optional[str] = None,
    ):  # @ReservedAssignment
        Entity.__init__(self, name=name, id=id, description=description,
                        role="Record")

    def to_xml(
        self,
        xml: Optional[etree._Element] = None,
        add_properties: INHERITANCE = "ALL",
        local_serialization: bool = False,
        visited_entities: Optional[Union[list, None]] = None,
    ):
        if xml is None:
            xml = etree.Element("Record")

        if visited_entities is None:
            visited_entities = []

        return super().to_xml(
            xml=xml,
            add_properties=add_properties,
            local_serialization=local_serialization,
            visited_entities=visited_entities
        )


class File(Record):

    """This class represents LinkAhead's file entities.

    For inserting a new file to the server, `path` gives the new location, and
    `file` specifies the source of the file.

    Symlinking from the "extroot" file system is not supported by this API yet,
    it can be done manually using the `InsertFilesInDir` flag.  For sample code,
    look at `test_files.py` in the Python integration tests of the
    `load_files.py` script in the advanced user tools.

    @param name
        A name for this file *Record* (That's an entity name - not to be confused with the last
        segment of the files path).
    @param id
        An ID.
    @param description
        A description for this file record.
    @param path
        The complete path, including the file name, of the file in the server's "caosroot" file
        system.
    @param file
        A local path or python file object.  The file designated by this argument will be uploaded
        to the server via HTTP.
    @param thumbnail
        (Local) filename to a thumbnail for this file.
    @param properties
        A list of properties for this file record. @todo is this implemented?
    """

    def __init__(
        self,
        name: Optional[str] = None,
        id: Optional[int] = None,
        description: Optional[str] = None,  # @ReservedAssignment
        path: Optional[str] = None,
        file: Union[str, TextIO, None] = None,
        thumbnail: Optional[str] = None,
    ):
        Record.__init__(self, id=id, name=name, description=description)
        self.role = "File"
        self.datatype = None

        # location in the fileserver
        self.path = path

        # local file path or pointer to local file
        self.file = file
        self.thumbnail = thumbnail

    def to_xml(
        self,
        xml: Optional[etree._Element] = None,
        add_properties: INHERITANCE = "ALL",
        local_serialization: bool = False,
        visited_entities: Optional[Union[list, None]] = None,
    ) -> etree._Element:
        """Convert this file to an xml element.

        @return: xml element
        """

        if xml is None:
            xml = etree.Element("File")

        if visited_entities is None:
            visited_entities = []

        return Entity.to_xml(self, xml=xml, add_properties=add_properties,
                             local_serialization=local_serialization,
                             visited_entities=visited_entities)

    def download(self, target: Optional[str] = None) -> str:
        """Download this file-entity's actual file from the file server. It
        will be stored to the target or will be hold as a temporary file.

        @param target: Where to store this file.
        @return: local path of the downloaded file.
        """
        self.clear_server_messages()

        if target:
            file_: Union[BufferedWriter,
                         _TemporaryFileWrapper] = open(target, "wb")
        else:
            file_ = NamedTemporaryFile(mode='wb', delete=False)
        checksum = File.download_from_path(file_, self.path)

        if self._checksum is not None and self._checksum.lower() != checksum.hexdigest().lower():
            raise ConsistencyError(
                "The downloaded file had an invalid checksum. Maybe the download did not finish?")

        return file_.name

    @staticmethod
    def download_from_path(
        target_file: Union[BufferedWriter, _TemporaryFileWrapper], path: str
    ):

        _log_request("GET (download): " + path)
        response = get_connection().download_file(path)

        data = response.read(8000)
        checksum = sha512()

        while data:
            target_file.write(data)
            checksum.update(data)
            data = response.read(8000)
        target_file.close()

        return checksum

    @staticmethod
    def _get_checksum(files):
        import locale

        if hasattr(files, "name"):
            return File._get_checksum_single_file(files.name)
        else:
            if isdir(files):
                checksumappend = ""

                for child in sorted(listdir(files),
                                    key=cmp_to_key(locale.strcoll)):

                    if isdir(files + '/' + child):
                        checksumappend += child
                    checksumappend += File._get_checksum(files + "/" + child)
                checksum = sha512()
                checksum.update(checksumappend.encode('utf-8'))

                return checksum.hexdigest()
            else:
                return File._get_checksum_single_file(files)

    @staticmethod
    def _get_checksum_single_file(single_file:  Union[str, bytes, PathLike[str], PathLike[bytes]]):
        _file = open(single_file, 'rb')
        data = _file.read(1000)
        checksum = sha512()

        while data:
            checksum.update(data)
            data = _file.read(1000)
        _file.close()

        return checksum.hexdigest()

    def add_property(self, property=None, id=None, name=None, description=None, datatype=None,
                     value=None, unit=None, importance=FIX, inheritance=FIX):  # @ReservedAssignment
        """See ``Entity.add_property``."""

        return super().add_property(
            property=property, id=id, name=name, description=description, datatype=datatype,
            value=value, unit=unit, importance=importance, inheritance=inheritance)


class PropertyList(list):
    """A list class for Property objects

    This class provides addional functionality like get/set_importance or get_by_name.
    """

    def __init__(self) -> None:
        super().__init__()
        self._importance: dict[Entity, IMPORTANCE] = dict()
        self._inheritance: dict[Entity, INHERITANCE] = dict()
        self._element_by_name: dict[str, Entity] = dict()
        self._element_by_id: dict[str, Entity] = dict()

    def get_importance(
        self, property: Union[Property, Entity, str, None]
    ):  # @ReservedAssignment
        if property is not None:
            if isinstance(property, str):
                property = self.get_by_name(property)  # @ReservedAssignment

            return self._importance.get(property)

    # @ReservedAssignment
    def set_importance(self, property: Optional[Property], importance: IMPORTANCE):
        if property is not None:
            self._importance[property] = importance

    def get_by_name(self, name: str) -> Entity:
        """Get a property of this list via it's name. Raises a LinkAheadException
        if not exactly one property has this name.

        @param name: the name of the property to be returned.
        @return: A property
        """

        return self._element_by_name[name]

    def extend(self, parents):
        self.append(parents)

        return self

    def append(
        self,
        property: Union[list[Entity], Entity, Property],
        importance: Optional[IMPORTANCE] = None,
        inheritance: Optional[INHERITANCE] = None,
    ):  # @ReservedAssignment
        if isinstance(property, list):
            for p in property:
                self.append(p, importance, inheritance)

            return

        if isinstance(property, Entity):
            if importance is not None:
                self._importance[property] = importance

            if inheritance is not None:
                self._inheritance[property] = inheritance
            else:
                self._inheritance[property] = "FIX"

            if property.id is not None:
                self._element_by_id[str(property.id)] = property

            if property.name is not None:
                self._element_by_name[property.name] = property
            list.append(self, property)
        else:
            raise TypeError("Argument was not an entity")

        return self

    def to_xml(self, add_to_element: etree._Element, add_properties: INHERITANCE,
               visited_entities: Optional[Union[list, None]] = None):

        if visited_entities is None:
            visited_entities = []

        p: Property
        for p in self:
            importance = self._importance.get(p)

            if add_properties == FIX and not importance == FIX:
                continue
            pelem = p.to_xml(xml=etree.Element("Property"), add_properties=FIX,
                             visited_entities=visited_entities.copy())

            if p in self._importance:
                pelem.set("importance", str(importance))

            if p in self._inheritance:
                pelem.set("flag", "inheritance:" +
                          str(self._inheritance.get(p)))
            add_to_element.append(pelem)

        return self

    def __repr__(self):
        xml = etree.Element("PropertyList")
        self.to_xml(xml, add_properties=FIX)

        return xml2str(xml)

    def filter(self, *args, **kwargs):
        warnings.warn(DeprecationWarning("This function was renamed to filter_by_identity."))
        return self.filter_by_identity(*args, **kwargs)

    def filter_by_identity(self, prop: Optional[Property] = None,
                           pid: Union[None, str, int] = None,
                           name: Optional[str] = None,
                           conjunction: bool = False) -> list:
        """
        Return all Properties from the given PropertyList that match the
        selection criteria.

        Please refer to the documentation of _filter_entity_list_by_identity for a detailed
        description of behaviour.

        Params
        ------
        prop              : Property
                            Property to match name and ID with. Cannot be set
                            simultaneously with ID or name.
        pid               : str, int
                            Property ID to match
        name              : str
                            Property name to match
        conjunction       : bool, defaults to False
                            Set to return only entities that match both id and name
                            if both are given.

        Returns
        -------
        matches          : list
                           List containing all matching Properties
        """
        return _filter_entity_list_by_identity(self, pid=pid, name=name, entity=prop,
                                               conjunction=conjunction)

    def _get_entity_by_cuid(self, cuid: str):
        '''
        Get the first entity which has the given cuid.
        Note: this method is intended for internal use.
        @param name: The cuid of the entity to be returned.
        @return: Entity with the given cuid.
        '''

        for e in self:
            if e._cuid is not None:
                if str(e._cuid) == str(cuid):
                    return e
        raise KeyError("No entity with that cuid in this container.")

    def remove(self, prop: Union[Entity, int]):
        if isinstance(prop, Entity):
            if prop in self:
                list.remove(self, prop)

                return
            else:
                if prop.id is not None:
                    # by id

                    for e in self:
                        if e.id is not None and e.id == prop.id:
                            list.remove(self, e)

                            return

                if prop.name is not None:
                    # by name

                    for e in self:
                        if e.name is not None and e.name == prop.name:
                            list.remove(self, e)

                            return
        elif hasattr(prop, "encode"):
            # by name

            for e in self:
                if e.name is not None and str(e.name) == str(prop):
                    list.remove(self, e)

                    return
        elif isinstance(prop, int):
            # by id

            for e in self:
                if e.id is not None and e.id == prop:
                    list.remove(self, e)

                    return
        raise KeyError(str(prop) + " not found.")


class ParentList(list):
    def _get_entity_by_cuid(self, cuid):
        '''
        Get the first entity which has the given cuid.
        Note: this method is intended for internal use.
        @param name: The cuid of the entity to be returned.
        @return: Entity with the given cuid.
        '''

        for e in self:
            if e._cuid is not None:
                if str(e._cuid) == str(cuid):
                    return e
        raise KeyError("No entity with that cuid in this container.")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._element_by_name = dict()
        self._element_by_id = dict()

    def extend(self, parents):
        self.append(parents)

        return self

    def append(self, parent):  # @ReservedAssignment
        if isinstance(parent, list):
            for p in parent:
                self.append(p)
            return

        if isinstance(parent, Entity):
            list.append(self, parent)
        else:
            raise TypeError("Argument was not an Entity")

        return self

    def to_xml(self, add_to_element: etree._Element,
               visited_entities: Optional[Union[list, None]] = None):

        if visited_entities is None:
            visited_entities = []

        for p in self:
            pelem = etree.Element("Parent")

            if p.id is not None:
                pelem.set("id", str(p.id))

            if p._cuid is not None:
                pelem.set("cuid", str(p._cuid))

            if p.name is not None:
                pelem.set("name", str(p.name))

            if p.description is not None:
                pelem.set("description", str(p.description))

            if len(p._flags) > 0:
                flagattr = ""

                for key in p._flags.keys():
                    flag = p._flags[key]

                    if flag is not None and flag != "":
                        flagattr += str(key) + ":" + str(flag) + ","
                    else:
                        flagattr += str(key) + ","
                pelem.set("flag", flagattr)
            add_to_element.append(pelem)

    def __repr__(self):
        xml = etree.Element("ParentList")
        self.to_xml(xml)

        return xml2str(xml)

    def filter(self, *args, **kwargs):
        warnings.warn(DeprecationWarning("This function was renamed to filter_by_identity."))
        return self.filter_by_identity(*args, **kwargs)

    def filter_by_identity(self, parent: Optional[Parent] = None,
                           pid: Union[None, str, int] = None,
                           name: Optional[str] = None,
                           conjunction: bool = False) -> list:
        """
        Return all Parents from the given ParentList that match the selection
        criteria.

        Please refer to the documentation of _filter_entity_list_by_identity for a detailed
        description of behaviour.

        Params
        ------
        listobject        : Iterable(Parent)
                            List to be filtered
        parent            : Parent
                            Parent to match name and ID with. Cannot be set
        pid               : str, int
                            Parent ID to match
        name              : str
                            Parent name to match
                            simultaneously with ID or name.
        conjunction       : bool, defaults to False
                            Set to return only entities that match both id and name
                            if both are given.

        Returns
        -------
        matches          : list
                           List containing all matching Parents
        """
        return _filter_entity_list_by_identity(self, pid=pid, name=name, entity=parent,
                                               conjunction=conjunction)

    def remove(self, parent: Union[Entity, int, str]):
        """
        Remove first occurrence of parent.

        Parameters
        ----------
        parent: Union[Entity, int, str], the parent to be removed identified via ID or name. If a
        Parent object is provided the ID and then the name is used to identify the parent to be
        removed.

        Returns
        -------
        None
        """

        if isinstance(parent, Entity):
            if parent in self:
                list.remove(self, parent)
            else:
                if parent.id is not None:
                    # by id

                    for e in self:
                        if e.id is not None and e.id == parent.id:
                            list.remove(self, e)

                            return

                if parent.name is not None:
                    # by name

                    for e in self:
                        if e.name is not None and str(e.name).lower() == str(parent.name).lower():
                            list.remove(self, e)

                            return
        elif isinstance(parent, str):
            # by name

            for e in self:
                if e.name is not None and e.name == parent:
                    list.remove(self, e)

                    return
        elif isinstance(parent, int):
            # by id

            for e in self:
                if e.id is not None and e.id == parent:
                    list.remove(self, e)

                    return
        raise KeyError(str(parent) + " not found.")


class _Properties(PropertyList):
    def __init__(self, *args, **kwargs):
        warnings.warn(DeprecationWarning("This class is deprecated. Please use PropertyList."))
        super().__init__(*args, **kwargs)


class _ParentList(ParentList):
    def __init__(self, *args, **kwargs):
        warnings.warn(DeprecationWarning("This class is deprecated. Please use ParentList "
                                         "(without underscore)."))
        super().__init__(*args, **kwargs)


class Messages(list):
    """This specialization of list stores error, warning, info, and other
    messages. The mentioned three messages types play a special role.
    They are generated by the client and the server while processing the entity
    to which the message in question belongs. It is RECOMMENDED NOT to specify
    such messages manually. The other messages are ignored by the server unless
    there is a plug-in which interprets them.

    Any message MUST have a type. It MAY have a code (an integer), a description (short string),
    or a body (longer string):

    <$Type code=$code description=$description>$body</$Type>

    Error, warning, and info messages will be deleted before any transaction.

    Examples:
    <<< msgs = Messages()

    <<< # create Message
    <<< msg = Message(type="HelloWorld", code=1, description="Greeting the world",
    ...               body="Hello, world!")

    <<< # append it to the Messages
    <<< msgs.append(msg)

    <<< # use Messages as list of Message objects
    <<< for m in msgs:
    ...     assert isinstance(m,Message)

    <<< # remove it
    <<< msgs.remove(msg)

    <<< # ok append it again ...
    <<< msgs.append(msg)
    <<< # get it back via get(...) and the key tuple (type, code)
    <<< assert id(msgs.get("HelloWorld",1))==id(msg)
    """

    def clear_server_messages(self):
        """Removes all messages of type error, warning and info. All other
        messages types are custom types which should be handled by custom
        code."""
        rem = []

        for m in self:
            if m.type.lower() in ["error", "warning", "info"]:
                rem.append(m)

        for m in rem:
            self.remove(m)

    #######################################################################
    # can be removed after 01.07.24
    # default implementation of list is sufficient
    def __setitem__(self, key, value):  # @ReservedAssignment
        if not isinstance(value, Message):
            warn("__setitem__ will in future only accept Message objects as second argument. "
                 "You will no longe be"
                 " able to pass bodys such that Message object is created on the fly",
                 DeprecationWarning)
        if not isinstance(key, int):
            warn("__setitem__ will in future only accept int as first argument",
                 DeprecationWarning)
        if isinstance(key, tuple):
            if len(key) == 2:
                type = key[0]  # @ReservedAssignment
                code = key[1]
            elif len(key) == 1:
                type = key[0]  # @ReservedAssignment
                code = None
            else:
                raise TypeError(
                    "('type', 'code'), ('type'), or 'type' expected.")
        elif isinstance(key, Messages._msg_key):
            type = key._type  # @ReservedAssignment
            code = key._code
        else:
            type = key  # @ReservedAssignment
            code = None

        if isinstance(value, tuple):
            if len(value) == 2:
                description = value[0]
                body = value[1]
            elif len(value) == 1:
                body = value[0]
                description = None
            else:
                raise TypeError(
                    "('description', 'body'), ('body'), or 'body' expected.")

        if isinstance(value, Message):
            body = value.body
            description = value.description
            m = Message()
        else:
            body = value
            description = None
            m = Message(type=type, code=code,
                        description=description, body=body)
        if isinstance(key, int):
            super().__setitem__(key, m)
        else:
            self.append(m)

    def __getitem__(self, key):
        if not isinstance(key, int):
            warn("__getitem__ only supports integer keys in future.",
                 DeprecationWarning)
        if isinstance(key, tuple):
            if len(key) == 2:
                type = key[0]  # @ReservedAssignment
                code = key[1]
            elif len(key) == 1:
                type = key[0]  # @ReservedAssignment
                code = None
            else:
                raise TypeError(
                    "('type', 'code'), ('type'), or 'type' expected.")
        elif isinstance(key, int) and key >= 0:
            return super().__getitem__(key)
        else:
            type = key  # @ReservedAssignment
            code = None
        m = self.get(type, code)
        if m is None:
            raise KeyError()
        if m.description:
            return (m.description, m.body)
        else:
            return m.body

    def __delitem__(self, key):
        if isinstance(key, tuple):
            warn("__delitem__ only supports integer keys in future.",
                 DeprecationWarning)
            if self.get(key[0], key[1]) is not None:
                self.remove(self.get(key[0], key[1]))
        else:
            super().__delitem__(key)

    def remove(self, obj, obj2=None):
        if obj2 is not None:
            warn("Supplying a second argument to remove is deprecated.",
                 DeprecationWarning)
            super().remove(self.get(obj, obj2))
        else:
            super().remove(obj)

    def append(self, msg):
        if isinstance(msg, Messages) or isinstance(msg, list):
            warn("Supplying a list-like object to append is deprecated. Please use extend"
                 " instead.", DeprecationWarning)
            for m in msg:
                self.append(m)
            return

        super().append(msg)

    @staticmethod
    def _hash(t, c):
        return hash(str(t).lower() + (str(",") + str(c) if c is not None else ''))
    # end remove
    #######################################################################

    def get(self, type, code=None, default=None, exact=False):  # @ReservedAssignment
        """
        returns a message from the list that kind of matches type and code

        case and types (str/int) are ignored

        If no suitable message is found, the default argument is returned
        If exact=True, the message has to match code and type exactly
        """
        if not exact:
            warn("The fuzzy mode (exact=False) is deprecated. Please use exact in future.",
                 DeprecationWarning)

        for msg in self:
            if exact:
                if msg.type == type and msg.code == code:
                    return msg
            else:
                if self._hash(msg.type, msg.code) == self._hash(type, code):
                    return msg

        return default

    def to_xml(self, add_to_element: etree._Element):
        for m in self:
            melem = m.to_xml()
            add_to_element.append(melem)

    def __repr__(self):
        xml = etree.Element("Messages")
        self.to_xml(xml)

        return xml2str(xml)

    #######################################################################
    # can be removed after 01.07.24
    class _msg_key:

        def __init__(self, type, code):  # @ReservedAssignment
            warn("This class is deprecated.", DeprecationWarning)
            self._type = type
            self._code = code

        @staticmethod
        def get(msg):
            return Messages._msg_key(msg.type, msg.code)

        def __eq__(self, obj):
            return self.__hash__() == obj.__hash__()

        def __hash__(self):
            return hash(str(self._type).lower() + (str(",") + str(self._code)
                                                   if self._code is not None else ''))

        def __repr__(self):
            return str(self._type) + (str(",") + str(self._code)
                                      if self._code is not None else '')
    # end remove
    #######################################################################


class _Messages(Messages):
    def __init__(self, *args, **kwargs):
        warn("_Messages is deprecated. "
             "Use class Messages instead and beware of the slightly different API of the new"
             " Messages class", DeprecationWarning)
        super().__init__(*args, **kwargs)


def _basic_sync(e_local, e_remote):
    '''Copy all state from a one entity to another.

    This method is used to syncronize an entity with a remote (i.e. a newly
    retrieved) one.

    Any entity state of the local one will be overriden.

    Parameters
    ----------
    e_local : Entity
        Destination of the copy.
    e_local : Entity
        Source of the copy.


    Returns
    -------
    e_local : Entity
        The syncronized entity.
        '''
    if e_local is None or e_remote is None:
        return None
    if e_local.role is None:
        e_local.role = e_remote.role
    elif e_remote.role is not None and not e_local.role.lower() == e_remote.role.lower():
        raise ValueError(f"The resulting entity had a different role ({e_remote.role}) "
                         f"than the local one ({e_local.role}). This probably means, that "
                         "the entity was intialized with a wrong class "
                         "by this client or it has changed in the past and "
                         "this client did't know about it yet.\nThis is the local version of the"
                         f" Entity:\n{e_local}\nThis is the remote one:\n{e_remote}")

    e_local.id = e_remote.id
    e_local.name = e_remote.name
    e_local.description = e_remote.description
    e_local.path = e_remote.path
    e_local._checksum = e_remote._checksum
    e_local._size = e_remote._size
    e_local.datatype = e_remote.datatype
    e_local.unit = e_remote.unit
    e_local.value = e_remote.value
    e_local.properties = e_remote.properties
    e_local.parents = e_remote.parents
    e_local.messages = e_remote.messages
    e_local.acl = e_remote.acl
    e_local.permissions = e_remote.permissions
    e_local.is_valid = e_remote.is_valid
    e_local.is_deleted = e_remote.is_deleted
    e_local.version = e_remote.version
    e_local.state = e_remote.state

    if hasattr(e_remote, "query"):
        e_local.query = e_remote.query

    if hasattr(e_remote, "affiliation"):
        e_local.affiliation = e_remote.affiliation

    return e_local


def _deletion_sync(e_local, e_remote):
    if e_local is None or e_remote is None:
        return

    try:
        e_remote.get_messages()["info", 10]  # try and get the deletion info
    except KeyError:
        # deletion info wasn't there
        e_local.messages = e_remote.messages

        return

    _basic_sync(e_local, e_remote)
    e_local.is_valid = lambda: False
    e_local.is_deleted = lambda: True
    e_local.id = None


class Container(list):
    """Container is a type safe list for Entities.

    It also provides several short-cuts for transactions like retrieval,
    insertion, update, and deletion which are a applied to all entities
    in the container or the whole container respectively.
    """

    _debug = staticmethod(
        lambda: (
            get_config().getint(
                "Container",
                "debug") if get_config().has_section("Container") and
            get_config().get(
                "Container",
                "debug") is not None else 0))

    def is_valid(self):
        for e in self:
            if not e.is_valid():
                return False

        return True

    def __hash__(self):
        return object.__hash__(self)

    def remove(self, entity: Entity):
        """Remove the first entity from this container which is equal to the
        given entity. Raise a ValueError if there is no such entity.

        Alternatively, if the argument is not an entity but an ID, the
        contained entity with this ID is removed.

        @param entity: The entity to be removed.
        """

        if entity in self:
            super().remove(entity)
        else:
            for ee in self:
                if entity == ee.id:
                    super().remove(ee)

                    return ee
            raise ValueError(
                "Container.remove(entity): entity not in Container")

        return entity

    def _get_entity_by_cuid(self, cuid):
        '''
        Get the first entity which has the given cuid.
        Note: this method is intended for internal use.
        @param name: The cuid of the entity to be returned.
        @return: Entity with the given cuid.
        '''

        for e in self:
            if e._cuid is not None:
                if str(e._cuid) == str(cuid):
                    return e
        raise KeyError("No entity with such cuid (" + str(cuid) + ")!")

    # @ReservedAssignment
    def get_entity_by_id(self, id: Union[int, str]) -> Entity:
        """Get the first entity which has the given id. Note: If several
        entities are in this list which have the same id, this method will only
        return the first and ignore the others.

        @param name: The id of the entity to be returned.
        @return: Entity with the given id.
        """

        for e in self:
            if e.id:
                if e.id == int(id):
                    return e
        raise KeyError("No entity with such id (" + str(id) + ")!")

    def get_all_errors(self):
        """Returns a dictionary with all errors from all entities in this
        container.

        The dictionary keys are the ids of those entities having
        contained an error.
        """
        error_list = dict()

        for e in self:
            if isinstance(e, Entity):
                el = e.get_errors_deep()

                if len(el) > 0:
                    error_list[str(e.id)] = el

        return error_list

    def get_entity_by_name(self, name: str, case_sensitive: bool = True) -> Entity:
        """Get the first entity which has the given name. Note: If several
        entities are in this list which have the same name, this method will
        only return the first and ignore the others.

        @param name: the name of the entity to be returned.
        @param case_sensitive (True/False): Do a case-sensitive search for name (or not).
        @return: Entity with the given name.
        """

        for e in self:
            if e.name is not None:
                if case_sensitive and e.name == str(name):
                    return e
                elif not case_sensitive and e.name.lower() == str(name).lower():
                    return e
        raise KeyError("No entity with such name (" + str(name) + ")!")

    def __init__(self):
        """Container is a list of entities which can be
        inserted/updated/deleted/retrieved at once."""
        list.__init__(self)
        self._timestamp = None
        self._srid = None
        self.messages = Messages()

    def extend(self, entities):
        """Extend this Container by appending all single entities in the given
        list of entities.

        @param entities: list of entities.
        """

        if isinstance(entities, Container):
            for entity in entities:
                self.append(entity)
        elif isinstance(entities, (list, set)):
            for entity in entities:
                self.extend(entity)
        elif isinstance(entities, Entity):
            self.append(entities)
        elif isinstance(entities, int):
            self.append(entities)
        elif hasattr(entities, "encode"):
            self.append(entities)
        else:
            raise TypeError(
                "Expected a list or a container (was " + str(type(entities)) + ").")

        return self

    def append(self, entity):
        """Append an entity container.

        If the parameter is an integer an entity with the corresponding ID is appended.
        If the parameter is a string an entity with the corresponding name is appended.
        Raise a TypeError if the entity is not a sub type of the correct class (as defined
        via the constructor).

        @param entity: The entity to be appended.
        """

        if isinstance(entity, Entity):
            super().append(entity)
        elif isinstance(entity, int):
            super().append(Entity(id=entity))
        elif hasattr(entity, "encode"):
            super().append(Entity(name=entity))
        elif isinstance(entity, QueryTemplate):
            super().append(entity)
        else:
            warn("Entity was neither an id nor a name nor an entity." +
                 " (was " + str(type(entity)) + ":\n" + str(entity) + ")")
            # raise TypeError(
            #     "Entity was neither an id nor a name nor an entity." +
            #     " (was " + str(type(entity)) + "\n" + str(entity) + ")")

        return self

    def to_xml(self, add_to_element: Optional[etree._Element] = None,
               local_serialization: bool = False) -> etree._Element:
        """Get an xml tree representing this Container or append all entities
        to the given xml element.

        Parameters
        ----------
        add_to_element : etree._Element, optional
            optional element to which all entities of this container is to
            be appended. Default is None

        Returns
        -------
        xml_element : etree._Element

        Note
        ----
        Calling this method has the side effect that all entities without ID will get a negative
        integer ID.
        """
        tmpid = 0

        # users might already have specified some tmpids. -> look for smallest.

        for e in self:
            tmpid = min(tmpid, Container._get_smallest_tmpid(e))
        tmpid -= 1

        if add_to_element is None:
            add_to_element = etree.Element("Entities")
        noscript_in_supplied_xml = list(add_to_element.iter("noscript", "TransactionBenchmark"))

        for m in self.messages:
            add_to_element.append(m.to_xml())

        for e in self:
            if e.id is None:
                e.id = tmpid
                tmpid -= 1

        for e in self:
            if isinstance(e, File):
                elem = e.to_xml(local_serialization=local_serialization)
            else:
                elem = e.to_xml()
            add_to_element.append(elem)

        # remove noscript and benchmark elements added by this function
        for elem in list(add_to_element.iter("noscript", "TransactionBenchmark")):
            if elem not in noscript_in_supplied_xml:
                parent = elem.getparent()
                if parent is not None:
                    parent.remove(elem)

        return add_to_element

    def get_errors(self):
        """Get all error messages of this container.

        @return Messages: Error messages.
        """

        if self.has_errors():
            ret = Messages()

            for m in self.messages:
                if m.type.lower() == "error":
                    ret.append(m)

            return ret
        else:
            return None

    def get_warnings(self):
        """Get all warning messages of this container.

        @return Messages: Warning messages.
        """

        if self.has_warnings():
            ret = Messages()

            for m in self.messages:
                if m.type.lower() == "warning":
                    ret.append(m)

            return ret
        else:
            return None

    def get_all_messages(self):
        ret = Messages()

        for e in self:
            ret.extend(e.get_all_messages())

        return ret

    def add_message(self, m):
        self.messages.append(m)

        return self

    def has_warnings(self):
        '''
        @return True: if and only if this container has any warning messages.
        '''

        for m in self.messages:
            if m.type.lower() == "warning":
                return True

        return False

    def has_errors(self):
        '''
        @return True: if and only if this container has any error messages.
        '''

        for m in self.messages:
            if m.type.lower() == "error":
                return True

        return False

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return xml2str(self.to_xml())

    def __getitem__(self, key):
        self_as_list_slice = super().__getitem__(key)
        if isinstance(self_as_list_slice, list):
            # Construct new Container from list slice
            return Container().extend(self_as_list_slice)
        else:
            return self_as_list_slice

    @staticmethod
    def from_xml(xml_str):
        """Creates a Container from the given xml string.

        @return The created Container.
        """

        c = Container()
        xml = etree.fromstring(xml_str)

        for element in xml:
            e = _parse_single_xml_element(element)
            c.append(e)

        return c

    @staticmethod
    def _response_to_entities(http_response):
        """Parse the response of a Http-request.

        Note: Method is intended for the internal use.
        """
        body = http_response.read()
        _log_response(body)

        xml = etree.fromstring(body)

        if xml.tag.lower() == "response":
            c = Container()

            for child in xml:
                e = _parse_single_xml_element(child)

                if isinstance(e, Message):
                    c.messages.append(e)
                elif isinstance(e, Query):
                    c.query = e  # type: ignore

                    if e.messages is not None:
                        c.messages.extend(e.messages)
                elif isinstance(e, (Entity, QueryTemplate)):
                    e.is_deleted = lambda: False

                    if e.has_errors() is True:
                        e.is_valid = lambda: False
                    elif e.id is None or e.id < 0:
                        e.is_valid = lambda: False
                    else:
                        e.is_valid = lambda: True
                    c.append(e)
                else:
                    # ignore
                    pass
            c._timestamp = xml.get("timestamp")
            c._srid = xml.get("srid")

            return c
        else:
            raise LinkAheadException(
                "The server's response didn't contain the expected elements. The configuration of"
                " this client might be invalid (especially the url).")

    def _sync(
        self,
        container: Container,
        unique: bool,
        raise_exception_on_error: bool,
        name_case_sensitive: bool = False,
        strategy=_basic_sync,
    ):
        """Synchronize this container (C1) with another container (C2).

        That is: 1)  Synchronize any entity e1 in C1 with the
        corresponding entity e2 from C2 via e1._sync(c2). 2)  Add any
        leftover entity from C2 to C1.
        """
        # TODO: This method is extremely slow. E.g. 30 seconds for 1000
        # entities.

        sync_dict = self._calc_sync_dict(
            remote_container=container,
            unique=unique,
            raise_exception_on_error=raise_exception_on_error,
            name_case_sensitive=name_case_sensitive)

        # sync every entity in this container

        for entity in self:
            try:
                e_sync = sync_dict[entity]

                if e_sync is not None:
                    strategy(entity, e_sync.pop())

                    for e in e_sync:
                        self.append(e)
            except KeyError:
                pass

        # add leftover entities
        try:
            if sync_dict[self] is not None:
                for e in sync_dict[self]:
                    self.append(e)
        except KeyError:
            pass

        # messages:

        for m in container.messages:
            self.add_message(m)

        self._timestamp = container._timestamp
        self._srid = container._srid

    def _calc_sync_dict(
        self,
        remote_container: Container,
        unique: bool,
        raise_exception_on_error: bool,
        name_case_sensitive: bool,
    ):
        # self is local, remote_container is remote.

        # which is to be synced with which:
        # sync_dict[local_entity]=sync_remote_enities
        sync_dict: dict[Union[Container, Entity],
                        Optional[list[Entity]]] = dict()

        # list of remote entities which already have a local equivalent
        used_remote_entities = []

        # match by cuid

        for local_entity in self:

            sync_dict[local_entity] = None

            if local_entity._cuid is not None:
                # a list of remote entities which are equivalents of
                # local_entity
                sync_remote_entities = []

                for remote_entity in remote_container:
                    if remote_entity._cuid is not None and str(remote_entity._cuid) == str(
                            local_entity._cuid) and remote_entity not in used_remote_entities:
                        sync_remote_entities.append(remote_entity)
                        used_remote_entities.append(remote_entity)

                if len(sync_remote_entities) > 0:
                    sync_dict[local_entity] = sync_remote_entities

                if unique and len(sync_remote_entities) > 1:
                    msg = "Request was not unique. CUID " + \
                        str(local_entity._cuid) + " was found " + \
                        str(len(sync_remote_entities)) + " times."
                    local_entity.add_message(
                        Message(description=msg, type="Error"))

                    if raise_exception_on_error:
                        raise MismatchingEntitiesError(msg)

        # match by id

        for local_entity in self:
            if sync_dict[local_entity] is None and local_entity.id is not None:
                sync_remote_entities = []

                for remote_entity in remote_container:
                    if (remote_entity.id is not None
                            and remote_entity.id == local_entity.id
                            and remote_entity not in used_remote_entities):
                        sync_remote_entities.append(remote_entity)
                        used_remote_entities.append(remote_entity)

                if len(sync_remote_entities) > 0:
                    sync_dict[local_entity] = sync_remote_entities

                if unique and len(sync_remote_entities) > 1:
                    msg = "Request was not unique. ID " + \
                        str(local_entity.id) + " was found " + \
                        str(len(sync_remote_entities)) + " times."
                    local_entity.add_message(
                        Message(description=msg, type="Error"))

                    if raise_exception_on_error:
                        raise MismatchingEntitiesError(msg)

        # match by path

        for local_entity in self:
            if (sync_dict[local_entity] is None
                    and local_entity.path is not None):
                sync_remote_entities = []

                for remote_entity in remote_container:
                    if (remote_entity.path is not None
                            and str(remote_entity.path) == (
                                local_entity.path

                                if local_entity.path.startswith("/") else "/" +
                                local_entity.path)
                            and remote_entity not in used_remote_entities):
                        sync_remote_entities.append(remote_entity)
                        used_remote_entities.append(remote_entity)

                if len(sync_remote_entities) > 0:
                    sync_dict[local_entity] = sync_remote_entities

                if unique and len(sync_remote_entities) > 1:
                    msg = "Request was not unique. Path " + \
                        str(local_entity.path) + " was found " + \
                        str(len(sync_remote_entities)) + " times."
                    local_entity.add_message(
                        Message(description=msg, type="Error"))

                    if raise_exception_on_error:
                        raise MismatchingEntitiesError(msg)

        # match by name

        for local_entity in self:
            if (sync_dict[local_entity] is None
                    and local_entity.name is not None):
                sync_remote_entities = []

                for remote_entity in remote_container:
                    if (remote_entity.name is not None
                        and (str(remote_entity.name) == str(local_entity.name)
                             or
                             (name_case_sensitive is False and
                              str(remote_entity.name).lower() == str(
                                  local_entity.name).lower()))
                            and remote_entity not in used_remote_entities):
                        sync_remote_entities.append(remote_entity)
                        used_remote_entities.append(remote_entity)

                if len(sync_remote_entities) > 0:
                    sync_dict[local_entity] = sync_remote_entities

                if unique and len(sync_remote_entities) > 1:
                    msg = "Request was not unique. Name " + \
                        str(local_entity.name) + " was found " + \
                        str(len(sync_remote_entities)) + " times."
                    local_entity.add_message(
                        Message(description=msg, type="Error"))

                    if raise_exception_on_error:
                        raise MismatchingEntitiesError(msg)

        # add remaining entities to this remote_container
        sync_remote_entities = []

        for remote_entity in remote_container:
            if not (remote_entity in used_remote_entities):
                sync_remote_entities.append(remote_entity)

        if len(sync_remote_entities) > 0:
            # FIXME: How is this supposed to work?
            sync_dict[self] = sync_remote_entities

        if unique and len(sync_remote_entities) != 0:
            msg = "Request was not unique. There are " + \
                str(len(sync_remote_entities)) + \
                " entities which could not be matched to one of the requested ones."
            remote_container.add_message(
                Message(description=msg, type="Error"))

            if raise_exception_on_error:
                raise MismatchingEntitiesError(msg)

        return sync_dict

    def filter_by_identity(self, entity: Optional[Entity] = None,
                           entity_id: Union[None, str, int] = None,
                           name: Optional[str] = None,
                           conjunction: bool = False) -> list:
        """
        Return all Entities from this Container that match the selection criteria.

        Please refer to the documentation of _filter_entity_list_by_identity for a detailed
        description of behaviour.

        Params
        ------
        entity            : Entity
                            Entity to match name and ID with
        entity_id         : str, int
                            Parent ID to match
        name              : str
                            Parent name to match
                            simultaneously with ID or name.
        conjunction       : bool, defaults to False
                            Set to return only entities that match both id and name
                            if both are given.

        Returns
        -------
        matches          : list
                           List containing all matching Entities
        """
        return _filter_entity_list_by_identity(self, pid=entity_id, name=name, entity=entity,
                                               conjunction=conjunction)

    @staticmethod
    def _find_dependencies_in_container(container: Container):
        """Find elements in a container that are a dependency of another element of the same.

        Parameters
        ----------
        container : Container
          A LinkAhead container.

        Returns
        -------
        out : set
          A set of IDs of unique elements that are a dependency of another element of ``container``.
        """
        item_id = set()
        is_parent = set()
        is_property = set()
        is_being_referenced = set()
        dependent_parents = set()
        dependent_properties = set()
        dependent_references = set()
        dependencies = set()

        container_item: Entity
        for container_item in container:
            item_id.add(container_item.id)

            for parents in container_item.get_parents():
                is_parent.add(parents.id)

            prop: Property
            for prop in container_item.get_properties():
                prop_dt: Union[DATATYPE, str, None] = prop.datatype
                if prop_dt is not None and is_reference(prop_dt):
                    # add only if it is a reference, not a simple property
                    # Step 1: look for prop.value
                    if prop.value is not None:
                        if isinstance(prop.value, int):
                            is_being_referenced.add(prop.value)
                        elif is_list_datatype(prop_dt):
                            for list_item in prop.value:
                                if list_item is None:
                                    continue
                                if isinstance(list_item, int):
                                    is_being_referenced.add(list_item)
                                else:
                                    is_being_referenced.add(list_item.id)
                        else:
                            try:
                                is_being_referenced.add(prop.value.id)
                            except AttributeError:
                                pass
                    # Step 2: Reference properties
                    if prop.is_reference():
                        if is_list_datatype(prop_dt):
                            ref_name = get_list_datatype(prop_dt)
                            try:
                                is_being_referenced.add(
                                    container.get_entity_by_name(ref_name).id)  # type: ignore
                            except KeyError:
                                pass
                        elif isinstance(prop_dt, str):
                            pass
                        else:
                            is_being_referenced.add(prop_dt.id)

                if hasattr(prop, 'id'):
                    is_property.add(prop.id)
            if isinstance(container_item, Property):
                dtype = container_item.datatype
                if isinstance(dtype, Entity):
                    is_being_referenced.add(dtype.id)
                elif isinstance(dtype, str):
                    if is_list_datatype(dtype):
                        dtype = get_list_datatype(dtype)
                    try:
                        is_being_referenced.add(container.get_entity_by_name(dtype).id)
                    except KeyError:
                        pass
                else:
                    # plain old scalar datatype
                    pass

        dependent_parents = item_id.intersection(is_parent)
        dependent_properties = item_id.intersection(is_property)
        dependent_references = item_id.intersection(is_being_referenced)
        dependencies = dependent_parents.union(dependent_references)
        dependencies = dependencies.union(dependent_properties)

        return dependencies

    def delete(self, raise_exception_on_error: bool = True,
               flags: Optional[QueryDict] = None, chunk_size: int = 100):
        """Delete all entities in this container.

        Entities are identified via their id if present and via their
        name otherwise.  If any entity has no id and no name a
        TransactionError will be raised.

        Note: If only a name is given this could lead to ambiguities. If this happens, none of them
        will be deleted. An error is raised instead.

        """
        item_count = len(self)
        # Split Container in 'chunk_size'-sized containers (if necessary) to avoid error 414
        # Request-URI Too Long

        if item_count > chunk_size:
            dependencies = Container._find_dependencies_in_container(self)

            # If there are as many dependencies as entities in the container and it is larger than
            # chunk_size it cannot be split and deleted. This case cannot be handled at the moment.

            if len(dependencies) == item_count:
                if raise_exception_on_error:
                    te = TransactionError(
                        msg=("The container is too large and with too many dependencies within to"
                             " be deleted."),
                        container=self)
                    raise te

                return self

            # items which have to be deleted later because of dependencies.
            dependencies_delete = Container()

            for i in range(0, int(item_count/chunk_size)+1):
                chunk = Container()

                for j in range(i*chunk_size, min(item_count, (i+1)*chunk_size)):
                    if len(dependencies):
                        if self[j].id in dependencies:
                            dependencies_delete.append(self[j])
                        else:
                            chunk.append(self[j])
                    else:
                        chunk.append(self[j])

                if len(chunk):
                    chunk.delete()
            if len(dependencies_delete):
                dependencies_delete.delete()

            return self

        if len(self) == 0:
            if raise_exception_on_error:
                te = TransactionError(
                    msg="There are no entities to be deleted. This container is empty.",
                    container=self)
                raise te

            return self
        self.clear_server_messages()

        c = get_connection()
        id_str = []

        for entity in self:
            if entity.is_deleted():
                continue
            entity._cuid = None

            if entity.id is not None:
                id_str.append(str(entity.id))
            elif entity.name is not None:
                id_str.append(str(entity.name))
            else:
                entity.add_message(
                    Message(
                        type="Error",
                        description="This entity has no identifier. It cannot be deleted."))

                if raise_exception_on_error:
                    ee = EntityError(
                        "This entity has no identifier. It cannot be deleted.", entity)
                    raise TransactionError(ee)
                entity.is_valid = lambda: False

        if len(id_str) == 0:
            if raise_exception_on_error:
                te = TransactionError(
                    msg="There are no entities to be deleted.",
                    container=self)
                raise te

            return self
        entity_url_segments = [_ENTITY_URI_SEGMENT, "&".join(id_str)]

        _log_request("DELETE: " + str(entity_url_segments) +
                     ("?" + str(flags) if flags is not None else ''))

        http_response = c.delete(entity_url_segments, query_dict=flags)
        cresp = Container._response_to_entities(http_response)
        self._sync(cresp, raise_exception_on_error=raise_exception_on_error,
                   unique=True, strategy=_deletion_sync)

        if raise_exception_on_error:
            raise_errors(self)

        return self

    def retrieve(
        self,
        query: Union[str, list, None] = None,
        unique: bool = True,
        raise_exception_on_error: bool = True,
        sync: bool = True,
        flags: Optional[QueryDict] = None,
    ):
        """Retrieve all entities in this container identified via their id if
        present and via their name otherwise. Any locally already existing
        attributes (name, description, ...) will be preserved. Any such
        properties and parents will be synchronized as well. They will not be
        overridden. This method returns a Container containing the this entity.

        If any entity has no id and no name a LinkAheadException will be raised.

        Note: If only a name is given this could lead to ambiguities. All entities with the name in
        question will be returned. Therefore, the container could contain more elements after the
        retrieval than before.
        """

        if isinstance(query, list):
            self.extend(query)
            query = None
        cresp = Container()
        entities_str = []

        if query is None:
            for entity in self:
                if entity.id is not None and entity.id < 0:
                    entity.id = None
                entity.clear_server_messages()

                if entity.id is not None:
                    entities_str.append(str(entity.id))
                elif entity.name is not None:
                    entities_str.append(str(entity.name))
                elif entity.path is not None:
                    # fetch by path (files only)
                    cresp.extend(execute_query(
                        "FIND FILE . STORED AT \"" + str(entity.path) + "\"", unique=False))
                else:
                    entity.add_message(
                        Message(
                            type="Error",
                            description="This entity has no identifier. It cannot be retrieved."))

                    if raise_exception_on_error:
                        ee = EntityError(
                            "This entity has no identifier. It cannot be retrieved.",
                            entity)
                        raise TransactionError(ee)
                    entity.is_valid = lambda: False
        else:
            entities_str.append(str(query))

        self.clear_server_messages()
        cresp2 = self._retrieve(entities=entities_str, flags=flags)
        cresp.extend(cresp2)
        cresp.messages.extend(cresp2.messages)

        if raise_exception_on_error:
            raise_errors(cresp)

        if sync:
            self._sync(cresp, unique=unique,
                       raise_exception_on_error=raise_exception_on_error)

            return self
        else:
            return cresp

    @staticmethod
    def _split_uri_string(entities):

        # get half length of entities_str
        hl = len(entities) // 2

        # split in two uris

        return (entities[0:hl], entities[hl:len(entities)])

    def _retrieve(self, entities, flags: Optional[QueryDict]):
        c = get_connection()
        try:
            _log_request("GET: " + _ENTITY_URI_SEGMENT + str(entities) +
                         ('' if flags is None else "?" + str(flags)))
            http_response = c.retrieve(
                entity_uri_segments=[
                    _ENTITY_URI_SEGMENT, str(
                        "&".join(entities))], query_dict=flags)

            return Container._response_to_entities(http_response)
        except HTTPURITooLongError as uri_e:
            try:
                # split up
                uri1, uri2 = Container._split_uri_string(entities)
            except ValueError as val_e:
                raise uri_e from val_e
            c1 = self._retrieve(entities=uri1, flags=flags)
            c2 = self._retrieve(entities=uri2, flags=flags)
            c1.extend(c2)
            c1.messages.extend(c2.messages)

            return c1

    def clear_server_messages(self):
        self.messages.clear_server_messages()

        for entity in self:
            entity.clear_server_messages()

        return self

    @staticmethod
    # @ReservedAssignment
    def _dir_to_http_parts(root: str, d: Optional[str], upload: str):
        ret = []
        x = (root + '/' + d if d is not None else root)

        for f in listdir(x):
            if isdir(x + '/' + f):
                part = MultipartParam(
                    name=hex(randint(0, sys.maxsize)), value="")
                part.filename = upload + \
                    ('/' + d + '/' if d is not None else '/') + f + '/'
                ret.extend(Container._dir_to_http_parts(
                    root, (d + '/' + f if d is not None else f), upload))
            else:
                part = MultipartParam.from_file(
                    paramname=hex(randint(0, sys.maxsize)), filename=x + '/' + f)
                part.filename = upload + \
                    ('/' + d + '/' if d is not None else '/') + f
            ret.append(part)

        return ret

    def update(
        self,
        strict: bool = False,
        raise_exception_on_error: bool = True,
        unique: bool = True,
        sync: bool = True,
        flags: Optional[dict[str, Any]] = None,
    ):
        """Update these entites."""

        if len(self) < 1:
            te = TransactionError(
                msg="There are no entities to be updated. This container is empty.",
                container=self)
            raise te

        self.clear_server_messages()
        insert_xml = etree.Element("Update")
        http_parts: list[MultipartParam] = []

        if flags is None:
            flags = {}

        if strict is True:
            flags["strict"] = "true"

        if unique is True:
            flags["uniquename"] = "true"

        for entity in self:
            if (entity.id is None or entity.id < 0):
                ee = EntityError(
                    "You tried to update an entity without a valid id.",
                    entity)
                raise TransactionError(ee)

        self._linearize()

        for entity in self:

            # process files if present
            Container._process_file_if_present_and_add_to_http_parts(
                http_parts, entity)

        for entity in self:
            entity_xml = entity.to_xml()

            if hasattr(entity, '_upload') and entity._upload is not None:
                entity_xml.set("upload", entity._upload)

            insert_xml.append(entity_xml)

        _log_request("PUT: " + _ENTITY_URI_SEGMENT +
                     ('' if flags is None else "?" + str(flags)), insert_xml)

        con = get_connection()

        if http_parts is not None and len(http_parts) > 0:
            http_parts.insert(
                0, MultipartParam("FileRepresentation", xml2str(insert_xml)))
            body, headers = multipart_encode(http_parts)

            http_response = con.update(
                entity_uri_segment=[_ENTITY_URI_SEGMENT],
                query_dict=flags,
                body=body,
                headers=headers)
        else:
            http_response = con.update(
                entity_uri_segment=[_ENTITY_URI_SEGMENT], query_dict=flags,
                body=xml2str(insert_xml))

        cresp = Container._response_to_entities(http_response)

        if raise_exception_on_error:
            raise_errors(cresp)

        if sync:
            self._sync(cresp, unique=unique,
                       raise_exception_on_error=raise_exception_on_error)

            return self
        else:
            return cresp

    @staticmethod
    def _process_file_if_present_and_add_to_http_parts(
        http_parts: list[MultipartParam], entity: Union[File, Entity]
    ):
        if isinstance(entity, File) and hasattr(
                entity, 'file') and entity.file is not None:
            new_checksum = File._get_checksum(entity.file)

            # do not transfer unchanged files.

            if entity._checksum is not None and entity._checksum.lower() == new_checksum.lower():
                entity._upload = None

                return

            entity._size = None
            entity._checksum = new_checksum
            entity._upload = hex(randint(0, sys.maxsize))

            if hasattr(entity.file, "name"):
                _file = entity.file.name
            else:
                _file = entity.file

            if isdir(_file):
                http_parts.extend(
                    Container._dir_to_http_parts(_file, None, entity._upload))
                part = MultipartParam(
                    name=hex(randint(0, sys.maxsize)), value="")
                part.filename = entity._upload + '/'
            else:
                part = MultipartParam.from_file(
                    paramname=hex(randint(0, sys.maxsize)), filename=_file)
                part.filename = entity._upload
            http_parts.append(part)

            if entity.thumbnail is not None:
                part = MultipartParam.from_file(paramname=hex(
                    randint(0, sys.maxsize)), filename=entity.thumbnail)
                part.filename = entity._upload + ".thumbnail"
                http_parts.append(part)
        else:
            entity._checksum = None

    # FIXME: The signature of Container.insert is completely different than the superclass'
    #        list.insert method. This may be a problem in the future, but is ignored for now.
    def insert(  # type: ignore
        self,
        strict: bool = False,
        raise_exception_on_error: bool = True,
        unique: bool = True,
        sync: bool = True,
        flags: Optional[QueryDict] = None,
    ):
        """Insert this file entity into LinkAhead. A successful insertion will
        generate a new persistent ID for this entity. This entity can be
        identified, retrieved, updated, and deleted via this ID until it has
        been deleted.

        If the insertion fails, a LinkAheadException will be raised. The server will have returned
        at least one error-message describing the reason why it failed in that case (call
        <this_entity>.get_all_messages() in order to get these error-messages).

        Some insertions might cause warning-messages on the server-side, but the entities are
        inserted anyway. Set the flag 'strict' to True in order to force the server to take all
        warnings as errors.  This prevents the server from inserting this entity if any warning
        occurs.

        Parameters
        ----------
        strict : bool, optional
            Flag for strict mode. Default is False.
        sync : bool, optional
            synchronize this container with the response from the
            server. Otherwise, this method returns a new container with the
            inserted entities and leaves this container untouched. Default is
            True.
        unique : bool, optional
            Flag for unique mode. If set to True, the server will check if the
            name of the entity is unique. If not, the server will return an
            error. Default is True.
        flags : dict, optional
            Additional flags for the server. Default is None.

        """

        self.clear_server_messages()
        insert_xml = etree.Element("Insert")
        http_parts: list[MultipartParam] = []

        if flags is None:
            flags = {}

        if strict:
            flags["strict"] = "true"

        if unique:
            flags["uniquename"] = "true"

        self._linearize()

        # TODO: This is a possible solution for ticket#137
        #         retrieved = Container()
        #         for entity in self:
        #             if entity.is_valid():
        #                 retrieved.append(entity)
        #         if len(retrieved)>0:
        #             retrieved = retrieved.retrieve(raise_exception_on_error=False, sync=False)
        #             for e_remote in retrieved:
        #                 if e_remote.id is not None:
        #                     try:
        #                         self.get_entity_by_id(e_remote.id).is_valid=e_remote.is_valid
        #                         continue
        #                     except KeyError:
        #                         pass
        #                 if e_remote.name is not None:
        #                     try:
        #                         self.get_entity_by_name(e_remote.name).is_valid=e_remote.is_valid
        #                         continue
        #                     except KeyError:
        #                         pass
        for entity in self:
            if entity.is_valid():
                continue

            # process files if present
            Container._process_file_if_present_and_add_to_http_parts(
                http_parts, entity)

        for entity in self:
            if entity.is_valid():
                continue
            entity_xml = entity.to_xml()

            if hasattr(entity, '_upload') and entity._upload is not None:
                entity_xml.set("upload", entity._upload)
            insert_xml.append(entity_xml)

        if len(self) > 0 and len(insert_xml) < 1:
            te = TransactionError(
                msg=("There are no entities to be inserted. This container contains existent"
                     " entities only."),
                container=self)
            raise te
        _log_request("POST: " + _ENTITY_URI_SEGMENT +
                     ('' if flags is None else "?" + str(flags)), insert_xml)

        con = get_connection()

        if http_parts is not None and len(http_parts) > 0:
            http_parts.insert(
                0, MultipartParam("FileRepresentation", xml2str(insert_xml)))

            body, headers = multipart_encode(http_parts)
            http_response = con.insert(
                entity_uri_segment=[_ENTITY_URI_SEGMENT],
                body=body,
                headers=headers,
                query_dict=flags)
        else:
            http_response = con.insert(
                entity_uri_segment=[_ENTITY_URI_SEGMENT],
                body=xml2str(insert_xml),
                query_dict=flags)

        cresp = Container._response_to_entities(http_response)

        if sync:
            self._sync(cresp, unique=unique,
                       raise_exception_on_error=raise_exception_on_error)

            if raise_exception_on_error:
                raise_errors(self)

            return self
        else:
            if raise_exception_on_error:
                raise_errors(cresp)

            return cresp

    @staticmethod
    def _get_smallest_tmpid(entity: Entity):
        tmpid = 0

        if entity.id is not None:
            tmpid = min(tmpid, int(entity.id))

        for p in entity.get_parents():
            if p.id is not None:
                tmpid = min(tmpid, int(p.id))

        for p in entity.get_properties():
            if p.id is not None:
                tmpid = min(tmpid, Container._get_smallest_tmpid(p))

        return tmpid

    def _linearize(self):
        tmpid = 0
        ''' users might already have specified some tmpids. -> look for smallest.'''

        for e in self:
            tmpid = min(tmpid, Container._get_smallest_tmpid(e))

        tmpid -= 1

        '''a tmpid for every entity'''

        for e in self:
            if e.id is None:
                e.id = tmpid
                tmpid -= 1

            # CUID

            if e._cuid is None or e._cuid == 'None' or e._cuid == '':
                e._cuid = str(e.id) + "--" + str(uuid())

        '''dereference properties and parents'''

        for e in self:
            """properties."""

            for p in e.get_properties():
                if p.id is None:
                    if p.name is not None:
                        # TODO using try except for normal execution flow is bad style
                        try:
                            w = self.get_entity_by_name(p.name)
                            p._wrap(w)
                        except KeyError:
                            pass

            '''parents'''

            for p in e.get_parents():
                if p.id is None:
                    if p.name is not None:
                        # TODO using try except for normal execution flow is bad style
                        try:
                            p._wrap(self.get_entity_by_name(p.name))
                        except KeyError:
                            pass

        return self

    def get_property_values(
        self, *selectors: Union[str, tuple[str]]
    ) -> list[tuple[str]]:
        """ Return a list of tuples with values of the given selectors.

        I.e. a tabular representation of the container's content.

        If the elements of the selectors parameter are tuples, they will return
        the properties of the referenced entity, if present. E.g. ("window",
        "height") will return the value of the height property of the
        referenced window entity.

        All tuples of the returned list have the same length as the selectors
        parameter and the ordering of the tuple's values correspond to the
        order of the parameter as well.

        The tuple contains None for all values that are not available in the
        entity. That does not necessarily mean, that the values are not stored
        in the database (e.g. if a single entity was retrieved without
        referenced entities).

        Parameters
        ----------
        *selectors : str or tuple of str
            Each selector is a list or tuple of property names, e.g. `"height",
            "width"`.

        Returns
        -------
        table : list of tuples
            A tabular representation of the container's content.
        """
        table = []

        for e in self:
            table.append(e.get_property_values(*selectors))

        return table


def sync_global_acl():
    c = get_connection()
    http_response = c.retrieve(entity_uri_segments=["EntityPermissions"])
    body = http_response.read()
    _log_response(body)

    xml = etree.fromstring(body)

    if xml.tag.lower() == "response":
        for child in xml:
            if child.tag == "EntityPermissions":
                Permissions.known_permissions = Permissions(child)

                for pelem in child:
                    if pelem.tag == "EntityACL":
                        ACL.global_acl = ACL(xml=pelem)
    else:
        raise LinkAheadException(
            "The server's response didn't contain the expected elements. The configuration of this"
            " client might be invalid (especially the url).")


def get_known_permissions():
    if Permissions.known_permissions is None:
        sync_global_acl()

    return Permissions.known_permissions


def get_global_acl():
    if ACL.global_acl is None:
        sync_global_acl()

    return ACL.global_acl


class ACI():
    """FIXME: Add docstring"""

    def __init__(
        self,
        realm: Optional[str],
        username: Optional[str],
        role: Optional[str],
        permission: Optional[str],
    ):
        self.role = role
        self.username = username
        self.realm = realm
        self.permission = permission

    def __hash__(self):
        return hash(self.__repr__())

    def __eq__(self, other):
        return (isinstance(other, ACI) and
                (self.role is None and self.username == other.username
                 and self.realm == other.realm)
                or self.role == other.role and self.permission == other.permission)

    def __repr__(self):
        return ":".join([str(self.realm), str(self.username), str(self.role), str(self.permission)])

    def add_to_element(self, e: etree._Element):
        if self.role is not None:
            e.set("role", self.role)
        else:
            if self.username is None:
                raise LinkAheadException("An ACI must have either a role or a username.")
            e.set("username", self.username)

            if self.realm is not None:
                e.set("realm", self.realm)
        p = etree.Element("Permission")
        if self.permission is None:
            raise LinkAheadException("An ACI must have a permission.")
        p.set("name", self.permission)
        e.append(p)


class ACL():
    """FIXME: Add docstring"""

    global_acl: Optional[ACL] = None

    def __init__(self, xml: Optional[etree._Element] = None):
        if xml is not None:
            self.parse_xml(xml)
        else:
            self.clear()

    def parse_xml(self, xml: etree._Element):
        """Clear this ACL and parse the xml.

        Iterate over the rules in the xml and add each rule to this ACL.

        Contradicting rules will both be kept.

        Parameters
        ----------
        xml : lxml.etree._Element
            The xml element containing the ACL rules, i.e. <Grant> and <Deny>
            rules.
        """
        self.clear()
        self._parse_xml(xml)

    def _parse_xml(self, xml: etree._Element):
        """Parse the xml.

        Iterate over the rules in the xml and add each rule to this ACL.

        Contradicting rules will both be kept.

        Parameters
        ----------
        xml : lxml.etree._Element
            The xml element containing the ACL rules, i.e. <Grant> and <Deny>
            rules.
        """
        # @review Florian Spreckelsen 2022-03-17
        for e in xml:
            role = e.get("role")
            username = e.get("username")
            realm = e.get("realm")
            priority = self._get_boolean_priority(e.get("priority"))

            for p in e:
                if p.tag == "Permission":
                    permission = p.get("name")

                    if e.tag == "Grant":
                        self.grant(username=username, realm=realm, role=role,
                                   permission=permission, priority=priority,
                                   revoke_denial=False)
                    elif e.tag == "Deny":
                        self.deny(username=username, realm=realm, role=role,
                                  permission=permission, priority=priority,
                                  revoke_grant=False)

    def combine(self, other: ACL) -> ACL:
        """ Combine and return new instance."""
        result = ACL()
        result._grants.update(other._grants)
        result._grants.update(self._grants)
        result._denials.update(other._denials)
        result._denials.update(self._denials)
        result._priority_grants.update(other._priority_grants)
        result._priority_grants.update(self._priority_grants)
        result._priority_denials.update(other._priority_denials)
        result._priority_denials.update(self._priority_denials)

        return result

    def __eq__(self, other):
        return (isinstance(other, ACL)
                and other._grants == self._grants
                and self._denials == other._denials
                and self._priority_grants == other._priority_grants
                and self._priority_denials == other._priority_denials)

    def is_empty(self):
        return len(self._grants) + len(self._priority_grants) + \
            len(self._priority_denials) + len(self._denials) == 0

    def clear(self) -> None:
        self._grants: set[ACI] = set()
        self._denials: set[ACI] = set()
        self._priority_grants: set[ACI] = set()
        self._priority_denials: set[ACI] = set()

    def _get_boolean_priority(self, priority: Any):
        return str(priority).lower() in ["true", "1", "yes", "y"]

    def _remove_item(self, item, priority: bool):
        try:
            self._denials.remove(item)
        except KeyError:
            pass
        try:
            self._grants.remove(item)
        except KeyError:
            pass

        if priority:
            try:
                self._priority_denials.remove(item)
            except KeyError:
                pass
            try:
                self._priority_grants.remove(item)
            except KeyError:
                pass

    def revoke_grant(
        self,
        username: Optional[str] = None,
        realm: Optional[str] = None,
        role: Optional[str] = None,
        permission: Optional[str] = None,
        priority: Union[bool, str] = False,
    ):
        priority = self._get_boolean_priority(priority)
        item = ACI(role=role, username=username,
                   realm=realm, permission=permission)

        if priority:
            if item in self._priority_grants:
                self._priority_grants.remove(item)

        if item in self._grants:
            self._grants.remove(item)

    def revoke_denial(
        self,
        username: Optional[str] = None,
        realm: Optional[str] = None,
        role: Optional[str] = None,
        permission: Optional[str] = None,
        priority: bool = False,
    ):
        priority = self._get_boolean_priority(priority)
        item = ACI(role=role, username=username,
                   realm=realm, permission=permission)

        if priority:
            if item in self._priority_denials:
                self._priority_denials.remove(item)

        if item in self._denials:
            self._denials.remove(item)

    def grant(
        self,
        permission: Optional[str],
        username: Optional[str] = None,
        realm: Optional[str] = None,
        role: Optional[str] = None,
        priority: bool = False,
        revoke_denial: bool = True,
    ):
        """Grant a permission to a user or role.

        You must specify either only the username and the realm, or only the
        role.

        By default a previously existing denial rule would be revoked, because
        otherwise this grant wouldn't have any effect. However, for keeping
        contradicting rules pass revoke_denial=False.

        Parameters
        ----------
        permission: str
            The permission to be granted.
        username : str, optional
            The username. Exactly one is required, either the `username` or the
            `role`.
        realm: str, optional
            The user's realm. Required when username is not None.
        role: str, optional
            The role (as in Role-Based Access Control). Exactly one is
            required, either the `username` or the `role`.
        priority: bool, default False
            Whether this permission is granted with priority over non-priority
            rules.
        revoke_denial: bool, default True
            Whether a contradicting denial (with same priority flag) in this
            ACL will be revoked.
        """
        # @review Florian Spreckelsen 2022-03-17
        priority = self._get_boolean_priority(priority)
        item = ACI(role=role, username=username,
                   realm=realm, permission=permission)
        if revoke_denial:
            self._remove_item(item, priority)

        if priority is True:
            self._priority_grants.add(item)
        else:
            self._grants.add(item)

    def deny(
        self,
        username: Optional[str] = None,
        realm: Optional[str] = None,
        role: Optional[str] = None,
        permission: Optional[str] = None,
        priority: bool = False,
        revoke_grant: bool = True,
    ):
        """Deny a permission to a user or role for this entity.

        You must specify either only the username and the realm, or only the
        role.

        By default a previously existing grant rule would be revoked, because
        otherwise this denial would override the grant rules anyways. However,
        for keeping contradicting rules pass revoke_grant=False.

        Parameters
        ----------
        permission: str
            The permission to be denied.
        username : str, optional
            The username. Exactly one is required, either the `username` or the
            `role`.
        realm: str, optional
            The user's realm. Required when username is not None.
        role: str, optional
            The role (as in Role-Based Access Control). Exactly one is
            required, either the `username` or the `role`.
        priority: bool, default False
            Whether this permission is denied with priority over non-priority
            rules.
        revoke_grant: bool, default True
            Whether a contradicting grant (with same priority flag) in this
            ACL will be revoked.
        """
        # @review Florian Spreckelsen 2022-03-17
        priority = self._get_boolean_priority(priority)
        item = ACI(role=role, username=username,
                   realm=realm, permission=permission)
        if revoke_grant:
            self._remove_item(item, priority)

        if priority is True:
            self._priority_denials.add(item)
        else:
            self._denials.add(item)

    def to_xml(self, xml: Optional[etree._Element] = None):
        if xml is None:
            xml = etree.Element("EntityACL")

        for aci in self._grants:
            e = etree.Element("Grant")
            e.set("priority", "False")
            aci.add_to_element(e)
            xml.append(e)

        for aci in self._denials:
            e = etree.Element("Deny")
            e.set("priority", "False")
            aci.add_to_element(e)
            xml.append(e)

        for aci in self._priority_grants:
            e = etree.Element("Grant")
            e.set("priority", "True")
            aci.add_to_element(e)
            xml.append(e)

        for aci in self._priority_denials:
            e = etree.Element("Deny")
            e.set("priority", "True")
            aci.add_to_element(e)
            xml.append(e)

        return xml

    def get_acl_for_role(self, role: str) -> ACL:
        ret = ACL()

        for aci in self._grants:
            if aci.role == role:
                ret._grants.add(aci)

        for aci in self._denials:
            if aci.role == role:
                ret._denials.add(aci)

        for aci in self._priority_grants:
            if aci.role == role:
                ret._priority_grants.add(aci)

        for aci in self._priority_denials:
            if aci.role == role:
                ret._priority_denials.add(aci)

        return ret

    def get_acl_for_user(self, username: str, realm: Optional[str] = None):
        ret = ACL()

        for aci in self._grants:
            if aci.username == username and (
                    realm is None or aci.realm == realm):
                ret._grants.add(aci)

        for aci in self._denials:
            if aci.username == username and (
                    realm is None or aci.realm == realm):
                ret._denials.add(aci)

        for aci in self._priority_grants:
            if aci.username == username and (
                    realm is None or aci.realm == realm):
                ret._priority_grants.add(aci)

        for aci in self._priority_denials:
            if aci.username == username and (
                    realm is None or aci.realm == realm):
                ret._priority_denials.add(aci)

        return ret

    def get_permissions_for_user(self, username: str, realm: Optional[str] = None):
        acl = self.get_acl_for_user(username, realm)
        _grants = set()

        for aci in acl._grants:
            _grants.add(aci.permission)
        _denials = set()

        for aci in acl._denials:
            _denials.add(aci.permission)
        _priority_grants = set()

        for aci in acl._priority_grants:
            _priority_grants.add(aci.permission)
        _priority_denials = set()

        for aci in acl._priority_denials:
            _priority_denials.add(aci.permission)

        return ((_grants - _denials) | _priority_grants) - _priority_denials

    def get_permissions_for_role(self, role: str):
        acl = self.get_acl_for_role(role)
        _grants = set()

        for aci in acl._grants:
            _grants.add(aci.permission)
        _denials = set()

        for aci in acl._denials:
            _denials.add(aci.permission)
        _priority_grants = set()

        for aci in acl._priority_grants:
            _priority_grants.add(aci.permission)
        _priority_denials = set()

        for aci in acl._priority_denials:
            _priority_denials.add(aci.permission)

        return ((_grants - _denials) | _priority_grants) - _priority_denials

    def is_permitted(self, role, permission):
        return permission in self.get_permissions_for_role(role)

    def __repr__(self):
        return xml2str(self.to_xml())


class Query():
    """Query

    Attributes
    ----------
    q : str, etree._Element
        The query string, may also be a query XML snippet.
    flags : dict of str
        A dictionary of flags to be send with the query request.
    messages : Messages()
        A container of messages included in the last query response.
    cached : bool
        indicates whether the server used the query cache for the execution of
        this query.
    results : int or Container
        The number of results (when this was a count query) or the container
        with the resulting entities.
    """

    def putFlag(self, key: str, value: Optional[str] = None):
        self.flags[key] = value

        return self

    def removeFlag(self, key):
        return self.flags.pop(key)

    def getFlag(self, key):
        return self.flags.get(key)

    def __init__(self, q: Union[str, etree._Element]):
        self.flags: QueryDict = dict()
        self.messages = Messages()
        self.cached: Optional[bool] = None
        self.etag = None

        if isinstance(q, etree._Element):
            q.get("string")
            self.q = q.get("string", "")
            results = q.get("results")
            if results is None:
                raise LinkAheadException("The query result count is not available in the response.")
            self.results = int(results)

            cached_value = q.get("cached")
            if cached_value is None:
                self.cached = False
            else:
                self.cached = cached_value.lower() == "true"
            self.etag = q.get("etag")

            for m in q:
                if str(m.tag).lower() == 'warning' or str(m.tag).lower() == 'error':
                    self.messages.append(_parse_single_xml_element(m))
        else:
            self.q = q

    def _query_request(self, query_dict: QueryDict):
        """Used internally to execute the query request..."""
        _log_request("GET Entity?" + str(query_dict), None)
        connection = get_connection()
        http_response = connection.retrieve(
            entity_uri_segments=["Entity"],
            query_dict=query_dict)
        cresp = Container._response_to_entities(http_response)
        return cresp

    def _paging_generator(
        self,
        first_page: Container,
        query_dict: QueryDict,
        page_length: int,
    ):
        """Used internally to create a generator of pages instead instead of a
        container which contais all the results."""
        if len(first_page) == 0:
            return  # empty page
        yield first_page
        index = page_length
        while self.results > index:
            query_dict["P"] = f"{index}L{page_length}"
            next_page = self._query_request(query_dict)
            etag = next_page.query.etag
            if etag is not None and etag != self.etag:
                raise PagingConsistencyError(
                    "The database state changed while retrieving the pages")
            yield next_page
            index += page_length

    def execute(
        self,
        unique: bool = False,
        raise_exception_on_error: bool = True,
        cache: bool = True,
        page_length: Optional[int] = None,
    ) -> Union[Container, int]:
        """Execute a query (via a server-requests) and return the results.

        Parameters
        ----------

        unique : bool
            Whether the query is expected to have only one entity as result.
            Defaults to False.
        raise_exception_on_error : bool
            Whether an exception should be raises when there are errors in the
            resulting entities. Defaults to True.
        cache : bool
            Whether to use the server-side query cache (equivalent to adding a
            "cache" flag) to the Query object. Defaults to True.
        page_length : int
            Whether to use paging. If page_length > 0 this method returns a
            generator (to be used in a for-loop or with list-comprehension).
            The generator yields containers with up to page_length entities.
            Otherwise, paging is disabled, as well as for count queries and
            when unique is True. Defaults to None.

        Raises:
        -------
        PagingConsistencyError
            If the database state changed between paged requests.

        Yields
        ------
        page : Container
            Returns a container with the next `page_length` resulting entities.

        Returns
        -------
        results : Container or integer
            Returns an integer when it was a `COUNT` query. Otherwise, returns a
            Container with the resulting entities.
        """
        flags = self.flags

        if cache is False:
            flags["cache"] = "false"
        query_dict = dict(flags)
        query_dict["query"] = str(self.q)

        has_paging = False
        is_count_query = self.q.split()[0].lower() == "count" if len(self.q.split()) > 0 else False

        if not unique and not is_count_query and page_length is not None and page_length > 0:
            has_paging = True
            query_dict["P"] = f"0L{page_length}"

        # retreive first/only page
        cresp = self._query_request(query_dict)

        self.results = cresp.query.results
        self.cached = cresp.query.cached
        self.etag = cresp.query.etag

        if is_count_query:
            return self.results

        if raise_exception_on_error:
            raise_errors(cresp)

        if unique:
            if len(cresp) > 1 and raise_exception_on_error:
                raise QueryNotUniqueError(
                    "Query '{}' wasn't unique.".format(self.q))

            if len(cresp) == 0 and raise_exception_on_error:
                raise EmptyUniqueQueryError(
                    "Query '{}' found no results.".format(self.q))

            if len(cresp) == 1:
                r = cresp[0]
                r.messages.extend(cresp.messages)

                return r
        self.messages = cresp.messages

        if has_paging and page_length is not None:
            return self._paging_generator(cresp, query_dict, page_length)
        else:
            return cresp


def execute_query(
    q: str,
    unique: bool = False,
    raise_exception_on_error: bool = True,
    cache: bool = True,
    flags: Optional[QueryDict] = None,
    page_length: Optional[int] = None,
) -> Union[Container, Entity, int]:
    """Execute a query (via a server-requests) and return the results.

    Parameters
    ----------

    q : str
        The query string.
    unique : bool
        Whether the query is expected to have only one entity as result.
        Defaults to False.
    raise_exception_on_error : bool
        Whether an exception should be raised when there are errors in the
        resulting entities. Defaults to True.
    cache : bool
        Whether to use the server's query cache (equivalent to adding a
        "cache" flag) to the Query object. Defaults to True.  Not to be
        confused with the ``cached`` module.
    flags : dict of str
        Flags to be added to the request.
    page_length : int
        Whether to use paging. If page_length > 0 this method returns a
        generator (to be used in a for-loop or with list-comprehension).
        The generator yields containers with up to page_length entities.
        Otherwise, paging is disabled, as well as for count queries and
        when unique is True. Defaults to None.

    Raises
    ------
    PagingConsistencyError
        If the database state changed between paged requests.

    Yields
    ------
    page : Container
        Returns a container with the next `page_length` resulting entities.

    Returns
    -------
    results : Container or Entity or integer
        Returns an integer when it was a `COUNT` query. Otherwise, returns a
        Container with the resulting entities.
    """
    query = Query(q)

    if flags is not None:
        query.flags = flags

    return query.execute(unique=unique,
                         raise_exception_on_error=raise_exception_on_error,
                         cache=cache, page_length=page_length)


class UserInfo():
    """User information from a server response.

    Attributes
    ----------
    name : str
        Username
    realm : str
        Realm in which this user lives, e.g., CaosDB or LDAP.
    roles : list[str]
        List of roles assigned to this user.
    """

    def __init__(self, xml: etree._Element):
        self.roles = [role.text for role in xml.findall("Roles/Role")]
        self.name = xml.get("username")
        self.realm = xml.get("realm")


class Info():
    """Info about the LinkAhead instance that you are connected to. It has a
    simple string representation in the form of "Connected to a LinkAhead with N
    Records".

    Attributes
    ----------
    messages : Messages
        Collection of messages that the server's ``Info`` response contained.
    user_info : UserInfo
        Information about the user that is connected to the server, such as
        name, realm or roles.
    time_zone : TimeZone
        The timezone information returned by the server.

    """

    def __init__(self) -> None:
        self.messages = Messages()
        self.user_info: Optional[UserInfo] = None
        self.time_zone: Optional[TimeZone] = None
        self.sync()

    def sync(self):
        """Retrieve server information from the server's ``Info`` response."""
        c = get_connection()
        try:
            http_response = c.retrieve(["Info"])
        except LinkAheadConnectionError as conn_e:
            print(conn_e)

            return

        xml = etree.fromstring(http_response.read())

        for e in xml:
            m = _parse_single_xml_element(e)

            if isinstance(m, UserInfo):
                self.user_info = m
            elif isinstance(m, TimeZone):
                self.time_zone = m
            else:
                self.messages.append(m)

    def __str__(self):
        if "Counts" not in [m.type for m in self.messages]:
            return "linkahead.Info"

        if int(self.messages["counts"]["records"]) > 0:
            return "Connection to LinkAhead with {} Records." .format(
                self.messages["counts"]["records"]
            )
        else:
            return "Connection to LinkAhead without Records."

    def __repr__(self):
        return self.__str__()


class Permission():

    def __init__(self, name: str, description: Optional[str] = None):
        self.name = name
        self.description = description

    def __repr__(self):
        return str(self)

    def __str__(self):
        return self.name

    def __eq__(self, p):
        if isinstance(p, Permission):
            return p.name == self.name

        return False

    def __hash__(self):
        return hash(self.name)


class Permissions():

    known_permissions: Optional[Permissions] = None

    def __init__(self, xml: etree._Element):
        self.parse_xml(xml)

    def clear(self):
        self._perms = set()

    def parse_xml(self, xml: etree._Element):
        self.clear()

        for e in xml:
            if e.tag == "Permission":
                name = e.get("name")
                if name is None:
                    raise LinkAheadException(
                        "The permission element has no name attribute."
                    )
                self._perms.add(Permission(name=name, description=e.get("description")))

    def __contains__(self, p):
        if isinstance(p, Permission):
            return p in self._perms
        else:
            return Permission(name=p) in self._perms

    def __repr__(self):
        return str(self)

    def __str__(self):
        return str(self._perms)


def parse_xml(xml: Union[str, etree._Element]):
    """parse a string or tree representation of an xml document to a set of
    entities (records, recordtypes, properties, or files).

    @param xml: a string or tree representation of an xml document.
    @return: list of entities or single entity.
    """

    if isinstance(xml, etree._Element):
        elem: etree._Element = xml
    else:
        elem = etree.fromstring(xml)

    return _parse_single_xml_element(elem)


def _parse_single_xml_element(elem: etree._Element):
    classmap = {
        "record": Record,
        "recordtype": RecordType,
        "property": Property,
        "file": File,
        "parent": Parent,
        "entity": Entity,
    }

    if str(elem.tag).lower() in classmap:
        klass = classmap.get(str(elem.tag).lower())
        if klass is None:
            raise LinkAheadException("No class for tag '{}' found.".format(str(elem.tag)))
        entity = klass()
        Entity._from_xml(entity, elem)

        return entity
    elif str(elem.tag).lower() == "version":
        return Version.from_xml(elem)
    elif str(elem.tag).lower() == "state":
        return State.from_xml(elem)
    elif str(elem.tag).lower() == "emptystring":
        return ""
    elif str(elem.tag).lower() == "value":
        if len(elem) == 1 and str(elem[0].tag).lower() == "emptystring":
            return ""
        elif len(elem) == 1 and str(elem[0].tag).lower() in classmap:
            return _parse_single_xml_element(elem[0])
        elif elem.text is None or elem.text.strip() == "":
            return None

        return str(elem.text.strip())
    elif str(elem.tag).lower() == "querytemplate":
        return QueryTemplate._from_xml(elem)
    elif str(elem.tag).lower() == 'query':
        return Query(elem)
    elif str(elem.tag).lower() == 'history':
        return Message(type='History', description=elem.get("transaction"))
    elif str(elem.tag).lower() == 'stats':
        counts = elem.find("counts")
        if counts is None:
            raise LinkAheadException("'stats' element without a 'count' found.")
        return Message(type="Counts", description=None, body=counts.attrib)
    elif elem.tag == "EntityACL":
        return ACL(xml=elem)
    elif elem.tag == "Permissions":
        return Permissions(xml=elem)
    elif elem.tag == "UserInfo":
        return UserInfo(xml=elem)
    elif elem.tag == "TimeZone":
        return TimeZone(
            zone_id=elem.get("id"),
            offset=elem.get("offset"),
            display_name=elem.text.strip() if elem.text is not None else "",
        )
    else:
        code = elem.get("code")
        return Message(
            type=str(elem.tag),
            code=int(code) if code is not None else None,
            description=elem.get("description"),
            body=elem.text,
        )


def _evaluate_and_add_error(parent_error: TransactionError,
                            ent: Union[Entity, QueryTemplate, Container]):
    """Evaluate the error message(s) attached to entity and add a
    corresponding exception to parent_error.

    Parameters:
    -----------
    parent_error : TransactionError
        Parent error to which the new exception will be attached. This
        exception will be a direct child.
    ent : Entity or Container or QueryTemplate
        Entity that caused the TransactionError. An exception is
        created depending on its error message(s).

    Returns:
    --------
    TransactionError :
        Parent error with new exception(s) attached to it.

    """

    if isinstance(ent, (Entity, QueryTemplate)):
        # Check all error messages
        found114 = False
        found116 = False

        for err in ent.get_errors():
            # Evaluate specific EntityErrors depending on the error
            # code

            if err.code is not None:
                if int(err.code) == 101:  # ent doesn't exist
                    new_exc: EntityError = EntityDoesNotExistError(entity=ent,
                                                                   error=err)
                elif int(err.code) == 110:  # ent has no data type
                    new_exc = EntityHasNoDatatypeError(entity=ent,
                                                       error=err)
                elif int(err.code) == 403:  # no permission
                    new_exc = AuthorizationError(entity=ent,
                                                 error=err)
                elif int(err.code) == 152:  # name wasn't unique
                    new_exc = UniqueNamesError(entity=ent, error=err)
                elif int(err.code) == 114:  # unqualified properties
                    found114 = True
                    new_exc = UnqualifiedPropertiesError(entity=ent,
                                                         error=err)

                    for prop in ent.get_properties():
                        new_exc = _evaluate_and_add_error(new_exc,
                                                          prop)
                elif int(err.code) == 116:  # unqualified parents
                    found116 = True
                    new_exc = UnqualifiedParentsError(entity=ent,
                                                      error=err)

                    for par in ent.get_parents():
                        new_exc = _evaluate_and_add_error(new_exc,
                                                          par)
                else:  # General EntityError for other codes
                    new_exc = EntityError(entity=ent, error=err)
            else:  # No error code causes a general EntityError, too
                new_exc = EntityError(entity=ent, error=err)
            parent_error.add_error(new_exc)
        # Check for possible errors in parents and properties that
        # weren't detected up to here

        if not found114:
            dummy_err = EntityError(entity=ent)

            for prop in ent.get_properties():
                dummy_err = _evaluate_and_add_error(dummy_err, prop)

            if dummy_err.errors:
                parent_error.add_error(dummy_err)

        if not found116:
            dummy_err = EntityError(entity=ent)

            for par in ent.get_parents():
                dummy_err = _evaluate_and_add_error(dummy_err, par)

            if dummy_err.errors:
                parent_error.add_error(dummy_err)

    elif isinstance(ent, Container):
        parent_error.container = ent

        if ent.get_errors() is not None:
            parent_error.code = ent.get_errors()[0].code
            # In the highly unusual case of more than one error
            # message, attach all of them.
            parent_error.msg = '\n'.join(
                [x.description for x in ent.get_errors()])
        # Go through all container elements and add them:

        for elt in ent:
            parent_error = _evaluate_and_add_error(parent_error, elt)

    else:
        raise TypeError("Parameter ent is to be an Entity or a Container")

    return parent_error


def raise_errors(arg0: Union[Entity, QueryTemplate, Container]):
    """Raise a TransactionError depending on the error code(s) inside
    Entity, QueryTemplate or Container arg0. More detailed errors may
    be attached to the TransactionError depending on the contents of
    arg0.

    Parameters:
    -----------
    arg0 : Entity, QueryTemplate, or Container
        LinkAhead object whose messages are evaluated according to their
        error codes

    """
    transaction_error = _evaluate_and_add_error(TransactionError(),
                                                arg0)
    # Raise if any error was found

    if len(transaction_error.all_errors) > 0:
        raise transaction_error
    # Cover the special case of an empty container with error
    # message(s) (e.g. query syntax error)

    if (transaction_error.container is not None and
            transaction_error.container.has_errors()):
        raise transaction_error


def delete(ids: Union[list[int], range], raise_exception_on_error: bool = True):
    c = Container()

    if isinstance(ids, list) or isinstance(ids, range):
        for i in ids:
            c.append(Entity(id=i))
    else:
        c.append(Entity(id=ids))

    return c.delete(raise_exception_on_error=raise_exception_on_error)


def _filter_entity_list_by_identity(listobject: list[Entity],
                                    entity: Optional[Entity] = None,
                                    pid: Union[None, str, int] = None,
                                    name: Optional[str] = None,
                                    conjunction: bool = False) -> list:
    """
    Returns a subset of entities from the list based on whether their id and
    name matches the selection criterion.

    If both pid and name are given, entities from the list are first matched
    based on id. If they do not have an id, they are matched based on name.
    If only one parameter is given, only this parameter is considered.

    If an Entity is given, neither name nor ID may be set. In this case, pid
    and name are determined by the attributes of given entity.

    This results in the following selection criteria:
    If an entity in the list
    - has both name and id, it is returned if the id matches the given not-None
      value for pid. If no pid was given, it is returned if the name matches.
    - has an id, but no name, it will be returned only if it matches the given
      not-None value
    - has no id, but a name, it will be returned if the name matches the given
      not-None value
    - has neither id nor name, it will never be returned

    As IDs can be strings, integer IDs are cast to string for the comparison.

    Params
    ------
    listobject        : Iterable(Entity)
                        List to be filtered
    entity            : Entity
                        Entity to match name and ID for. Cannot be set
                        simultaneously with ID or name.
    pid               : str, int
                        Entity ID to match
    name              : str
                        Entity name to match
    conjunction       : bool, defaults to False
                        Set to true to return only entities that match both id
                        and name if both are given.

    Returns
    -------
    matches          : list
                       A List containing all matching Entities
    """
    # Check correct input params and setup
    if entity is not None:
        if pid is not None or name is not None:
            raise ValueError("If an entity is given, pid and name must not be set.")
        pid = entity.id
        name = entity.name
    if pid is None and name is None:
        if entity is None:
            raise ValueError("One of entity, pid or name must be set.")
        else:
            raise ValueError("A given entity must have at least one of name and id.")
    if pid is None or name is None:
        conjunction = False

    # Iterate through list and match based on given criteria
    matches = []
    for candidate in listobject:
        name_match, pid_match = False, False

        # Check whether name/pid match
        # Comparison is only possible if both are not None
        pid_none = pid is None or candidate.id is None
        # Cast to string in case one is f.e. "12" and the other is 12
        if not pid_none and str(candidate.id) == str(pid):
            pid_match = True
        name_none = name is None or candidate.name is None
        if not name_none and str(candidate.name).lower() == str(name).lower():
            name_match = True

        # If the criteria are satisfied, append the match.
        if pid_match and name_match:
            matches.append(candidate)
        elif not conjunction:
            if pid_match:
                matches.append(candidate)
            if pid_none and name_match:
                matches.append(candidate)
    return matches


def value_matches_versionid(value: Union[int, str]):
    """Returns True if the value matches the pattern <id>@<version>"""
    if isinstance(value, int):
        return False
    if not isinstance(value, str):
        raise ValueError(f"A reference value needs to be int or str. It was {type(value)}. "
                         "Did you call value_matches_versionid on a non reference value?")
    return "@" in value


def get_id_from_versionid(versionid: str):
    """Returns the ID part of the versionid with the pattern <id>@<version>"""
    return versionid.split("@")[0]
