#!/usr/bin/env python


from release_manager import utils, _version, logger
from os.path import expanduser
import os
import sys


# --- Constants


HOME = expanduser("~")
DEFAULT_SERVER = 'https://pypi.python.org/pypi'
DEFAULT_REPO = 'pypi'
PYPIRC_FILE = '%s/.pypirc' % HOME

if 'TRAVIS_TAG' in os.environ:
    TRAVIS_TAG = os.environ.get('TRAVIS_TAG')
else:
    sys.exit("Environment variable TRAVIS_TAG is unavailable")

if 'TRAVIS_BUILD_DIR' in os.environ:
    TRAVIS_BUILD_DIR = os.environ.get('TRAVIS_BUILD_DIR')
else:
    sys.exit("Environment variable TRAVIS_BUILD_DIR is unavailable")

if 'PYPI_USERNAME' in os.environ:
    PYPI_USERNAME = os.environ.get('PYPI_USERNAME')
else:
    sys.exit("Environment variable PYPI_USERNAME is unavailable")

if 'PYPI_PASSWORD' in os.environ:
    PYPI_PASSWORD = os.environ.get('PYPI_PASSWORD')
else:
    sys.exit("Environment variable PYPI_PASSWORD is unavailable")


# --- Helpers


def check_version():
    """Fail deploy if tag version doesn't match version"""
    logger.log_start("Checking versions")
    if TRAVIS_TAG != _version.__version__:
        sys.exit("Version extracted from project doesn't match the TRAVIS_TAG variable!")
    else:
        logger.log_info("Versions match!")
        logger.log_done()


def write_config():
    """Writes an array of lines to the PyPi config file"""
    logger.log_start("Writing ~/.pypirc file")
    lines = [
        '[distutils]\n',
        'index-servers =\n',
        '  %s\n' % DEFAULT_REPO,
        '\n',
        '[%s]\n' % DEFAULT_REPO,
        'repository=%s\n' % DEFAULT_SERVER,
        'username=%s\n' % PYPI_USERNAME,
        'password=%s\n' % PYPI_PASSWORD
    ]

    with open(PYPIRC_FILE, 'w') as outfile:
        for line in lines:
            outfile.write(line)
    logger.log_info("The ~/.pypirc file has been written!")
    logger.log_done()


def deploy_to_pypi():
    """Deploys the release to PyPi"""
    logger.log_start("Deploying to PyPi")
    os.chdir(TRAVIS_BUILD_DIR)
    utils.execute("python setup.py register -r pypi", shell=True)
    utils.execute("python setup.py sdist upload -r pypi", shell=True)
    logger.log_info("Module deployed to PyPi!")
    logger.log_done()


# --- Main


if __name__ == "__main__":
    logger.log_header("Deploying release-manager to PyPi")
    check_version()
    write_config()
    deploy_to_pypi()
    logger.log_footer("Deployed version %s to PyPi!" % TRAVIS_TAG)
