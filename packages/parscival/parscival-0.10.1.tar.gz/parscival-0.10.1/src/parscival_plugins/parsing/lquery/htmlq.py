# -*- coding: utf-8 -*-
# module htmlq.py
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
import copy
import logging
import os
import re
from pathlib import Path

import pluginlib

import parscival_plugins.parsing

log = logging.getLogger(__name__)
# ---------------------------------------------------------------------------
from pyquery import PyQuery as pq


# ---------------------------------------------------------------------------
class Parser(parscival_plugins.parsing.Parser):

  _alias_ = 'parsing.lquery.htmlq'
  _version_ = '1.0.0'

  # check_spec(parsing_spec)
  # type:
  #   text
  #   list_text (needs repeated key)

  @staticmethod
  def init(parsing_spec, **params):
    log.info("Starting parser for {} ({}) data".format(
              parsing_spec['data']['source'], parsing_spec['data']['format']))
    try:
      if (parsing_spec['misc']['record_finalizer']['regex']['text'] is not None and
          parsing_spec['data']['parsing']['lquery']['keys'] is not None):
        return True
    except KeyError:
      return False

    return False

  @staticmethod
  @pluginlib.abstractmethod
  def can_parse(parsing_spec, dataset_info, document_info, document_line, **params):
    # Find all non-overlapping matches of the record_finalizer in the document buffer
    record_finalizer_regex = parsing_spec['misc']['record_finalizer']['regex']['text']
    finalizer_matches = record_finalizer_regex.findall(document_info['buffer'])

    # Check if there is exactly one match
    if len(finalizer_matches) == 1:
        return True

    return False

  @staticmethod
  @pluginlib.abstractmethod
  def buffer_restart(parsing_spec, dataset_info, document_info, document_line, **params):
    record_separator_regex = parsing_spec['misc']['record_separator']['regex']['text']
    record_finalizer_reverse_regex =parsing_spec['misc']['record_finalizer']['regex']['text_reverse']
    # check if the first line contains the record separator
    matches = record_separator_regex.findall(document_line)
    # if the line already contains the record separator simple return it
    if len(matches) == 1:
      return document_line

    # otherwise, we must backtrack in the buffer for latest record finalizer

    # reverse the buffer
    reversed_buffer = document_info['buffer'][::-1]

    # search for the first occurrence of the reversed pattern
    match = record_finalizer_reverse_regex.search(reversed_buffer)
    buffer_len = len(document_info['buffer'])

    if match:
      # Calculate the position of the last record_finalizer in the original buffer
      start_pos = buffer_len - match.end() + parsing_spec['misc']['record_finalizer']['len']
      last_occurrence = document_info['buffer'][start_pos:].strip()
      return ''.join([last_occurrence, document_line])

    # not match was found return the input line
    return document_line

  @staticmethod
  def perform_chained_actions(elements, actions, dataset_info, document_info):
    for action in actions:
        try:
            method = action['method']
            params = action.get('params', None)
            if params is not None:
                elements = getattr(elements, method)(params)
            else:
                elements = getattr(elements, method)()
        except Exception as e:
            log.warning("[cyan]{}[/cyan] - error executing action \"{}\" at document on line {}: '{}'".format(
                dataset_info['filename'], action, document_info['line']['start'], e))
            break
    return elements

  @staticmethod
  def is_required_key(parsing_spec, key):
    return parsing_spec['data']['initializing']['keys']['parsing'].get(key, {}).get('qualifier') == 'required'

  # Pre-compiled regular expressions
  newline_space_re = re.compile(r'\r?\n +')
  multiple_spaces_re = re.compile(r'  +')

  @staticmethod
  def clean_value(value):
    if not value:
      return ''
    # common processing for any value
    custom_value_text = value.strip()
    custom_value_text = Parser.newline_space_re.sub(' ', custom_value_text)
    custom_value_text = Parser.multiple_spaces_re.sub(' ', custom_value_text)
    return custom_value_text

  @staticmethod
  def extract_value(elements, selector, extraction_type, dataset_info, document_info, level=1):
      if extraction_type == 'text':
          return Parser.clean_value(elements.text())
      elif extraction_type == 'attr':
          return Parser.clean_value(elements.attr(selector['attribute']))
      elif extraction_type in ['list_text', 'list_attr']:
        cleaned_values = []
        # item_chain, item_item_chain, ...
        chain_actions_level = '_'.join(['_'.join(['item'] * level), 'chain'])
        for element in elements.items():
          # perform item level actions
          element = Parser.perform_chained_actions(element,
                    selector.get(chain_actions_level, []), dataset_info, document_info)
          # if element have multiple items
          if len(element) > 1:
            cleaned_text = Parser.extract_value(element, selector,
                                                extraction_type, dataset_info,
                                                document_info, level+1)
          else:
            # use element text
            if extraction_type == 'list_text':
              text = element.text()
              cleaned_text = Parser.clean_value(text)
            # use attribute text
            elif extraction_type == 'list_attr':
              attr_value = element.attr(selector['attribute'])
              cleaned_text = Parser.clean_value(attr_value)

          # as we are dealing with a list, always add the result, even if its empty
          cleaned_values.append(cleaned_text)
        return cleaned_values

      return ""

  @staticmethod
  def is_buffer_empty(buffer):
    return len(buffer.strip()) == 0

  @staticmethod
  def is_single_record_separator(parsing_spec, buffer):
    record_separator_regex = parsing_spec['misc']['record_separator']['regex']['text']
    separator_matches = record_separator_regex.findall(buffer)
    return len(separator_matches) == 1

  @staticmethod
  def load_document(dataset_info, document_info):
    try:
      # Parse the HTML content
      return pq(document_info['buffer'])
    except Exception as e:
      if str(e) != "Document is empty":
        log.warning("[cyan]{}[/cyan] - malformed document (line {})".format(
            dataset_info['filename'], document_info['line']['start']))
        log.debug("[cyan]{}[/cyan] - rule: '{}' didn't match (line {}, column {})".format(
            dataset_info['filename'], e.expr.name, (e.line() + document_info['line']['start'] - 1), e.column()))
      return None

  @staticmethod
  def should_process_key(parsing_spec, key):
    return  (parsing_spec['data']['options']['only_requested_keys'] == False or
             key in parsing_spec['data']['initializing']['keys']['parsing'])

  @staticmethod
  def extract_document_data(parsing_spec, dataset_info, document_info, doc):
    # dictionary to hold the extracted data
    extracted_data = []
    # get all the keys to parse
    keys = parsing_spec['data']['parsing']['lquery']['keys']

    # apply the selectors and extract data based on instructions
    for key, parsing_info in keys.items():
      # ignore not requested keys
      if not Parser.should_process_key(parsing_spec, key):
        continue

      # loop over all the listed queries until a valid found
      extracted_value = ""
      for selector in parsing_info['selectors']:
        query = selector['query']
        extraction_type = selector.get('type', 'text')
        actions = selector.get('chain', [])

        # get the elements related to this query
        elements = doc(query)
        # perform chained actions
        elements = Parser.perform_chained_actions(elements, actions, dataset_info, document_info)

        # retrieve the final value
        if elements and extraction_type in ['text', 'attr', 'list_text', 'list_attr']:
           extracted_value = Parser.extract_value(elements, selector, extraction_type, dataset_info, document_info)

        # if we already found the requested value
        if extracted_value:
          # we don't need to further explore an alternative selector
          break

      # log a warning if a required value was not found
      if Parser.is_required_key(parsing_spec, key) and not extracted_value:
        ## e.g. malformed document (line 227717)
        log.warning("[cyan]{}[/cyan] - requiered key '{}' with selectors '{}' not found (line {})".format(
                                          dataset_info['filename'],
                                          key,
                                          parsing_info['selectors'],
                                          document_info['line']['start']))

      # ignore empty values from keys not qualified as 'required'
      if not extracted_value and not Parser.is_required_key(parsing_spec, key):
        continue

      extracted_data.append((key, extracted_value))

    return extracted_data

  @staticmethod
  def process(parsing_spec, dataset_info, document_info, **params):
    # only if the buffer is not empty
    if Parser.is_buffer_empty(document_info['buffer']):
      return False

    # only if the record separator is present and there is exactly one match
    if not Parser.is_single_record_separator(parsing_spec, document_info['buffer']):
      return False

    # load the html document using pq
    doc = Parser.load_document(dataset_info, document_info)
    if doc is None:
      return False

    # extract data from the document
    extracted_data = Parser.extract_document_data(parsing_spec, dataset_info, document_info, doc)

    # if we extracted some data
    if len(extracted_data):
      dataset_info['documents'].append(extracted_data)
      return True

    return False
