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

"""Tests for lift.loader functions"""

import os
import unittest
from collections import OrderedDict

from lift.localtest import LocalTest
from lift.remotetest import RemoteTest
from lift.exception import InvalidDescriptionFile
from lift.loader import (load_upper_inheritance,
                         load_config_file,
                         string_to_remote,
                         remote_to_string)


class LoadUpperInheritanceTestCase(unittest.TestCase):
    """Test the lift.loader.load_upper_inheritance function

    These tests use the tests_resources folder and compare its known content
    with what the lift functions parse.
    """

    def test_no_upper_inheritance(self):
        """No setting should be inheritable in the top-level directory"""

        directory = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                 'tests_resources', 'valid')
        self.assertTrue(os.path.isdir(directory), '%s does not exist!' % directory)

        remotes, environment = load_upper_inheritance(directory, {})
        self.assertEqual(remotes, {},
                         'Remotes: inherited %s instead of nothing'
                         % str(remotes))
        self.assertEqual(environment, {},
                         'Environment: inherited %s instead of nothing'
                         % str(environment))

    def test_upper_inheritance(self):
        """Check the upper settings inheritance with 1 depth level"""
        directory = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                 'tests_resources', 'valid', 'sub_test')
        self.assertTrue(os.path.isdir(directory), '%s does not exist!' % directory)

        expected_remotes = {'my_remote':
                            OrderedDict([('host', 'example.com'),
                                         ('username', 'root'),
                                         ('password', 'foobar')])}
        expected_environment = {'MY_ENV_VAR2': 'bar', 'MY_ENV_VAR1': 'foo'}
        remotes, environment = load_upper_inheritance(directory, {})
        self.assertEqual(remotes, expected_remotes,
                         'Remotes: inherited %s instead of %s'
                         % (str(remotes), str(expected_remotes)))
        self.assertEqual(environment, expected_environment,
                         'Environment: inherited %s instead of %s'
                         % (str(environment), str(expected_environment)))

    def test_upper_inheritance_with_preset(self):
        """Check the upper settings inheritance with preset remotes"""
        directory = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                 'tests_resources', 'valid', 'sub_test')
        self.assertTrue(os.path.isdir(directory), '%s does not exist!' % directory)

        # Here preset fully override what is defined in lift.yaml
        preset_remotes = {'my_remote': {'host': 'foo',
                                        'bar': 'foobar',
                                        'username': 'root'},
                          'my_other_remote': {'host': 'foo',
                                              'bar': 'foobar',
                                              'username': 'root'}}

        expected_environment = {'MY_ENV_VAR2': 'bar', 'MY_ENV_VAR1': 'foo'}
        remotes, environment = load_upper_inheritance(directory, preset_remotes)
        self.assertEqual(remotes, preset_remotes,
                         'Remotes: inherited %s instead of %s'
                         % (str(remotes), str(preset_remotes)))
        self.assertEqual(environment, expected_environment,
                         'Environment: inherited %s instead of %s'
                         % (str(environment), str(expected_environment)))

    def test_upper_upper_inheritance(self):
        """Check the upper settings inheritance with 2 depth levels

        Test overriding/merging of upper level settings.
        """
        directory = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                 'tests_resources', 'valid',
                                 'sub_test', 'sub_sub_test')
        self.assertTrue(os.path.isdir(directory), '%s does not exist!' % directory)

        expected_remotes = {'my_remote':
                            OrderedDict([('host', 'example.com'),
                                         ('username', 'root'),
                                         ('password', 'foobar2')])}
        expected_environment = {'MY_ENV_VAR1': 'foo',
                                'MY_ENV_VAR2': 'not_bar',
                                'MY_ENV_VAR3': 'foobar'}
        remotes, environment = load_upper_inheritance(directory, {})
        self.assertEqual(remotes, expected_remotes,
                         'Remotes: inherited %s instead of %s'
                         % (str(remotes), str(expected_remotes)))
        self.assertEqual(environment, expected_environment,
                         'Environment: inherited %s instead of %s'
                         % (str(environment), str(expected_environment)))


