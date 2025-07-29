# -*- coding: utf-8 -*-
#
# This file is a part of the LinkAhead Project.
#
# Copyright (C) 2023 IndiScale GmbH <info@indiscale.com>
# Copyright (C) 2023 Henrik tom Wörden <h.tomwoerden@indiscale.com>
# Copyright (C) 2023 Daniel Hornung <d.hornung@indiscale.com>
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

"""
This module provides some cached versions of functions that retrieve Entities from a remote server.

See also
========

- ``cache_initialize(...)`` : Re-initialize the cache.
- ``cache_clear()`` : Clear the cache.
- ``cached_query(query)`` : A cached version of ``execute_query(query)``.
- ``cached_get_entity_by(...)`` : Get an Entity by name, id, ...
"""

from __future__ import annotations
from enum import Enum
from functools import lru_cache
from typing import Any, Optional, Union

from .exceptions import EmptyUniqueQueryError, QueryNotUniqueError
from .utils import get_entity
from .common.models import execute_query, Entity, Container


# roughly 1GB for typical entity sizes
DEFAULT_SIZE = 33333

# This dict cache is solely for filling the real cache manually (e.g. to reuse older query results)
_DUMMY_CACHE: dict[Union[str, int], Any] = {}


class AccessType(Enum):
    """Different access types for cached queries.  Needed for filling the cache manually with
:func:`cache_fill` .

    """
    QUERY = 1
    PATH = 2
    EID = 3
    NAME = 4


def cached_get_entity_by(eid: Union[str, int, None] = None,
                         name: Optional[str] = None,
                         path: Optional[str] = None,
                         query: Optional[str] = None) -> Union[Entity, tuple[None]]:
    """Return a single entity that is identified uniquely by one argument.

You must supply exactly one argument.

If a query phrase is given, the result must be unique.  If this is not what you need, use
:func:`cached_query` instead.

    """
    count = 0
    if eid is not None:
        count += 1
    if name is not None:
        count += 1
    if path is not None:
        count += 1
    if query is not None:
        count += 1
    if count != 1:
        raise ValueError("You must supply exactly one argument.")

    result = (None, )
    if eid is not None:
        result = _cached_access(AccessType.EID, eid, unique=True)
    if name is not None:
        result = _cached_access(AccessType.NAME, name, unique=True)
    if path is not None:
        result = _cached_access(AccessType.PATH, path, unique=True)
    if query is not None:
        result = _cached_access(AccessType.QUERY, query, unique=True)

    if result != (None, ):
        if isinstance(result, (QueryNotUniqueError, EmptyUniqueQueryError)):
            raise result
        return result

    raise RuntimeError("This line should never be reached.")


def cached_query(query_string: str) -> Container:
    """A cached version of :func:`linkahead.execute_query<linkahead.common.models.execute_query>`.

    All additional arguments are at their default values.

    """
    result = _cached_access(AccessType.QUERY, query_string, unique=False)
    if isinstance(result, (QueryNotUniqueError, EmptyUniqueQueryError)):
        raise result
    return result


@lru_cache(maxsize=DEFAULT_SIZE)
def _cached_access(kind: AccessType, value: Union[str, int], unique: bool = True):
    # This is the function that is actually cached.
    # Due to the arguments, the cache has kind of separate sections for cached_query and
    # cached_get_entity_by with the different AccessTypes. However, there is only one cache size.

    # The dummy dict cache is only for filling the cache manually, it is deleted afterwards.
    if value in _DUMMY_CACHE:
        return _DUMMY_CACHE[value]

    try:
        if kind == AccessType.QUERY:
            if not isinstance(value, str):
                raise TypeError(
                    f"If AccessType is QUERY, value must be a string, not {type(value)}.")
            return execute_query(value, unique=unique)
        if kind == AccessType.NAME:
            if not isinstance(value, str):
                raise TypeError(
                    f"If AccessType is NAME, value must be a string, not {type(value)}.")
            return get_entity.get_entity_by_name(value)
        if kind == AccessType.EID:
            if not isinstance(value, (str, int)):
                raise TypeError(
                    f"If AccessType is EID, value must be a string or int, not {type(value)}.")
            return get_entity.get_entity_by_id(value)
        if kind == AccessType.PATH:
            if not isinstance(value, str):
                raise TypeError(
                    f"If AccessType is PATH, value must be a string, not {type(value)}.")
            return get_entity.get_entity_by_path(value)
    except (QueryNotUniqueError, EmptyUniqueQueryError) as exc:
        return exc

    raise ValueError(f"Unknown AccessType: {kind}")


def cache_clear() -> None:
    """Empty the cache that is used by `cached_query` and `cached_get_entity_by`."""
    _cached_access.cache_clear()


def cache_info():
    """Return info about the cache that is used by `cached_query` and `cached_get_entity_by`.

    Returns
    -------

    out: named tuple
      See the standard library :func:`functools.lru_cache` for details.
    """
    return _cached_access.cache_info()


def cache_initialize(maxsize: int = DEFAULT_SIZE) -> None:
    """Create a new cache with the given size for `cached_query` and `cached_get_entity_by`.

    This implies a call of :func:`cache_clear`, the old cache is emptied.

    """
    cache_clear()
    global _cached_access
    _cached_access = lru_cache(maxsize=maxsize)(_cached_access.__wrapped__)


def cache_fill(items: dict[Union[str, int], Any],
               kind: AccessType = AccessType.EID,
               unique: bool = True) -> None:
    """Add entries to the cache manually.

    This allows to fill the cache without actually submitting queries.  Note that this does not
    overwrite existing entries with the same keys.

    Parameters
    ----------

    items: dict
      A dictionary with the entries to go into the cache.  The keys must be compatible with the
      AccessType given in ``kind``

    kind: AccessType, optional
      The AccessType, for example ID, name, path or query.

    unique: bool, optional
      If True, fills the cache for :func:`cached_get_entity_by`, presumably with
      :class:`linkahead.Entity<linkahead.common.models.Entity>` objects.  If False, the cache should be
      filled with :class:`linkahead.Container<linkahead.common.models.Container>` objects, for use with
      :func:`cached_query`.

    """

    if kind == AccessType.QUERY:
        assert all(isinstance(key, str) for key in items.keys()), "Keys must be strings."
    elif kind == AccessType.NAME:
        assert all(isinstance(key, str) for key in items.keys()), "Keys must be strings."
    elif kind == AccessType.EID:
        assert all(isinstance(key, (str, int))
                   for key in items.keys()), "Keys must be strings or integers."
    elif kind == AccessType.PATH:
        assert all(isinstance(key, str) for key in items.keys()), "Keys must be strings."
    else:
        raise ValueError(f"Unknown AccessType: {kind}")

    # 1. add the given items to the corresponding dummy dict cache
    _DUMMY_CACHE.update(items)

    # 2. call the cache function with each key (this only results in a dict look up)
    for key in items.keys():
        _cached_access(kind, key, unique=unique)

    # 3. empty the dummy dict cache again
    _DUMMY_CACHE.clear()
