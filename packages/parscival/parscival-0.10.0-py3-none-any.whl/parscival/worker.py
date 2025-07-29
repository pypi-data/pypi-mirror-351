# -*- coding: utf-8 -*-
# module worker.py
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
import argparse
import atexit
import contextlib
import importlib.util
import logging
import logging.handlers
import mmap
import os
import re
import shutil
import signal
import site
import sys
from collections.abc import Mapping
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

import jinja2
import klepto
import pluginlib
import psutil
import semver
import yaml
from box import Box
from deepdiff import DeepDiff
from dotenv import load_dotenv
from jinja2 import meta
from parsimonious.exceptions import ParseError
from rich.console import Console, RenderableType
from rich.logging import RichHandler
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    Task,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from rich.table import Column
from rich.text import Text
from rich.theme import Theme

from parscival import __version__
from parscival.utils.logging import logging_decorator, logging_set_context
from parscival.utils.version import (
    get_custom_metadata,
    get_version_major,
    get_version_major_minor_patch,
)
from parscival_plugins.initializing.validate.dogma import (
    dogma_schema_normalize,
    dogma_schema_validate,
)
from parscival_plugins.utils.logging_mixin import LoggingMixin

# ---------------------------------------------------------------------------
__doc__ = """
Worker for Parscival
=============================================================================

This module implements a generic approach to process datasets according
to a YAML-based specification
"""
__author__ = "Cristian Martinez, Lionel Villard"
__license__ = "MIT"
# ---------------------------------------------------------------------------
# parscival engine major version
engine_major_version = get_version_major(module='engine')
# parscival engine version
engine_version = get_custom_metadata('engine', 'version')
logging_default_context = f"|{__package__}.worker:{engine_version}       |"
# ---------------------------------------------------------------------------
logging.TRACE = 5
logging.addLevelName(logging.TRACE, "TRACE")


def trace(self, message, *args, **kws):
  if self.isEnabledFor(logging.TRACE):
    self._log(logging.TRACE, message, args, **kws)


logging.Logger.trace = trace
# ---------------------------------------------------------------------------
log = logging.getLogger(__name__)
# short log levels names
# according to the RCF5424
# @see https://datatracker.ietf.org/doc/html/rfc5424
logging.addLevelName(logging.TRACE,    "(~~)")
logging.addLevelName(logging.DEBUG,    "(%%)")
logging.addLevelName(logging.INFO,     "(II)")
logging.addLevelName(logging.WARNING,  "(WW)")
logging.addLevelName(logging.ERROR,    "(EE)")
logging.addLevelName(logging.CRITICAL, "(CC)")
logging.addLevelName(logging.NOTSET,   "(--)")

# create a custom logging theme
# level names must be in lowercase
log_theme = Theme({
    "repr.number": "",
    "repr.error": "bold red",
    "logging.level.(%%)": "green",
    "logging.level.(ii)": "white",
    "logging.level.(ww)": "bold blue",
    "logging.level.(ee)": "bold red",
    "logging.level.(cc)": "bold red",
    "logging.level.(@@)": "bold red",
    "logging.level.(--)": "white"
})

# setup rich console for logging
console = Console(
    record=False,
    theme=log_theme
  )
# ---------------------------------------------------------------------------

# ---- Python API ----
# The functions defined in this section can be imported by users in their
# Python scripts/interactive interpreter, e.g. via
# `from parscival.main import process_datasets`,
# when using this Python module as a library.


def task_ingesting(parscival_spec, parscival_data):
  """Get metadata about the documents to parse
  """
  log.info("Ingesting data...")

  # try to load plugins
  plugin_group = 'ingesting'
  loader = get_plugins_loader(plugin_group)

  # exit early if we failed to get the interface of the loader
  if loader is None:
    return False

  log.info("Getting documents information...")
  records_total = 0
  files_total = 0

  # get the record separator from the parscival spec
  spec_identifier = (parscival_spec.get('data', {})
                     .get('identifier', 'unknown'))

  spec_category = parscival_spec.get('category', {})

  # add misc regex to the parscival spec
  record_split = {
      'raw': '',
      'len': 0,
      'regex': {
          'bytes': {},
          'text': {}
      }
  }

  parscival_spec['misc']['record_finalizer'] = record_split
  parscival_spec['misc']['record_separator'] = record_split

  # get the record separator from the parscival spec
  record_separator = (parscival_spec.get('data', {})
                      .get('parsing', {})
                      .get(spec_category, {})
                      .get('record_separator', None))

  # continue only if a record separator is defined
  if record_separator is None:
    log.error(
        "[yellow]{}[/yellow] - undefined {}.record_separator".format(spec_identifier, spec_category))
    return False

  parscival_spec['misc']['record_separator']['raw'] = record_separator
  parscival_spec['misc']['record_separator']['len'] = len(record_separator)

  # compile the record separator as a regex bytes
  record_separator_regex_bytes = re.compile(bytes(record_separator, encoding='utf-8'))
  parscival_spec['misc']['record_separator']['regex']['bytes'] = record_separator_regex_bytes

  # compile the record separator as a regex text
  record_separator_regex_text = re.compile(record_separator)
  parscival_spec['misc']['record_separator']['regex']['text'] = record_separator_regex_text

  # get the record finalizer from the parscival spec
  record_finalizer = (parscival_spec.get('data', {})
                      .get('parsing', {})
                      .get(spec_category, {})
                      .get('record_finalizer', None))

  # set record finalizer_regex
  if record_finalizer is not None:
    # compile the record finalizer as a regex bytes
    record_finalizer_regex_bytes = re.compile(bytes(record_finalizer, encoding='utf-8'))
    # compile the record finalizer as a regex text
    record_finalizer_regex_text = re.compile(record_finalizer)
    # compile the reverse record finalizer as a regex text
    record_finalizer_regex_text_reverse = re.compile(record_finalizer[::-1])

    parscival_spec['misc']['record_finalizer']['raw'] = record_finalizer
    parscival_spec['misc']['record_finalizer']['len'] = len(record_finalizer)
    parscival_spec['misc']['record_finalizer']['regex']['bytes'] = record_finalizer_regex_bytes
    parscival_spec['misc']['record_finalizer']['regex']['text'] = record_finalizer_regex_text
    parscival_spec['misc']['record_finalizer']['regex']['text_reverse'] = record_finalizer_regex_text_reverse

  # loop over each file
  for f in parscival_data['files']:
    file_path = Path(f.name)
    filename = file_path.name

    # ensure that we have an existing non empty file
    if not file_path.exists() or file_path.stat().st_size == 0:
      log.warning("[cyan]{}[/cyan] is empty".format(filename))
      continue

    # @see https://stackoverflow.com/a/11692134/2042871
    mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
    with contextlib.closing(mm) as dataset:
      records = record_separator_regex_bytes.findall(dataset)
      records_count = len(records)
      records_total = records_total + records_count
      files_total += 1

      # update documents information
      parscival_data['datasets'].append({
          'file': f,
          'documents': [],
          'filename': filename,
          'shortname': os.path.basename(filename),
          'stats': {
              'total': records_count,
              'parsed': 0,
              'missed': 0,
              'lines': 0
          }
      })

    log.info("[cyan]{}[/cyan] - found {} documents".format(filename, records_count))

  # report about the number of documents and files to parse
  log.info("Preparing to parse {} documents from {} files".format(records_total,
                                                                  len(parscival_data['datasets'])))

  # update the number of documents
  parscival_data['stats']['total'] = records_total
  parscival_data['stats']['files'] = files_total

  return True


def check_parscival_spec_referenced_variables(section_name, section,
                                              parsing_keys, mapping_keys):
  """
  Validates that all referenced variables within a given section are defined
  either in the 'keys.parsing' or 'keys.mapping' sections

  Args:
      section_name (str): The name of the section being checked, used for logging purposes.
      section (any): The section data to be checked, which can be a dict, list, or str.
      parsing_keys (set): A set of keys defined in 'keys.parsing'.
      mapping_keys (set): A set of keys defined in 'keys.mapping'.

  Returns:
      bool: True if all referenced variables are defined, False otherwise.

  The function recursively checks nested structures within the section.
  It ignores variables of the form '{{_...}}' or '{{ _... }}' as they are considered safe.
  """
  safe_variable_pattern = re.compile(r'{{\s*_\[.*?\]\s*}}')

  if isinstance(section, dict):
    for key, items in section.items():
      if isinstance(items, dict):
        if not check_parscival_spec_referenced_variables(
                f'{section_name}.{key}', items, parsing_keys, mapping_keys):
          return False
      elif isinstance(items, list):
        for index, item in enumerate(items):
          if isinstance(item, dict):
            if not check_parscival_spec_referenced_variables(
                    f'{section_name}.{key}[{index}]', item, parsing_keys, mapping_keys):
              return False
          elif isinstance(item, str):
            variables = re.findall(r'{{(.*?)}}', item)
            for var in variables:
              if (not safe_variable_pattern.match(f'{{{{ {var} }}}}') and
                  var not in parsing_keys and var not in mapping_keys):
                log.error(
                    f"Undefined variable '{var}' in '{section_name}.{key}[{index}]'")
                return False
      elif isinstance(items, str):
        variables = re.findall(r'{{(.*?)}}', items)
        for var in variables:
          if (not safe_variable_pattern.match(f'{{{{ {var} }}}}') and
              var not in parsing_keys and var not in mapping_keys):
            log.error(f"Undefined variable '{var}' in '{section_name}.{key}'")
            return False
  elif isinstance(section, list):
    for index, item in enumerate(section):
      if isinstance(item, dict):
        if not check_parscival_spec_referenced_variables(
                f'{section_name}[{index}]', item, parsing_keys, mapping_keys):
          return False
      elif isinstance(item, str):
        variables = re.findall(r'{{(.*?)}}', item)
        for var in variables:
          if (not safe_variable_pattern.match(f'{{{{ {var} }}}}') and
              var not in parsing_keys and var not in mapping_keys):
            log.error(f"Undefined variable '{var}' in '{section_name}[{index}]'")
            return False
  elif isinstance(section, str):
    variables = re.findall(r'{{(.*?)}}', section)
    for var in variables:
      if (not safe_variable_pattern.match(f'{{{{ {var} }}}}') and
          var not in parsing_keys and var not in mapping_keys):
        log.error(f"Undefined variable '{var}' in '{section_name}'")
        return False
  return True


def check_parscival_spec_key_values_consistency(section_name, section,
                                                key_to_check, valid_values, path=""):
  """
  Validates that the specified key within a section has values consistent with the allowed values.

  Args:
      section_name (str): The name of the section being checked, used for logging purposes.
      section (any): The section data to be checked, which can be a dict, list, or str.
      key_to_check (str): The specific key whose values need to be validated.
      valid_values (set): A set of allowed values for the specified key.
      path (str): The current path within the section being checked, used for logging purposes.

  Returns:
      bool: True if all values of the specified key are valid, False otherwise.

  The function recursively checks nested structures within the section.
  Logs an error with the specific path if an invalid value is found.
  """
  if isinstance(section, dict):
    for key, value in section.items():
      new_path = f"{path}.{key}" if path else key
      if key == key_to_check:
        if value not in valid_values:
          log.error(
              f"Invalid value '{value}' for key '{key}' in '{section_name}.{new_path}'")
          return False
      if isinstance(value, (dict, list)):
        if not check_parscival_spec_key_values_consistency(section_name, value,
                                                           key_to_check, valid_values, new_path):
          return False
  elif isinstance(section, list):
    for index, item in enumerate(section):
      new_path = f"{path}[{index}]"
      if isinstance(item, (dict, list)):
        if not check_parscival_spec_key_values_consistency(section_name, item,
                                                           key_to_check, valid_values, new_path):
          return False
  elif isinstance(section, str):
    variables = re.findall(r'{{(.*?)}}', section)
    for var in variables:
      if var not in valid_values:
        log.error(f"Undefined variable '{var}' in '{section_name}.{path}'")
        return False
  return True


