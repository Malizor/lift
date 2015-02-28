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
import re
from collections import OrderedDict

import yaml

from lift.localtest import LocalTest
from lift.remotetest import RemoteTest
from lift.exception import InvalidDescriptionFile


# Tune the yaml module to use an OrderedDict (keep tests ordering)
def dict_representer(dumper, data):
    return dumper.represent_mapping(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
                                    data.iteritems())

def dict_constructor(loader, node):
    return OrderedDict(loader.construct_pairs(node))

yaml.add_representer(OrderedDict, dict_representer)
yaml.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
                     dict_constructor)

def load_upper_inheritance(directory_path):
    """Look for and load remotes/environment from upper level lift.yaml files

    Returns remotes and environment to inherit from in directory_path.
    """
    remotes = {}
    environment = {}

    # First, find the higher level lift.yaml file
    browsed = []

    directory = os.path.realpath(directory_path)
    parent_directory = os.path.realpath(os.path.join(directory, '..'))
    while directory != parent_directory:  # not in root dir
        upper_file = os.path.join(parent_directory, 'lift.yaml')
        if not os.path.isfile(upper_file):
            break
        browsed.insert(0, upper_file)
        parent_directory = os.path.realpath(os.path.join(parent_directory, '..'))

    # Load configuration from top to bottom
    for lift_file in browsed:
        try:
            _, remotes, environment = load_config_file(lift_file,
                                                       remotes,
                                                       environment)
        except InvalidDescriptionFile as e:
            sys.exit('%s is not a valid description file: %s' % (lift_file, e))

    return remotes, environment

def load_config_file(yaml_path, remotes, environment):
    """Load a test-suite description file

    Parsed remotes and environment are merged with the provided parameters
    (inheritance).
    Returns a list of run-able tests and the new remotes and environment dicts.
    """

    with open(yaml_path) as config_file:
        conf = yaml.load(config_file)

    # Handle empty files
    if conf is None:
        conf = {}

    tests = []  # list of all tests
    # load settings
    if 'settings' in conf:
        for item in conf['settings']:
            match = re.match('^define ([a-zA-Z0-9_\-\.]+)$', item)
            if match:
                name = match.group(1)
                if name in ('test', 'define', 'complex', 'settings'):
                    raise InvalidDescriptionFile('Hosts definition: "%s" '
                                                 'is a reserved word' % name)


                remotes[name] = conf['settings'][item]
                # Does the host definition contain all needed fields?
                if not remotes[name].get('host', None):
                    raise InvalidDescriptionFile('Missing host in "%s" definition'
                                                 % name)
                if not remotes[name].get('username', None):
                    raise InvalidDescriptionFile('Missing username in "%s" definition'
                                                 % name)
                # 'password' is optional, do not look for it

            elif item == 'environment':
                environment.update(conf['settings']['environment'])
            else:
                raise InvalidDescriptionFile('Unknown section in settings: %s'
                                             % item)

    for section in conf:
        if section == 'settings':
            # Already handled
            continue

        # local test
        match = re.match('^test ([a-zA-Z0-9_\-\.]+)$', section)
        if match:
            # validate items
            for item in conf[section]:
                if item not in ('command', 'return code', 'timeout', 'environment'):
                    raise InvalidDescriptionFile('Unknown section in "%s": %s'
                                                 % (section, item))

            test_name = match.group(1)
            for test in tests:
                if test.name == test_name:
                    raise InvalidDescriptionFile('Duplicated test: %s' % test_name)

            if 'command' not in conf[section]:
                raise InvalidDescriptionFile('No command defined for "%s".' % section)

            # Create the test object
            test = LocalTest(test_name,
                             conf[section]['command'],
                             directory=os.path.dirname(yaml_path),
                             expected_return_code=conf[section].get('return code', 0),
                             timeout=conf[section].get('timeout', 0),
                             environment=environment.copy())
            # Set the test environment
            test.environment.update(conf[section].get('environment', {}))

            # Add it to the queue
            tests.append(test)
            continue

        # Remote test
        match = re.match('^([a-zA-Z0-9_\-\.]+) test ([a-zA-Z0-9_\-\.]+)$', section)
        if match:

            remote = match.group(1)
            if remote not in remotes:
                raise InvalidDescriptionFile('Unknown remote: %s' % remote)

            # validate items
            for item in conf[section]:
                if item not in ('command', 'return code', 'timeout', 'resources', 'environment'):
                    raise InvalidDescriptionFile('Unknown section in %s: %s'
                                                 % (section, item))

            test_name = match.group(2)
            for test in tests:
                if test.name == test_name:
                    raise InvalidDescriptionFile('Duplicated test: %s' % test_name)

            if 'command' not in conf[section]:
                raise InvalidDescriptionFile('No command defined for "%s".' % section)

            # Create the test object
            test = RemoteTest(test_name,
                              conf[section]['command'],
                              remotes[remote],
                              resources=conf[section].get('resources', []),
                              directory=os.path.dirname(yaml_path),
                              expected_return_code=conf[section].get('return code', 0),
                              timeout=conf[section].get('timeout', 0),
                              environment=environment.copy())
            # Set the test environment
            test.environment.update(conf[section].get('environment', {}))

            # Add it to the queue
            tests.append(test)
            continue

        else:
            raise InvalidDescriptionFile('Unknown section: %s' % section)

    return tests, remotes, environment
