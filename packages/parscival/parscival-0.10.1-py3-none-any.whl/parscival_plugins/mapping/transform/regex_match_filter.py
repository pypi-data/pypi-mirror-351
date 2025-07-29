# -*- coding: utf-8 -*-
# module regex_match_filter.py
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
import parscival_plugins.mapping                  #
import logging                                    #
import re                                         #
import copy                                       #
from pathlib import Path                          #
import jinja2                                     #
log = logging.getLogger(__name__)                 #
# ---------------------------------------------------------------------------
class RegexMatchFilter(parscival_plugins.mapping.Mapper):

  _alias_ = 'mapping.transform.regex_match_filter'
  _version_ = '1.0.0'

  @staticmethod
  def process(parsing_spec, parsing_data, mapping_nodes, **params):
    """use regular expression for mapping nodes data
       Note that the node is ignored wheneaver the pattern does not match
       the data and the parameter fallback is not given

    Args:
      params (list): list of parameters to use within this plugin
        mandatory:
          - regex: regular expression to use for matching data
        optional:
          - value: format string to use with regex matched groups
          - fallback: value when regex don't have matches

    Returns:
      Boolean: True if the process is successful, False otherwise
    """
    # check the mandatory params
    if not 'regex' in params:
      log.warning("Param 'regex' is required")
      return False

    # try to compile the regular expression pattern
    try:
      pattern = re.compile(params['regex'])
    except re.error as e:
      log.error("'{}' is not a valid regular expression ({})".format(params['regex'], e))
      return False

    # we expected to include only nodes that match the regex pattern
    input_mapping_nodes  = copy.deepcopy(mapping_nodes)
    mapping_nodes.clear()

    try:
      # prepare a template for the expected output value
      template = None
      if 'value' in params:
        template = jinja2.Template(params['value'])

      # loop over each input node
      for node in input_mapping_nodes:
        matches = re.match(pattern, node['data'])
        # check if we have at least one match
        if matches:
          # if requested, render the template using the matching groups to
          # produce the mapped value
          if 'value' in params:
            # if a matched group is None, then replace it by an empty string
            matched_groups = ['' if m is None else m for m in matches.groups()]
            node['data'] = template.render(_ = matched_groups)

          # copy matched node to the result
          mapping_nodes.append(node.copy())

        elif 'fallback' in params:
          # if a fallback value is given use it
          node['data'] = params['fallback']
          mapping_nodes.append(node.copy())
        else:
          # ignore this record as match fails
          continue

    except Exception as e:
      log.warning("Error while executing plugin")
      return False

    return True
