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


"""Local test implementation"""

import os
import shlex
import threading
from subprocess import Popen, PIPE


class LocalTest(object):

    def __init__(self, name, command,
                 directory='.', expected_return_code=0, timeout=0, environment={}):
        self.name = name
        self.command = command
        self.directory = directory
        self.expected_return_code = expected_return_code
        self.timeout = timeout
        self.environment = environment

        # Test result
        self.return_code = -42
        self.stdout = ''
        self.stderr = ''

        # Internal variable
        self._process = None

    def __repr__(self):
        return 'LocalTest<%s>' % self.name

    def __eq__(self, other):
        return (isinstance(other, self.__class__)
                and self.__dict__ == other.__dict__)

    def run(self):
        """Execute the test.

        Returns a boolean, representing the test success, and fill the
        return_code, stdout and stderr attributes.
        The test is considered successful if its returned value correspond to
        expected_return_code.
        """

        args = shlex.split(self.command)

        def run_command():
            """The command is ran in a thread to implement the timeout setting"""
            try:
                self._process = Popen(args, stdout=PIPE, stderr=PIPE, env=self.environment)
            except OSError:
                # The test program is not in path, try in the current directory
                path = os.path.join(self.directory, args[0])
                if not os.path.isfile(path):
                    raise
                args[0] = path
                self._process = Popen(path, stdout=PIPE, env=environment)
            self.stdout, self.stderr = self._process.communicate()
            self.return_code = self._process.wait()

        thread = threading.Thread(target=run_command)
        thread.start()

        timeout = self.timeout
        if timeout <= 0:
            timeout = None  # adapt to the thread API
        thread.join(timeout)
        if thread.is_alive():
            self._process.terminate()
            thread.join()
            self.return_code = 124  # same as the 'timeout' command
            self.stderr += '\nTest interrupted: timeout'

        return self.return_code == self.expected_return_code
