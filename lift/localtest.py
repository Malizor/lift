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


"""Local test implementation"""

import shlex
from subprocess import Popen, PIPE, STDOUT

from lift.basetest import BaseTest


class LocalTest(BaseTest):
    """Test as a local command execution"""

    def __init__(
        self,
        name,
        command,
        directory=".",
        expected_return_code=0,
        timeout=0,
        environment={},
        streaming_output=None,
    ):
        """Create a ready to run LocalTest object

        Args:
            name (str): The test name
            command (str): The command to execute
            directory (str): The directory in which the test will be executed
            expected_return_code (int): The expected return code of the test
            timeout (int): The time the test run must not exceed.
                0 means infinite.
            environment (dict): Environment that will be set for the test
            streaming_output (file): File in which the command output will be
                dynamically written. This is typically used to print on
                sys.stdout or a file. None means 'nowhere'.
        """
        # This is the same as BaseTest constructor, except for a new internal
        # class variable
        super(LocalTest, self).__init__(
            name,
            command,
            directory,
            expected_return_code,
            timeout,
            environment,
            streaming_output,
        )
        self._process = None

    def command_launch(self):
        """Launch the command and return the output stream without blocking

        Returns:
            The output stream of the command OR a string containing a message
            if the command launch failed.
        """
        args = shlex.split(self.command)
        try:
            self._process = Popen(
                args, stdout=PIPE, stderr=STDOUT, env=self.environment, bufsize=0
            )
        except OSError as exc:
            return "Failed to launch command `%s`: %s" % (args, exc)
        return self._process.stdout

    def wait_command_completion(self):
        """Block until the command completion

        Returns:
            An int corresponding to the command return code
        """
        if self._process:
            return self._process.wait()
        else:
            return 127  # command not found

    def interrupt_command(self):
        """This function is called when the test is aborted

        This can be because of a timeout or a "Ctrl+C"
        """
        self._process.terminate()
