"""
    logger.py

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


def log_header(header):
    """Styling for a function header log statement"""
    print("===============================================================")
    print(" %s" % header)
    print("---------------------------------------------------------------")


def log_footer(footer):
    """Styling for a function footer log statement"""
    print("---------------------------------------------------------------")
    print(" %s" % footer)
    print("===============================================================")


def log_start(start):
    """Styling for a block start log statement"""
    print("%s...\n" % start)


def log_done():
    """Styling for a block done log statement"""
    print(" - Done!\n")


def log_info(info):
    """Styling for a block info log statement"""
    if info != "":
        print(" + %s" % info)


def log_output(output):
    """Styling for an output log statement"""
    if output != "":
        for line in output.splitlines():
            print("   - %s" % line)
