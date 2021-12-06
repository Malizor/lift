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
import re
import sys
from collections import OrderedDict

import yaml

from lift.localtest import LocalTest
from lift.remotetest import RemoteTest
from lift.exception import InvalidDescriptionFile


# Tune the yaml module to use an OrderedDict (keep tests ordering)
def ordered_load(stream):
    class OrderedSafeLoader(yaml.SafeLoader):
        pass

    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return OrderedDict(loader.construct_pairs(node))

    OrderedSafeLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, construct_mapping
    )
    return yaml.load(stream, OrderedSafeLoader)


def string_to_remote(string):
    """Return the name and the remote dictionary matching the input string.

    The input should be in the following form:
    REMOTENAME=USERNAME:PASSWORD@HOST

    Note that the PASSWORD field (along with the ':' separator) is optional.
    Return None if the input is not valid.
    """
    if "=" not in string:
        return None
    name, rstring = string.split("=", 1)
    if not name or "@" not in rstring:
        return None
    remote = {}
    lstring, remote["host"] = rstring.rsplit("@", 1)
    if not lstring or not remote["host"]:
        return None

    if ":" in lstring:
        remote["username"], remote["password"] = lstring.split(":", 1)
    else:
        remote["username"] = lstring

    if not remote["username"]:
        return None

    return name, remote


def remote_to_string(remote):
    """Return a string matching the input remote dictionary

    The input should be in the following form:
    {'host': 'HOST', 'username': 'USERNAME', 'password': 'PASSWORD'}
    Note that the PASSWORD item is optional.

    The output will be in the following form:
    USERNAME:PASSWORD@HOST
    The ':PASSWORD' part is optional.

    Return None if the input is not valid.
    """
    if "host" not in remote or "username" not in remote:
        return None
    if "password" in remote:
        return "%s:%s@%s" % (remote["username"], remote["password"], remote["host"])
    else:
        return "%s@%s" % (remote["username"], remote["host"])


def load_upper_inheritance(directory_path, preset_remotes):
    """Look for and load remotes/environment from upper level lift.yaml files

    @preset_remotes is a dict of remotes that should be set but not overridden.
    Returns remotes and environment to inherit from in directory_path.
    """

    remotes = {}
    environment = {}

    # First, find the higher level lift.yaml file
    browsed = []

    directory = os.path.realpath(directory_path)
    parent_directory = os.path.realpath(os.path.join(directory, ".."))
    while directory != parent_directory:  # not in root dir
        upper_file = os.path.join(parent_directory, "lift.yaml")
        if not os.path.isfile(upper_file):
            break
        browsed.insert(0, upper_file)
        parent_directory = os.path.realpath(os.path.join(parent_directory, ".."))

    # Load configuration from top to bottom
    for lift_file in browsed:
        try:
            _, remotes, environment = load_config_file(
                lift_file, remotes, environment, preset_remotes
            )
        except InvalidDescriptionFile as e:
            sys.exit("%s is not a valid description file: %s" % (lift_file, e))

    return remotes, environment


def load_config_file(
    yaml_path, remotes, environment, preset_remotes, remotes_in_env=False
):
    """Load a test-suite description file

    Parsed remotes and environment are merged with the provided parameters
    (inheritance).
    @preset_remotes is a dict of remotes that should be set but not overridden.
    Returns a list of run-able tests and the new remotes and environment dicts.
    """
    remotes.update(preset_remotes)

    with open(yaml_path) as config_file:
        conf = ordered_load(config_file)

    # Handle empty files
    if conf is None:
        conf = {}

    tests = []  # list of all tests
    # load settings
    if "settings" in conf:
        for item in conf["settings"]:
            match = re.match("^define ([a-zA-Z0-9_\-\.]+)$", item)
            if match:
                name = match.group(1)
                if name in ("test", "define", "complex", "settings"):
                    raise InvalidDescriptionFile(
                        'Hosts definition: "%s" ' "is a reserved word" % name
                    )

                remotes[name] = conf["settings"][item]
                # Does the host definition contain all needed fields?
                if not remotes[name].get("host", None):
                    raise InvalidDescriptionFile(
                        'Missing host in "%s" definition' % name
                    )
                if not remotes[name].get("username", None):
                    raise InvalidDescriptionFile(
                        'Missing username in "%s" definition' % name
                    )
                # 'password' is optional, do not look for it

            elif item == "environment":
                environment.update(conf["settings"]["environment"])
            else:
                raise InvalidDescriptionFile("Unknown section in settings: %s" % item)

    remotes.update(preset_remotes)  # if a preset remote was overridden

    for section in conf:
        if section == "settings":
            # Already handled
            continue

        # local test
        match = re.match("^test ([a-zA-Z0-9_\-\.]+)$", section)
        if match:
            # validate items
            for item in conf[section]:
                if item not in ("command", "return code", "timeout", "environment"):
                    raise InvalidDescriptionFile(
                        'Unknown section in "%s": %s' % (section, item)
                    )

            test_name = match.group(1)
            for test in tests:
                if test.name == test_name:
                    raise InvalidDescriptionFile("Duplicated test: %s" % test_name)

            if "command" not in conf[section]:
                raise InvalidDescriptionFile('No command defined for "%s".' % section)

            # Create the test object
            test = LocalTest(
                test_name,
                conf[section]["command"],
                directory=os.path.dirname(yaml_path),
                expected_return_code=conf[section].get("return code", 0),
                timeout=conf[section].get("timeout", 0),
                environment=environment.copy(),
            )
            # Set the test environment
            test.environment.update(conf[section].get("environment", {}))

            if remotes_in_env:
                remotes_env = {}
                for remote in remotes:
                    remotes_env["LIFT_REMOTE_%s" % remote] = remote_to_string(
                        remotes[remote]
                    )
                test.environment.update(remotes_env)

            # Add it to the queue
            tests.append(test)
            continue

        # Remote test
        match = re.match("^([a-zA-Z0-9_\-\.]+) test ([a-zA-Z0-9_\-\.]+)$", section)
        if match:

            remote = match.group(1)
            if remote not in remotes:
                raise InvalidDescriptionFile("Unknown remote: %s" % remote)

            # validate items
            for item in conf[section]:
                if item not in (
                    "command",
                    "return code",
                    "timeout",
                    "resources",
                    "environment",
                ):
                    raise InvalidDescriptionFile(
                        "Unknown section in %s: %s" % (section, item)
                    )

            test_name = match.group(2)
            for test in tests:
                if test.name == test_name:
                    raise InvalidDescriptionFile("Duplicated test: %s" % test_name)

            if "command" not in conf[section]:
                raise InvalidDescriptionFile('No command defined for "%s".' % section)

            # Create the test object
            test = RemoteTest(
                test_name,
                conf[section]["command"],
                remotes[remote],
                resources=conf[section].get("resources", []),
                directory=os.path.dirname(yaml_path),
                expected_return_code=conf[section].get("return code", 0),
                timeout=conf[section].get("timeout", 0),
                environment=environment.copy(),
            )
            # Set the test environment
            test.environment.update(conf[section].get("environment", {}))

            if remotes_in_env:
                remotes_env = {}
                for remote in remotes:
                    remotes_env["LIFT_REMOTE_%s" % remote] = remote_to_string(
                        remotes[remote]
                    )
                test.environment.update(remotes_env)

            # Add it to the queue
            tests.append(test)
            continue

        else:
            raise InvalidDescriptionFile("Unknown section: %s" % section)

    return tests, remotes, environment
