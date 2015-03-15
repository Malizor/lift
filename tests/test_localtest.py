# LIFT Integration-Functional Testing - A meta test framework
# Copyright © 2014-2015 Arkena S.A and Nicolas Delvaux
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

from lift.localtest import LocalTest


class LocalTestTestCase(unittest.TestCase):
    """Test the LocalTest class"""

    def test_run(self):
        """Test a simple run"""

        expected_return_code = 0
        expected_output = 'foobar\n'

        test = LocalTest('simple', 'echo foobar')
        self.assertTrue(test.run(), 'The test should have succeded')
        self.assertEqual(test.return_code, expected_return_code,
                         'Test return code is %d instead of %d'
                         % (test.return_code, expected_return_code))
        self.assertEqual(test.output, expected_output,
                         'Test output is %s instead of %s'
                         % (test.output, expected_output))

    def test_run_fail(self):
        """Test if a test fail as it should"""

        expected_return_code = 1
        expected_output = ''

        test = LocalTest('simple', 'sh -c "exit 1"')
        self.assertFalse(test.run(), 'The test should have failed')
        self.assertEqual(test.return_code, expected_return_code,
                         'Test return code is %d instead of %d'
                         % (test.return_code, expected_return_code))
        self.assertEqual(test.output, expected_output,
                         'Test output is %s instead of %s'
                         % (test.output, expected_output))

    def test_timeout(self):
        """Test that the timeout mecanism works"""

        expected_return_code = 124
        expected_output = '\n\nTest interrupted: timeout\n'

        test = LocalTest('simple', 'sleep 10', timeout=1)
        self.assertFalse(test.run(), 'The test should have failed')
        self.assertEqual(test.return_code, expected_return_code,
                         'Test return code is %d instead of %d'
                         % (test.return_code, expected_return_code))
        self.assertEqual(test.output, expected_output,
                         'Test output is %s instead of %s'
                         % (test.output, expected_output))

    def test_run_with_environment(self):
        """Test that the environment is passed to the program"""

        expected_return_code = 0
        expected_output = 'TEST\n'

        test = LocalTest('simple',
                         'sh -c "echo $foobar"',
                         environment={'foobar': 'TEST'})
        self.assertTrue(test.run(), 'The test should have succeded')
        self.assertEqual(test.return_code, expected_return_code,
                         'Test return code is %d instead of %d'
                         % (test.return_code, expected_return_code))
        self.assertEqual(test.output, expected_output,
                         'Test output is %s instead of %s'
                         % (test.output, expected_output))

    def test_executable(self):
        """Test the directory switching and executable scripts"""

        cur_dir = os.path.dirname(os.path.realpath(__file__))

        expected_return_code = 0
        expected_output = u'foobarééé\n'

        test = LocalTest('simple',
                         './my_script.sh',
                         directory=os.path.join(cur_dir, 'tests_resources'))

        self.assertTrue(test.run(), 'The test should have succeded')
        self.assertEqual(test.return_code, expected_return_code,
                         'Test return code is %d instead of %d'
                         % (test.return_code, expected_return_code))
        self.assertEqual(test.output, expected_output,
                         'Test output is %s instead of %s'
                         % (test.output, expected_output))
