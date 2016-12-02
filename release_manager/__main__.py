"""
    __main__.py

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

import argparse

import release_manager.targets.bintray as bintray
import release_manager.targets.awss3 as s3

import release_manager._version as _version
import release_manager.logger as logger
import release_manager.utils as utils
import release_manager.package as pack


# --- Main


def main():
    """Main function entry point"""
    parser = argparse.ArgumentParser(description="Utility for creating and uploading zip packages.")
    parser.add_argument("--config", help="the path to the configuration yaml file")
    parser.add_argument("--make-version", action='store_true', default=False, help="makes a new version for the package (bintray-specific)")
    parser.add_argument("--make-artifact", action='store_true', default=False, help="makes the artifacts that will be uploaded")
    parser.add_argument("--upload-artifact", action='store_true', default=False, help="uploads the artifacts to the targets")
    parser.add_argument("--check-version", action='store_true', default=False, help="checks that the version specified matches the build")
    parser.add_argument("--version", action='version', version=_version.__version__)
    args = parser.parse_args()

    # Parse args
    if not args.config:
        raise ValueError("A config must be passed to the program")
    config = utils.parse_config(args.config)

    if not args.make_version and not args.make_artifact and not args.upload_artifact and not args.check_version:
        logger.log_start("No actions selected, quitting")
        exit(0)

    if not args.make_artifact and args.upload_artifact:
        raise ValueError("Cannot upload artifact without first creating; please add '--make-artifact' to resolve...")

    logger.log_header("Starting Package uploader...")

    # Upload packages
    for package in config["packages"]:

        logger.log_start("Processing package %s" % package["name"])

        # Check the versions
        if args.check_version:
            pack.check_version(package["version"], package["build_version"])

        # Push to targets
        for target in config['targets']:
            if target['type'] == 'bintray':
                bintray.deploy_to_bintray(args, config['local'], package, target)
            elif target['type'] == 'awss3':
                s3.upload_to_s3(args, config['local'], package, target)
            else:
                raise ValueError("Invalid target specified; expected one of [bintray, awss3] and got %s" % target["type"])

        logger.log_footer("Finished processing package %s!" % package["name"])


if __name__ == "__main__":
    main()
