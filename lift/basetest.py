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


"""Base test implementation"""

import os
from io import StringIO
from threading import Thread

from junit_xml import TestCase


class BaseTest(TestCase):
    """Base class for Lift tests

    Concrete tests types are supposed to inherit from this.
    Each Lift test object is designed to be self-sufficient: from the outside,
    one just has to call the run() function on it and look for the finished,
    return_code and output attributes.

    Subclasses shoud override the following functions:

    setup()
    command_launch()
    wait_command_completion()
    interrupt_command()
    cleanup()

    Please refer to their individual docstrings.
    """

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
        """Create a ready to run test object

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
        super().__init__(name, classname="%s/%s" % (directory, name))

        self.name = name
        self.command = command
        self.directory = directory
        self.expected_return_code = expected_return_code
        self.timeout = timeout
        self.environment = environment
        self.streaming_output = streaming_output

        # Test result
        self.finished = False
        self.return_code = None
        self.output = ""

        # Internal variables
        self._iothread = None
        self._output = StringIO()

    def __getattribute__(self, name):
        """Please junit_xml that wants an stdout attribute.

        Our self.output combines both stdout and stderr, so it would be
        confusing to rename it to just "stdout".
        Just consider self.stdout an (hidden) alias of self.output.
        """
        if name == "stdout":
            return self.output
        else:
            return super().__getattribute__(name)

    def __repr__(self):
        return "%s<%s>" % (self.__class__.__name__, self.name)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        for item in self.__dict__:
            # Do not compare private attributes
            if item.startswith("_"):
                continue
            if self.__dict__[item] != other.__dict__[item]:
                return False
        return True

    def _finalize_output(self):
        """Store the output in the object public attribute

        Also flush the streaming_output if it exists.
        """
        self._output.seek(0)
        self.output = self._output.read()
        self._output.close()

        if self.streaming_output is not None:
            self.streaming_output.flush()

    def setup(self):
        """Do whatever preparation before running the test.

        This can be used, for example, to upload resources to a distant server.
        Its eventual return value is ignored.
        If it raises, the test will be aborted.

        This implementation does nothing.
        """
        pass

    def cleanup(self):
        """Do whatever cleanup after the test was ran.

        This can be used, for example, to clean resources that were uploaded
        to a distant server during setup().
        Its eventual return value is ignored.
        If it raises, the test will be aborted.

        This implementation does nothing.
        """
        pass

    def run(self):
        """Launch and manage the test execution.

        This function block until the completion. It cannot raise.

        If the test takes more than the 'timeout' attribute (seconds)
        to be ran, it is aborted and return_code is set to 124.

        Returns:
            A boolean that state if the test was successful or not.
            The test is considered successful if the return_code and
            expected_return_code attributes are identical.
        """
        try:
            return self._run()
        except Exception as exc:
            msg = "An exception was raised during the test execution:\n%s\n" % str(exc)
            if self.streaming_output is not None:
                print(self.streaming_output)
                self.streaming_output.write(msg)
            self._output.write(msg)
            self._finalize_output()
            self.failure_message = msg
            return False

    def _run(self):
        """Actual implementation of run()"""
        if self.finished:
            # Do not re-run the test
            return self.return_code == self.expected_return_code
        try:
            orig_dir = os.getcwd()
            os.chdir(self.directory)
        except OSError as exc:
            msg = "\n\n%s: %s\n" % (self.directory, exc)
            if self.streaming_output is not None:
                self.streaming_output.write(msg)
            self._output.write(msg)
            self._finalize_output()
            self.failure_message = msg
            return False

        self.setup()

        def copy_output(infile, *outfiles):
            """Write the content of one file to others.

            This is implemented via a dedicated thread to avoid blocking.

            Args:
                infile: The input file. It should be opened and readable.
                outfiles: One or multiple output files. They should be opened
                    and writable.
            """

            def actual_copy_output(infile, *outfiles):
                for line in iter(infile.readline, b""):
                    if isinstance(line, bytes):
                        line = line.decode("utf8")
                    elif line == "":  # ...and if we did not read bytes
                        break  # another sentinel, as b'' != ''
                    for f in outfiles:
                        f.write(line)
                infile.close()

            t = Thread(target=actual_copy_output, args=(infile,) + outfiles)
            t.daemon = True
            t.start()
            return t

        def run_command():
            """Run the actual command

            This function is ran in a thread to implement the timeout setting.
            """
            out = self.command_launch()
            if isinstance(out, str):
                # An error occurred
                msg = "\nAn error occurred: %s" % out
                if self.streaming_output is not None:
                    self.streaming_output.write(msg)
                    self.streaming_output.flush()
                self._output.write(msg)
                return

            if self.streaming_output is not None:
                self._iothread = copy_output(out, self.streaming_output, self._output)
            else:
                self._iothread = copy_output(out, self._output)

            self.return_code = self.wait_command_completion()

        thread = Thread(target=run_command)
        thread.start()

        timeout = self.timeout
        if timeout <= 0:
            timeout = None  # adapt to the thread API
        thread.join(timeout)
        if thread.is_alive():
            self.interrupt_command()
            thread.join()
            self.return_code = 124  # same as the 'timeout' command
            msg = "\n\nTest interrupted: timeout\n"
            if self.streaming_output is not None:
                self.streaming_output.flush()
                self.streaming_output.write(msg)
            self._output.write(msg)

        self._iothread.join()
        self._finalize_output()

        self.cleanup()
        os.chdir(orig_dir)

        self.finished = True
        status = self.return_code == self.expected_return_code

        if not status:
            self.failure_message = "Returned %s instead of %s" % (
                self.return_code,
                self.expected_return_code,
            )
        return status

    def command_launch(self):
        """Launch the command and return the output stream without blocking

        This implementation does nothing.

        Returns:
            The output stream of the command OR a string containing a message
            if the command launch failed.
        """
        return "Not implemented"

    def wait_command_completion(self):
        """Block until the command completion

        This implementation does nothing.

        Returns:
            An int corresponding to the command return code
        """
        return 1

    def interrupt_command(self):
        """This function is called when the test is aborted

        This can be because of a timeout or a "Ctrl+C"

        This implementation does nothing.
        """
        pass
