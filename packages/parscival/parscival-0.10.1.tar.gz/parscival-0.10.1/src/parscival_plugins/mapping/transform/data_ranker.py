# -*- coding: utf-8 -*-
# module data_ranker.py
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
class DataRanker(parscival_plugins.mapping.Mapper):

  _alias_ = 'mapping.transform.data_ranker'
  _version_ = '1.0.0'

  @staticmethod
  def process_node(input_nodes, mapping_nodes, **params):
    for node in input_nodes:
      matches = node['data']
      if isinstance(matches, list):
        for rank, data in enumerate(matches):
          # ignore empty node members
          if not data:
            continue

          # if data is a list, add each item in a different parserank
          if isinstance(data, list) and params.get('parserank', False):
            for parserank, match in enumerate(data):
              local_node = node.copy()
              local_node['parserank'] = parserank
              local_node['rank'] = rank
              local_node['data'] = match
              mapping_nodes.append(local_node)
          else:
            local_node = node.copy()
            local_node['rank'] = rank
            local_node['data'] = data
            mapping_nodes.append(local_node)
      else:
        local_node = node.copy()
        # simple copy this node with data as string
        # if isinstance(matches, list):
        #   if len(matches) == 1:
        #     local_node['data'] = str(matches[0])
        #   else:
        #     local_node['data'] = ''.join(matches)
        # else:
        local_node['data'] = matches

        mapping_nodes.append(local_node)

  @staticmethod
  def process(parsing_spec, parsing_data, mapping_nodes, **params):
    """use the parsed data for mapping and parse ranking nodes data

    Args:
      params (list): list of parameters to use within this plugin

    Returns:
      Boolean: True if the process is successful, False otherwise
    """
    # we expected to explode a node into multiple ones with incremental parseranks
    input_mapping_nodes  = copy.deepcopy(mapping_nodes)
    mapping_nodes.clear()

    # process each input node
    DataRanker.process_node(input_mapping_nodes, mapping_nodes, **params)

    return True
