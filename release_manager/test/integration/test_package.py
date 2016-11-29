"""
    test_package.py

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
from release_manager.package import create_artifact


class PackageTest(unittest.TestCase):

    def test_correct_asis_artifact(self):
        result = create_artifact('.', '0.4.0-M1', "package name doesn't matter", 'asis', 'test-package-', '.jar', ['path/to/binary.jar'])
        self.assertEqual(result, {
            'artifact_name': 'test-package-0.4.0-M1.jar',
            'artifact_path': './path/to/binary.jar'
        })

    def test_correct_zip_artifact(self):
        result = create_artifact('.', '0.4.0', "kinesis-sink", 'zip', 'test-package-', '', ['setup.py'])
        self.assertEqual(result, {
            'artifact_name': 'test_package_0.4.0.zip',
            'artifact_path': './dist/kinesis-sink/test_package_0.4.0.zip'
        })

