# -*- coding: utf-8 -*-
# module utils.py
#
# Copyright (c) 2021  CorTexT Platform
# Copyright (c) 2021  Cogniteva SAS
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# ---------------------------------------------------------------------------
from parscival import __version__
# ---------------------------------------------------------------------------
import configparser
import os
import semver
from importlib.resources import read_text, read_binary
# ---------------------------------------------------------------------------
def get_custom_metadata(section, key):
    config = configparser.ConfigParser()

    # Read the metadata.cfg file from the package resources
    data = read_text('parscival', 'version.ini')

    config.read_string(data)

    # Extract custom metadata
    if section in config and key in config[section]:
        return config[section][key]
    else:
        raise KeyError(f"'{key}' not found in section '{section}'")

def get_version_major_minor_patch(module='core'):
  core_version = get_custom_metadata(module, 'version')

  # Parse the version using semver
  parsed_version = semver.VersionInfo.parse(core_version)
  # Return the major.minor.patch part
  return f"{parsed_version.major}.{parsed_version.minor}.{parsed_version.patch}"

def get_version_major(module='core'):
  core_version = get_custom_metadata(module, 'version')

  # Parse the version using semver
  parsed_version = semver.VersionInfo.parse(core_version)
  # Return the major.minor.patch part
  return parsed_version.major

def get_version_major_minor(module='core'):
  core_version = get_custom_metadata(module, 'version')

  # Parse the version using semver
  parsed_version = semver.VersionInfo.parse(core_version)
  # Return the major.minor.patch part
  return f"{parsed_version.major}.{parsed_version.minor}"
