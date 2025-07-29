#!/usr/bin/env python
# encoding: utf-8
#
# This file is a part of the LinkAhead Project.
#
# Copyright (C) 2022 Alexander Schlemmer <alexander.schlemmer@ds.mpg.de>
# Copyright (C) 2022 Timm Fitschen <t.fitschen@indiscale.com>
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
"""This module implements a registration procedure for integration tests which
need a running LinkAhead instance.

It ensures that tests do not accidentally overwrite data in real
LinkAhead instances, as it checks whether the running LinkAhead
instance is actually the correct one, that should be used for these
tests.

The test files have to define a global variable ``TEST_KEY`` which
must be unique for each test using
:py:meth:`~linkahead.utils.register_tests.set_test_key`.

The test procedure (invoked by pytest) checks whether a registration
information is stored in one of the server properties or otherwise

- offers to register this test in the currently running database ONLY if this is
  empty.
- fails otherwise with a RuntimeError

.. note::

    you probably need to use pytest with the -s option to be able to
    register the test interactively. Otherwise, the server property
    has to be set before server start-up in the server.conf of the
    LinkAhead server.

This module is intended to be used with pytest.

There is a pytest fixture
:py:meth:`~linkahead.utils.register_tests.clear_database` that
performs the above mentioned checks and clears the database in case of
success.

"""

import linkahead as db
from linkahead import administration as admin

TEST_KEY = None


def set_test_key(KEY: str):
    """Set the global ``TEST_KEY`` variable to `KEY`. Afterwards, if
    `KEY` matches the ``_CAOSDB_INTEGRATION_TEST_SUITE_KEY`` server
    environment variable, mehtods like :py:meth:`clear_database` can
    be used. Call this function in the beginning of your test file.

    Parameters
    ----------
    KEY : str
        key with which the test using this function is registered and
        which is checked against the
        ``_CAOSDB_INTEGRATION_TEST_SUITE_KEY`` server environment
        variable.

    """
    global TEST_KEY
    TEST_KEY = KEY


def _register_test():
    res = db.execute_query("COUNT Entity")
    if not isinstance(res, int):
        raise RuntimeError("Response from server for Info could not be interpreted.")
    if res > 0:
        raise RuntimeError("This instance of LinkAhead contains entities already."
                           "It must be empty in order to register a new test.")

    print("Current host of LinkAhead instance is: {}".format(
        db.connection.connection.get_connection()._delegate_connection.setup_fields["host"]))
    answer = input("This method will register your current test with key {} with the currently"
                   " running instance of LinkAhead. Do you want to continue (y/N)?".format(
                       TEST_KEY))
    if answer != "y":
        raise RuntimeError("Test registration aborted by user.")

    admin.set_server_property("_CAOSDB_INTEGRATION_TEST_SUITE_KEY",
                              TEST_KEY)


def _get_registered_test_key():
    try:
        return admin.get_server_property("_CAOSDB_INTEGRATION_TEST_SUITE_KEY")
    except KeyError:
        return None


def _is_registered():
    registered_test_key = _get_registered_test_key()
    if not registered_test_key:
        return False
    elif registered_test_key == TEST_KEY:
        return True
    else:
        raise RuntimeError("The database has been setup for a different test.")


def _assure_test_is_registered():
    global TEST_KEY
    if TEST_KEY is None:
        raise RuntimeError("TEST_KEY is not defined.")
    if not _is_registered():
        answer = input("Do you want to register this instance of LinkAhead"
                       " with the current test? Do you want to continue (y/N)?")
        if answer == "y":
            _register_test()
            raise RuntimeError("Test has been registered. Please rerun tests.")
        else:
            raise RuntimeError("The database has not been setup for this test.")


def _clear_database():
    c = db.execute_query("FIND ENTITY WITH ID>99")
    c.delete(raise_exception_on_error=False)
    return None


try:
    import pytest

    @pytest.fixture
    def clear_database():
        """Remove Records, RecordTypes, Properties, and Files ONLY IF
        the LinkAhead server the current connection points to was
        registered with the appropriate key using
        :py:meth:`set_test_key`.

        PyTestInfo Records and the corresponding RecordType and
        Property are preserved.

        """
        _assure_test_is_registered()
        yield _clear_database()  # called before the test function
        _clear_database()  # called after the test function
except ImportError:
    raise Warning("""The register_tests module depends on pytest and is
                  intended to be used in integration test suites for the
                  linkahead-pylib library only.""")