def check_parscival_spec_target_template_circular_references(mapping, section_name):
  """
  Checks for circular references in template mappings within a specified section.

  Args:
    template_mapping (dict): The template mappings to be checked. Each key maps to a dictionary with a template.
      Example:

      .. code-block:: python

        {
          'key1': {'template': '{{key2}} ...'},
          'key2': {'template': '{{key3}} ...'}
        }

    section_name (str): The name of the section being checked, used for logging purposes.

  Returns:
    bool: True if no circular references are found, False if a circular reference is detected.

  Logs an error if a circular reference is detected, specifying the exact key and section.
  """
  circular_reference_found = False

  env = jinja2.Environment()

  for key, value in mapping.items():
    if 'template' in value:
      template = value['template']
      # parse the template
      ast = env.parse(template)
      # create a list of variables
      template_variables = meta.find_undeclared_variables(ast)

      if key in template_variables:
        log.error(f"Circular reference detected for key '{key}' in '{section_name}'")
        circular_reference_found = True

  return not circular_reference_found


def check_parscival_spec_source_target_circular_references(mapping, section_name):
  """
  Checks for circular references in key mappings within a specified section.

  Args:
    mapping (dict): The key mappings to be checked. Each key maps to a list of target dictionaries.

      Example:

      .. code-block:: python

        {
          'key1': [{'target': 'key2'}],
          'key2': [{'target': 'key3'}]
        }

    section_name (str): The name of the section being checked, used for logging purposes.

  Returns:
    bool: True if no circular references are found, False if a circular reference is detected.

  The function uses a depth-first search (DFS) approach to detect circular references by tracking visited keys.
  Logs an error if a circular reference is detected, specifying the exact key and section.
  """
  def find_references(key, visited):
    if key in visited:
      log.error(f"Circular reference detected for key '{key}' in '{section_name}'")
      return False
    visited.add(key)
    targets = mapping.get(key, [])
    for target in targets:
      if isinstance(target, dict) and 'target' in target:
        if not find_references(target['target'], visited):
          return False
    visited.remove(key)
    return True

  for key in mapping.keys():
    if not find_references(key, set()):
      return False
  return True


def check_parscival_spec_mapping_duplicate_variables(mapping):
  """
  Validates that no 'target' in mapping.source_targets is present as a key in mapping.target_template.

  Args:
    mapping (dict): The mapping to be validated. Expected to have 'source_targets' and 'target_template' keys.
      Example:

      .. code-block:: python

        {
          'source_targets': {
            'key1': [{'target': 'key2'}]
          },
          'target_template': {
            'key2': {'template': '...'}
          }
        }

  Returns:
    bool: True if the mapping is valid, False if a target is present as a key in target_template.

  Logs an error if an invalid mapping is detected.
  """
  source_targets = mapping.get('source_targets', {})
  target_template = mapping.get('target_template', {})

  # collect all targets in source_targets
  targets = set()
  for source, targets_list in source_targets.items():
    for target_dict in targets_list:
      if 'target' in target_dict:
        targets.add(target_dict['target'])

  # check if any target is present as a key in target_template
  invalid_targets = targets.intersection(target_template.keys())
  if invalid_targets:
    for invalid_target in invalid_targets:
      log.error(
          f"Invalid mapping: target '{invalid_target}' in 'source_targets' is also a key in 'target_template'")
    return False

  return True


def check_parscival_spec_required_structure(section, required_structure, section_name):
  """
  Validates that a section adheres to a specified required structure.

  Args:
      section (dict): The section to be checked.
      required_structure (dict): A dictionary representing the required structure.
          Keys represent required fields, and values specify the type or further nested structure.
          To check for a list of dictionaries, use [{}].
      section_name (str): The name of the section being checked, used for logging purposes.

  Returns:
      bool: True if the section adheres to the required structure, False otherwise.

  The function recursively checks nested structures, ensuring that each required key
  exists and has the correct type.
  Logs an error with the specific path if any required structure is missing or invalid.
  """
  if isinstance(section, dict):
    for key, value in section.items():
      new_path = f"{section_name}.{key}" if section_name else key
      if isinstance(value, dict):
        for req_key, req_value in required_structure.items():
          if req_key not in value:
            log.error(f"Missing required field '{req_key}' in '{new_path}'")
            return False
          if isinstance(req_value, dict):
            if not check_parscival_spec_required_structure(
                    value[req_key], req_value, f"{new_path}.{req_key}"):
              return False
          elif isinstance(req_value, list) and req_value == [{}]:
            # Check that each item in the list is a dictionary
            if not isinstance(value[req_key], list):
              log.error(f"Expected a list for '{new_path}.{req_key}'")
              return False
            for index, item in enumerate(value[req_key]):
              if not isinstance(item, dict):
                log.error(
                    f"Invalid structure in '{new_path}.{req_key}[{index}]', expected a dictionary")
                return False
              if 'params' in item and not isinstance(item['params'], dict):
                log.error(
                    f"Invalid structure for 'params' in '{new_path}.{req_key}[{index}]', expected a dictionary")
                return False
      else:
        log.error(f"Invalid structure in '{new_path}', expected a dictionary")
        return False
  else:
    log.error(f"Invalid structure in '{section_name}', expected a dictionary")
    return False
  return True


def check_parscival_spec_valid_plugins_recursive(plugin_group, section_path, section_content, plugins):
  """
  Recursively validates if the given section contains valid plugins.

  Args:
      section_name (str): The name and path of the section being checked, used for logging purposes.
      section (dict or list): The section data to be checked for valid plugins.
      plugins (obj): The loaded plugins.

  Returns:
      bool: True if all plugins are valid, False otherwise.

  The function recursively checks each plugin in the given section to ensure it exists
  in the provided plugins dictionary. Logs an error with the specific path if an unknown
  plugin is found.
  """
  if isinstance(section_content, dict):
    for key, value in section_content.items():
      new_section_path = f"{section_path}.{key}" if section_path else key
      if key == 'plugins':
        # Check plugins directly
        for plugin_call in value:
          plugin_category = list(plugin_call.keys())[0]
          plugin_name = plugin_call[plugin_category]
          plugin_id = "{}.{}.{}".format(plugin_group, plugin_category, plugin_name)
          if plugin_group not in plugins or (
                  plugin_id not in plugins[plugin_group]):
            log.error("Requesting to call an unknown plugin '{}' in section '{}'".format(
                plugin_id, new_section_path))
            return False
      elif isinstance(value, (dict, list)):
        if not check_parscival_spec_valid_plugins_recursive(plugin_group, new_section_path, value, plugins):
          return False
  elif isinstance(section_content, list):
    for index, item in enumerate(section_content):
      new_section_path = f"{section_path}[{index}]"
      if not check_parscival_spec_valid_plugins_recursive(plugin_group, new_section_path, item, plugins):
        return False
  return True


def check_parscival_spec_valid_plugin_group(sections_to_check, plugin_group, parscival_spec_path):
  """
  Validates if the given sections contain valid plugins for the specified plugin group.

  Args:
      sections_to_check (list): List of section names to be checked.
      plugin_group (str): The name of the plugin group.
      parscival_spec_path (dict): The dictionary representing the path in the specification to be checked.

  Returns:
      bool: True if all plugins are valid, False otherwise.

  The function checks each plugin in the given sections and plugin group to ensure they
  exist in the provided plugins dictionary.
  Logs an error with the specific path if an unknown plugin is found.
  """
  # Try to load plugins
  loader = get_plugins_loader(plugin_group)
  # Exit early if we failed to get the interface of the loader
  if loader is None:
    log.error(f"Failed to load plugins for plugin group '{plugin_group}'")
    return False

  # Get the nested dictionary of plugins
  plugins = loader.plugins

  # Check in the given sections
  for section_name in sections_to_check:
    if section_name in parscival_spec_path:
      section_path = f"{plugin_group}.{section_name}"
      if (not check_parscival_spec_valid_plugins_recursive(plugin_group,
                                                           section_path,
                                                           parscival_spec_path[section_name], plugins)):
        return False

  return True


def check_parscival_spec_version(file_spec_version, engine_version):
  file_version = semver.VersionInfo.parse(file_spec_version)
  engine_version = semver.VersionInfo.parse(engine_version)
  # Compare major versions
  if file_version.major == engine_version.major:
    return True
  return False


def check_parscival_spec_schema(parscival_spec, engine_major_version):
  # Determine the path to the schema file
  package_dir = os.path.dirname(__file__)
  schema_file_path = os.path.join(
      package_dir, 'schemas', str(engine_major_version), 'engine.yaml')

  # Read the schema file
  try:
    with open(schema_file_path, 'r') as schema_file:
      schema = yaml.safe_load(schema_file.read())
      return dogma_schema_validate(parscival_spec, schema)
  except yaml.YAMLError as e:
    log.error("Error while parsing yaml engine schema from '{}': {}".format(
        Path(schema_file_path), str(e.problem_mark).strip()))
    raise e
  except Exception as e:
    log.error("Error while loading engine schema from '{}': {} - {}".format(
        Path(schema_file_path).name, type(e).__name__, e))
    raise e


def check_parscival_spec_config(parscival_spec, parscival_spec_config, section):
  log.info(f"Checking configuration in '{section}'")
  # split the section into keys to traverse both dictionaries
  section_keys = section.split('.')

  # navigate through the parscival_spec to get the corresponding schema
  current_schema = parscival_spec
  for key in section_keys:
    if key in current_schema:
      current_schema = current_schema[key]
    else:
      return True

  # navigate through the parscival_spec_config to get the corresponding document
  current_document = parscival_spec_config
  for key in section_keys:
    if key in current_document:
      current_document = current_document[key]
      if current_document is None:
        break
    else:
      # if the key doesn't exist, use an empty document
      current_document = None
      break

  # if current_document is None, use an empty document
  if current_document is None:
    current_document = {}

  # now, current_schema should have the structure schema
  # and current_document should have the document to validate

  # validate each member in the document against the corresponding schema
  for member_key, member_schema in current_schema.items():
    if isinstance(member_schema, dict) and 'type' in member_schema:
      schema = {member_key: member_schema}
      document = current_document.get(member_key, None)
      document = {member_key: document} if document is not None else {member_key: {}}
      if not dogma_schema_validate(document, schema):
        log.error(f"Configuration for '{member_key}' has errors")
        return False

      # try to normalize the document
      values = dogma_schema_normalize(document, schema)

      if values:
        # assign validated values to parscival_spec
        current_schema[member_key]['config'] = values[member_key]
    else:
      log.error(f"No 'members' key found in the schema for section '{section}'")
      return False

  log.info("The parscival configuration is valid")
  return True


