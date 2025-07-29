# -*- coding: utf-8 -*-
# module filter_render_template.py
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
import pluginlib                                 #
import parscival_plugins.curating                #
import logging                                   #
log = logging.getLogger(__name__)                #
# ---------------------------------------------------------------------------
import bisect                                    #
import jinja2                                    #
from jinja2 import Environment, meta             #
# ---------------------------------------------------------------------------
from pathlib import Path                         #
# ---------------------------------------------------------------------------
class HashKeyDeduplicator(parscival_plugins.curating.Curator):

  _alias_ = 'curating.deduplicate.hash_key_deduplicator'
  _version_ = '0.1.0'

  @staticmethod
  def process(parsing_spec, parsing_data, **params):
    """remove duplicated entries based on a id
    """
    # no duplicates by default
    parsing_data['stats']['duplicated'] = 0

    # check the mandatory params
    if not 'hash_key' in params :
      log.warning("Param 'hash_key' is required")
      return False

    # check if the mappings were already created
    if not 'mappings' in parsing_data:
      log.warning("There are not mappings to process")
      return False

    # check if the hash_key can be resolved using the mapping keys
    hash_key = params['hash_key']
    env = jinja2.Environment()
    ast = env.parse(hash_key)
    hash_variables = meta.find_undeclared_variables(ast)

    # # loop over each variable and check if there is a mapping key for it
    # for hash_variable in hash_variables:
    #   if hash_variable not in parsing_data['mappings']:
    #     log.warning("Plugin 'curating.{}' v{}: required the mapping '{}'" \
    #             "".format(HashKeyDeduplicator._alias_,
    #             HashKeyDeduplicator._version_),hash_variable)
    #     return False


    # initialize values
    hash_context = {}
    start_index = {}
    current_node_id = {}
    number_of_nodes = {}

    # loop over each variable and check if there is a mapping key for it
    for hash_variable in hash_variables:
      hash_context[hash_variable] = None
      start_index[hash_variable] = 0
      current_node_id[hash_variable] = 0
      if hash_variable not in parsing_data['mappings']:
        log.warning("Unavailable required mapping '{}'".format(hash_variable))
        return False

      number_of_nodes[hash_variable] = len(parsing_data['mappings'][hash_variable])



    try:
      # compute a list of hash keys related to document ids
      seen = {}
      index = 0
      continue_explore = True

      # prepare a template for the expected output value
      template = jinja2.Template(hash_key)

      # only while there are nodes to explore
      while continue_explore is True:

        # we loop over the keys needed to create the hash key
        for key_name in hash_context:
          hash_context[key_name]  = ''
          # we loop over each document id
          for i, node in enumerate(parsing_data['mappings'][key_name][start_index[key_name]:]):
            index = i + start_index[key_name]
            if node['id'] == current_node_id[key_name]:
              hash_context[key_name] = hash_context[key_name] + node['data']
            else:
              break

          # only if there are more elements on the current node
          # update iteration variables and keep track of the node indexes to
          # remove
          if start_index[key_name] + 1 < number_of_nodes[key_name]:
            start_index[key_name] = index
          else:
            start_index[key_name] = number_of_nodes[key_name]

          selected_node_id = current_node_id[key_name]
          current_node_id[key_name] = node['id']


        # render the template using the created context
        resolved_hash_key =  template.render(hash_context)

        # if it is not the first time that we see this key, then append it
        # to the list, otherwise create a list
        if resolved_hash_key in seen:
          seen[resolved_hash_key].append(selected_node_id)
        else:
          seen[resolved_hash_key] = [ selected_node_id  ]

        # check if there are more nodes to explore
        continue_explore = False
        for key_name in hash_context:
          if start_index[key_name] < number_of_nodes[key_name] :
            continue_explore = True
            break

      # build a list of duplicated ids
      duplicated_documents_ids = []
      for hash_id in seen:
        if len(seen[hash_id]) > 1:
          duplicated_documents_ids.extend(seen[hash_id][1:])

      # if there are not duplicated values, exit earlier
      if len(duplicated_documents_ids) == 0:
        return True

      # sort and remove duplicates id
      duplicated_documents_ids = sorted(set(duplicated_documents_ids),key=int)
      duplicated_documents_length = len(duplicated_documents_ids)
      parsing_data['stats']['duplicated'] = duplicated_documents_length

      # report about duplicate ids
      log.info("There are {} duplicate documents which will be ignored"\
               "".format(parsing_data['stats']['duplicated']))

      # mark as None any node that must be removed
      for key_name in parsing_data['mappings']:
        for index, node in enumerate(parsing_data['mappings'][key_name]):
          # check if the node id is found in the list of
          # leftmost value exactly equal to node['id'] duplicated ids
          pos = bisect.bisect_left(duplicated_documents_ids, node['id'])
          if pos != duplicated_documents_length and \
                    duplicated_documents_ids[pos] == node['id']:
            # this node must be removed
            parsing_data['mappings'][key_name][index] = None


      # remove all nodes marked as None
      for key_name in parsing_data['mappings']:
        parsing_data['mappings'][key_name][:] = [ node for node in parsing_data['mappings'][key_name] if node is not None ]

    except Exception as e:
      log.warning("Error while executing plugin")
      return False

    return True
