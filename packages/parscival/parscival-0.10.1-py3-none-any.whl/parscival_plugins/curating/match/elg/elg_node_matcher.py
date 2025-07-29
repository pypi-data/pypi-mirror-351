# -*- coding: utf-8 -*-
# module elg_node_matcher.py
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
import os                                         #
import pluginlib                                  #
import parscival_plugins.curating                 #
import logging                                    #
import re                                         #
import copy                                       #
from pathlib import Path                          #
log = logging.getLogger(__name__)                 #
# ---------------------------------------------------------------------------
import tempfile                                   #
import sys                                        #
# ---------------------------------------------------------------------------
# calculate the relative path to the src directory
relative_source_path = os.path.join(os.path.dirname(__file__), '../../../../../src')
# append the source directory to sys.path
sys.path.append(os.path.abspath(relative_source_path))
# import the elglib
from elglib import elg_tagger
# ---------------------------------------------------------------------------
class ElgNodeMatcher(parscival_plugins.curating.Curator):

  _alias_ = 'curating.match.elg_node_matcher'
  _version_ = '1.0.0'
  _engine_path_ = 'elg'

  @staticmethod
  def get_registry(parsing_spec, registry_filename):
    # step 1: check in the assets directory under the spec_path
    spec_path = Path(parsing_spec['file'].name).parent
    path1 = spec_path / 'assets' / ElgNodeMatcher._engine_path_ / registry_filename
    if path1.exists():
      return {
        'filename': os.path.abspath(path1), 'valid': True
      }

    # step 2: check in the default assets directory in the parent of spec_path
    path2 = spec_path.parent / 'default' / 'assets' / ElgNodeMatcher._engine_path_ / registry_filename
    if path2.exists():
      return {
        'filename': os.path.abspath(path2), 'valid': True
      }

    log.warning("Registry not found '{}'".format(registry_filename))

    return {
      'valid': False
    }

  @staticmethod
  def save_node_data(parsing_data, **params):
    collapse_spaces  = re.compile(r'\s+')
    sanitize_special = re.compile(r'[][}{}-]')
    normalize = params.get('normalize',{})
    try:
      # create a temporary file and write the data to it
      with tempfile.NamedTemporaryFile(prefix='parscival-transient-', delete=False, mode='w', encoding='utf-8') as temp_file:
        line_count = 0
        for item in parsing_data['mappings'][params['node']]:
          data = item.get('data', '').strip()
          if not data or data.isspace():
            data = '[[]]'

          #  sanitize special characters
          data = sanitize_special.sub(' ', data)

          for rule in normalize:
            # get the first (and only) key in the dictionary
            key = list(rule.keys())[0]
            if not rule[key]: continue
            # lowercase
            if key == 'lowercase':
              data = data.lower()
            # collapse multiple spaces
            elif key == 'collapse':
              data = collapse_spaces.sub(' ', data)
            # remove leading and trailing whitespace
            elif key == 'trim':
              data = data.strip()

          temp_file.write(data + '\n')
          line_count += 1

    except Exception as e:
      log.error("Error while executing plugin")

      return { 'valid': False }

    return {
      'filename': temp_file.name,
      'line_count': line_count,
      'valid': True
    }


  def load_node_data(parsing_data, tagged_data, **params):
    """
    Load tagged data from a file and assign it to the 'data' attribute of each item
    in parsing_data['mappings'][params['node']].

    Args:
      parsing_data (dict): The parsed data containing mappings.
      tagged_data (dict): The tagged data containing the file path and other metadata.
      params (dict): Additional parameters, including the node to process.
    """
    try:
      # ensure the length of the mappings matches the line count in the tagged data
      assert len(parsing_data['mappings'][params['node']]) == tagged_data['line_count']

      # read the tagged data file and assign each line to the corresponding mapping
      with open(tagged_data['file'], 'r', encoding='utf-8') as file:
        for i, line in enumerate(file):
          # remove newline character
          line = line.rstrip('\n')
          # remove quotes if the line is quoted
          if line.startswith('"') and line.endswith('"'):
            line = line[1:-1]
          # assign the line to the 'data' attribute
          parsing_data['mappings'][params['node']][i]['data'] = line

    except AssertionError:
      log.error("The number of mappings does not match the line count in the tagged data.")
      return {'valid': False}
    except Exception as e:
      log.error("Error while loading node data '{}': {} - {}".format(
                  params['node'], type(e).__name__, e.__doc__))
      return False

    return True


  @staticmethod
  def process(parsing_spec, parsing_data, **params):
    # check the mandatory params
    if not 'node' in params or not 'registry' in params:
      log.warning("Params 'node' and 'registry' are required")
      return False

    # check if the node is avalaible
    if not params['node'] in parsing_data['mappings']:
      # node is not available, this must not be considered as an error
      return True

    try:
      # save data node data on a temporal file
      input_data = ElgNodeMatcher.save_node_data(parsing_data, **params)
      if not input_data['valid']:
        log.error("ELG execution failed")
        return False

      # the number of lines in the temporal data file must be equal to the number
      # of items in the node
      if input_data['line_count'] != len(parsing_data['mappings'][params['node']]):
        log.warning("Node '{}' mismatched data count".format(params['node']))
        return False

      # get the registry
      registry = ElgNodeMatcher.get_registry(parsing_spec, params['registry'])
      if not registry['valid']:
        # if none of the paths exist, raise a FileNotFoundError
        raise FileNotFoundError(f"File '{params['registry']}' not found in any of the specified paths.")

      # run the process
      tagged_data = elg_tagger(input_data['filename'],
                               input_data['line_count'],
                               registry['filename'],
                               'parscival-transient-',
                               **params)
      if not tagged_data:
        log.error("ELG execution failed")
        return False

      # test if global remove temporal files is enabled
      if parsing_spec['data']['options'].get('remove_transient', False):
        # if the non tagged input file exists
        if os.path.exists(input_data['filename']):
          parsing_data['transient']['files'].append(Path(input_data['filename']))
        # if the tagged input file exists
        if os.path.exists(tagged_data['input']):
          parsing_data['transient']['files'].append(Path(tagged_data['input']))
        # if the tagged file exists
        if os.path.exists(tagged_data['file']):
          parsing_data['transient']['files'].append(Path(tagged_data['file']))
        # if the tagged file number of matches exists
        if os.path.exists(tagged_data['file_n_matches']):
          parsing_data['transient']['files'].append(Path(tagged_data['file_n_matches']))

      # replace tagged data on the related node
      if not ElgNodeMatcher.load_node_data(parsing_data, tagged_data, **params):
        log.error("ELG execution failed")
        return False

    except ValueError as e:
      log.error("Error while executing plugin")
      return False

    except Exception as e:
      log.error("Error while executing plugin")
      return False

    return True
