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

"""Tests for the lift.localtest file"""

import os
import unittest
from collections import OrderedDict

from lift.localtest import LocalTest
from lift.remotetest import RemoteTest
from lift.exception import InvalidDescriptionFile
from lift.loader import load_upper_inheritance, load_config_file


class LocalTestTestCase(unittest.TestCase):
    """Test the LocalTest class"""

    def test_run(self):
        """Test a simple run"""

        expected_return_code = 0
        expected_stdout = 'foobar\n'
        expected_stderr = ''

        test = LocalTest('simple',
                         'echo foobar',
                         '.',
                         expected_return_code,
                         10,
                         {})
        self.assertTrue(test.run(), 'The test should have succeded')
        self.assertEqual(test.return_code, expected_return_code,
                         'Test return code is %d instead of %d'
                         % (test.return_code, expected_return_code))
        self.assertEqual(test.stdout, expected_stdout,
                         'Test stdout is %s instead of %s'
                         % (test.stdout, expected_stdout))
        self.assertEqual(test.stderr, expected_stderr,
                         'Test stderr is %s instead of %s'
                         % (test.stderr, expected_stderr))

    def test_run_fail(self):
        """Test if a test fail as it should"""

        expected_return_code = 1
        expected_stdout = ''
        expected_stderr = ''

        test = LocalTest('simple',
                         'sh -c "exit 1"',
                         '.',
                         0,
                         10,
                         {})
        self.assertFalse(test.run(), 'The test should have failed')
        self.assertEqual(test.return_code, expected_return_code,
                         'Test return code is %d instead of %d'
                         % (test.return_code, expected_return_code))
        self.assertEqual(test.stdout, expected_stdout,
                         'Test stdout is %s instead of %s'
                         % (test.stdout, expected_stdout))
        self.assertEqual(test.stderr, expected_stderr,
                         'Test stderr is %s instead of %s'
                         % (test.stderr, expected_stderr))

    def test_timeout(self):
        """Test that the timeout mecanism works"""

        expected_return_code = 124
        expected_stdout = ''
        expected_stderr = '\nTest interrupted: timeout'

        test = LocalTest('simple',
                         'sleep 10',
                         '.',
                         0,
                         1,
                         {})
        self.assertFalse(test.run(), 'The test should have failed')
        self.assertEqual(test.return_code, expected_return_code,
                         'Test return code is %d instead of %d'
                         % (test.return_code, expected_return_code))
        self.assertEqual(test.stdout, expected_stdout,
                         'Test stdout is %s instead of %s'
                         % (test.stdout, expected_stdout))
        self.assertEqual(test.stderr, expected_stderr,
                         'Test stderr is %s instead of %s'
                         % (test.stderr, expected_stderr))

    def test_run_with_environment(self):
        """Test that the environment is passed to the program"""

        expected_return_code = 0
        expected_stdout = 'TEST\n'
        expected_stderr = ''

        test = LocalTest('simple',
                         'sh -c "echo $foobar"',
                         '.',
                         expected_return_code,
                         10,
                         {'foobar': 'TEST'})
        self.assertTrue(test.run(), 'The test should have succeded')
        self.assertEqual(test.return_code, expected_return_code,
                         'Test return code is %d instead of %d'
                         % (test.return_code, expected_return_code))
        self.assertEqual(test.stdout, expected_stdout,
                         'Test stdout is %s instead of %s'
                         % (test.stdout, expected_stdout))
        self.assertEqual(test.stderr, expected_stderr,
                         'Test stderr is %s instead of %s'
                         % (test.stderr, expected_stderr))

    def test_executable(self):
        """Test that executable test.directory are usable"""

        expected_return_code = 0
        expected_stdout = 'foobar\n'
        expected_stderr = ''

        test = LocalTest('simple',
                         './my_script.sh',
                         'tests_resources',
                         expected_return_code,
                         10,
                         {})

        self.assertTrue(test.run(), 'The test should have succeded')
        self.assertEqual(test.return_code, expected_return_code,
                         'Test return code is %d instead of %d'
                         % (test.return_code, expected_return_code))
        self.assertEqual(test.stdout, expected_stdout,
                         'Test stdout is %s instead of %s'
                         % (test.stdout, expected_stdout))
        self.assertEqual(test.stderr, expected_stderr,
                         'Test stderr is %s instead of %s'
                         % (test.stderr, expected_stderr))
