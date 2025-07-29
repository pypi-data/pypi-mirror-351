# -*- coding: utf-8 -*-
# module regex_sub.py
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
class RegexSub(parscival_plugins.mapping.Mapper):

  _alias_ = 'mapping.transform.regex_sub'
  _version_ = '1.0.0'

  @staticmethod
  def process(parsing_spec, parsing_data, mapping_nodes, **params):
    """use as mapping the value obtained by replacing the leftmost
       non-overlapping occurrences of pattern in data by a replacement string.
       Note that this is the same behavior as the re.sub() function

    Args:
      params (list): list of parameters to use within this plugin
        mandatory:
          - pattern: regular expression to use for matching data
          - repl: string to replace leftmost non-overlapping occurrences

    Returns:
      Boolean: True if the process is successful, False otherwise
    """
    # check the mandatory params
    if not 'regex' in params or not 'repl' in params:
      log.warning("Params 'regex', 'repl' are required")
      return False

    # create a local copy of the passed params
    local_params = copy.deepcopy(params)
    # try to compile the regular expression pattern
    try:
      pattern = re.compile(local_params['regex'])
      # we no longer need to keep this parameter
      local_params.pop('regex')
    except re.error as e:
      log.error("'{}' is not a valid regular expression ({})".format(local_params['regex'], e))
      return False

    try:
      # loop over each input node
      for node in mapping_nodes:
        # try to perform the substitution
        node['data'] = re.sub(string = node['data'], pattern = pattern, **local_params)

    except Exception as e:
      log.warning("Error while executing plugin")
      return False

    return True
