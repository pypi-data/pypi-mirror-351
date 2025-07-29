# -*- coding: utf-8 -*-
#
# This file is a part of the LinkAhead Project.
#
# Copyright (C) 2018 Research Group Biomedical Physics,
# Max-Planck-Institute for Dynamics and Self-Organization Göttingen
# Copyright (C) 2020 Timm Fitschen <t.fitschen@indiscale.com>
# Copyright (C) 2020-2022 IndiScale GmbH <info@indiscale.com>
# Copyright (C) 2024 Indiscale GmbH <info@indiscale.com>
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
# ** end header
#
"""API-Utils: Some simplified functions for generation of records etc.

"""
from __future__ import annotations

import logging
import warnings
from collections.abc import Iterable
from typing import Any, Optional, Union

from .common.datatype import is_reference
from .common.models import (SPECIAL_ATTRIBUTES, Container, Entity, File,
                            Property, Record, RecordType, execute_query)
from .exceptions import LinkAheadException
from .utils.git_utils import (get_branch_in, get_commit_in, get_diff_in,
                              get_origin_url_in)

logger = logging.getLogger(__name__)


class EntityMergeConflictError(LinkAheadException):
    """An error that is raised in case of an unresolvable conflict when merging
    two entities.
    """


def new_record(record_type: Union[str],
               name: Optional[str] = None,
               description: Optional[str] = None,
               tempid: Optional[int] = None,
               insert: bool = False, **kwargs) -> Record:
    """Function to simplify the creation of Records.

    record_type: The name of the RecordType to use for this record.
    name: Name of the new Record.
    kwargs: Key-value-pairs for the properties of this Record.

    Returns: The newly created Record.

    Of course this functions requires an open database connection!
    """

    rt = RecordType(name=record_type)
    rt.retrieve()

    r = Record(name)
    r.add_parent(rt)

    if tempid is not None:
        r.id = tempid

    if description is not None:
        r.description = description

    # Add all additional properties, treat iterables als multiple
    # additions.

    for k, v in kwargs.items():
        if hasattr(v, "encode") or not isinstance(v, Iterable):
            v = [v]

        for vv in v:
            p = Property(k)
            p.retrieve()
            p.value = vv
            r.add_property(p)

    if insert:
        r.insert()

    return r


def id_query(ids: list[int]) -> Container:
    warnings.warn("Please use 'create_id_query', which only creates"
                  "the string.", DeprecationWarning)

    return execute_query(create_id_query(ids))  # type: ignore


def create_id_query(ids: list[int]) -> str:
    return "FIND ENTITY WITH " + " OR ".join(
        ["ID={}".format(id) for id in ids])


def get_type_of_entity_with(id_: int):
    objs = retrieve_entities_with_ids([id_])

    if len(objs) == 0:
        raise RuntimeError("ID {} not found.".format(id_))

    if len(objs) > 1:
        raise RuntimeError(
            "ID {} is not unique. This is probably a bug in the LinkAhead server." .format(id_))
    obj = objs[0]

    if isinstance(obj, Record):
        return Record
    elif isinstance(obj, RecordType):
        return RecordType
    elif isinstance(obj, Property):
        return Property
    elif isinstance(obj, File):
        return File
    elif isinstance(obj, Entity):
        return Entity


def retrieve_entity_with_id(eid: int):
    return execute_query("FIND ENTITY WITH ID={}".format(eid), unique=True)


