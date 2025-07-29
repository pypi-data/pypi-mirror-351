# -*- coding: utf-8 -*-
# module regex_parseranker.py
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
log = logging.getLogger(__name__)                 #
# ---------------------------------------------------------------------------
class RegexParseranker(parscival_plugins.mapping.Mapper):

  _alias_ = 'mapping.transform.regex_parseranker'
  _version_ = '1.0.0'

  @staticmethod
  def process(parsing_spec, parsing_data, mapping_nodes, **params):
    """use regular expression for mapping and parse ranking nodes data

    Args:
      params (list): list of parameters to use within this plugin
        mandatory:
          - regex: regular expression to use for split matching data

    Returns:
      Boolean: True if the process is successful, False otherwise
    """
    # check the mandatory params
    if not 'regex' in params :
      log.warning("Param 'regex' is required")
      return False

    # try to compile the regular expression pattern
    try:
      pattern = re.compile(params['regex'])
    except re.error as e:
      log.error("'{}' is not a valid regular expression ({})".format(params['regex'], e))
      return False

    # we expected to explode a node into multiple ones with incremental parseranks
    input_mapping_nodes  = copy.deepcopy(mapping_nodes)
    mapping_nodes.clear()

    # loop over each input node
    for node in input_mapping_nodes:
      mapped_value = node['data']
      matches = re.split(pattern, mapped_value)
      if len(matches) > 1:
        for parserank, match in enumerate(matches):
          node['data'] = match
          node['parserank'] = parserank
          mapping_nodes.append(node.copy())
      else:
        # simple copy this node as regex split do nothing
        mapping_nodes.append(node.copy())

    return True
