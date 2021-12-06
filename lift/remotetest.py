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


"""Remote test implementation"""

import os
import paramiko

from lift.basetest import BaseTest
from lift.exception import TestException


class RemoteTest(BaseTest):
    """Test as a remote (via ssh) command execution"""

    def __init__(
        self,
        name,
        command,
        remote,
        resources=[],
        directory=".",
        expected_return_code=0,
        timeout=0,
        environment={},
        streaming_output=None,
    ):

        super(RemoteTest, self).__init__(
            name,
            command,
            directory,
            expected_return_code,
            timeout,
            environment,
            streaming_output,
        )
        self.remote = remote
        self.resources = resources

        # Internals
        self._remote_test_folder = "/tmp/lift_test_%s" % self.name
        self._ssh = paramiko.SSHClient()
        self._channel = None

    def setup(self):
        # Do not fail on key errors
        self._ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self._ssh.connect(
            self.remote["host"],
            username=self.remote["username"],
            password=self.remote.get("password", None),
        )
        # Keep alive may be useful for some big tests
        self._ssh.get_transport().set_keepalive(1)

        ftp = self._ssh.open_sftp()
        _, out, _ = self._ssh.exec_command("rm -rf %s" % self._remote_test_folder)
        out.channel.recv_exit_status()  # Wait for completion
        ftp.mkdir(self._remote_test_folder)

        # Upload needed resources
        for resource in self.resources:
            if os.path.isfile(resource):
                remote_path = os.path.join(
                    self._remote_test_folder, os.path.basename(resource)
                )
                ftp.put(resource, remote_path)
                # Also copy the file mode
                ftp.chmod(remote_path, os.stat(resource).st_mode)
                continue
            elif os.path.isdir(resource):
                # Upload the whole folder
                for root, _, files in os.walk(resource):
                    ftp.mkdir(os.path.join(self._remote_test_folder, root))

                    for file_ in files:
                        local_path = os.path.join(root, file_)
                        remote_path = os.path.join(self._remote_test_folder, local_path)

                        ftp.put(local_path, remote_path)
                        # Also copy the file mode
                        ftp.chmod(remote_path, os.stat(local_path).st_mode)
            else:
                raise TestException(
                    "Could not upload resource - %s: "
                    "No such file or directory." % resource
                )

    def cleanup(self):
        self._ssh.exec_command("rm -rf %s" % self._remote_test_folder)
        self._ssh.close()

    def command_launch(self):
        """Launch the command and return the output stream without blocking

        Returns:
            The output stream of the command
        """
        # Insert the environment directly on the command line
        try:
            command = self.command
            for key, value in self.environment.items():
                command = "%s=%s %s" % (key, value, command)
            self._channel = self._ssh.get_transport().open_session()
            self._channel.get_pty()
            out_stream = self._channel.makefile()
            self._channel.exec_command(
                "cd %s; %s" % (self._remote_test_folder, command)
            )
            return out_stream
        except Exception as exc:
            return "Failed to launch command `%s`: %s" % (command, exc)

    def wait_command_completion(self):
        return self._channel.recv_exit_status()

    def interrupt_command(self):
        self._channel.close()
