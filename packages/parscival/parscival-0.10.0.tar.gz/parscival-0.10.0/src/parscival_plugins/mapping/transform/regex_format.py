# -*- coding: utf-8 -*-
# module regex_format.py
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
from pathlib import Path                          #
import jinja2                                     #
log = logging.getLogger(__name__)                 #
# ---------------------------------------------------------------------------
class RegexFormat(parscival_plugins.mapping.Mapper):

  _alias_ = 'mapping.transform.regex_format'
  _version_ = '1.0.1'

  @staticmethod
  def process(parsing_spec, parsing_data, mapping_nodes, **params):
    """use regular expression for format mapping nodes data

    Args:
      params (list): list of parameters to use within this plugin
        mandatory:
          - regex: regular expression to use for matching data
          - value: format string to use with regex matched groups
        optional:
          - fallback: value when regex don't have matches

    Returns:
      Boolean: True if the process is successful, False otherwise
    """
    # check the mandatory params
    if not 'regex' in params or not 'value' in params:
      log.warning("Params 'regex', 'value' are required")
      return False

    # try to compile the regular expression pattern
    try:
      pattern = re.compile(params['regex'])
    except re.error as e:
      log.error("'{}' is not a valid regular expression ({})".format(params['regex'], e))
      return False

    try:
      # prepare a template for the expected output value
      template = jinja2.Template(params['value'])
      # loop over each input node
      for node in mapping_nodes:
        matches = re.match(pattern, node['data'])
        # check if we have at least one match
        if matches:
          # if so, render the template using the matching groups
          # if a matched group is None, then replace it by an empty string
          matched_groups = ['' if m is None else m for m in matches.groups()]
          node['data'] = template.render(_ = matched_groups)
        elif 'ignore_unmatch' in params and params['ignore_unmatch']:
          node['data'] = None
        elif 'fallback' in params:
          node['data'] = params['fallback']
    except Exception as e:
      log.warning("Error while executing plugin")
      return False

    return True