class LoadConfigFileTestCase(unittest.TestCase):
    """Test the lift.loader.load_config_file function

    These tests use the tests_resources folder and compare its known content
    with what the lift functions parse.
    """

    def test_unknown_section(self):
        """Check that a proper exception is raised"""
        path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                            'tests_resources', 'not_valid', '1-lift.yaml')

        self.assertTrue(os.path.isfile(path), '%s does not exist!' % path)
        with self.assertRaisesRegexp(InvalidDescriptionFile, 'Unknown section'):
            load_config_file(path, {}, {}, {})

    def test_no_command(self):
        """Check that a proper exception is raised"""
        path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                            'tests_resources', 'not_valid', '2-lift.yaml')

        self.assertTrue(os.path.isfile(path), '%s does not exist!' % path)
        with self.assertRaisesRegexp(InvalidDescriptionFile, 'No command defined'):
            load_config_file(path, {}, {}, {})

    def test_duplicated_test(self):
        """Check that a proper exception is raised"""
        path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                            'tests_resources', 'not_valid', '3-lift.yaml')

        self.assertTrue(os.path.isfile(path), '%s does not exist!' % path)
        with self.assertRaisesRegexp(InvalidDescriptionFile, 'Duplicated test'):
            load_config_file(path, {}, {}, {})

    def test_unknown_remote(self):
        """Check that a proper exception is raised"""
        path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                            'tests_resources', 'not_valid', '4-lift.yaml')

        self.assertTrue(os.path.isfile(path), '%s does not exist!' % path)
        with self.assertRaisesRegexp(InvalidDescriptionFile, 'Unknown remote'):
            load_config_file(path, {}, {}, {})

    def test_load(self):
        """Check a load, without external inheritance"""
        path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                            'tests_resources', 'valid', 'lift.yaml')

        self.assertTrue(os.path.isfile(path), '%s does not exist!' % path)

        expected_remotes = {'my_remote':
                            OrderedDict([('host', 'example.com'),
                                         ('username', 'root'),
                                         ('password', 'foobar')])}

        expected_environment = {'MY_ENV_VAR1': 'foo',
                                'MY_ENV_VAR2': 'bar'}

        expected_tests = [LocalTest('ping', 'sleep 1',
                                    directory=os.path.dirname(path),
                                    expected_return_code=0,
                                    timeout=10,
                                    environment=expected_environment.copy()),
                          RemoteTest('remote_env_with_resource',
                                     'sh test/test.sh',
                                     expected_remotes['my_remote'],
                                     resources=['test/'],
                                     directory=os.path.dirname(path),
                                     expected_return_code=0,
                                     timeout=2,
                                     environment={'MY_ENV_VAR1': 'foo',
                                                  'MY_ENV_VAR2': 'edit_bar',
                                                  'MY_VAR': 'content'})]

        tests, remotes, environment = load_config_file(path, {}, {}, {})

        self.assertEqual(remotes, expected_remotes,
                         'Remotes: inherited %s instead of %s'
                         % (str(remotes), str(expected_remotes)))
        self.assertEqual(environment, expected_environment,
                         'Environment: inherited %s instead of %s'
                         % (str(environment), str(expected_environment)))
        self.assertEqual(tests, expected_tests,
                         'Expected and parsed tests are not the same')

    def test_load_remotes_in_env(self):
        """Check a load with the option to put remotes in tests environment"""
        path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                            'tests_resources', 'valid', 'lift.yaml')

        self.assertTrue(os.path.isfile(path), '%s does not exist!' % path)

        expected_remotes = {'my_remote':
                            OrderedDict([('host', 'example.com'),
                                         ('username', 'root'),
                                         ('password', 'foobar')])}

        expected_environment = {'MY_ENV_VAR1': 'foo',
                                'MY_ENV_VAR2': 'bar'}

        expected_tests = [LocalTest('ping', 'sleep 1',
                                    directory=os.path.dirname(path),
                                    expected_return_code=0,
                                    timeout=10,
                                    environment={'MY_ENV_VAR1': 'foo',
                                                 'MY_ENV_VAR2': 'bar',
                                                 'LIFT_REMOTE_my_remote':
                                                 'root:foobar@example.com'}),
                          RemoteTest('remote_env_with_resource',
                                     'sh test/test.sh',
                                     expected_remotes['my_remote'],
                                     resources=['test/'],
                                     directory=os.path.dirname(path),
                                     expected_return_code=0,
                                     timeout=2,
                                     environment={'MY_ENV_VAR1': 'foo',
                                                  'MY_ENV_VAR2': 'edit_bar',
                                                  'MY_VAR': 'content',
                                                  'LIFT_REMOTE_my_remote':
                                                  'root:foobar@example.com'})]

        tests, remotes, environment = load_config_file(path, {}, {}, {}, True)

        self.assertEqual(remotes, expected_remotes,
                         'Remotes: inherited %s instead of %s'
                         % (str(remotes), str(expected_remotes)))
        self.assertEqual(environment, expected_environment,
                         'Environment: inherited %s instead of %s'
                         % (str(environment), str(expected_environment)))
        self.assertEqual(tests, expected_tests,
                         'Expected and parsed tests are not the same')

    def test_load_with_inheritance(self):
        """Check a load, with external inheritance"""
        path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                            'tests_resources', 'valid', 'lift.yaml')

        self.assertTrue(os.path.isfile(path), '%s does not exist!' % path)

        expected_remotes = {'my_remote':
                            OrderedDict([('host', 'example.com'),
                                         ('username', 'root'),
                                         ('password', 'foobar')]),
                            'my_remote2':
                            OrderedDict([('host', 'example.org'),
                                         ('username', 'root'),
                                         ('password', 'barfoo')])}

        expected_environment = {'MY_ENV_VAR1': 'foo',
                                'MY_ENV_VAR2': 'bar',
                                'MY_ENV_VAR3': 'foobar'}

        expected_tests = [LocalTest('ping', 'sleep 1',
                                    directory=os.path.dirname(path),
                                    expected_return_code=0,
                                    timeout=10,
                                    environment=expected_environment.copy()),
                          RemoteTest('remote_env_with_resource',
                                     'sh test/test.sh',
                                     expected_remotes['my_remote'],
                                     resources=['test/'],
                                     directory=os.path.dirname(path),
                                     expected_return_code=0,
                                     timeout=2,
                                     environment={'MY_ENV_VAR1': 'foo',
                                                  'MY_ENV_VAR2': 'edit_bar',
                                                  'MY_ENV_VAR3': 'foobar',
                                                  'MY_VAR': 'content'})]

        tests, remotes, environment = load_config_file(path,
                                                       {'my_remote2':
                                                        OrderedDict([('host', 'example.org'),
                                                                     ('username', 'root'),
                                                                     ('password', 'barfoo')])},
                                                       {'MY_ENV_VAR3': 'foobar'},
                                                       {})

        self.assertEqual(remotes, expected_remotes,
                         'Remotes: inherited %s instead of %s'
                         % (str(remotes), str(expected_remotes)))
        self.assertEqual(environment, expected_environment,
                         'Environment: inherited %s instead of %s'
                         % (str(environment), str(expected_environment)))
        self.assertEqual(tests, expected_tests,
                         'Expected and parsed tests are not the same')


