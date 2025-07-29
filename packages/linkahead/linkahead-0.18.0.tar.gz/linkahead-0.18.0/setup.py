#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
#
"""linkahead"""
import os
import re
import subprocess
import sys

from setuptools import find_packages, setup

########################################################################
# The following code is largely based on code in numpy
########################################################################
#
# Copyright (c) 2005-2019, NumPy Developers.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#    * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#
#    * Redistributions in binary form must reproduce the above
#       copyright notice, this list of conditions and the following
#       disclaimer in the documentation and/or other materials provided
#       with the distribution.
#
#    * Neither the name of the NumPy Developers nor the names of any
#       contributors may be used to endorse or promote products derived
#       from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
########################################################################

ISRELEASED = True
MAJOR = 0
MINOR = 18
MICRO = 0
# Do not tag as pre-release until this commit
# https://github.com/pypa/packaging/pull/515
# has made it into a release. Probably we should wait for pypa/packaging>=21.4
# https://github.com/pypa/packaging/releases
PRE = ""  # "dev"  # e.g. rc0, alpha.1, 0.beta-23

if PRE:
    VERSION = "{}.{}.{}-{}".format(MAJOR, MINOR, MICRO, PRE)
else:
    VERSION = "{}.{}.{}".format(MAJOR, MINOR, MICRO)


# Return the git revision as a string
def git_version():
    def _minimal_ext_cmd(cmd):
        # construct minimal environment
        env = {}

        for k in ['SYSTEMROOT', 'PATH', 'HOME']:
            v = os.environ.get(k)

            if v is not None:
                env[k] = v
        # LANGUAGE is used on win32
        env['LANGUAGE'] = 'C'
        env['LANG'] = 'C'
        env['LC_ALL'] = 'C'
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, env=env)

        return out

    try:
        out = _minimal_ext_cmd(['git', 'rev-parse', 'HEAD'])
        GIT_REVISION = out.strip().decode('ascii')
    except (subprocess.SubprocessError, OSError):
        GIT_REVISION = "Unknown"

    return GIT_REVISION


def get_version_info():
    # Adding the git rev number needs to be done inside write_version_py(),
    # otherwise the import of linkahead.version messes up the build under
    # Python 3.
    FULLVERSION = VERSION

    # Magic which is only really needed in the pipelines. Therefore: a lot of dark pipeline magic.
    GIT_REVISION = "Unknown"
    if os.path.exists('.git'):
        GIT_REVISION = git_version()
    elif os.path.exists('linkahead_pylib_commit'):
        with open('linkahead_pylib_commit', 'r') as f:
            GIT_REVISION = f.read().strip()
    elif os.path.exists('src/linkahead/version.py'):
        # must be a source distribution, use existing version file
        with open('src/linkahead/version.py') as fi:
            rev_pattern = re.compile(r"^git_revision = '(?P<rev>.*)'$")
            for line in fi.readlines():
                match = rev_pattern.match(line)
                if match is not None:
                    GIT_REVISION = match.group('rev')
                    break

    if not ISRELEASED:
        FULLVERSION += '.dev0+' + GIT_REVISION[:7]

    return FULLVERSION, GIT_REVISION


def write_version_py(filename='src/linkahead/version.py'):
    cnt = """
# THIS FILE IS GENERATED FROM linkahead SETUP.PY
#
short_version = '%(version)s'
version = '%(version)s'
full_version = '%(full_version)s'
git_revision = '%(git_revision)s'
release = %(isrelease)s

if not release:
    version = full_version
"""
    FULLVERSION, GIT_REVISION = get_version_info()

    a = open(filename, 'w')
    try:
        a.write(cnt % {'version': VERSION,
                       'full_version': FULLVERSION,
                       'git_revision': GIT_REVISION,
                       'isrelease': str(ISRELEASED)})
    finally:
        a.close()


def setup_package():
    # load README
    with open("README.md", "r") as fh:
        long_description = fh.read()

    src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
    sys.path.insert(0, src_path)

    # Rewrite the version file everytime
    write_version_py()

    if 'PKGNAME' in os.environ and os.environ['PKGNAME'] == 'caosdb':
        pname = 'caosdb'
        pdesc = 'Deprecated! Please install linkahead.'
    else:
        pname = 'linkahead'
        pdesc = 'Python Interface for LinkAhead'
    metadata = dict(
        name=pname,
        version=get_version_info()[0],
        description=pdesc,
        long_description=long_description,
        long_description_content_type="text/markdown",
        author='Timm Fitschen',
        author_email='t.fitschen@indiscale.com',
        url='https://www.linkahead.org',
        license="AGPLv3+",
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
            "Operating System :: OS Independent",
            "Topic :: Database",
            "Topic :: Scientific/Engineering :: Information Analysis",
        ],
        packages=find_packages('src'),
        python_requires='>=3.9',
        package_dir={'': 'src'},
        install_requires=['lxml>=4.6.3',
                          "requests[socks]>=2.26",
                          "python-dateutil>=2.8.2",
                          'PyYAML>=5.4.1',
                          'future',
                          ],
        extras_require={
            "jsonschema": ["jsonschema>=4.4.0"],
            "keyring": ["keyring>=13.0.0"],
            "mypy": [
                "mypy",
                "types-PyYAML",
                "types-jsonschema",
                "types-requests",
                "types-setuptools",
                "types-lxml",
                "types-python-dateutil",
            ],
            "test": [
                "pytest",
                "pytest-cov",
                "coverage>=4.4.2",
                "jsonschema>=4.4.0",
            ]

        },
        setup_requires=["pytest-runner>=2.0,<3dev"],
        package_data={
            'linkahead': ['py.typed', 'cert/indiscale.ca.crt', 'schema-pycaosdb-ini.yml'],
        },
        scripts=[
            "src/linkahead/utils/caosdb_admin.py",
            "src/linkahead/utils/linkahead_admin.py"
        ]
    )
    try:
        setup(**metadata)
    finally:
        del sys.path[0]
    return


if __name__ == '__main__':
    setup_package()
