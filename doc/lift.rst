====
lift
====


---------------------
Run a Lift test suite
---------------------

:Authors: Written an maintained by Nicolas Delvaux <contact@nicolas-delvaux.org>
:Version: 2.5.0
:Copyright: GPL2+
:Manual section: 1
:Manual group: Lift Manual


Synopsis
========

lift [*OPTION*]... [*TEST*]...

Description
===========

The lift command runs all or parts of a Lift test suite.
By default, with no option, *lift* run all test it discovers in the current
directory and its sub-directories.

Lift stands for Lift Integration-Functional Testing.

Options
=======

**-h**, **--help**
  Show an help message and exit.

**-V**, **--version**
  Show the lift version.

**-q**, **--quiet**
  Do not print the output of tests as they run.

**-d**, **--detailed-summary**
  Print the output of failed tests in the final summary.

**-n**, **--no-color**
  Disable colored output.
  Maybe useful, for example if colors interfere with your term.

**--regex**
  Process *TEST* strings as standard Python regex.
  See below for more information.

**--no-upper-inheritance**
  Do not load remotes/environment from upper level *lift.yaml* files.
  By default, lift will look for *lift.yaml* files in upper level folders in
  order to find settings to inherit for the current test file.
  This option disable this behaviour and consider the current test directory
  as a top level one.

**--put-remotes-in-environment**
  All defined remotes will be passed as environment variables to tests.
  Variables will be in the following form:
  *LIFT_REMOTE_remotename=login:password@host*. Note that the password (along
  with the ":" separator) will not be there if it was not defined in the first
  place. **SECURITY WARNING**: Do not use this option if some of your binary
  tests can not be trusted to keep these credentials for themselves.

**-f** *FOLDER*, **--folder** *FOLDER*
  Specify the root folder in which tests will be looked for.
  By default, use the current working directory.

**-r** *REMOTE*, **--remote** *REMOTE*
  Define a remote. The value should be in the following form:
  *REMOTENAME=USERNAME:PASSWORD@HOST*. Note that the PASSWORD field (along with
  the ":" separator) is optional if SSH keys are properly set. This option can
  be used multiple times to define multiple remotes.
  Remotes defined via this option supersede those defined via lift.yaml files.

**--with-xunit**
  Provide test results in the standard XUnit XML format.

**--xunit-file** *XUNIT_FILE*
  Specify the path of the XML file to store the XUnit report in.
  The default is *lift.xml* in the current working directory.


Run specific tests
==================

You can select specific tests to run directly on the command line.
You can use the test string format as found in the normal lift output,
ie. "FOLDER/TEST_NAME".

If you set the "--regex" option, expressions will be matched as standard
Python regex. For example, ".*foo" will match all tests containing the
word "foo".

See http://docs.python.org/library/re.html for more information on the Python
regex syntax.


See also
========

For the test suite definition, see **lift.yaml** (1) 