def check_parscival_spec(parscival_spec):
  """
  Validates the structure and referenced variables of a Parscival specification.

  Args:
      parscival_spec (dict): The specification to be validated.

  Returns:
      bool: True if the specification is valid, False otherwise.

  The function performs the following checks:
      - Ensures engine and file specification are compatible.
      - Ensures required top-level keys are present.
      - Ensures 'keys' contains both 'parsing' and 'mapping'.
      - Validates that keys in the first child of 'parsing' are defined in 'keys.parsing'.
      - Ensures target keys in 'mapping.source_targets' are defined in 'keys.mapping'.
      - Ensures variables in 'mapping.target_template' are defined in 'keys.parsing' or 'keys.mapping'.
      - Ensures variables in the 'curating' section are defined in 'keys.parsing' or 'keys.mapping'.
      - Ensures 'type' consistency in 'keys.parsing' and 'keys.mapping'
      - Ensures 'qualifier' consistency in 'keys.parsing' and 'keys.mapping'
      - Ensures no circular references in 'mapping.source_targets'
      - Ensures required structure in 'storing'
      - Ensures required 'mapping', 'curating' plugins are available
  """
  file_spec_version = parscival_spec.get('parscival_spec_version', '1.0.0')
  if not check_parscival_spec_version(file_spec_version, engine_version):
    log.error(
        f"The specification v{file_spec_version} is not compatible with the Parscival Engine v{engine_version}")
    return False

  # validate schema
  if not check_parscival_spec_schema(parscival_spec, engine_major_version):
    return False

  log.info("Specification schema is valid")

  # ensure keys in the first child of 'parsing' are defined in 'keys.parsing'
  parsing_keys = set(parscival_spec['initializing']['keys']['parsing'].keys())

  first_child_key = next(iter(parscival_spec['parsing'].keys()))
  first_child = parscival_spec['parsing'][first_child_key]

  for key, value in first_child.get('keys', {}).items():
    if key not in parsing_keys:
      log.error(f"Non declared key in 'parsing.{first_child_key}.keys': '{key}'")
      return False

  # ensure keys in 'mapping.source_targets' targets are defined in 'keys.mapping'
  mapping_keys = set(parscival_spec['initializing']['keys']['mapping'].keys())
  for source, targets in parscival_spec['mapping'].get('source_targets', {}).items():
    for target in targets:
      if target['target'] not in mapping_keys:
        log.error(
            f"Undefined target key in 'mapping.source_targets': '{target['target']}'")
        return False

  # ensure keys in 'mapping.target_template' are defined in 'keys.mapping'
  for target, sources in parscival_spec['mapping'].get('target_template', {}).items():
    if target not in mapping_keys:
      log.error(f"Undefined target key in 'mapping.target_template': '{target}'")
      return False

    # ensure variables referenced in template are defined in 'keys.parsing' or 'keys.mapping'
    if not check_parscival_spec_referenced_variables(
            f'mapping.target_template.{target}',
            sources,
            parsing_keys,
            mapping_keys):
      return False

  # ensure variables in 'curating' are defined in 'keys.parsing' or 'keys.mapping'
  curating_sections = parscival_spec.get('curating', {})
  if not check_parscival_spec_referenced_variables(
          'curating', curating_sections, parsing_keys, mapping_keys):
    return False

  # check key types consistency in 'keys.parsing' and 'keys.mapping'
  keys_section = parscival_spec.get('keys', {})
  keys_valid_values = {'string', 'integer', 'date'}
  key_to_check = 'type'
  for section_name in ['parsing', 'mapping']:
    if section_name in keys_section:
      if not check_parscival_spec_key_values_consistency(
              f"keys.{section_name}", keys_section[section_name], key_to_check, keys_valid_values):
        return False

  # check qualifier consistency in 'keys.parsing' and 'keys.mapping'
  qualifier_valid_values = {'optional', 'required', 'repeated'}
  key_to_check = 'qualifier'
  for section_name in ['parsing', 'mapping']:
    if section_name in keys_section:
      if not check_parscival_spec_key_values_consistency(
              f"keys.{section_name}", keys_section[section_name], key_to_check, qualifier_valid_values):
        return False

  # check for circular references in 'mapping.target_template'
  if 'mapping' in parscival_spec and 'target_template' in parscival_spec['mapping']:
    if not check_parscival_spec_target_template_circular_references(
            parscival_spec['mapping']['target_template'], 'mapping.target_template'):
      return False

  # check there is not duplicated mappings between mapping.source_targets and
  # mapping.target_template
  if not check_parscival_spec_mapping_duplicate_variables(parscival_spec['mapping']):
    return False

  # check required structure in 'storing'
  required_structure = {
      'plugins': [{}]
  }
  if 'storing' in parscival_spec:
    if not check_parscival_spec_required_structure(parscival_spec['storing'], required_structure, 'storing'):
      return False

  # check mapping plugins
  plugin_group = 'mapping'
  sections_to_check = ['source_targets', 'target_template']
  if not check_parscival_spec_valid_plugin_group(sections_to_check, plugin_group,
                                                 parscival_spec.get('mapping')):
    return False

  # check curating plugins
  plugin_group = 'curating'
  sections_to_check = ['after_initializing', 'before_ingesting',
                       'after_ingesting',    'before_parsing',
                       'after_parsing',      'before_mapping',
                       'after_mapping',      'before_storing',
                       'after_storing',      'before_finishing']
  if not check_parscival_spec_valid_plugin_group(sections_to_check, plugin_group,
                                                 parscival_spec.get('curating')):
    return False

  return True


def get_parscival_spec(file_parscival_spec):
  """Get the parscival specification
  """
  parscival_spec = {
      'data': {},
      'misc': {},
      'category': '',
      'type': '',
      'valid': True
  }

  try:
    parscival_spec['data'] = yaml.safe_load(file_parscival_spec)
    parscival_spec['file'] = file_parscival_spec

    log.info(
        f"Checking specification in [yellow]{Path(file_parscival_spec.name).name}[/yellow]...")
    if not check_parscival_spec(parscival_spec['data']):
      raise ValueError("Specification is invalid")
    log.info("Specification is valid")

    log_spec_info(parscival_spec)

    parser_category = next(iter(parscival_spec['data']['parsing']))

    # shorthand for cateroty and the type of parser
    parscival_spec['category'] = parser_category
    parscival_spec['type'] = parscival_spec['data']['parsing'].get(parser_category)['type']

  except yaml.YAMLError as e:
    log.error("Error while parscival spec {}".format(str(e.problem_mark).strip()))
    parscival_spec['valid'] = False
  except Exception as e:
    log.error("Error loading the parscival specification from '{}': {} - {}".format(
        Path(file_parscival_spec.name).name, type(e).__name__, e))
    parscival_spec['valid'] = False

  return parscival_spec


def parse_dataset(parscival_spec, dataset_info, main_task, main_progress):
  """parse files

  Args:

  Returns:
    Boolean: True if the parsing was successful, False otherwise
  """
  filename_short = dataset_info['shortname']

  if dataset_info['stats']['total'] <= 0:
    log.warning("[cyan]{}[/cyan] - no documents found".format(filename_short))
    return False

  log.info("[cyan]{}[/cyan] - parsing...".format(filename_short))

  # show the progress of the current file parsing
  local_task = main_progress.add_task(
      "[green]Parsing {:<20s}".format(filename_short),
      total=dataset_info['stats']['total'])

  # parse document by document
  document_info = {
      'buffer': "",
      'line': {
          'start': 0
      },
      'tree': None
  }

  document_info['buffer'] = ""
  document_parsed_count = 0
  dataset_line_count = 0
  parser = parscival_spec['parser']

  mm = mmap.mmap(dataset_info['file'].fileno(), 0, access=mmap.ACCESS_READ)
  with contextlib.closing(mm) as dataset:
    for line in iter(dataset.readline, b""):
      # as mmap file is open in read binary (r+b) mode we need to
      # decode it as UTF-8 to use match() and parse()
      line = line.decode('utf-8')

      # increment the number of lines processed
      dataset_line_count += 1

      # for suppress(Exception):
      # @see https://stackoverflow.com/a/15566001/2042871

      # START
      try:
        if parser.can_parse(parscival_spec,
                            dataset_info,
                            document_info,
                            line):
          # test if we have a document buffer to process
          if document_info['buffer']:
            if parser.process(parscival_spec,
                              dataset_info,
                              document_info):
              document_parsed_count += 1

            main_progress.advance(main_task, advance=1)
            main_progress.advance(local_task, advance=1)

          # reinitialize the document buffer
          document_info['buffer'] = parser.buffer_restart(
              parscival_spec,
              dataset_info,
              document_info,
              line)
          document_info['line']['start'] = dataset_line_count
          continue

      except ParseError:
        pass

      except Exception as e:
        log.error(e)
        return False

      # MEMBER OR END
      document_info['buffer'] += line

    # try to parse the last document
    # this is because above documents are only parsed whenever
    # a new document is found
    if document_info['buffer']:
      if parser.process(parscival_spec,
                        dataset_info,
                        document_info):
        # increment only if at least 1 well formed document was found
        if len(dataset_info['documents']):
          document_parsed_count += 1

      main_progress.advance(main_task, advance=1)
      main_progress.advance(local_task, advance=1)

  # update the number of the documents found
  dataset_info['stats']['parsed'] = document_parsed_count

  # update the number of lines scanned
  dataset_info['stats']['lines'] = dataset_line_count

  # document with errors
  document_error_count = 0

  # documents parsed
  log.info("[cyan]{}[/cyan] - {} of {} documents were parsed".format(
      dataset_info['filename'],
      dataset_info['stats']['parsed'],
      dataset_info['stats']['total']
  ))

  # documents missed
  dataset_info['stats']['missed'] = (
      dataset_info['stats']['total'] -
      (dataset_info['stats']['parsed'] + document_error_count))

  # if we found less documents than expected
  if dataset_info['stats']['missed'] > 0:
    # update progress to reflect the number of missed documents
    main_progress.advance(main_task, advance=dataset_info['stats']['missed'])
    main_progress.advance(local_task, advance=dataset_info['stats']['missed'])
    log.warning("[cyan]{}[/cyan] - {} malformed documents were missing".format(
        dataset_info['filename'], dataset_info['stats']['missed']
    ))

  # lines scanned
  log.info("[cyan]{}[/cyan] - {} lines scanned".format(dataset_info['filename'],
                                                       dataset_info['stats']['lines']))

  return True


def normalize_path(file):
  return os.path.normpath(str(Path(file).resolve().absolute()))


