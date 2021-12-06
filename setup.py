#!/usr/bin/python3

# LIFT Integration-Functional Testing - A meta test framework
# Copyright © 2014-2021 Cognacq-Jay Image and Nicolas Delvaux
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
from distutils.command.build import build
from distutils.command.clean import clean
from setuptools import setup, find_packages

import lift


data_files = []
MANPAGES_MAPPING = {
    "doc/lift.1": "doc/lift.rst",
    "doc/lift.yaml.1": "doc/lift.yaml.rst",
}


class MyBuild(build):
    """Customized build command - build manpages."""

    def run(self):
        try:
            for page in MANPAGES_MAPPING:
                if not os.path.isfile(page) or os.path.getmtime(
                    page
                ) < os.path.getmtime(MANPAGES_MAPPING[page]):
                    subprocess.call(["rst2man", MANPAGES_MAPPING[page], page])
                data_files.append(
                    ("/usr/share/man/man1/", list(MANPAGES_MAPPING.keys()))
                )
        except FileNotFoundError:
            print("Warning: rst2man was not found, skipping the manpage generation.")
        build.run(self)


class MyClean(clean):
    """Customized clean command - remove built manpages."""

    def run(self):
        for page in MANPAGES_MAPPING:
            if os.path.isfile(page):
                os.remove(page)
        clean.run(self)


LDESC = open(
    os.path.join(os.path.dirname(__file__), "README.md"), encoding="utf8"
).read()

setup(
    name="lift",
    version=lift.version,
    description="High level test framework",
    long_description=LDESC,
    author="Nicolas Delvaux",
    author_email="contact@nicolas-delvaux.org",
    url="https://github.com/Malizor/lift",
    download_url="https://github.com/Malizor/lift/tarball/%s" % lift.version,
    license="GPL2+",
    packages=find_packages(exclude=("tests",)),
    scripts=["bin/lift"],
    test_suite="tests",
    data_files=data_files,
    cmdclass={"build": MyBuild, "clean": MyClean},
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
