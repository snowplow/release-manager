"""
    setup.py

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


from distutils.core import setup
import setuptools
import os


# Load _version.py
version_file_path = os.path.join(
    os.path.dirname(__file__),
    'release_manager',
    '_version.py'
    )
exec(open(version_file_path).read(), {}, locals())


setup(
    name="release-manager",
    version=__version__,
    description="Utility for creating and uploading zip packages",
    long_description=open('README.rst').read(),
    author="Joshua Beemster",
    author_email="support@snowplowanalytics.com",
    url="https://github.com/snowplow/release-manager",
    download_url="https://github.com/snowplow/release-manager/tarball/%s" % __version__,
    license="http://www.apache.org/licenses/LICENSE-2.0",
    packages=[
        "release_manager",
        "release_manager.targets",
        "release_manager.test"
    ],
    install_requires=[
        "requests[security]==2.11.1",
        "pyyaml==3.12",
        "jinja2==2.8",
        "boto3==1.4.1"
    ],
    tests_require=[
        "nose"
    ],
    test_suite="nose.collector",
    entry_points={
        "console_scripts": [
            "release-manager = release_manager.__main__:main"
        ]
    }
)
