|Release| |License| |Travis|

Overview
--------

The release-manager is a Python utility for easily uploading zipped
or plain binaries to a destination target. It allows you to:

-  Create new package versions
-  Upload artifacts to said version
-  Currently only support zip
-  Upload to multiple targets
-  Currently supports Bintray and AWS S3
-  Combine N binaries into the artifact that is then uploaded
-  Upload N artifacts to for the package

Installing
----------

-  Option 1: Download this repository and run:
   ``python setup.py install``
-  Option 2: Install from pip: ``pip install release-manager``

Usage
-----

::

    usage: release-manager.py [-h] [--config CONFIG] [--make-version]
                              [--make-artifact] [--upload-artifact]
                              [--check-version] [--version]

    Bintray utility for creating and uploading zip packages.

    optional arguments:
      -h, --help         show this help message and exit
      --config CONFIG    the path to the configuration yaml file
      --make-version     makes a new version for the package
      --make-artifact    makes the artifacts that will be uploaded
      --upload-artifact  uploads the artifacts to the targets
      --check-version    checks that the version specified matches the build
      --version          show program's version number and exit

Please note when specifying the options to run that they will be applied
to every package in your config file.

Options:

-  You cannot upload the artifacts without also making the artifacts:
-  ``--upload-artifact`` requires ``--make-artifact``
-  Checking the version is useful for automated build tools such as
   travis to assert that you have the correct build versions specified

Config
~~~~~~

The release-manager requires a config be passed to it in the form of a
yaml file. You can find a sample config in the **resources** directory.

Environment resolver
^^^^^^^^^^^^^^^^^^^^

To get values from the environment at runtime set the value like the
following:

::

    some_env_key: <%= ENV['SOME_ENV_VALUE'] %>

Shell resolver
^^^^^^^^^^^^^^

To evaluate a shell command at runtime set the value like the following:

::

    some_cmd_value: <%= CMD['cat VERSION'] %>

**NOTE**: If the command does not exit with code 0 the config will not
load.

Variable resolver
^^^^^^^^^^^^^^^^^

If you need to access a variable many-times in your config and it is okay 
for it to be hardcoded you can use the local variable resolver.

This works like so:

::

    some_var_value: "hello_world"
    some_ref_var_value: {{ some_var_value }}

Function resolver
^^^^^^^^^^^^^^^^^

release-manager provides you one (for now) predefined function - 
`sbt_version(path)`. Using it you can extract version of SBT project in 
specified `path`.

This works like so:

::

    some_cmd_value: <%= FUNC['sbt_version(../scalaz)'] %>


Example config
^^^^^^^^^^^^^^

::
    
    # Required: local settings
    local:
      root_dir : <%= ENV['TRAVIS_BUILD_DIR'] %>

    # Required: deployment targets
    targets:
      - type     : "bintray" # Options: bintray
        user     : <%= ENV['BINTRAY_USER'] %>
        password : <%= ENV['BINTRAY_PASSWORD'] %>

    # Required: packages to be deployed
    packages:
      - repo     : "generic"
        name     : "release-manager"
        user_org : "jbeemster"
        publish  : true

        # Will attempt to overwrite a published entity if one is found
        override : false

        # If the artifact already exists will determine whether or not
        # to fail the release
        continue_on_conflict : false

        # The version of this package
        version  : <%= CMD['cat VERSION'] %>
        
        # Required IF '--check-version' is passed: will assert that 
        # both versions are the same
        build_version : <%= ENV['TRAVIS_TAG'] %>
        
        # Optional: Build commands
        # You can nest your artifact creation commands here!
        build_commands:
          - ls -ls

        # Required: Artifact
        artifacts:
            # The artifact name is composed like so:
            # {{prefix}}{{version}}{{suffix}}.zip
          - prefix : "release_manager_"
            suffix : ""
            type   : "zip"

            # The binaries to put in the zip
            binary_paths:
              - setup.py


Multiple locations
^^^^^^^^^^^^^^^^^^
Same artifact can be uploaded into two or more buckets, without unnecessary boilerplate if you use `locations` keyword instead of first-level `buckets`, `path` and `region`.

::

    packages:
      - name     : "acme-app-multiple-locations"
        locations:
        - bucket   : "acme-hosted-assets-us-east-1"
          path     : "software/acme-app"
          region   : "us-east-1"
        - bucket   : "acme-hosted-assets-us-west-1"
          path     : "software/acme-app"
          region   : "us-west-1"
        publish  : true
        override : false
        continue_on_conflict : false
        version  : "0.1.0"

Note that if you're using `locations` array - first-level `bucket`, `path` and `region` must be absent.

AWS S3 target
^^^^^^^^^^^^^

In addition to Bintray you can also upload your files to Amazon S3. 

::

    targets:
      - type     : "awss3" # Options: bintray
        user     : <%= ENV['AWS_ACCESS_KEY'] %>
        password : <%= ENV['AWS_SECRET_KEY'] %>

As is artifacts
^^^^^^^^^^^^^^^

In addition to zip artifacts you can also upload plain files from your local FS.

::

        artifacts:
          - prefix : "release_manager_"
            suffix : ""
            type   : "asis"

            binary_paths:
              - setup.py

File `setup.py` will be renamed to `release_manager_{{ version}}` and upload 
into specified path.

Copyright and license
---------------------

The Release Manager is copyright 2016 Snowplow Analytics Ltd.

Licensed under the `Apache License, Version
2.0 <http://www.apache.org/licenses/LICENSE-2.0>`__ (the "License"); you
may not use this software except in compliance with the License.

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

.. |Release| image:: https://badge.fury.io/py/release-manager.svg
   :target: https://badge.fury.io/py/release-manager
.. |License| image:: http://img.shields.io/badge/license-Apache--2-blue.svg?style=flat
   :target: http://www.apache.org/licenses/LICENSE-2.0
.. |Travis| image:: https://travis-ci.org/snowplow/release-manager.svg?branch=master
   :target: https://travis-ci.org/snowplow/release-manager
