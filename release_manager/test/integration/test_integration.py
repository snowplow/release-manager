"""
    test_integration.py

    Copyright (c) 2016 Snowplow Analytics Ltd. All rights reserved.

    This program is licensed to you under the Apache License Version 2.0,
    and you may not use this file except in compliance with the Apache License
    Version 2.0. You may obtain a copy of the Apache License Version 2.0 at
    http://www.apache.org/licenses/LICENSE-2.0.

    Unless required by applicable law or agreed to in writing,
    software distributed under the Apache License Version 2.0 is distributed on
    an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
    express or implied. See the Apache License Version 2.0 for the specific
    language governing permissions and limitations there under.

    Authors: Joshua Beemster
    Copyright: Copyright (c) 2016 Snowplow Analytics Ltd
    License: Apache License Version 2.0
"""


import unittest
import release_manager._version as _version
import release_manager.utils as utils
import os
import sys


# --- Helpers


def process_output(output):
    """Returns the value of the command output"""
    (stdout, stderr) = output.communicate()
    return {
        'code': output.returncode,
        'stdout': stdout.decode("utf-8"),
        'stderr': stderr.decode("utf-8")
    }


# --- Tests


class IntegrationTest(unittest.TestCase):


    def setUp(self):
        """SetUp the test environment with env vars"""
        os.environ["TRAVIS_BUILD_DIR"] = os.getcwd()
        os.environ["BINTRAY_USER"] = "jbeemster"
        os.environ["BINTRAY_PASSWORD"] = "password"
        os.environ["TRAVIS_TAG"] = _version.__version__


    def test_integration_config_no_actions(self):
        """Test running main with just --config"""
        cwd = os.environ["TRAVIS_BUILD_DIR"]

        retval = process_output(
            utils.execute([
                "python", "-W", "ignore",
                "%s/release_manager/__main__.py" % cwd,
                "--config",
                "%s/resources/integration/good.yml" % cwd
            ], None, True)
        )

        self.assertEquals(retval['code'], 0)
        self.assertEquals(retval['stdout'], "No actions selected, quitting...\n\n")


    def test_integration_bad_config_path(self):
        """Test running main with just --config"""
        cwd = os.environ["TRAVIS_BUILD_DIR"]

        retval = process_output(
            utils.execute([
                "python", "-W", "ignore",
                "%s/release_manager/__main__.py" % cwd,
                "--config",
                "%s/resources/bad_config.yml" % cwd
            ], None, True)
        )

        self.assertEquals(retval['code'], 1)
        self.assertEquals(retval['stdout'], "")
        self.assertNotEquals(retval['stderr'], "")


    def test_integration_version(self):
        """Test running main with just --version"""
        cwd = os.environ["TRAVIS_BUILD_DIR"]

        retval = process_output(
            utils.execute([
                "python", "-W", "ignore",
                "%s/release_manager/__main__.py" % cwd,
                "--version"
            ], None, True)
        )

        self.assertEquals(retval['code'], 0)

        # argparse --version prints to stderr before Python 3.4, stdout afterwards
        if sys.version_info >= (3, 4):
            self.assertEquals(retval['stdout'], "%s\n" % _version.__version__)
        else:
            self.assertEquals(retval['stderr'], "%s\n" % _version.__version__)


    def test_integration_check_version(self):
        """Test running main with --config & --check-version"""
        cwd = os.environ["TRAVIS_BUILD_DIR"]

        retval = process_output(
            utils.execute([
                "python", "-W", "ignore",
                "%s/release_manager/__main__.py" % cwd,
                "--config",
                "%s/resources/integration/good.yml" % cwd,
                "--check-version"
            ], None, True)
        )
        self.assertEquals(retval['code'], 0)

        os.environ["TRAVIS_TAG"] = "some-version"
        retval = process_output(
            utils.execute([
                "python", "-W", "ignore",
                "%s/release_manager/__main__.py" % cwd,
                "--config",
                "%s/resources/integration/good.yml" % cwd,
                "--check-version"
            ], None, True)
        )
        self.assertEquals(retval['code'], 1)

        os.environ["TRAVIS_TAG"] = _version.__version__


    def test_integration_make_artifact(self):
        """Test running main with --config & --make-artifact"""
        cwd = os.environ["TRAVIS_BUILD_DIR"]

        retval = process_output(
            utils.execute([
                "python", "-W", "ignore",
                "%s/release_manager/__main__.py" % cwd,
                "--config",
                "%s/resources/integration/good.yml" % cwd,
                "--make-artifact"
            ], None, True)
        )
        self.assertEquals(retval['code'], 0)

        retval = process_output(
            utils.execute([
                "python", "-W", "ignore",
                "%s/release_manager/__main__.py" % cwd,
                "--config",
                "%s/resources/integration/bad.yml" % cwd,
                "--make-artifact"
            ], None, True)
        )
        self.assertEquals(retval['code'], 1)