def remove_duplicates(input_list):
    seen = set()
    result = []
    for item in input_list:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def get_plugins_loader(plugin_group, package_name='parscival_plugins'):
  """get the pluginlib interface to import and access plugins of a targeted type

  Args:
    plugin_group(str): Retrieve plugins of a group ('storing', 'mapping', ...)

  Returns:
    Class: Interface for importing and accessing plugins
  """
  # get the plugin loader
  loader = pluginlib.PluginLoader()

  # return early if the group is already loaded
  if loader is not None and plugin_group in loader.plugins:
    return loader

  try:
    # get the semicolon delimited list of paths from environment
    plugins_paths = os.getenv('PARSCIVAL_PLUGINS_PATHS')

    # create a list of paths
    if plugins_paths is not None:
      plugins_paths = plugins_paths.split(';')
    else:
      plugins_paths = []

    # find the location of the package
    package_spec = importlib.util.find_spec(package_name)
    if package_spec and package_spec.submodule_search_locations:
      # Use the first location listed in submodule_search_locations
      package_path = Path(package_spec.submodule_search_locations[0])
      plugins_fallback_path = str(package_path)
      plugins_paths.insert(0, plugins_fallback_path)

    if not plugins_fallback_path:
      # compute a fallback path relative to project
      plugins_fallback_path = str(Path.joinpath(
          Path(__file__).parent.parent.relative_to
          (Path(__file__).parent.parent.parent),
          package_name))
      plugins_paths.insert(0, plugins_fallback_path)

    # add some extra paths from site-packages directories
    sitepackages = site.getsitepackages() + [site.getusersitepackages()]
    for path in sitepackages:
      plugins_paths.insert(0, str(Path.joinpath(Path(path), package_name)))

    # append the plugin type to each of paths
    plugins_type_paths = [os.path.join(p, plugin_group) for p in plugins_paths]
    # remove non-existing paths
    plugins_type_paths = [p for p in plugins_type_paths if os.path.isdir(p)]

    # test if there is at least one valid path
    if not plugins_type_paths:
      log.error("There are not valid paths pointed out by '%s'",
                'PARSCIVAL_PLUGINS_PATHS')
      return None

    # remove duplicate paths
    plugins_type_paths = remove_duplicates(plugins_type_paths)

    # recursively load plugins from paths
    loader = pluginlib.PluginLoader(paths=plugins_type_paths)

  except pluginlib.PluginImportError as e:
    if e.friendly:
      log.error("{}".format(e))
    else:
      log.error("Unexpected error loading %s plugins", plugin_group)
    return None

  # and return loader
  return loader


def data_binary_search_id(data_list, target_id):
  left, right = 0, len(data_list) - 1
  result = []

  # perform binary search to find one occurrence of the target id
  while left <= right:
    mid = (left + right) // 2
    mid_id = data_list[mid]['id']

    if mid_id == target_id:
      # find all occurrences of the target id
      result.append(data_list[mid])

      # search to the left of mid
      sl = mid - 1
      while sl >= 0 and data_list[sl]['id'] == target_id:
        result.append(data_list[sl])
        sl -= 1

      # search to the right of mid
      sr = mid + 1
      while sr < len(data_list) and data_list[sr]['id'] == target_id:
        result.append(data_list[sr])
        sr += 1

      return result

    elif mid_id < target_id:
      left = mid + 1
    else:
      right = mid - 1

  # return empty list if the id is not found
  return result


def group_mapping_nodes(data):
  """
  Groups mapping items by 'id', 'rank', and 'parserank', and includes
  additional metadata in the output.

  Args:
    data (dict): A dictionary where keys are mapping key names and values are lists
      of dictionaries containing the following keys:
      - 'id' (int): The identifier for the group.
      - 'rank' (int): The rank within the group.
      - 'parserank' (int): The parserank within the group.
      - 'data' (str): The data associated with the entry.

  Returns:
    list: A list of dictionaries where each dictionary represents a grouped entry.

    Each dictionary contains:
      - '_id' (int): The identifier for the group.
      - '_rank' (int): The rank within the group.
      - '_parserank' (int): The additional ranking metric.
      - [source_name] (str or list): The data associated with the entry,
        either as a single string if there's one entry or as a list of strings
        if there are multiple entries.

  Example:
    .. code-block:: python

      data = {
          'OtherSourceDate': [
              {'file': 'file1.html', 'id': 1, 'rank': 2, 'parserank': 0, 'data': '2020-01-01'},
              {'file': 'file2.html', 'id': 1, 'rank': 2, 'parserank': 1, 'data': '2020-01-02'}
          ],
          'OtherSourceName': [
              {'file': 'file3.html', 'id': 1, 'rank': 2, 'parserank': 0, 'data': 'Source A'},
              {'file': 'file4.html', 'id': 1, 'rank': 2, 'parserank': 1, 'data': 'Source B'}
          ]
      }

      grouped_data = group_sources(data)
      # grouped_data will be:
      # [
      #   {'_id': 1, '_rank': 2, '_parserank': 0, 'OtherSourceDate': '2020-01-01', 'OtherSourceName': 'Source A'},
      #   {'_id': 1, '_rank': 2, '_parserank': 1, 'OtherSourceDate': '2020-01-02', 'OtherSourceName': 'Source B'}
      # ]
  """
  # create a dictionary to store entries by (id) with rank = 0 and parserank = 0
  base_dict = {}
  grouped_dict = {}

  # First pass: Group items by (id) where rank and parserank are both 0
  for source_name, items in data.items():
    for item in items:
      if item['rank'] == 0 and item['parserank'] == 0:
        key = item['id']
        if key not in base_dict:
          base_dict[key] = {'_id': item['id'], '_rank': 0, '_parserank': 0}
        if source_name not in base_dict[key]:
          base_dict[key][source_name] = []
        base_dict[key][source_name].append(item['data'])

  # second pass: Loop over items where rank > 0, clone the base item, update
  # the data and the rank, and add the new item
  for source_name, items in data.items():
    for item in items:
      if item['rank'] > 0:
        base_key = item['id']
        new_key = (item['id'], item['rank'], 0)

        if base_key in base_dict:
          if new_key not in grouped_dict:
            grouped_dict[new_key] = base_dict[base_key].copy()
          grouped_dict[new_key]['_rank'] = item['rank']
          if source_name not in grouped_dict[new_key]:
            grouped_dict[new_key][source_name] = []
          grouped_dict[new_key][source_name] = [item['data']]
        else:
          # If there is no base item, initialize new entry
          grouped_dict[new_key] = {
              '_id': item['id'],
              '_rank': item['rank'],
              '_parserank': 0,
              source_name: [item['data']]
          }

  # third pass: Group items by (id, rank) where parserank is 0
  for source_name, items in data.items():
    for item in items:
      if item['parserank'] == 0:
        key = (item['id'], item['rank'], 0)
        if key not in grouped_dict:
          grouped_dict[key] = {'_id': item['id'],
                               '_rank': item['rank'], '_parserank': 0}
        if source_name not in grouped_dict[key]:
          grouped_dict[key][source_name] = []
        grouped_dict[key][source_name] = [item['data']]

  # fourth pass: Loop over items where rank > 0 and parserank > 0, clone the base item,
  # update the data and the parserank, and add the new item
  for source_name, items in data.items():
    for item in items:
      if item['rank'] > 0 and item['parserank'] > 0:
        base_key = (item['id'], item['rank'], 0)
        new_key = (item['id'], item['rank'], item['parserank'])

        if base_key in grouped_dict:
          grouped_dict[new_key] = grouped_dict[base_key].copy()
          grouped_dict[new_key]['_parserank'] = item['parserank']
          if source_name not in grouped_dict[new_key]:
            grouped_dict[new_key][source_name] = []
          grouped_dict[new_key][source_name] = [item['data']]
        else:
          # If there is no base item, initialize new entry
          grouped_dict[new_key] = {
              '_id': item['id'],
              '_rank': item['rank'],
              '_parserank': item['parserank'],
              source_name: [item['data']]
          }

  # Create the final grouped list directly from grouped_dict
  grouped_list = []
  for key, sources in grouped_dict.items():
    entry = {
        '_id': sources['_id'],
        '_rank': sources['_rank'],
        '_parserank': sources['_parserank']
    }
    for source_name, data_list in sources.items():
      if source_name not in ['_id', '_rank', '_parserank']:
        if len(data_list) == 1:
          entry[source_name] = data_list[0]
        else:
          entry[source_name] = data_list
    grouped_list.append(entry)

  return grouped_list


@logging_decorator(logging_default_context)
def call_node_plugins(spec_node,
                      plugins,
                      parscival_spec,
                      parscival_data,
                      nodes,
                      map_key,
                      document_id,
                      plugin_group):
  """
  Calls the plugins defined in the mapping for the given key.

  Args:
    mapping (dict): The spec node containing the list of plugins to call.
    plugins (dict): The loaded plugins.
    parscival_spec (dict): The parscival specification.
    parscival_data (dict): The parsing data.
    nodes (list): The list of nodes to process.
    map_key (str): The key being processed.
    document_id (int): The ID of the document being processed.
  """
  if 'plugins' in spec_node and spec_node['plugins'] is not None:
    for plugin_call in spec_node['plugins']:
      plugin_category = list(plugin_call.keys())[0]
      plugin_name = list(plugin_call.values())[0]
      plugin_id = "{}.{}.{}".format(plugin_group, plugin_category, plugin_name)

      # get the requested plugin
      plugin = plugins[plugin_group][plugin_id]

      # get plugin parameters
      params = plugin_call['params'] if 'params' in plugin_call and plugin_call['params'] else {
      }
      if 'enabled' not in params or params['enabled'] is True:
        # update the logging context with the prefix of the plugin
        logging_set_context(log, LoggingMixin.get_logging_prefix(plugin))

        # call the process function of each plugin
        log.debug(
            "Calling plugin '[green]{}[/green]' for key '{}' in document {}".format(plugin_id, map_key, document_id))

        if not plugin.process(parscival_spec, parscival_data, nodes, **params):
          log.warning("Plugin '{}' finished with issues for key '{}' and nodes: {}".format(
              plugin_id, map_key, nodes))
      else:
        log.debug("Ignoring plugin '[green]{}[/green]'".format(plugin_id))


@logging_decorator(logging_default_context)
def map_parsed_data_source_targets(parscival_spec,
                                   parscival_data,
                                   plugins,
                                   main_task,
                                   main_progress):
  log.info("Processing mappings of type: 'source_targets'")
  source_targets = parscival_spec['data']['mapping']['source_targets']

  # loop over datasets and documents
  file_id = 0
  document_id = 0
  for dataset_info in parscival_data['datasets']:
    main_progress.advance(main_task, advance=1)

    shortname = dataset_info['shortname']
    documents = dataset_info['documents']

    # loop over parsed documents
    for document in documents:
      document_key_rank_id = {}
      # 'source_targets': loop over key-values
      for key, value in document:
        # loop over key mappings
        # TODO(martinec) lint check if key exists before outer loops

        # get mappings for the current key
        mappings = source_targets.get(key, [])

        # do nothing if there are not mappings
        if not mappings:
          continue

        # loop over each mapping
        for mapping in mappings:
          # key to create
          map_key = mapping['target']

          # check if the rank key is defined by the current mapping key
          # or if it depends on a key referenced by the 'rank' attribute
          rank_key = mapping.get('rank', map_key)

          # initialize or increase the rank id counter for this key
          if rank_key not in document_key_rank_id:
            document_key_rank_id[rank_key] = 0
          # increase the rank id counter for this key
          elif map_key == rank_key:
            document_key_rank_id[rank_key] = document_key_rank_id[rank_key] + 1

          # get the current rank id
          rank_id = document_key_rank_id[rank_key]

          # if needed, initialize the mappings for this key
          parscival_data['mappings'].setdefault(map_key, [])

          # create a list of nodes with a default node row
          nodes = [
              {
                  'file': shortname,
                  'id': document_id,
                  'rank': rank_id,
                  'parserank': 0,
                  'data': value
              }
          ]

          # call requested plugins
          call_node_plugins(mapping,
                            plugins,
                            parscival_spec,
                            parscival_data,
                            nodes,
                            key,
                            document_id,
                            'mapping')

          # filter nodes to include only those where 'data' is not None
          filtered_nodes = [node for node in nodes if node['data'] is not None]

          # add the mapped nodes for the current key
          parscival_data['mappings'][map_key].extend(filtered_nodes)

      # increase the document_id
      document_id += 1

    # increase file id
    file_id += 1

  return True


