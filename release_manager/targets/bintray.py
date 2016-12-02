"""
    bintray.py

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

import json
import requests

import release_manager.logger as logger
import release_manager.package as pack


def create_bintray_version(version, package, repo, user_org, user, api_key):
    """Creates a new Bintray version for the package"""
    logger.log_start("Creating Bintray version %s in package %s" % (version, package))

    url = "https://api.bintray.com/packages/%s/%s/%s/versions" % (user_org, repo, package)

    payload = {
        'name': version,
        'desc': 'Release of %s' % package
    }
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(url, data=json.dumps(payload), headers=headers, auth=(user, api_key))

    code = response.status_code
    success = False

    if code == 409:
        logger.log_info("Bintray version %s already exists, skipping." % version)
        success = True
    else:
        code_family = code // 100
        if code_family == 2 or code_family == 3:
            logger.log_info("Bintray Version created!")
            success = True
        else:
            logger.log_info("Bintray API response %s is not 409 (package already exists) nor in 2xx or 3xx range" % code)
            success = False

    logger.log_done()
    return success


def upload_bintray_artifact(version, package, repo, user_org, user, api_key, artifact_name, artifact_path, publish, override, continue_on_conflict):
    """Uploads the artifact to Bintray"""
    logger.log_start("Uploading artifact to Bintray")

    url = 'https://api.bintray.com/content/%s/%s/%s/%s/%s' % (user_org, repo, package, version, artifact_name)
    parameters = {
        'publish': publish,
        'override': override
    }

    with open(artifact_path, "rb") as package_fp:
        response = requests.put(
            url,
            auth=(user, api_key),
            params=parameters,
            data=package_fp
        )

    code = response.status_code
    code_family = int(code) // 100
    success = False

    if code_family == 2 or code_family == 3:
        logger.log_info("Bintray artifact uploaded!")
        success = True
    else:
        logger.log_info("Bintray API response %s is not in 2xx or 3xx range" % code)
        if continue_on_conflict:
            logger.log_info("continue_on_conflict flag is true, not failing release...")
            success = True
        else:
            success = False

    logger.log_done()
    return success


def deploy_to_bintray(args, local, package, target):
    """Deploys the package to Bintray"""

    # Make the version
    if args.make_version:
        retval_1 = create_bintray_version(
            package["version"],
            package["name"],
            package["repo"],
            package["user_org"],
            target["user"],
            target["password"]
        )
        if retval_1 is False:
            raise ValueError("Could not create new Bintray version for the package!")

    # Make the artifacts
    if args.make_artifact:

        # Run build commands
        if "build_commands" in package.keys():
            pack.execute_commands(package["build_commands"])

        # Build artifacts
        for artifact in package["artifacts"]:
            retval_2 = pack.create_artifact(
                local["root_dir"],
                package["version"],
                package["name"],
                artifact["type"],
                artifact["prefix"],
                artifact["suffix"],
                artifact["binary_paths"]
            )

            # Upload the artifacts
            if args.make_artifact and args.upload_artifact:
                retval_3 = upload_bintray_artifact(
                    package["version"],
                    package["name"],
                    package["repo"],
                    package["user_org"],
                    target["user"],
                    target["password"],
                    retval_2["artifact_name"],
                    retval_2["artifact_path"],
                    "1" if package["publish"] else "0",
                    "1" if package["override"] else "0",
                    package["continue_on_conflict"]
                )
                if retval_3 is False:
                    raise ValueError("Could not upload artifact to Bintray!")
