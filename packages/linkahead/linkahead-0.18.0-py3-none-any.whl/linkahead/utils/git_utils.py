# -*- coding: utf-8 -*-
#
# This file is a part of the CaosDB Project.
#
# Copyright (C) 2018 Research Group Biomedical Physics,
# Max-Planck-Institute for Dynamics and Self-Organization Göttingen
# Copyright (C) 2020 Timm Fitschen <t.fitschen@indiscale.com>
# Copyright (C) 2020-2022 IndiScale GmbH <info@indiscale.com>
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
"""git-utils: Some functions for retrieving information about git repositories.

"""

import logging
import tempfile

from subprocess import call

logger = logging.getLogger(__name__)


def get_origin_url_in(folder: str):
    """return the Fetch URL of the git repository in the given folder."""
    with tempfile.NamedTemporaryFile(delete=False, mode="w", encoding="utf8") as tempf:
        call(["git", "remote", "show", "origin"], stdout=tempf, cwd=folder)
    with open(tempf.name, "r", encoding="utf8") as t:
        urlString = "Fetch URL:"

        for line in t.readlines():
            if urlString in line:
                return line[line.find(urlString) + len(urlString):].strip()

    return None


def get_diff_in(folder: str, save_dir=None):
    """returns the name of a file where the out put of "git diff" in the given
    folder is stored."""
    with tempfile.NamedTemporaryFile(delete=False, mode="w", dir=save_dir) as t:
        call(["git", "diff"], stdout=t, cwd=folder)

    return t.name


def get_branch_in(folder: str):
    """returns the current branch of the git repository in the given folder.

    The command "git branch" is called in the given folder and the
    output is returned
    """
    with tempfile.NamedTemporaryFile(delete=False, mode="w") as tempf:
        call(["git", "rev-parse", "--abbrev-ref", "HEAD"], stdout=tempf, cwd=folder)
    with open(tempf.name, "r") as t:
        return t.readline().strip()


def get_commit_in(folder: str):
    """returns the commit hash in of the git repository in the given folder.

    The command "git log -1 --format=%h" is called in the given folder
    and the output is returned
    """

    with tempfile.NamedTemporaryFile(delete=False, mode="w") as tempf:
        call(["git", "log", "-1", "--format=%h"], stdout=tempf, cwd=folder)
    with open(tempf.name, "r") as t:
        return t.readline().strip()
