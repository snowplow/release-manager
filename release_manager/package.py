"""
    package.py

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


from __future__ import print_function
import os
import os.path

import release_manager.logger as logger
import release_manager.utils as utils


# --- Constants


ARTIFACT_STAGING_DIR = "dist"

AVAILABLE_ARTIFACT_TYPES = ['zip', 'asis']


# --- Functions


def create_zip_artifact(root_dir, version, package, artifact_prefix, artifact_suffix, binary_paths):
    """Builds the artifact for upload"""

    artifact_root = "%s%s%s" % (artifact_prefix, version, artifact_suffix,)
    artifact_name = "%s.zip" % artifact_root
    artifact_name = artifact_name.replace("-", "_")

    logger.log_info("Building artifact %s..." % artifact_name)

    artifact_folder = "%s/%s/%s" % (root_dir, ARTIFACT_STAGING_DIR, package)
    utils.execute(['mkdir', '-p', artifact_folder])

    file_names = []
    for path in binary_paths:
        utils.execute(['cp', path, artifact_folder])
        file_names.append(os.path.basename(path))

    os.chdir(artifact_folder)
    utils.execute(['zip', artifact_name] + file_names)
    os.chdir(root_dir)

    logger.log_done()

    return {
        'artifact_name': artifact_name,
        'artifact_path': "%s/%s" % (artifact_folder, artifact_name)
    }


def create_asis_artifact(root_dir, version, package, artifact_prefix, artifact_suffix, binary_paths):
    """Construct artifact name and perform no operations"""

    if len(binary_paths) != 1 and type(binary_paths) != str:
        raise ValueError("Invalid binary_paths for 'asis' artifact type. It must contain single item. %s items instead" % len(binary_paths))

    artifact_name = "%s%s%s" % (artifact_prefix, version, artifact_suffix,)
    return {
        'artifact_name': artifact_name,
        'artifact_path': os.path.join(root_dir, binary_paths[0])
    }


def create_artifact(root_dir, version, package, artifact_type, artifact_prefix, artifact_suffix, binary_paths):
    """Builds the artifact for upload"""
    logger.log_start("Creating artifact for package %s" % package)

    if artifact_type == 'zip':
        result = create_zip_artifact(root_dir, version, package, artifact_prefix, artifact_suffix, binary_paths)
    elif artifact_type == 'asis':
        result = create_asis_artifact(root_dir, version, package, artifact_prefix, artifact_suffix, binary_paths)
    else:
        raise ValueError("Invalid type specified; expected one of %s and got %s" % (AVAILABLE_ARTIFACT_TYPES, artifact_type,))

    return result


def check_version(version, build_version):
    """Fail deploy if tag version doesn't match version"""
    logger.log_start("Asserting versions match")
    if version != build_version:
        raise ValueError("Version extracted from build [%s] doesn't match declared in config [%s]" % (build_version, version))
    else:
        logger.log_info("Version match!")
    logger.log_done()


def execute_commands(commands):
    """Execute build commands"""
    logger.log_start("Executing build commands")
    for command in commands:
        utils.execute([command], shell=True)
    logger.log_done()
