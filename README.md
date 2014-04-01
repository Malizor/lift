Lift Integration-Functional Testing - A meta test framework
===========================================================

Usually, there is not much to discuss when writing unit tests.  
They have to use the same programming language as the code they are testing
and most languages have a set of dedicated test frameworks that you may chose from.

However, functional and integration tests are more often a bunch of
scripts/executables written in different languages.  
For example, you may prefer to use shell scripts to test a web-service
(eg. via `curl`) and a Python program to interact with Python modules.  
And if C/Ruby/Perl/PHP/whatever is more suited to some of your test cases,
you want to use these languages too without having to write the full test suite with it.

Currently, most projects seem to have either multiple functional/integration
test suites (re-using different unit testing frameworks) or internal solutions
to group all the tests executable together in a more or less clean way.

Lift provides an integration/functional test platform which handle *executable*
tests easily and generically.  


### Features

* Lift only deals with *executables* and their return code  
  → write your tests in whatever form you want to
* Test declaration in a simple YAML syntax  
  → no need to learn a programming language to integrate your test in a suite
* Easily declare a test as running locally or on a remote machine
* Remote tests: auto upload of your needed assets and cleanup afterward
* Organize your test suite in multiple sub-folders/sub-test suites
* Easily run a sub-test suite or specific tests from the command line
* Pass environment variables to your tests
* Inheritance of remotes and environment across sub-test suites  
  → For example, you can define all your remotes in the top folder and use them below
* Only one command to run all or specific tests: `lift`


### Example

For a fully commented example of a lift test suite (which can also be seen as
a functional test suite for lift itself), see the `example` folder.


### Installation

Just use `sudo python setup.py install`

##### Dependencies

* Python 2.7
* python-yaml
* python-paramiko
* python-docutils (for the man page)


### License

GNU General Public License (GPL) version 2+  
Please refer to the COPYING file.
