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


"""Remote test implementation"""

import os
import paramiko
import threading
from time import sleep

from lift.exception import TestException


class RemoteTest(object):

    def __init__(self, name, command, remote,
                 directory='.',
                 expected_return_code=0,
                 timeout=0,
                 environment={},
                 resources=[]):
        self.name = name
        self.command = command
        self.remote = remote
        self.directory = directory
        self.expected_return_code = expected_return_code
        self.timeout = timeout
        self.environment = environment
        self.resources = resources

        # Test result
        self.return_code = -42
        self.stdout = ''
        self.stderr = ''

        # Internal variables for the command process
        self._out = None
        self._err = None
        self._process = None

    def __repr__(self):
        return 'RemoteTest<%s>' % self.name

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

        # Remote folder where everything will happen
        test_folder = '/tmp/lift_test_%s' % self.name

        ssh = paramiko.SSHClient()
        # Do not fail on key errors
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(self.remote['host'],
                    username=self.remote['username'],
                    password=self.remote.get('password', None))
        # Keep alive may be useful for some big tests
        ssh.get_transport().set_keepalive(1)

        ftp = ssh.open_sftp()
        _, out, _ = ssh.exec_command('rm -rf %s' % test_folder)
        out.channel.recv_exit_status()  # Wait for completion
        ftp.mkdir(test_folder)

        # Upload needed resources
        for resource in self.resources:
            if not os.path.isabs(resource):
                resource = os.path.join(self.directory, resource)
            if os.path.isfile(resource):
                ftp.put(resource, os.path.join(test_folder, os.path.basename(resource)))
                continue
            elif os.path.isdir(resource):
                # Upload the whole folder
                for root, _, files in os.walk(resource):
                    ftp.mkdir(os.path.join(test_folder,
                                           os.path.relpath(root, self.directory)))

                    for file_ in files:
                        local_path = os.path.join(root, file_)
                        remote_path = os.path.join(test_folder,
                                                   os.path.relpath(local_path, self.directory))
                        ftp.put(local_path, remote_path)
                        # Also copy the file mode
                        ftp.chmod(remote_path,
                                  os.stat(local_path).st_mode)
            else:
                raise TestException('Could not upload resource - %s: '
                                    'No such file or directory.' % resource)

        def run_command():
            """The command is ran in a thread to implement the timeout setting"""
            # Insert the environment directly on the command line
            command = self.command
            for key, value in self.environment.items():
                command = '%s=%s %s' % (key, value, command)
            _, self._out, self._err = ssh.exec_command('cd %s; %s' %
                                                       (test_folder, command))
            # Wait for the command completion
            self.return_code = self._out.channel.recv_exit_status()

        thread = threading.Thread(target=run_command)
        thread.daemon = True
        thread.start()

        run_time = 0
        try:
            while thread.is_alive() and (self.timeout <= 0 or run_time < self.timeout):
                # We can't join with the timeout to handle KeyboardInterrupt
                thread.join(0.1)
                run_time += 0.1
        except KeyboardInterrupt:
            self._out.channel.close()
            thread.join()
            raise

        if thread.is_alive():
            self._out.channel.close()
            thread.join()
            self.return_code = 124  # same as the 'timeout' command

        self.stdout = self._out.read()
        self.stderr = self._err.read()

        if self.return_code == 124:
            self.stderr += '\nTest interrupted: timeout'

        # Cleanup
        ssh.exec_command('rm -rf /tmp/test_case')

        return self.return_code == self.expected_return_code