def map_parsed_data_check_template_variables(parscival_data, target_template, env):
  # check if the required key mappings exist
  for map_key, mapping in target_template.items():
    # parse the template for the current mapping
    ast = env.parse(mapping['template'])
    template_variables = meta.find_undeclared_variables(ast)

    # use set operations for efficient checking
    missing_variables = template_variables - parscival_data['mappings'].keys()
    if missing_variables:
      for variable in missing_variables:
        log.warning("target_template.'{}' requires the key '{}'".format(map_key, variable))
      return False
  return True


@logging_decorator(logging_default_context)
def map_parsed_data_target_template(parscival_spec, parscival_data, plugins):
  log.info("Processing mappings of type: 'target_template'")
  target_template = parscival_spec['data']['mapping']['target_template']
  env = jinja2.Environment()

  # Check if the required key mappings exist
  if not map_parsed_data_check_template_variables(parscival_data, target_template, env):
    return False

  # pre-parse the templates and extract variables
  template_cache = {}
  for map_key, mapping in target_template.items():
    template_string = mapping['template']
    ast = env.parse(template_string)
    template_variables = meta.find_undeclared_variables(ast)
    template_cache[map_key] = {
        'template': jinja2.Template(template_string),
        'variables': template_variables,
        'rank_key': mapping.get('rank', map_key)
    }

  # pre-allocate mappings
  for map_key in template_cache:
    parscival_data['mappings'].setdefault(map_key, [])

  # loop over datasets and documents
  file_id = 0
  document_id = 0
  for dataset_info in parscival_data['datasets']:
    shortname = dataset_info['shortname']

    # loop over parsed documents
    for document in dataset_info['documents']:
      document_key_rank_id = {}

      for map_key, cache in template_cache.items():
        # initialize or increase the rank id counter for this key
        rank_key = cache['rank_key']
        # check if we need to initialize the rank id counter for this key
        if rank_key not in document_key_rank_id:
          document_key_rank_id[rank_key] = 0
        # increase the rank id counter for this key
        elif map_key == rank_key:
          document_key_rank_id[rank_key] = document_key_rank_id[rank_key] + 1

        # get the current rank id
        rank_id = document_key_rank_id[rank_key]

        try:
          # prepare the context nodes for the template
          template_context_nodes = {}
          for key_name in cache['variables']:
            document_key_nodes = data_binary_search_id(
                parscival_data['mappings'][key_name],
                document_id)
            # assign the nodes to the template context
            template_context_nodes.setdefault(
                key_name, []).extend(document_key_nodes)

          # group template context nodes by 'id', 'rank', and 'parserank'
          group_template_context = group_mapping_nodes(template_context_nodes)

          # default settings if the template is not using variables
          if not group_template_context:
            group_template_context.append({
                '_id': document_id,
                '_rank': rank_id,
                '_parserank': 0,
            })

          for template_context in group_template_context:
            resolved_template = cache['template'].render(template_context)

            # skip empty templates
            if not resolved_template:
              continue

            # Create a list of nodes with a default node row
            nodes = [{
                'file': shortname,
                'id': template_context['_id'],
                'rank': template_context['_rank'],
                'parserank': template_context['_parserank'],
                'data': resolved_template
            }]

            # Call requested plugins
            call_node_plugins(target_template[map_key],
                              plugins,
                              parscival_spec,
                              parscival_data,
                              nodes,
                              map_key,
                              document_id,
                              'mapping')

            # Filter nodes to include only those where 'data' is not None
            filtered_nodes = [node for node in nodes if node['data'] is not None]

            # Add the mapped nodes for the current key
            parscival_data['mappings'][map_key].extend(filtered_nodes)

        except Exception as e:
          log.warning("Unknown error while resolving '{}' template: {} - {}".format(
              map_key, type(e).__name__, e.__doc__))
          return False

      # Increase the document_id
      document_id += 1

    # increase file id
    file_id += 1

  return True


def map_parsed_data(parscival_spec, parscival_data, main_task, main_progress):
  """map an already parsed dataset according to a spec

  Args:

  Returns:
    Boolean: True if the mapping is successful, False otherwise
  """
  # try to load plugins
  plugin_category = 'mapping'

  # try to load plugins
  loader = get_plugins_loader(plugin_category)

  # exit early if we failed to get the interface of the loader
  if loader is None:
    return False

  # get the nested dictionary of plugins
  plugins = loader.plugins

  # first pass: 'source_targets'
  if not map_parsed_data_source_targets(parscival_spec,
                                        parscival_data,
                                        plugins,
                                        main_task,
                                        main_progress):
    return False

  # return early if not 'target_template' are needed
  if 'target_template' not in parscival_spec['data']['mapping']:
    return True

  # second pass: 'target_template'
  if not map_parsed_data_target_template(parscival_spec,
                                         parscival_data,
                                         plugins):
    return False

  return True


def curate_data(process_stage, parscival_spec, parscival_data, main_task, main_progress):
  """curate data according to a spec

  Args:

  Returns:
    Boolean: True if the process is successful, False otherwise
  """

  # check if there are curating tasks to be performed
  if 'curating' not in parscival_spec['data']:
    return True

  # check if there are curating tasks for this stage
  if (process_stage not in parscival_spec['data']['curating'] or
      parscival_spec['data']['curating'][process_stage] is None):
    return True

  # try to load plugins
  plugin_group = 'curating'
  loader = get_plugins_loader(plugin_group)
  # exit early if we failed to get the interface of the loader
  if loader is None:
    return False

  # get the nested dictionary of plugins
  plugins = loader.plugins

  # check if there are plugings to call for this processing stage
  if not ('plugins' in parscival_spec['data'][plugin_group][process_stage] and
          parscival_spec['data'][plugin_group][process_stage]['plugins'] is not None):
    return False

  # now loop calling the requested plugins
  for plugin_call in parscival_spec['data'][plugin_group][process_stage]['plugins']:
    try:
      main_progress.advance(main_task, advance=1)
      # get the group and name of the requested plugin
      plugin_type = list(plugin_call.keys())[0]
      plugin_name = list(plugin_call.values())[0]
      plugin_id = "{}.{}.{}".format(plugin_group, plugin_type, plugin_name)

      if plugin_id not in plugins[plugin_group]:
        log.error("Plugin '[green]{}[/green]' not found".format(plugin_id))
        return False

      # get the request plugin
      plugin = plugins[plugin_group][plugin_id]

      # update the logging context with the prefix of the plugin
      logging_set_context(log, LoggingMixin.get_logging_prefix(plugin))

      # call the process function of this plugin
      log.info("Calling plugin '[green]{}[/green]'".format(plugin_id))
      params = plugin_call['params'] if 'params' in plugin_call and plugin_call['params'] else {
      }
      if 'enabled' not in params or params['enabled'] is True:
        if plugin.process(parscival_spec, parscival_data, **params):
          log.debug("The execution of '{}' was successful".format(plugin_id))
        else:
          log.error("Plugin '{}' finished with errors".format(plugin_id))
          return False
      else:
        log.debug("Ignoring plugin '[green]{}[/green]'".format(plugin_id))
    except Exception as e:
      log.debug(f"{e}")
      return False

  return True


@logging_decorator(logging_default_context)
def store_parsed_data(parscival_spec,
                      parscival_data,
                      output_info,
                      main_task,
                      main_progress):
  """store parsed data

  Args:

  Returns:
    Boolean: True if the store is successful, False otherwise
  """
  try:
    # try to load plugins
    plugin_group = 'storing'
    loader = get_plugins_loader(plugin_group)

    # exit early if we failed to get the interface of the loader
    if loader is None:
      return False

    # get the nested dictionary of plugins
    plugins = loader.plugins

    # first loop to check if the requested plugins are available
    store_type = output_info['type']
    for plugin_call in parscival_spec['data'][plugin_group][store_type]['plugins']:
      plugin_category = list(plugin_call.keys())[0]
      plugin_name = list(plugin_call.values())[0]
      plugin_id = "{}.{}.{}".format(plugin_group, plugin_category, plugin_name)

      # test if plugin exists
      if plugin_group not in plugins or plugin_id not in plugins[plugin_group]:
        log.error("Calling undefined plugin '{}' while processing output of type '{}'".format(
                  plugin_id, store_type))
        return False

    # now we call each plugin following the declaration order
    log.info("Processing output of type '[green]{}[/green]'".format(store_type))
    for plugin_call in parscival_spec['data'][plugin_group][store_type]['plugins']:
      main_progress.advance(main_task, advance=1)
      plugin_category = list(plugin_call.keys())[0]
      plugin_name = list(plugin_call.values())[0]
      plugin_id = "{}.{}.{}".format(plugin_group, plugin_category, plugin_name)

      # get the request plugin
      plugin = plugins[plugin_group][plugin_id]

      # update the logging context with the prefix of the plugin
      logging_set_context(log, LoggingMixin.get_logging_prefix(plugin))

      params = plugin_call['params'] if 'params' in plugin_call and plugin_call['params'] else {
      }
      if 'enabled' not in params or params['enabled'] is True:
        # call the process function of each plugin
        log.info("Calling plugin '[green]{}[/green]'".format(plugin_id))
        if plugin.process(parscival_spec, parscival_data, output_info, **params):
          log.debug("The execution of '{}' was successful".format(plugin_id))
        else:
          log.error("Plugin '{}' finished with errors".format(plugin_id))
          return False
      else:
        log.debug("Ignoring plugin '[green]{}[/green]'".format(plugin_id))

  except pluginlib.PluginImportError as e:
    if e.friendly:
      log.error("{}".format(e))
    else:
      log.error("Unexpected error loading %s plugins", plugin_group)
    return False

  return True


def load_parsing_plugin(parscival_spec):
  # Load parsing plugins
  plugin_group = 'parsing'
  try:
    loader = get_plugins_loader(plugin_group)

    # exit early if we failed to get the interface of the loader
    if loader is None:
      return False

    # get the nested dictionary of plugins
    plugins = loader.plugins

  except pluginlib.PluginImportError as e:
    if e.friendly:
      log.error("{}".format(e))
    else:
      log.error("Unexpected error loading %s plugins", plugin_group)
    return False

  parser_category = parscival_spec['category']
  parser_type = parscival_spec['type']
  plugin_id = "{}.{}.{}".format(plugin_group, parser_category, parser_type)

  # test if parsing plugin exists
  if plugin_group not in plugins or plugin_id not in plugins[plugin_group]:
    log.error("Requesting to use an unknown parsing plugin '{}'".format(
              plugin_id))
    return False

  # get the requested parser plugin
  parscival_spec['parser'] = plugins[plugin_group][plugin_id]

  # call the parser initialization routine
  log.info("Calling plugin '{}'".format(plugin_id))
  if not parscival_spec['parser'].init(parscival_spec):
    log.error("Parsing plugin '{}' - Initialization error".format(
              plugin_id))
    return False

  return True


