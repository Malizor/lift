====
lift
====


---------------------
Run a Lift test suite
---------------------

:Authors: Written an maintained by Nicolas Delvaux <nicolas.delvaux@arkena.com>
:Version: 1.0.0
:Date: |date|
:Copyright: GPL2+
:Manual section: 1
:Manual group: Lift Manual

.. |date| date::


SYNOPSIS
========

lift [*OPTION*]... [*TEST*]...

DESCRIPTION
===========

The lift command runs all or parts of a Lift test suite.
By default, with no option, *lift* run all test it discovers in the current
directory and its sub-directories.

Lift stands for Lift Integration-Functional Testing.

OPTIONS
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

**-r**, **--regex**
  Process *TEST* strings as standard Python regex.
  See below for more information.

**--no-upper-inheritance**
  Do not load remotes/environment from upper level *lift.yaml* files.
  By default, lift will look for *lift.yaml* files in upper level folders in
  order to find settings to inherit for the current test file.
  This option disable this behaviour and consider the current test directory
  as a top level one.

**-f** *FOLDER*, **--folder** *FOLDER*
  Specify the root folder in which tests will be looked for.
  By default, use the current working directory.


RUN SPECIFIC TESTS
==================

You can specify specific tests to run directly on the command line.
You can use the test string format as one found in the lift output,
ie. "FOLDER/TEST_NAME".

If you set the "--regex" option, expressions will be matched as standard
Python regex. For example, ".*foo" will match all tests containing the
word "foo".

See http://docs.python.org/library/re.html for more information on the Python
regex syntax.


