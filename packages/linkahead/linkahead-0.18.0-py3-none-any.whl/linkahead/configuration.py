# -*- coding: utf-8 -*-
#
# ** header v3.0
# This file is a part of the LinkAhead Project.
#
# Copyright (C) 2018 Research Group Biomedical Physics,
# Max-Planck-Institute for Dynamics and Self-Organization Göttingen
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
from __future__ import annotations
import os
import warnings

import yaml

try:
    optional_jsonschema_validate: Optional[Callable] = None
    from jsonschema import validate as optional_jsonschema_validate

    # Adapted from https://github.com/python-jsonschema/jsonschema/issues/148
    # Defines Validator to allow parsing of all iterables as array in jsonschema
    # CustomValidator can be removed if/once jsonschema allows tuples for arrays
    from collections.abc import Iterable
    from jsonschema import validators
    default = validators.validator_for(True)   # Returns latest supported draft
    t_c = (default.TYPE_CHECKER.redefine('array', lambda x, y: isinstance(y, Iterable)))
    CustomValidator = validators.extend(default, type_checker=t_c)
except ImportError:
    pass

from configparser import ConfigParser
from os import environ, getcwd
from os.path import expanduser, isfile, join

from typing import Union, Callable, Optional

_pycaosdbconf = ConfigParser(allow_no_value=False)


def _reset_config():
    global _pycaosdbconf
    _pycaosdbconf = ConfigParser(allow_no_value=False)


def configure(inifile: str) -> list[str]:
    """read config from file.

    Return a list of files which have successfully been parsed.
    """
    global _pycaosdbconf
    if ("_pycaosdbconf" not in globals() or _pycaosdbconf is None):
        _reset_config()
    read_config = _pycaosdbconf.read(inifile)
    validate_yaml_schema(config_to_yaml(_pycaosdbconf))

    if "HTTPS_PROXY" in environ:
        _pycaosdbconf["Connection"]["https_proxy"] = environ["HTTPS_PROXY"]
    if "HTTP_PROXY" in environ:
        _pycaosdbconf["Connection"]["http_proxy"] = environ["HTTP_PROXY"]
    return read_config


def get_config() -> ConfigParser:
    global _pycaosdbconf
    if ("_pycaosdbconf" not in globals() or _pycaosdbconf is None):
        _reset_config()
    return _pycaosdbconf


def config_to_yaml(config: ConfigParser) -> dict[str, dict[str, Union[int, str, bool, tuple, None]]]:
    """
    Generates and returns a dict with all config options and their values
    defined in the config.
    The values of the options 'debug', 'timeout', and 'ssl_insecure' are
    parsed, all other values are saved as string.

    Parameters
    ----------
    config : ConfigParser
        The config to be converted to a dict

    Returns
    -------
    valobj : dict
        A dict with config options and their values as key value pairs
    """
    valobj: dict[str, dict[str, Union[int, str, bool, tuple, None]]] = {}
    for s in config.sections():
        valobj[s] = {}
        for key, value in config[s].items():
            # TODO: Can the type be inferred from the config object?
            if key in ["debug"]:
                valobj[s][key] = int(value)
            elif key in ["timeout"]:
                value = "".join(value.split())          # Remove whitespace
                if str(value).lower() in ["none", "null"]:
                    valobj[s][key] = None
                elif value.startswith('(') and value.endswith(')'):
                    content = [None if str(s).lower() in ["none", "null"] else int(s)
                               for s in value[1:-1].split(',')]
                    valobj[s][key] = tuple(content)
                else:
                    valobj[s][key] = int(value)
            elif key in ["ssl_insecure"]:
                valobj[s][key] = bool(value)
            else:
                valobj[s][key] = value

    return valobj


def validate_yaml_schema(valobj: dict[str, dict[str, Union[int, str, bool, tuple, None]]]):
    if optional_jsonschema_validate:
        with open(os.path.join(os.path.dirname(__file__), "schema-pycaosdb-ini.yml")) as f:
            schema = yaml.load(f, Loader=yaml.SafeLoader)
        optional_jsonschema_validate(instance=valobj, schema=schema["schema-pycaosdb-ini"],
                                     cls=CustomValidator)
    else:
        warnings.warn("""
            Warning: The validation could not be performed because `jsonschema` is not installed.
        """)


def _read_config_files() -> list[str]:
    """Read config files from different paths.

    Read the config from either ``$PYLINKAHEADINI`` or home directory (``~/.pylinkahead.ini``), and
    additionally adds config from a config file in the current working directory
    (``pylinkahead.ini``).
    If deprecated names are used (starting with 'pycaosdb'), those used in addition but the files
    with the new naming scheme take precedence.
    All of these files are optional.

    Returns
    -------

    ini files: list
      The successfully parsed ini-files. Order: environment variable or home directory, then cwd.
      Used for testing the function.

    """
    return_var = []
    ini_user = expanduser('~/.pylinkahead.ini')
    ini_cwd = join(getcwd(), "pylinkahead.ini")
    # LinkAhead rename block ##################################################
    ini_user_caosdb = expanduser('~/.pycaosdb.ini')
    ini_cwd_caosdb = join(getcwd(), "pycaosdb.ini")
    if os.path.exists(ini_user_caosdb):
        warnings.warn("\n\nYou have a config file with the old naming scheme (pycaosdb.ini). "
                      f"Please use the new version and rename\n"
                      f"    {ini_user_caosdb}\nto\n    {ini_user}", DeprecationWarning)
    if os.path.exists(ini_cwd_caosdb):
        warnings.warn("\n\nYou have a config file with the old naming scheme (pycaosdb.ini). "
                      f"Please use the new version and rename\n"
                      f"    {ini_cwd_caosdb}\nto\n    {ini_cwd}", DeprecationWarning)
    if "PYCAOSDBINI" in environ:
        warnings.warn("\n\nYou have an environment variable PYCAOSDBINI. "
                      "Please rename it to PYLINKAHEADINI.")
    # End: LinkAhead rename block ##################################################

    if "PYLINKAHEADINI" in environ:
        if not isfile(expanduser(environ["PYLINKAHEADINI"])):
            raise RuntimeError(
                f"No configuration file found at\n{expanduser(environ['PYLINKAHEADINI'])}"
                "\nwhich was given via the environment variable PYLINKAHEADINI"
            )
        return_var.extend(configure(expanduser(environ["PYLINKAHEADINI"])))
    else:
        if isfile(ini_user_caosdb):
            return_var.extend(configure(ini_user_caosdb))
        if isfile(ini_user):
            return_var.extend(configure(ini_user))
    if isfile(ini_cwd):
        return_var.extend(configure(ini_cwd))
    if isfile(ini_cwd_caosdb):
        return_var.extend(configure(ini_cwd_caosdb))
    return return_var