def initialize_parscival_data(file_datasets):
  return {
      'files': file_datasets,
      'datasets': [],
      'mappings':  {},
      'transient': {
          'files': [],
          'directories': []
      },
      'stats': {
          'total': 0,
          'parsed': 0,
          'missed': 0,
          'lines': 0,
          'files': 0
      },
      'status': {
          'processed': False
      }
  }


@logging_decorator(logging_default_context)
def task_curating(phase, parscival_spec, parscival_data, progress):
  curating_phases = ['after_initializing', 'before_ingesting',
                     'after_ingesting',    'before_parsing',
                     'after_parsing',      'before_mapping',
                     'after_mapping',      'before_storing',
                     'after_storing',      'before_finishing']
  if phase not in curating_phases:
    log.error(f"'Invaliding curating phase: '{phase}'")
    return False

  if phase in parscival_spec['data']['curating']:
    log.info(f"Curating data... ([yellow]{phase}[/yellow])")
    curating_task = progress.add_task(
        "Curating data", total=len(parscival_spec['data']['curating'][phase]))
    if not curate_data(phase, parscival_spec, parscival_data, curating_task, progress):
      log.error(f"Unexpected error curating data for phase {phase}")
      return False
    progress.advance(curating_task, advance=len(
        parscival_spec['data']['curating'][phase]))

  return True

def log_spec_info(parscival_spec):
  log.info("Identifier: [yellow]{}-{}-{}-{}[/yellow]".format(
      parscival_spec['data']['source'],
      parscival_spec['data']['schema'],
      parscival_spec['data']['format'],
      parscival_spec['data']['version']))

  log.info("Description: [yellow]{}[/yellow]".format(
      parscival_spec['data']['description']))

  log.info("Pipeline: [yellow]{}[/yellow]".format(
      parscival_spec['data']['pipeline']))

def log_parsing_info(parscival_spec):
  log.info("Parser category: [yellow]{}[/yellow]".format(
      parscival_spec['category']))

  log.info("Parser type: [yellow]{}[/yellow]".format(
      parscival_spec['type']))

@logging_decorator(logging_default_context)
def task_parsing(parscival_spec, parscival_data, progress):
  log.info("Starting parsing process...")
  log_parsing_info(parscival_spec)

  # load parsing plugins
  if not load_parsing_plugin(parscival_spec):
    log.critical("It was not possible to initialize the parser plugin")
    return False

  # update the logging context with the prefix of the parsing plugin
  logging_set_context(log, LoggingMixin.get_logging_prefix(parscival_spec['parser']))

  dataset_parsing_task = progress.add_task("Parsing files",
                                           total=parscival_data['stats']['total'])

  log.info("Parsing data...")
  # parse each dataset
  for dataset_info in parscival_data['datasets']:
    if parse_dataset(parscival_spec, dataset_info, dataset_parsing_task, progress):
      # update stats
      parscival_data['stats']['parsed'] += dataset_info['stats']['parsed']
      parscival_data['stats']['missed'] += dataset_info['stats']['missed']
      parscival_data['stats']['lines'] += dataset_info['stats']['lines']

  # check if there is at least 1 parsed document
  if parscival_data['stats']['parsed'] <= 0:
    log.error("No documents parsed. Nothing to do!")
    return False

  return True


def task_parsing_log_global_stats(parscival_data):
  if parscival_data['stats']['files'] > 1:
    # total parsed
    log.info("{} of {} documents were parsed".format(parscival_data['stats']['parsed'],
                                                     parscival_data['stats']['total']))
    # total missed
    if parscival_data['stats']['missed'] > 1:
      log.info("{} malformed documents were missing".format(
          parscival_data['stats']['missed']))

    # lines scanned
    log.info("{} lines scanned".format(parscival_data['stats']['lines']))


@logging_decorator(logging_default_context)
def task_mapping(parscival_spec, parscival_data, progress):
  # map whole parsed data according to the spec
  log.info("Mapping data...")
  # FIXME(martinec) total is not equal to the number of docs, but the number of key to map
  dataset_mapping_task = progress.add_task("Mapping data",
                                           total=len(parscival_data['datasets']))
  if not map_parsed_data(parscival_spec, parscival_data, dataset_mapping_task, progress):
    log.error("Unexpected error mapping data")
    return False
  progress.advance(dataset_mapping_task, advance=len(parscival_data['datasets']))
  return True


@logging_decorator(logging_default_context)
def task_storing(parscival_spec, parscival_data, output_info, progress):
  # dump from the cache to the archive representing the parsed data
  parscival_data.dump()

  # store whole parsed data according to the requested output type
  log.info("Storing data...")
  store_type = output_info['type']

  dataset_storing_task = progress.add_task("Storing data",
                                           total=len(parscival_spec['data']['storing'][store_type]['plugins']))
  if not store_parsed_data(parscival_spec,
                           parscival_data,
                           output_info,
                           dataset_storing_task,
                           progress):
    log.error("Unexpected error storing data")
    return False

  progress.advance(dataset_storing_task,
                   advance=len(parscival_spec['data']['storing'][store_type]['plugins']))

  return progress.finished


def log_finishing_stats(parscival_data):
  log.info("Process successfully completed...")
  log.info(f"Files processed: {parscival_data['stats']['files']}")
  log.info(f"Lines scanned: {parscival_data['stats']['lines']}")
  log.info(
      f"Documents found: {parscival_data['stats']['total']}, "
      f"parsed: {parscival_data['stats']['parsed']}, "
      f"missed: {parscival_data['stats']['missed']}, "
      f"duplicated: {parscival_data['stats']['duplicated']}, "
      f"unique: {parscival_data['stats']['unique']}"
  )


@logging_decorator(logging_default_context)
def resolve_parscival_spec(parscival_spec):
  """
  Resolve all variables in the parscival_spec YAML content using Jinja2.

  Args:
    parscival_spec (dict): Loaded YAML content to be processed.

  Returns:
    dict: Processed YAML content with all variables resolved.
  """
  log.info("Processing interpolated variables '${}' in the specification...")

  missing_key = '__dogma::MISSING__'
  unresolved_optional_key = '__dogma::UNRESOLVED_OPTIONAL__'

  def clean_unresolved_optionals(node):
    """
    Recursively remove any field whose value is the unresolved optional sentinel.

    Args:
      node (Any): The resolved YAML structure.

    Returns:
      Cleaned version without unresolved optional placeholders.
    """
    if isinstance(node, dict):
      return {
        k: clean_unresolved_optionals(v)
        for k, v in node.items()
        if v != unresolved_optional_key
      }
    elif isinstance(node, list):
      return [clean_unresolved_optionals(v) for v in node if v != unresolved_optional_key]
    else:
      return node

  # helper for safe nested access
  def optional_lookup(path, default=unresolved_optional_key):
    if not isinstance(path, str):
      raise TypeError(
        f"optional() expected a string path as first argument, "
        f"but got {type(path).__name__}: {path!r}. "
        f"Did you forget to quote it? Use: optional(\"your.path.here\")"
      )
    try:
      value = box_context
      for part in path.split('.'):
        value = value[part]
      if value == missing_key:
        return default
      return value
    except Exception:
      return default

  # Configure Jinja2 to use ${} for variables
  env = jinja2.Environment(
      variable_start_string='${',
      variable_end_string='}',
      autoescape=False
  )

  # add optional to env globals
  env.globals["optional"] = optional_lookup

  def recursive_resolve(content, context, track=None):
    """
    Recursively resolve variables in the content using the provided context.

    Args:
      content (dict, list, str): The content to process.
      context (dict): The context for variable resolution.
      track (set): Set of variables currently being resolved to avoid circular references.

    Returns:
      The content with variables resolved.
    """
    if track is None:
      track = set()

    if isinstance(content, Mapping):
      resolved_content = {}
      for key, value in content.items():
        resolved_key = recursive_resolve(key, context, track)
        resolved_value = recursive_resolve(value, context, track)
        resolved_content[resolved_key] = resolved_value
      return resolved_content
    elif isinstance(content, list):
      return [recursive_resolve(item, context, track) for item in content]
    elif isinstance(content, str):
      # Check for circular references
      if content in track:
        raise ValueError(f"Circular reference detected: '{content}'")
      track.add(content)

      while isinstance(content, str) and '${' in content and '}' in content:
        log.debug(f"Substituting variable: '{content}'")
        if '.values' in content:
          raise ValueError(
              f"Unable to resolve variable: '{content}', 'values' is a reserved keyword")
        template = env.from_string(content)
        try:
          # render the template
          new_content = template.render(context)

          # the path exists, but the variable is missed
          if new_content == missing_key:
            raise ValueError(f"Missing value: '{content}'")
          elif not new_content:
            # try to get the variable directly from context
            try:
              # template variable '${foo}' becomes 'spec'
              variable_value = content[2:-1]
              variable_value = context[variable_value]
            except Exception as e:
              raise ValueError(f"Invalid variable reference: '{content}': {e}")

            # check if the variable resolves to empty
            if not new_content:
              log.warning(f"Variable '{content}' resolves to an empty string")

          # check if nothing was resolved
          if new_content == content:
            break

          # assign the new content
          try:
            data = yaml.safe_load(new_content)
          except yaml.YAMLError as e:
            log.error(f"Failed to parse YAML content: {new_content}")
            raise ValueError(f"Invalid YAML format: {e}")
          if data is not None:
            content = data
          else:
            content = new_content
        except jinja2.exceptions.UndefinedError as e:
          raise ValueError(f"Cannot resolve variable: '{content}': {e}")
        except Exception as e:
          raise e

      if content in track:
        track.remove(content)
      return content
    else:
      return content

  # box_dots, makes my_box.a.b.c also be accessible via my_box["a.b.c"]
  box_context = Box(parscival_spec, default_box=True,
                    box_dots=True, default_box_attr=missing_key)
  # resolve '${variables}'
  parscival_spec_resolved = recursive_resolve(parscival_spec, box_context)
  # clean up unresolved optional values
  parscival_spec_resolved = clean_unresolved_optionals(parscival_spec_resolved)
  return parscival_spec_resolved


