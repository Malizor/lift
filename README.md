Lift Integration-Functional Testing - A meta test framework
===========================================================


[![Build Status](https://github.com/Malizor/lift/actions/workflows/main.yml/badge.svg?branch=main)](https://github.com/Malizor/lift/actions/workflows/main.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)


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

Lift provides an integration/functional test platform which handles *executable*
tests easily and generically.  


### Features

* Lift only deals with *executables* and their return code  
  → A particular test can be written in the language that fit it the most
* Test declaration in a simple YAML syntax  
  → No need to learn a programming language to integrate a test in a suite
* Easily declare a test as running locally or on a remote machine
* Remote tests: upload needed assets automatically and cleanup afterward
* Naturally organize a test suite in multiple sub-folders/sub-test suites
* Easily run a sub-test suite or specific tests from the command line
* Pass environment variables to tests
* Inheritance of remotes and environment across sub-test suites  
  → For example, remotes can be defined in the top folder and used below
* Only one command to run all or specific tests: `lift`
* Export XUnit reports, for easy integration with Jenkins & friends


### Documentation

The `doc` folder contains man pages.


### Example

For a fully commented example of a lift test suite (which can also be seen as
a functional test suite for Lift itself), see the `example` folder.


### Installation

Use `sudo python3 setup.py install`  

If you want to build and install the man pages, run:
```
sudo rst2man doc/lift.rst /usr/share/man/man1/lift.1
sudo rst2man doc/lift.yaml.rst /usr/share/man/man1/lift.yaml.1
```

##### Dependencies

* Python 3 (>= 3.4)
* python3-yaml
* python3-paramiko
* python3-docutils (for man pages)
* python3-junit.xml


### Home page

https://github.com/Malizor/lift


### License

GNU General Public License (GPL) version 2+  
Please refer to the COPYING file.
