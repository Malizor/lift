#!/usr/bin/python3

# LIFT Integration-Functional Testing - A meta test framework
# Copyright © 2014-2022 Cognacq-Jay Image and Nicolas Delvaux
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301,
# USA.

import os
import subprocess
from setuptools import setup, find_packages

import lift


LDESC = open(
    os.path.join(os.path.dirname(__file__), "README.md"), encoding="utf8"
).read()

setup(
    name="lift",
    version=lift.version,
    description="High level test framework",
    long_description=LDESC,
    long_description_content_type='text/markdown',
    author="Nicolas Delvaux",
    author_email="contact@nicolas-delvaux.org",
    url="https://github.com/Malizor/lift",
    download_url="https://github.com/Malizor/lift/tarball/%s" % lift.version,
    license="GPL2+",
    packages=find_packages(exclude=("tests",)),
    scripts=["bin/lift"],
    test_suite="tests",
    setup_requires=["docutils"],
    install_requires=["paramiko", "pyyaml", "junit-xml"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Operating System :: Unix",
        "Programming Language :: Python :: 3",
        "Environment :: Console",
    ],
    keywords="test testing",
)