@logging_decorator(logging_default_context)
def task_initializing(args, parscival, progress):
  log.info("Initializing...")
  initializing_task = progress.add_task("Initializing", total=1)

  # try to load plugins
  plugin_group = 'initializing'
  loader = get_plugins_loader(plugin_group)

  # exit early if we failed to get the interface of the loader
  if loader is None:
    return False

  # get the nested dictionary of plugins
  # plugins = loader.plugins

  file_parscival_spec = args.file_parscival_spec
  file_output = args.file_output
  file_datasets = args.file_datasets

  # first get the specification
  parscival['spec'] = get_parscival_spec(file_parscival_spec)
  if parscival['spec']['valid'] is False or 'data' not in parscival['spec']:
    log.critical("The parscival specification is not valid")
    parscival['data'] = None
    return False

  # load the configuration
  parscival_spec_config = combine_configuration_files(args.configuration_files)

  # validate parscival_spec_config
  if not check_parscival_spec_config(parscival['spec']['data'], parscival_spec_config, "initializing.args"):
    log.critical("The parscival configuration is not valid")
    parscival['data'] = None
    return False

  # substitute interpolated '${foo}' variables
  parscival_spec_resolved = resolve_parscival_spec(parscival['spec']['data'])
  if not parscival_spec_resolved:
    log.critical("Error resolving the parscival specification")
    parscival['data'] = None
    return False

  # compare original vs resolved specification
  log.debug(DeepDiff(parscival['spec']['data'],
                     parscival_spec_resolved,
                     verbose_level=2,
                     view='text'))

  # update the spec
  parscival['spec']['data'].update(parscival_spec_resolved)

  # initial dictionary to seed the hdf5 parscival_data
  parscival_data_init_dict = initialize_parscival_data(file_datasets)

  # check the type of the output to create
  # /path/to/foo.bar.zaz
  # foo
  output_name = file_output.with_suffix('').stem
  # bar.zaz
  output_extension = file_output.name[len(output_name)+1:]

  # keep track about the requested output
  parscival['output_info'] = {
      'type': None,
      'file': file_output
  }

  # by default we need to create a hdf5
  parscival_data_output_file = str(Path.joinpath(
      file_output.parent, output_name + '.hdf5'))
  log.info(
      "Saving intermediate processing data on [yellow]{}[/yellow]".format(parscival_data_output_file))

  # only .hdf5 and spec tranforms format types are valid
  if output_extension != 'hdf5':
    if 'storing' not in parscival['spec']['data']:
      log.critical("No 'storing' key found on the parscival specification")
      parscival['data'] = parscival_data_init_dict
      return False

    # eg. cortext.json or cortext.db
    parscival['output_info']['type'] = output_extension
    if output_extension not in parscival['spec']['data']['storing']:
      log.critical("A valid output type is required to continue")
      log.critical("Requested output type: [yellow].{}[/yellow]"
                   .format(output_extension))
      log.critical("The known output types are: [yellow][.hdf5; .{}][/yellow]"
                   .format('; .'.join(parscival['spec']['data']['storing'])))
      parscival['data'] = parscival_data_init_dict
      return False

  # ensure to have an empty output file
  open(parscival_data_output_file, 'w').close()

  # initialize a dictionary with a single hdf5 file archive backend
  parscival['data'] = klepto.archives.hdf_archive(
      parscival_data_output_file,
      dict=parscival_data_init_dict,
      cached=True,
      meta=True)

  # only continues if we have a valid specification
  if not parscival['spec']['valid']:
    log.critical("A valid specification is required to continue")
    return False

  progress.advance(initializing_task, advance=1)
  return True


class TimeColumn(TextColumn):
  def __init__(self):
    super().__init__("")

  def render(self, task: Task) -> Text:
    current_time = datetime.now().strftime('%X')
    return Text(f"[{current_time}]")

  def get_table_column(self) -> Column:
    return Column(header="Time")


class StatusTextColumn(TextColumn):
  def render(self, task: Task) -> RenderableType:
      # Access custom status from the task fields
    status = task.fields.get("status", "[  ]")
    # Render the text with the status included, using Text.from_markup to preserve markup
    text = Text.from_markup(f"[green]{status}[/green] [cyan]{task.description}[/cyan]")
    return text


class WorkerProgress(Progress):
  def add_task(self, description, *args, **kwargs):
    # Add custom fields in the task
    task_id = super().add_task(description, *args, **kwargs)
    self.update(task_id, status="[  ]")
    return task_id

  def _check_completion_status(self, task_id: int) -> None:
    task = self.tasks[task_id]
    if task.completed >= task.total and task.fields.get("status") != "[OK]":
      self.update(task_id, status="[OK]")

  def update_task_status(self, task_id, status):
    self.update(task_id, status=status)

  def advance(self, task_id: int, advance: float = 1) -> None:
    super().advance(task_id, advance)
    self._check_completion_status(task_id)

# ---- CLI ----
# The functions defined in this section are wrappers around the main Python
# API allowing them to be called directly from the terminal as a CLI
# executable/script.


def parse_args(args):
  """Parse command line parameters

  Args:
    args (List[str]): command line parameters as list of strings
        (for example  ``["--help"]``).

  Returns:
    :obj:`argparse.Namespace`: command line parameters namespace
  """
  parser = argparse.ArgumentParser(description="""
    A modular framework for ingesting, parsing, mapping, curating, validating and storing data
    """)
  parser.add_argument(
      "--job-id",
      dest="job_id",
      help="job identifier for logging",
      type=str,
      default=None
  )
  parser.add_argument(
      "--version",
      action="version",
      version="parscival {ver}".format(ver=__version__),
  )
  parser.add_argument(
      dest="file_parscival_spec",
      help="parscival specification",
      type=argparse.FileType('r'),
      metavar="FILE_PARSER_SPEC")
  parser.add_argument(
      dest="file_output",
      help="processed data output",
      type=lambda p: Path(p).absolute(),
      metavar="FILE_OUTPUT")
  parser.add_argument(
      dest="file_datasets",
      help="input dataset",
      type=argparse.FileType('r'),
      metavar="FILE_DATASET",
      nargs='+')
  parser.add_argument(
      "--with-config",
      dest="configuration_files",
      help="YAML configuration files",
      type=argparse.FileType('r'),
      nargs='*',
      default=[]
  )
  parser.add_argument(
      "-v",
      "--verbose",
      dest="loglevel",
      help="set loglevel to INFO",
      action="store_const",
      const=logging.INFO
  )
  parser.add_argument(
      "-vv",
      "--very-verbose",
      dest="loglevel",
      help="set loglevel to DEBUG",
      action="store_const",
      const=logging.DEBUG,
  )
  parser.add_argument(
      "-vvv",
      "--very-very-verbose",
      dest="loglevel",
      help="set loglevel to TRACE",
      action="store_const",
      const=logging.TRACE,
  )

  # parse the arguments
  parsed_args = parser.parse_args(args)

  # set default loglevel if not set by verbose flags
  if not any([parsed_args.loglevel == level for level in
              [logging.INFO, logging.DEBUG, logging.TRACE]]):
      parsed_args.loglevel = logging.WARNING

  return parsed_args


def get_log_directory():
  """Return the log directory, prioritizing the PARSCIVAL_LOG_PATH environment variable."""
  log_path = os.getenv('PARSCIVAL_LOG_PATH')

  if log_path:
    os.makedirs(log_path, exist_ok=True)
    if os.access(log_path, os.W_OK):
      return log_path

  # Fallback to a user-writable directory
  home_dir = os.path.expanduser('~')
  fallback_log_path = os.path.join(home_dir, '.parscival', 'log')
  os.makedirs(fallback_log_path, exist_ok=True)

  if not os.access(fallback_log_path, os.W_OK):
    return None

  return fallback_log_path


class JobIDFormatter(logging.Formatter):
  def __init__(self, fmt=None, datefmt=None, style='%', job_id_name=None):
    super().__init__(fmt, datefmt, style)
    self.job_id_name = job_id_name

  def format(self, record):
    record.job_id_name = self.job_id_name
    return super().format(record)


class ContextRichHandler(RichHandler):
  """
  Custom RichHandler that supports setting and displaying a context.
  """

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.context = ""
    self._log_render.level_width = 4
    self.KEYWORDS = ['Initializing', 'Ingesting', 'Parsing',
                     'Mapping', 'Curating', 'Storing']

  def set_context(self, context):
    """
    Set the context value for this handler.
    """
    self.context = context

  def emit(self, record):
    """
    Emit a log record with the context.
    """
    if self.context:
      record.msg = f"{self.context} {record.msg}"
    super().emit(record)


def setup_logging(loglevel, job_id=None):
  """Setup basic logging

  Args:
    loglevel (int): minimum loglevel for emitting messages
  """
  # setup the logger rich handler
  rh = ContextRichHandler(
      console=console,
      enable_link_path=False,
      markup=True,
      omit_repeated_times=False,
      rich_tracebacks=True,
      show_level=True,
      show_path=False,
      show_time=True,
  )

  # get the log directory
  log_dir = get_log_directory()

  # determine the global log file
  log_global_path = normalize_path(os.path.join(log_dir, 'parscival.log'))

  # determine the current job name
  job_id_name = job_id if job_id and job_id.strip() else os.getpid()

  # Setup the global rotating file handler
  gfh = RotatingFileHandler(log_global_path, maxBytes=10**6, backupCount=5)
  gfh.setLevel(loglevel)
  global_file_formatter = JobIDFormatter("%(asctime)s [%(job_id_name)s] %(levelname)s %(message)s",
                                         datefmt="[%X]", job_id_name=job_id_name)
  gfh.setFormatter(global_file_formatter)

  # Setup the logger
  logging.basicConfig(
      level=loglevel,
      format="%(message)s",
      datefmt="[%X]",
      handlers=[rh, gfh]
  )

  if job_id is None:
    return [log_global_path]

  # Determine the log file name
  log_job_file_name = f'parscival_{job_id_name}.log'
  log_job_file_path = normalize_path(os.path.join(log_dir, log_job_file_name))

  # Setup the job file handler
  jfh = logging.FileHandler(log_job_file_path, mode='w')
  jfh.setLevel(loglevel)
  job_file_formatter = logging.Formatter(
      "%(asctime)s %(levelname)s %(message)s", datefmt="[%X]")
  jfh.setFormatter(job_file_formatter)

  log.parent.addHandler(jfh)

  return [log_global_path, log_job_file_path]


def check_open_file_descriptors(whitelist_files=[]):
  """
  Check and return the list of open file descriptors for the
  current process.

  Returns:
      list of dict: A list of dictionaries containing path
                    and file descriptor.
  """
  # Get the current process
  process = psutil.Process(os.getpid())

  # List all open file descriptors
  open_files = process.open_files()

  # Prepare the list of open files
  open_files_list = []
  for open_file in open_files:
    if normalize_path(open_file.path) not in whitelist_files:
      open_files_list.append({
          'path': open_file.path,
          'fd': open_file.fd
      })

  return open_files_list


def is_whitelisted_path(path, whitelist_keywords):
  """
  Check if the given path contains any of the whitelist keywords.

  Parameters:
    path (str): The path to check.
    whitelist_keywords (list): A list of keywords to whitelist.

  Returns:
    bool: True if the path contains any of the whitelist keywords, False otherwise.
  """
  return any(keyword in str(path) for keyword in whitelist_keywords)


def clean_transient_files(files, whitelist_keywords):
  """
  Safely delete files listed in the provided list.

  Parameters:
    files (list): A list of file paths to delete.
    whitelist_keywords (list): A list of keywords that must be in the path to allow deletion.
  """
  for file_path in files:
    try:
      if file_path.exists() and file_path.is_file():
        if is_whitelisted_path(file_path, whitelist_keywords):
          log.debug(f"Deleting file: {file_path}")
          file_path.unlink()
        else:
          log.warning(f"File not whitelisted for deletion: {file_path}")
      else:
        log.warning(f"File not found or is not a file: {file_path}")
    except Exception as e:
      log.error(f"Error deleting file {file_path}: {e}")


