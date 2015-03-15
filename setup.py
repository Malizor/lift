#!/usr/bin/python
# -*- coding: utf-8 -*-

# LIFT Integration-Functional Testing - A meta test framework
# Copyright © 2014 SmartJog S.A
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
from setuptools import setup, find_packages

import lift


data_files = []


class MyBuild(build):
    """Customized build command - build manpages."""
    def run(self):
        try:
            print('Generating the manpage...')
            subprocess.call(['rst2man', 'doc/lift.rst', 'doc/lift.1'])
            data_files.append(('/usr/share/man/man1/', ['doc/lift.1']))
        except OSError:
            print('Warning: rst2man was not found, skipping the manpage generation.')
        build.run(self)

ldesc = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()

setup(
    name='lift',
    version=lift.version,
    description='High level test framework',
    long_description=ldesc,
    author='Nicolas Delvaux',
    author_email='nicolas.delvaux@arkena.com',
    license='GPL2+',
    packages=find_packages(),
    scripts=['bin/lift'],
    test_suite='tests',
    data_files=data_files,
    cmdclass={'build': MyBuild},
    classifiers=[
        'Operating System :: Unix',
        'Programming Language :: Python',
    ],
    setup_requires=['docutils'],
    install_requires=['paramiko', 'pyyaml'],
)
