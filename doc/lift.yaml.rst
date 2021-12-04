=========
lift.yaml
=========


------------------------
Define a Lift test suite
------------------------

:Authors: Written an maintained by Nicolas Delvaux <contact@nicolas-delvaux.org>
:Version: 2.5.0
:Copyright: GPL2+
:Manual section: 1
:Manual group: Lift Manual


Description
===========

Lift provides an integration/functional test platform which handle
**executable** tests easily and generically.

*lift.yaml* files are used to define a test suite.
Such a file is written in YAML (http://yaml.org/) and support 3 root sections
types: **settings**, **local tests** and **remote tests**. These are documented
further below in this documentation.

A Lift test suite is composed of at least one *lift.yaml* file but it is often
a folder hierarchy with one *lift.yaml* file at each level.

Such a hierarchy is useful to define more specialized sub-suites (eg. one for
basic functionalities, one for performances...). Each sub-suite has its own
*lift.yaml* and can be run individually.

Settings defined on a *lift.yaml* file are inherited in sub-suites.
Sub-suites can override inherited settings if they need to.


Settings definition
===================

This section is used to define remotes machines that will be used for remote
tests and to define environment variables that will be passed to tests.

Environment variables can be overridden for each test individually in their
definition.

The 'settings' section has to be defined at the root of the *lift.yaml* file.

::

 settings:
     # The 'define' keyword followed by the remote name
     define my_remote:
         host: localhost  # mandatory
         username: root  # mandatory
         password: foobar  # optional (if ssh keys are set properly)
     define my_other_remote:
         host: localhost
         username: not_root
         password: foobar
     # These will be transmitted to the test commands
     # They can be used as a way to pass common settings around
     environment:
         MY_ENV_VAR1: foo
         MY_ENV_VAR2: bar


Local test definition
=====================

Each test is represented by a single section at the root of the *lift.yaml*
file. Here is an example:

::

 # the 'test' keyword followed by the test name
 test my_test_name:
     command: "./my_test_executable --my-arg"  # mandatory
     return code: 0  # optional (default to 0)
     timeout: 10  # optional, in seconds (no timeout by default)
     environment:  # optional
         MY_VAR: 42  # may override an already defined variable

If a test timeouts, it will return 124. You can therefore test that a command
does timeout by setting the 'return code' value to 124.

The actual environment used by a test is computed in the following order:
environment defined in higher level *lift.yaml* files (inheritance), then
the environment defined in the current *lift.yaml* file and finally the
environment defined in the test itself.

The 'command' can be an absolute path, a path relative to the current
*lift.yaml* position or a system command (like ping, curl...)


Remote test definition
======================

Each remote test is represented by a single section at the root of the
*lift.yaml* file.
Please also refer to the local test definition documentation, as all
options are reused in the same way for remote tests.
Here is an example:

::

 # A known remote name followed by the 'test' keyword and the test name
 # This defines a test that will be ran on my_remote.
 my_remote test my_remote_test_name:
     command: "sh test/test.sh --my-arg"
     return code: 0
     timeout: 2
     # List files and folders that will be uploaded to the remote
     # before running the test.
     resources:
         - test/
     environment:
         MY_VAR: content

To be known, a remote has to be defined either in a higher level *lift.yaml*
file (inheritance) or in the current *lift.yaml* or directly via the
**--remote** option of the **lift** command line.

Files resources are uploaded "flatly" whereas folders keep their structure.
Lift will take care of deleting all resources from the remote after the test is
over.

The command will be executed in a temporary directory that will be created on
the remote. Resources will be put in this directory, so you can use relative
paths to them in your command/executable.


Full test suite example
=======================

The *example* folder at the root of the Lift sources contains a fully commented
example of a Lift test suite, which can also be used as a functional test suite
for Lift itself.

On Debian systems, the *example* folder can be found in
*/usr/share/doc/lift/example*.


See also
========

For the command line utility, see **lift** (1)