def clean_transient_directories(directories, whitelist=None, blacklist=None, whitelist_keywords=None):
  """
  Safely delete directories listed in the provided list.

  Parameters:
    directories (list): A list of directory paths to delete.
    whitelist (list): Directories allowed to be removed.
    blacklist (list): Directories not allowed to be removed.
    whitelist_keywords (list): A list of keywords that must be in the path to allow deletion.

  Raises:
    ValueError: If an attempt is made to delete a protected or root directory.
  """
  # set default whitelists and blacklists if not provided
  if whitelist is None:
    whitelist = []
  if blacklist is None:
    blacklist = ["/", "/bin", "/boot", "/dev", "/etc",
                 "/lib", "/proc", "/root", "/sys", "/usr", "/var"]
  if whitelist_keywords is None:
    whitelist_keywords = []

  for dir_path in directories:
    try:
      # normalize the path to avoid issues with trailing slashes
      path = Path(normalize_path(dir_path))

      # ensure the directory is not root
      if path == Path("/"):
        raise ValueError("Attempt to delete root directory is not allowed.")

      # check if path is in the blacklist
      if path in [Path(p) for p in blacklist]:
        raise ValueError(
            f"Attempt to delete a protected directory is not allowed: {path}")

      # if a whitelist is provided, ensure the path is within the whitelist
      if whitelist and path not in [Path(p) for p in whitelist]:
        raise ValueError(f"Attempt to delete a directory not in the whitelist: {path}")

      # check if the path contains any of the whitelist keywords
      if not is_whitelisted_path(path, whitelist_keywords):
        raise ValueError(f"Directory not whitelisted for deletion: {path}")

      # check if the directory exists before attempting to delete
      if path.exists() and path.is_dir():
        log.debug(f"Deleting directory: {path}")
        shutil.rmtree(path)
      else:
        log.warning(f"Directory not found or is not a directory: {path}")
    except Exception as e:
      log.error(f"{e}")


def clean_transient(transient):
  """
  Safely delete files and directories listed in the transient dictionary.

  Parameters:
    transient (dict): A dictionary containing 'files' and 'directories' keys with lists of paths to delete.
  """
  if not transient:
    return

  whitelist_keywords = ['/parscival-transient-']

  # Delete files
  clean_transient_files(transient.get('files', []), whitelist_keywords)

  # Delete directories
  clean_transient_directories(transient.get('directories', []),
                              whitelist_keywords=whitelist_keywords)


def combine_configuration_files(configuration_files):
  """Combine multiple YAML configuration files with the latest taking precedence

  Args:
      configuration_files (List[str]): List of file paths to YAML files

  Returns:
      dict: Combined YAML content
  """
  combined_data = {}
  for config_file in configuration_files:
    with config_file:
      log.info(f"Loading configuration from '{config_file.name}'")
      data = yaml.safe_load(config_file)
      if data is not None:
        combined_data.update(data)
  return combined_data


def task_update_global_stats(parscival_data):
  documents_duplicated = parscival_data['stats'].get('duplicated', '?')
  documents_unique = parscival_data['stats']['parsed']

  if documents_duplicated != '?':
    documents_unique = parscival_data['stats']['parsed'] - documents_duplicated

  parscival_data['stats']['duplicated'] = documents_duplicated
  parscival_data['stats']['unique'] = documents_unique


class Worker:
  def __init__(self, args):
    self.args = args
    self.clean_up_called = False

  def close_log_handlers(self, logger):
    """Clean up the log handlers by closing them."""
    log.debug('Cleaning log handlers...')
    handlers = logger.parent.handlers[:]
    for handler in handlers:
      handler.close()
      logger.removeHandler(handler)

  def close_file(self, file_obj):
    try:
      file_obj.close()
    except Exception as e:
      log.error(f"Error closing file: {getattr(file_obj, 'name', 'unknown')}, {e}")

  def close_open_files(self):
    # close file_parscival_spec
    self.close_file(self.args.file_parscival_spec)

    # close all file objects in file_datasets
    for file_obj in self.args.file_datasets:
      self.close_file(file_obj)

    # close all file objects in configuration_files
    for file_obj in self.args.configuration_files:
      self.close_file(file_obj)

  def show_open_file_descriptors(self, log_files):
    # get the open file descriptors
    open_files = check_open_file_descriptors(log_files)
    if open_files:
      log.warning(
          "A plugin or module has opened one or more file descriptors without closing them:")
      for file in open_files:
        log.warning(f"File Descriptor: {file['fd']}, Path: {file['path']}")

  def clean_up(self):
    if not self.clean_up_called:
      self.clean_up_called = True
      self.close_open_files()
      log.debug('Performing clean-up tasks')

  def signal_handler(self, sig, frame):
    log.info(f'Received signal {sig}. Gracefully exiting...')
    self.clean_up()
    sys.exit(0)

  def process(self):
    """Parscival parse files

    Args:

    Returns:
      Boolean: True if data was parsed, False otherwise
    """
    parscival = {
        'spec': None,
        'data': None,
        'output_info': None
    }

    # visualize progress on the console
    with WorkerProgress(
        StatusTextColumn("[progress.description]{task.description}"),
        SpinnerColumn(),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
        TimeElapsedColumn(),
        console=console,
        transient=True,
    ) as progress:
      # initializing
      if not task_initializing(self.args, parscival, progress):
        return parscival['data']

      # after_initializing: curate raw input data according to the spec
      if not task_curating('after_initializing', parscival['spec'], parscival['data'], progress):
        return parscival['data']

      # before_ingesting: curate raw input data according to the spec
      if not task_curating('before_ingesting', parscival['spec'], parscival['data'], progress):
        return parscival['data']

      # then get information about the datasets to process
      if not task_ingesting(parscival['spec'], parscival['data']):
        return parscival['data']

      # after_ingesting: curate ingested data according to the spec
      if not task_curating('after_ingesting', parscival['spec'], parscival['data'], progress):
        return parscival['data']

      # before_parsing: curate ingested data according to the spec
      if not task_curating('before_parsing', parscival['spec'], parscival['data'], progress):
        return parscival['data']

      # parsing
      if not task_parsing(parscival['spec'], parscival['data'], progress):
        return parscival['data']

      # log global stats if multiple files
      task_parsing_log_global_stats(parscival['data'])

      # after_parsing: curate parsed data according to the spec
      if not task_curating('after_parsing', parscival['spec'], parscival['data'], progress):
        return parscival['data']

      # before_mapping: curate parsed data according to the spec
      if not task_curating('before_mapping', parscival['spec'], parscival['data'], progress):
        return parscival['data']

      # mapping
      if not task_mapping(parscival['spec'], parscival['data'], progress):
        return parscival['data']

      # after_mapping: curate mapped data according to the spec
      if not task_curating('after_mapping', parscival['spec'], parscival['data'], progress):
        return parscival['data']

      # before_storing: curate mapped data according to the spec
      if not task_curating('before_storing', parscival['spec'], parscival['data'], progress):
        return parscival['data']

      # storing
      if not task_storing(parscival['spec'], parscival['data'], parscival['output_info'], progress):
        return parscival['data']

      # after_mapping: curate mapped data according to the spec
      if not task_curating('after_storing', parscival['spec'], parscival['data'], progress):
        return parscival['data']

      # update global stats
      task_update_global_stats(parscival['data'])

      # before_storing: curate mapped data according to the spec
      if not task_curating('before_finishing', parscival['spec'], parscival['data'], progress):
        return parscival['data']

      # show final stats
      log_finishing_stats(parscival['data'])

      parscival['data']['status']['processed'] = True
      return parscival['data']

  @logging_decorator(logging_default_context)
  def work(self):
    log.info("Starting the worker...")

    parscival_data = None
    # process_datasets
    try:
      parscival_data = self.process()
    except Exception as e:
      log_level = logging.getLogger().getEffectiveLevel()
      exc_info = log_level <= logging.DEBUG

      # log exception with filename, line number and function name
      if hasattr(e, 'details'):
        # conditionally set exc_info based on log level
        log.error(
            f"An error occurred at file [yellow]{e.details.filename}[/yellow]:"
            f"[blue]{e.details.line_number}[/blue] in "
            f"[green]{e.details.function_name}[/green]"
        )

      log.error("%s", e, exc_info=exc_info)
      if log_level > logging.DEBUG:
        log.error("run with '--vv' for details")

    finally:
      self.close_open_files()

    # there is nothing more to do if parsing data was not initialized
    if not parscival_data:
      return False

    # clean transient directories and files
    clean_transient(parscival_data.get('transient', []))

    # return true if no error
    return ('status' in parscival_data and
            'processed' in parscival_data['status'] and
            parscival_data['status']['processed'])

  def start(self):
    # register the signal handlers
    # handle Ctrl+C
    signal.signal(signal.SIGINT, self.signal_handler)
    # handle Ctrl+\
    signal.signal(signal.SIGQUIT, self.signal_handler)
    # handle termination signal
    signal.signal(signal.SIGTERM, self.signal_handler)

    # setup logging at level
    log_files = setup_logging(self.args.loglevel, self.args.job_id)

    if not log_files:
      raise RuntimeError("Unable to create a logging files. Use PARSCIVAL_LOG_PATH")

    # ensure log handlers are properly closed on exit
    atexit.register(self.close_log_handlers, log)

    # show open file descriptors
    atexit.register(self.show_open_file_descriptors, log_files)

    log.info("Parscival [cyan]v{}[/cyan]".format(get_version_major_minor_patch()))

    global engine_version
    log.info("Using Parscival Engine [cyan]v{}[/cyan]".format(engine_version))

    log.info(f"Logging global activity in {log_files[0]}")
    if len(log_files) > 1:
      for log_file in log_files[1:]:
        log.info(f"Logging activity in {log_file}")

    # launch the working routine
    success = self.work()

    # final logging message
    if success:
      log.info("Worker finished successfully")
    else:
      log.critical("Worker finished with errors")


def main(args):
  """Wrapper allowing :func:`parse` to be called with string arguments in a CLI fashion

  Instead of returning the value from :func:`parse`, it prints the result to the
  ``stdout`` in a nicely formatted message.

  Args:
    args (List[str]): command line parameters as list of strings
        (for example  ``["--verbose", "42"]``).
  """
  # take environment variables from .env
  load_dotenv()

  parsed_args = parse_args(args)
  # start the worker with the parsed arguments
  worker = Worker(parsed_args)

  worker.start()


def run():
  """Calls :func:`main` passing the CLI arguments extracted from :obj:`sys.argv`

  This function is used as entry point to create a console script with setuptools.
  """
  main(sys.argv[1:])


if __name__ == "__main__":
  # ^  This is a guard statement that will prevent the following code from
  #    being executed in the case someone imports this file instead of
  #    executing it as a script.
  #    https://docs.python.org/3/library/__main__.html

  # After installing your project with pip, users can also run this Python
  # module as scripts via the ``-m`` flag, as defined in PEP 338::
  #
  #     python -m parscival.worker PARAMS...
  #
  run()
