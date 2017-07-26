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


class S3Location(object):
    """Entity storing information about where artifact should be uploaded.
    Parsed from package, by `get_locations`"""
    def __init__(self, bucket, path, region):
        self.bucket = bucket
        self.path = path
        self.region = region

    def __str__(self):
        return "AWS S3 bucket [{}] at [{}] region. Key [{}]".format(self.bucket, self.region, self.path)


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

            # Process all S3 locations
            for location in get_locations(package):
                full_s3_path = get_full_path(location, artifact_file)

                client = boto3.client('s3', region_name=location.region, aws_access_key_id=target['access_key_id'], aws_secret_access_key=target['secret_access_key'])
                transfer = S3Transfer(client)

                if package['override']:
                    transfer.upload_file(artifact_file['artifact_path'], location.bucket, full_s3_path)
                else:
                    try:
                        transfer.download_file(location.bucket, full_s3_path, tempfile.mktemp())
                        if package['continue_on_conflict']:
                            logger.log_info("Artifact [%s] exists, but continue_on_conflict flag is true, not failing deploy..." % full_s3_path)
                        else:
                            raise ValueError("Artifact at %s already exists" % (full_s3_path,))
                    except ClientError as e:
                        if e.response['Error']['Code'] == '404':
                            transfer.upload_file(artifact_file['artifact_path'], location.bucket, full_s3_path)
                            logger.log_info("Artifact uploaded to {}".format(location))
                        else:
                            logger.log_info("continue_on_conflict flag is true, not failing release...")
                            raise

    else:
        logger.log_info("make-artifact flag was not passed. Do nothing")


def get_locations(package):
    """Return list of S3 locations extracted from package. Always return array"""
    if 'bucket' in package and 'locations' in package:
        raise RuntimeError("Package cannot contain both 'bucket' and 'locations' property")
    elif 'bucket' in package:
        try:
            return [S3Location(package['bucket'], package['path'], package['region'])]
        except KeyError:
            raise RuntimeError("Package missing required keys (bucket, path, region)")
    elif 'locations' in package:
        return [S3Location(location['bucket'], location['path'], location['region']) for location in package['locations']]
    else:
        raise RuntimeError("Either 'locations' array or 'bucket' must be present")


def get_full_path(location, artifact_file):
    if location.path.endswith('/'):
        path = location.path
    elif not location:
        path = ''
    else:
        path = location.path + '/'
    return path + artifact_file['artifact_name']
