"""
    utils.py

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

import contextlib
import os
import subprocess
import random
import string
import threading
import re
import time

from jinja2 import Template
import yaml

import release_manager.logger as logger


# --- Command Execution

@contextlib.contextmanager
def working_directory(path):
    """A context manager which changes the working directory to the given
    path, and then changes it back to its previous value on exit.

    """
    prev_cwd = os.getcwd()
    os.chdir(path)
    yield
    os.chdir(prev_cwd)


def output_everything(output):
    """Callback to log stdout"""
    (stdout, stderr) = output.communicate()
    if output.returncode == 0:
        logger.log_output(stdout)
    else:
        logger.log_output("Process has failed.\n" + stdout.decode("utf-8"))
        raise ValueError(stderr)


def output_value(output, fail_on_err=False):
    """Returns the value of the command output"""
    (stdout, stderr) = output.communicate()
    if output.returncode == 0:
        return stdout
    else:
        if fail_on_err:
            raise ValueError(stderr)
        else:
            return stderr


def execute(command, callback=output_everything, quiet=False, shell=False):
    """Execute shell command with optional callback"""
    if not quiet:
        formatted_command = " ".join(command) if (type(command) == list) else command
        logger.log_info("Executing [{0}]".format(formatted_command))

    output = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=shell)

    if hasattr(callback, '__call__'):
        return callback(output)
    else:
        return output


class AwakeThread(threading.Thread):
    """Thread printing messages to console, keeping Travis CI from shut down prematurely"""
    def run(self):
        print("Starting AwakeThread")
        count = 0
        while count < 10:
            message = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(128))
            print("Tick %s. %s seconds passed. Random output: %s" % (str(count), str(40 * count), message))
            time.sleep(40)
            count = count + 1
        print("Exit AwakeThread")


def sbt_version(directory):
    """Return version of project in some directory"""
    t = AwakeThread()
    t.setDaemon(True)
    t.start()

    with working_directory(directory):
        sbt_output = execute(['sbt', 'version', '-Dsbt.log.noformat=true'], None)
        print(sbt_output.stderr.read())
        for line in sbt_output.stdout.read().split("\n"):
            print(line)
            match = re.search('\[info\]\s*(\d+\.\d+\.\d+.*)$', line)
            if match:
                return match.group(1)
        raise ValueError("Not SBT Project: " + directory)

    t.join()
    print("Some result should appear")



PREDEFINED_FUNCTIONS = {
    'sbt_version': sbt_version
}

# --- Config

def parse_config(config_path):
    """Checks if secrets need to be fetched from the environment"""

    temp_path = "%s.tmp" % config_path

    # Template yaml file
    with open(config_path, 'r') as stream:
        try:
            temp = template_yaml(yaml.load(stream))
        except yaml.YAMLError as exc:
            raise ValueError("Invalid config passed to the program: %s" % exc)

    # Dump templated file back to file-system
    with open(temp_path, 'w') as outfile:
        yaml.safe_dump(temp, outfile, default_flow_style=False)

    # Add environment resolver
    pattern_env = re.compile(r'^(.*)\<%= ENV\[\'(.*)\'\] %\>(.*)$')
    yaml.add_implicit_resolver("!pathex", pattern_env)

    # Add command resolver
    pattern_cmd = re.compile(r'^(.*)\<%= CMD\[\'(.*)\'\] %\>(.*)$')
    yaml.add_implicit_resolver("!pathcmd", pattern_cmd)

    # Add function resolver
    pattern_fun = re.compile(r'^(.*)\<%= FUNC\[\'(.*)\((.*)\)\'\] %\>(.*)$')
    yaml.add_implicit_resolver("!func", pattern_fun)

    def pathex_constructor(loader, node):
        """Processes environment variables found in the YAML"""
        value = loader.construct_scalar(node)
        before_path, env_var, remaining_path = pattern_env.match(value).groups()
        return before_path + os.environ[env_var] + remaining_path

    def pathcmd_constructor(loader, node):
        """Processes command variables found in the YAML"""
        value = loader.construct_scalar(node)
        before_path, cmd_var, remaining_path = pattern_cmd.match(value).groups()
        retval = output_value(execute(cmd_var, None, True, True), True)
        return before_path + retval.decode("utf-8") + remaining_path

    def fun_constructor(loader, node):
        """Processes embedded functions found in the YAML"""
        value = loader.construct_scalar(node)
        before_path, fun, arg, remaining_path = pattern_fun.match(value).groups()
        retval = PREDEFINED_FUNCTIONS[fun](arg)
        return before_path + retval.decode("utf-8") + remaining_path

    yaml.add_constructor("!pathex", pathex_constructor)
    yaml.add_constructor("!pathcmd", pathcmd_constructor)
    yaml.add_constructor("!func", fun_constructor)

    with open(temp_path, 'r') as stream:
        try:
            return yaml.load(stream)
        except yaml.YAMLError as exc:
            raise ValueError("Invalid config passed to the program: %s" % exc)


def template_yaml(yaml_dict):
    """Runs the YAML through the Jinja2 templater"""
    template_yaml_dict = Template(yaml.safe_dump(yaml_dict, default_flow_style=False))
    template_rendered = template_yaml_dict.render(yaml_dict)
    return yaml.load(template_rendered)
