"""
    awss3.py

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


from __future__ import division

import tempfile

import boto3
from boto3.s3.transfer import S3Transfer
from botocore.exceptions import ClientError

import release_manager.logger as logger
import release_manager.package as pack


def upload_to_s3(args, local, package, target):
    """Upload artifact to AWS S3"""

    if args.make_artifact:

        # Run build commands
        if "build_commands" in package.keys():
            pack.execute_commands(package["build_commands"])

        for artifact in package["artifacts"]:
            artifact_file = pack.create_artifact(
                local['root_dir'],
                package['version'],
                package['name'],
                artifact['type'],
                artifact['prefix'],
                artifact['suffix'],
                artifact['binary_paths']
            )

            full_s3_path = get_full_path(package, artifact_file)

            client = boto3.client('s3', package['region'], aws_access_key_id=target['access_key_id'], aws_secret_access_key=target['secret_access_key'])
            transfer = S3Transfer(client)

            if package['override']:
                transfer.upload_file(artifact_file['artifact_path'], package['bucket'], full_s3_path)
            else:
                try:
                    transfer.download_file(package['bucket'], full_s3_path, tempfile.mktemp())
                    if package['continue_on_conflict']:
                        logger.log_info("Artifact [%s] exists, but continue_on_conflict flag is true, not failing deploy..." % full_s3_path)
                    else:
                        raise ValueError("Artifact at %s already exists" % (full_s3_path,))
                except ClientError as e:
                    if e.response['Error']['Code'] == '404':
                        transfer.upload_file(artifact_file['artifact_path'], package['bucket'], full_s3_path)
                    else:
                        logger.log_info("continue_on_conflict flag is true, not failing release...")
                        raise

    else:
        logger.log_info("make-artifact flag was not passed. Do nothing")


def get_full_path(package, artifact_file):
    if package['path'].endswith('/'):
        path = package['path']
    elif not package:
        path = ''
    else:
        path = package['path'] + '/'
    return path + artifact_file['artifact_name']