class RemoteHandlingTestCase(unittest.TestCase):
    """Test the lift.loader remote handling functions"""

    def test_from_string(self):
        """Check with a full string"""
        res = string_to_remote('name=login:pass@127.0.0.1')
        self.assertEqual(res, ('name', {'host': '127.0.0.1',
                                        'username': 'login',
                                        'password': 'pass'}),
                         'The function returned: %s' % str(res))

    def test_from_string_no_pass(self):
        """Check without the optional password"""
        res = string_to_remote('name=login@127.0.0.1')
        self.assertEqual(res, ('name', {'host': '127.0.0.1',
                                        'username': 'login'}),
                         'The function returned: %s' % str(res))

    def test_from_bad_string(self):
        """Check that the function returns None with a non-compliant string"""
        res = string_to_remote('=foobar@')
        self.assertEqual(res, None, 'The function returned: %s' % str(res))

    def test_to_string(self):
        """Check with a full remote"""
        res = remote_to_string({'host': '127.0.0.1',
                                'username': 'login',
                                'password': 'pass'})
        self.assertEqual(res, 'login:pass@127.0.0.1',
                         'The function returned: %s' % res)

    def test_to_string_no_pass(self):
        """Check without the optional password"""
        res = remote_to_string({'host': '127.0.0.1',
                                'username': 'login'})
        self.assertEqual(res, 'login@127.0.0.1',
                         'The function returned: %s' % res)

    def test_to_string_bad_input(self):
        """Check that the function returns None with a non-compliant input"""
        res = remote_to_string({'foobar': 42})
        self.assertEqual(res, None, 'The function returned: %s' % res)