def retrieve_entities_with_ids(entities: list) -> Container:
    collection = Container()
    step = 20

    for i in range(len(entities)//step+1):
        collection.extend(
            execute_query(
                create_id_query(entities[i*step:(i+1)*step])))

    return collection


def getOriginUrlIn(folder):
    warnings.warn("""
                  This function is deprecated and will be removed with the next release.
                  Please use the linkahead.utils.git_utils.get_origin_url_in instead.""",
                  DeprecationWarning)
    return get_origin_url_in(folder)


def getDiffIn(folder, save_dir=None):
    warnings.warn("""
                  This function is deprecated and will be removed with the next release.
                  Please use the linkahead.utils.git_utils.get_diff_in instead.""",
                  DeprecationWarning)
    return get_diff_in(folder, save_dir)


def getBranchIn(folder):
    warnings.warn("""
                  This function is deprecated and will be removed with the next release.
                  Please use the linkahead.utils.git_utils.get_branch_in instead.""",
                  DeprecationWarning)
    return get_branch_in(folder)


def getCommitIn(folder):
    warnings.warn("""
                  This function is deprecated and will be removed with the next release.
                  Please use the linkahead.utils.git_utils.get_commit_in instead.""",
                  DeprecationWarning)
    return get_commit_in(folder)


def compare_entities(entity0: Optional[Entity] = None,
                     entity1: Optional[Entity] = None,
                     compare_referenced_records: bool = False,
                     entity_name_id_equivalency: bool = False,
                     old_entity: Optional[Entity] = None,
                     new_entity: Optional[Entity] = None,
                     ) -> tuple[dict[str, Any], dict[str, Any]]:
    """Compare two entities.

    Returns two dicts listing the differences between the two entities. The
    order of the two returned dicts corresponds to the two input entities.
    The dicts contain two keys, 'parents' and 'properties'. The list saved
    under the 'parents' key contains those parents of the respective entity
    that are missing in the other entity, and the 'properties' dict contains
    properties and SPECIAL_ATTRIBUTES if they are missing or different from
    their counterparts in the other entity.

    The key used to represent a parent in the parent list or a
    property in the property dictionary is the entity's name if the
    name is present for both compared entities, the id otherwise.

    The value of the properties dict for each listed property is again a dict
    detailing the differences between this property and its counterpart.
    The characteristics that are checked to determine whether two properties
    match are the following:

    - datatype
    - importance
    - value

    If any of these characteristics differ for a property, the respective
    string (datatype, importance, value) is added as a key to the dict of the
    property with its value being the characteristics value,
    e.g. {"prop": {"value": 6, 'importance': 'SUGGESTED'}}. Except: None as
    value is not added to the dict.
    If a property is of type LIST, the comparison is order-sensitive.

    Comparison of multi-properties is not yet supported, so should either
    entity have several instances of one Property, the comparison is aborted
    and an error is raised.

    Two parents match if their name and id are the same, any further
    differences are ignored.

    Should records referenced in the value field not be checked for equality
    between the entities but for equivalency, this is possible by setting the
    parameter compare_referenced_records.

    Params
    ------
    entity0:                    Entity
                                First entity to be compared.
    entity1:                    Entity
                                Second entity to be compared.
    compare_referenced_records: bool, default: False
                                If set to True, values with referenced records
                                are not checked for equality but for
                                equivalency using this function.
                                compare_referenced_records is set to False for
                                these recursive calls, so references of
                                references need to be equal. If set to `False`,
                                only the Python objects are compared, which may
                                lead to unexpected behavior.
    entity_name_id_equivalency: bool, default: False
                                If set to True, the comparison between an
                                entity and an int or str also checks whether
                                the int/str matches the name or id of the
                                entity, so Entity(id=100) == 100 == "100".

    """
    # ToDo: Discuss intended behaviour
    # Questions that need clarification:
    #    - What is intended behaviour for multi-properties and multi-parents?
    #    - Do different inheritance levels for parents count as a difference?
    #    - Do we care about parents and properties of properties?
    #    - Should there be a more detailed comparison of parents without id?
    #    - Revisit filter - do we care about RecordType when matching?
    #      How to treat None?
    #    - Should matching of parents also take the recordtype into account
    #      for parents that have a name but no id?
    # Suggestions for enhancements:
    #    - For the comparison of entities in value and properties, consider
    #      keeping a list of traversed entities, not only look at first layer
    #    - Make the empty_diff functionality faster by adding a parameter to
    #      this function so that it returns after the first found difference?
    #    - Add parameter to restrict diff to some characteristics
    #    - Implement comparison of date where one is a string and the other is
    #      datetime
    if entity0 is None and old_entity is None:
        raise ValueError("Please provide the first entity as first argument (`entity0`)")
    if entity1 is None and new_entity is None:
        raise ValueError("Please provide the second entity as second argument (`entity1`)")
    if old_entity is not None:
        warnings.warn("Please use 'entity0' instead of 'old_entity'.", DeprecationWarning)
        if entity0 is not None:
            raise ValueError("You cannot use both entity0 and old_entity")
        entity0 = old_entity
    if new_entity is not None:
        warnings.warn("Please use 'entity1' instead of 'new_entity'.", DeprecationWarning)
        if entity1 is not None:
            raise ValueError("You cannot use both entity1 and new_entity")
        entity1 = new_entity
    assert entity0 is not None
    assert entity1 is not None

    diff: tuple[dict[str, Any], dict[str, Any]] = ({"properties": {}, "parents": []},
                                                   {"properties": {}, "parents": []})

    if entity0 is entity1:
        return diff

    # FIXME Why not simply return a diff which says that the types are different?
    if type(entity0) is not type(entity1):
        diff[0]["type"] = type(entity0)
        diff[1]["type"] = type(entity1)

    # compare special attributes
    for attr in SPECIAL_ATTRIBUTES:
        if attr == "value":
            continue

        attr0 = entity0.__getattribute__(attr)
        # we consider "" and None to be nonexistent
        attr0_unset = (attr0 == "" or attr0 is None)

        attr1 = entity1.__getattribute__(attr)
        # we consider "" and None to be nonexistent
        attr1_unset = (attr1 == "" or attr1 is None)

        # in both entities the current attribute is not set
        if attr0_unset and attr1_unset:
            continue

        # treat datatype separately if one datatype is an object and the other
        # a string or int, and therefore may be a name or id
        if attr == "datatype":
            if not attr0_unset and not attr1_unset:
                if isinstance(attr0, RecordType):
                    if attr0.name == attr1:
                        continue
                    if str(attr0.id) == str(attr1):
                        continue
                if isinstance(attr1, RecordType):
                    if attr1.name == attr0:
                        continue
                    if str(attr1.id) == str(attr0):
                        continue

        # add to diff if attr has different values or is not set for one entity
        if (attr0_unset != attr1_unset) or (attr0 != attr1):
            diff[0][attr] = attr0
            diff[1][attr] = attr1

    # compare value
    ent0_val, ent1_val = entity0.value, entity1.value
    if ent0_val != ent1_val:
        same_value = False

        # Surround scalar values with a list to avoid code duplication -
        # this way, the scalar values can be checked against special cases
        # (compare refs, entity id equivalency etc.) in the list loop
        if not isinstance(ent0_val, list) and not isinstance(ent1_val, list):
            ent0_val, ent1_val = [ent0_val], [ent1_val]

        if isinstance(ent0_val, list) and isinstance(ent1_val, list):
            # lists can't be the same if the lengths are different
            if len(ent0_val) == len(ent1_val):
                lists_match = True
                for val0, val1 in zip(ent0_val, ent1_val):
                    if val0 == val1:
                        continue
                    # Compare Entities
                    if (compare_referenced_records and
                            isinstance(val0, Entity) and isinstance(val1, Entity)):
                        try:
                            same = empty_diff(val0, val1, False,
                                              entity_name_id_equivalency)
                        except (ValueError, NotImplementedError):
                            same = False
                        if same:
                            continue
                    # Compare Entity name and id
                    if entity_name_id_equivalency:
                        if (isinstance(val0, Entity)
                                and isinstance(val1, (int, str))):
                            if (str(val0.id) == str(val1)
                                    or str(val0.name) == str(val1)):
                                continue
                        if (isinstance(val1, Entity)
                                and isinstance(val0, (int, str))):
                            if (str(val1.id) == str(val0)
                                    or str(val1.name) == str(val0)):
                                continue
                    # val0 and val1 could not be matched
                    lists_match = False
                    break
                if lists_match:
                    same_value = True

        if not same_value:
            diff[0]["value"] = entity0.value
            diff[1]["value"] = entity1.value

    # compare properties
    for prop in entity0.properties:
        # ToDo: Would making id default break anything?
        key = prop.name if prop.name is not None else prop.id
        matching = entity1.properties.filter_by_identity(prop)
        if len(matching) == 0:
            # entity1 has prop, entity0 does not
            diff[0]["properties"][key] = {}
        elif len(matching) == 1:
            # It's possible that prop has name and id, but match only has id
            key = prop.name if (prop.name is not None and
                                matching[0].name == prop.name) else prop.id
            diff[0]["properties"][key] = {}
            diff[1]["properties"][key] = {}
            propdiff = (diff[0]["properties"][key],
                        diff[1]["properties"][key])

            # We should compare the wrapped properties instead of the
            # wrapping entities if possible:
            comp1, comp2 = prop, matching[0]
            if (comp1._wrapped_entity is not None
                    and comp2._wrapped_entity is not None):
                comp1, comp2 = comp1._wrapped_entity, comp2._wrapped_entity
            # Recursive call to determine the differences between properties
            # Note: Can lead to infinite recursion if two properties have
            # themselves or each other as subproperties
            od, nd = compare_entities(comp1, comp2, compare_referenced_records,
                                      entity_name_id_equivalency)
            # We do not care about parents and properties here, discard
            od.pop("parents")
            od.pop("properties")
            nd.pop("parents")
            nd.pop("properties")
            # use the remaining diff
            propdiff[0].update(od)
            propdiff[1].update(nd)

            # As the importance of a property is an attribute of the record
            # and not the property, it is not contained in the diff returned
            # by compare_entities and needs to be added separately
            if (entity0.get_importance(prop) !=
                    entity1.get_importance(matching[0])):
                propdiff[0]["importance"] = entity0.get_importance(prop)
                propdiff[1]["importance"] = entity1.get_importance(matching[0])

            # in case there is no difference, we remove the dict keys again
            if len(propdiff[0]) == 0 and len(propdiff[1]) == 0:
                diff[0]["properties"].pop(key)
                diff[1]["properties"].pop(key)

        else:
            raise NotImplementedError(
                "Comparison not implemented for multi-properties.")

    # we have not yet compared properties that do not exist in entity0
    for prop in entity1.properties:
        key = prop.name if prop.name is not None else prop.id
        # check how often the property appears in entity0
        num_prop_in_ent0 = len(entity0.properties.filter_by_identity(prop))
        if num_prop_in_ent0 == 0:
            # property is only present in entity0 - add to diff
            diff[1]["properties"][key] = {}
        if num_prop_in_ent0 > 1:
            # Check whether the property is present multiple times in entity0
            # and raise error - result would be incorrect
            raise NotImplementedError(
                "Comparison not implemented for multi-properties.")

    # compare parents
    for index, parents, other_entity in [(0, entity0.parents, entity1),
                                         (1, entity1.parents, entity0)]:
        for parent in parents:
            key = parent.name if parent.name is not None else parent.id
            matching = other_entity.parents.filter_by_identity(parent)
            if len(matching) == 0:
                diff[index]["parents"].append(key)
                continue

    return diff


def empty_diff(entity0: Entity,
               entity1: Entity,
               compare_referenced_records: bool = False,
               entity_name_id_equivalency: bool = False,
               old_entity: Optional[Entity] = None,
               new_entity: Optional[Entity] = None,
               ) -> bool:
    """Check whether the `compare_entities` found any differences between
    entity0 and entity1.

    Parameters
    ----------
    entity0, entity1 : Entity
        Entities to be compared
    compare_referenced_records : bool, optional
        Whether to compare referenced records in case of both, `entity0` and
        `entity1`, have the same reference properties and both have a Record
        object as value.
    entity_name_id_equivalency : bool, optional
        If set to True, the comparison between an entity and an int or str also
        checks whether the int/str matches the name or id of the entity, so
        Entity(id=100) == 100 == "100".
    """
    if entity0 is None and old_entity is None:
        raise ValueError("Please provide the first entity as first argument (`entity0`)")
    if entity1 is None and new_entity is None:
        raise ValueError("Please provide the second entity as second argument (`entity1`)")
    if old_entity is not None:
        warnings.warn("Please use 'entity0' instead of 'old_entity'.", DeprecationWarning)
        if entity0 is not None:
            raise ValueError("You cannot use both entity0 and old_entity")
        entity0 = old_entity
    if new_entity is not None:
        warnings.warn("Please use 'entity1' instead of 'new_entity'.", DeprecationWarning)
        if entity1 is not None:
            raise ValueError("You cannot use both entity1 and new_entity")
        entity1 = new_entity
    e0diff, e1diff = compare_entities(entity0, entity1, compare_referenced_records,
                                      entity_name_id_equivalency)
    for diff in [e0diff, e1diff]:
        for key in ["parents", "properties"]:
            if len(diff[key]) > 0:
                # There is a difference somewhere in the diff
                return False
        for key in SPECIAL_ATTRIBUTES:
            if key in diff and diff[key]:
                # There is a difference in at least one special attribute
                return False
    # all elements of the two diffs were empty
    return True


def merge_entities(entity_a: Entity,
                   entity_b: Entity,
                   merge_references_with_empty_diffs=True,
                   force=False,
                   merge_id_with_resolved_entity: bool = False
                   ) -> Entity:
    """Merge entity_b into entity_a such that they have the same parents and properties.

    The attributes datatype, unit, value, name and description will only be changed
    in entity_a if they are None for entity_a and set for entity_b. If one of those attributes is
    set in both entities and they differ, then an
    EntityMergeConflictError will be raised to inform about an unresolvable merge
    conflict.

    The merge operation is done in place.

    Returns entity_a.

    Parameters
    ----------
    entity_a, entity_b : Entity
        The entities to be merged. entity_b will be merged into entity_a in place
    merge_references_with_empty_diffs : bool, optional
        Whether the merge is performed if entity_a and entity_b both reference
        record(s) that may be different Python objects but have empty diffs. If
        set to `False` a merge conflict will be raised in this case
        instead. Default is True.
    force : bool, optional
        If True, in case `entity_a` and `entity_b` have the same properties, the
        values of `entity_a` are replaced by those of `entity_b` in the
        merge. If `False`, an EntityMergeConflictError is raised
        instead. Default is False.
    merge_id_with_resolved_entity : bool, optional
        If true, the values of two reference properties will be considered the
        same if one is an integer id and the other is a db.Entity with this
        id. I.e., a value 123 is identified with a value ``<Record
        id=123/>``. Default is False.

    Returns
    -------
    entity_a : Entity
       The initial entity_a after the in-place merge

    Raises
    ------
    EntityMergeConflictError
        In case of an unresolvable merge conflict.

    """

    # Compare both entities:
    diff_r1, diff_r2 = compare_entities(
        entity_a, entity_b,
        entity_name_id_equivalency=merge_id_with_resolved_entity,
        compare_referenced_records=merge_references_with_empty_diffs)

    # Go through the comparison and try to apply changes to entity_a:
    for key in diff_r2["parents"]:
        entity_a.add_parent(entity_b.get_parent(key))

    for key in diff_r2["properties"]:
        if key in diff_r1["properties"]:
            if ("importance" in diff_r1["properties"][key] and
                    "importance" in diff_r2["properties"][key]):
                if (diff_r1["properties"][key]["importance"] !=
                        diff_r2["properties"][key]["importance"]):
                    raise NotImplementedError()
            elif ("importance" in diff_r1["properties"][key] or
                  "importance" in diff_r2["properties"][key]):
                raise NotImplementedError()

            for attribute in ("datatype", "unit", "value"):
                if (attribute in diff_r2["properties"][key] and
                        diff_r2["properties"][key][attribute] is not None):
                    if (attribute not in diff_r1["properties"][key] or
                            diff_r1["properties"][key][attribute] is None):
                        setattr(entity_a.get_property(key), attribute,
                                diff_r2["properties"][key][attribute])
                    elif force:
                        setattr(entity_a.get_property(key), attribute,
                                diff_r2["properties"][key][attribute])
                    else:
                        raise_error = True
                        if merge_id_with_resolved_entity is True and attribute == "value":
                            # Do a special check for the case of an id value on the
                            # one hand, and a resolved entity on the other side.
                            prop_a = entity_a.get_property(key)
                            assert prop_a is not None, f"Property {key} not found in entity_a"
                            prop_b = entity_b.get_property(key)
                            assert prop_b is not None, f"Property {key} not found in entity_b"
                            this = prop_a.value
                            that = prop_b.value
                            same = False
                            if isinstance(this, list) and isinstance(that, list):
                                if len(this) == len(that):
                                    same = all([_same_id_as_resolved_entity(a, b)
                                                for a, b in zip(this, that)])
                            else:
                                same = _same_id_as_resolved_entity(this, that)
                            if same is True:
                                setattr(entity_a.get_property(key), attribute,
                                        diff_r2["properties"][key][attribute])
                                raise_error = False
                        if raise_error is True:
                            raise EntityMergeConflictError(
                                f"Entity a ({entity_a.id}, {entity_a.name}) "
                                f"has a Property '{key}' with {attribute}="
                                f"{diff_r2['properties'][key][attribute]}\n"
                                f"Entity b ({entity_b.id}, {entity_b.name}) "
                                f"has a Property '{key}' with {attribute}="
                                f"{diff_r1['properties'][key][attribute]}")
        else:
            # TODO: This is a temporary FIX for
            #       https://gitlab.indiscale.com/caosdb/src/caosdb-pylib/-/issues/105
            prop_b = entity_b.get_property(key)
            assert prop_b is not None, f"Property {key} not found in entity_b"
            entity_a.add_property(id=prop_b.id,
                                  name=prop_b.name,
                                  datatype=prop_b.datatype,
                                  value=prop_b.value,
                                  unit=prop_b.unit,
                                  importance=entity_b.get_importance(key))
            # entity_a.add_property(
            #     entity_b.get_property(key),
            #     importance=entity_b.get_importance(key))

    for special_attribute in ("name", "description"):
        sa_a = getattr(entity_a, special_attribute)
        sa_b = getattr(entity_b, special_attribute)
        if sa_a != sa_b:
            if sa_a is None:
                setattr(entity_a, special_attribute, sa_b)
            elif force:
                # force overwrite
                setattr(entity_a, special_attribute, sa_b)
            else:
                raise EntityMergeConflictError(
                    f"Conflict in special attribute {special_attribute}:\n"
                    f"A: {sa_a}\nB: {sa_b}")
    return entity_a


def describe_diff(entity0_diff: dict[str, Any], entity1_diff: dict[str, Any],
                  name: Optional[str] = None,
                  as_update: Optional[bool] = None,
                  label_e0: str = "first version",
                  label_e1: str = "second version",
                  olddiff: Any = None,
                  newdiff: Any = None,
                  ) -> str:
    """
    Generate a textual description of the differences between two entities.
    These can be generated using :func:`compare_entities` and used within this function like this:

    `describe_diff(*compare_entities(...))`

    Arguments:
    ----------

    entity0_diff: dict[str, Any]
      First element of the tuple output of :func:`compare_entities`.
      This is referred to as the "first" version.

    entity1_diff: dict[str, Any]
      Second element of the tuple output of :func:`compare_entities`.
      This is referred to as the "second" version.


    name: Optional[str]
      Default None. Name of the entity that will be shown in the output text.

    as_update: Optional[bool]
      Default None. Not used anymore.

    label_e0: str
      Can be used to set a custom label for the diff that is associated with the first entity.

    label_e1: str
      Can be used to set a custom label for the diff that is associated with the second entity.

    olddiff: Any
      Deprecated. Replaced by entity0_diff.

    newdiff: Any
      Deprecated. Replaced by entity1_diff.

    Returns:
    --------
    A text description of the differences.

    """
    description = ""

    if as_update:
        warnings.warn("'as_update' is deprecated. Do not use it.", DeprecationWarning)
    if olddiff:
        warnings.warn("'olddiff' is deprecated. Use 'entity0_diff' instead.", DeprecationWarning)
        entity0_diff = olddiff
    if newdiff:
        warnings.warn("'newdiff' is deprecated. Use 'entity1_diff' instead.", DeprecationWarning)
        entity1_diff = newdiff

    for attr in list(set(list(entity0_diff.keys()) + list(entity1_diff.keys()))):
        if attr == "parents" or attr == "properties":
            continue
        description += "{} differs:\n".format(attr)
        description += label_e0 + ": {}\n".format(
            entity0_diff[attr] if attr in entity0_diff else "not set")
        description += label_e1 + ": {}\n\n".format(
            entity1_diff[attr] if attr in entity1_diff else "not set")

    if len(entity0_diff["parents"]) > 0:
        description += ("Parents that are only in the " + label_e0 + ":\n"
                        + ", ".join(entity0_diff["parents"]) + "\n")

    if len(entity1_diff["parents"]) > 0:
        description += ("Parents that are only in the " + label_e1 + ":\n"
                        + ", ".join(entity0_diff["parents"]) + "\n")

    for prop in list(set(list(entity0_diff["properties"].keys())
                         + list(entity1_diff["properties"].keys()))):
        description += "property {} differs:\n".format(prop)

        if prop not in entity0_diff["properties"]:
            description += "it does not exist in the " + label_e0 + ":\n"
        elif prop not in entity1_diff["properties"]:
            description += "it does not exist in the " + label_e1 + ":\n"
        else:
            description += label_e0 + ": {}\n".format(
                entity0_diff["properties"][prop])
            description += label_e1 + ": {}\n\n".format(
                entity1_diff["properties"][prop])

    if description != "":
        description = ("## Difference between the " +
                       label_e0 +
                       " and the " +
                       label_e1 +
                       " of {}\n\n".format(name)) + description

    return description


def apply_to_ids(entities, func):
    """ Apply a function to all ids.

    All ids means the ids of the entities themselves but also to all parents,
    properties and referenced entities.

    Parameters
    ----------
    entities : list of Entity
    func : function with one parameter.
    """

    for entity in entities:
        _apply_to_ids_of_entity(entity, func)


def _apply_to_ids_of_entity(entity, func):
    entity.id = func(entity.id)

    for par in entity.parents:
        par.id = func(par.id)

    for prop in entity.properties:
        prop.id = func(prop.id)
        isref = is_reference(prop.datatype)

        if isref:
            if isinstance(prop.value, list):
                prop.value = [func(el) for el in prop.value]
            else:
                if prop.value is not None:
                    prop.value = func(prop.value)


def resolve_reference(prop: Property):
    """resolves the value of a reference property

    The integer value is replaced with the entity object.
    If the property is not a reference, then the function returns without
    change.
    """

    if not prop.is_reference(server_retrieval=True):
        return

    if isinstance(prop.value, list):
        referenced = []

        for val in prop.value:
            if isinstance(val, int):
                referenced.append(retrieve_entity_with_id(val))
            else:
                referenced.append(val)
        prop.value = referenced
    else:
        if isinstance(prop.value, int):
            prop.value = retrieve_entity_with_id(prop.value)


def create_flat_list(ent_list: list[Entity], flat: list[Entity]):
    """
    Recursively adds all properties contained in entities from ent_list to
    the output list flat. Each element will only be added once to the list.

    TODO: Currently this function is also contained in newcrawler module crawl.
          We are planning to permanently move it to here.
    """
    for ent in ent_list:
        for p in ent.properties:
            # For lists append each element that is of type Entity to flat:
            if isinstance(p.value, list):
                for el in p.value:
                    if isinstance(el, Entity):
                        if el not in flat:
                            flat.append(el)
                        # TODO: move inside if block?
                        create_flat_list([el], flat)
            elif isinstance(p.value, Entity):
                if p.value not in flat:
                    flat.append(p.value)
                # TODO: move inside if block?
                create_flat_list([p.value], flat)


def _same_id_as_resolved_entity(this, that):
    """Checks whether ``this`` and ``that`` either are the same or whether one
    is an id and the other is a db.Entity with this id.

    """
    if isinstance(this, Entity) and not isinstance(that, Entity):
        # this is an Entity with an id, that is not
        return this.id is not None and this.id == that
    if not isinstance(this, Entity) and isinstance(that, Entity):
        return that.id is not None and that.id == this
    return this == that
