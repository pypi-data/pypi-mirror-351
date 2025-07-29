# -*- coding: utf-8 -*-
# module peg.py
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
import parscival_plugins.parsing                  #
import logging                                    #
import re                                         #
import copy                                       #
from pathlib import Path                          #
log = logging.getLogger(__name__)                 #
# ---------------------------------------------------------------------------
from parsimonious.grammar import Grammar          #
from parsimonious.nodes import NodeVisitor        #
from parsimonious.exceptions import ParseError    #
# ---------------------------------------------------------------------------
class Parser(parscival_plugins.parsing.Parser):

  # parsing expression grammar (PEG)
  # space = O(grammar size * text length)
  # complexity = O(text length)

  _alias_ = 'parsing.grammar.PEG'
  _version_ = '1.0.0'

  @staticmethod
  def process_tree(parsing_spec, dataset_info, document_info, document_tree):
    """process the document tree

    Args:

    Returns:
      Text: Parsed Keys - Values
    """
    class KeyValueVisitor(NodeVisitor):
      def visit_dataset(self, node, visited_children):
        """ Gets the dataset. """
        documents = visited_children
        return documents

      def visit_document(self, node, visited_children):
        """ Gets the document. """
        _, record_start, record_members, record_end, = visited_children
        record_members.insert(0,record_start)
        record_members.append(record_end)
        return [r for r in record_members if r is not None]

      def visit_record_member(self, node, visited_children):
        """ Returns a key-value pair. """
        key, _, value, *_ = node.children

        # common processing for any value
        custom_value_text = value.text.strip()
        custom_value_text = re.sub(r'\r?\n +', ' ', custom_value_text)
        custom_value_text = re.sub(r'  +', ' ',  custom_value_text)

        # only process requested keys
        if (parsing_spec['data']['options']['only_requested_keys'] == False or
           key.text in parsing_spec['data']['initializing']['keys']['parsing']):
          return key.text, custom_value_text

        # mark this member as not to be used
        return None

      def visit_record_start(self, node, visited_children):
        """ Returns record start. """
        return self.visit_record_member(node, visited_children)

      def visit_record_end(self, node, visited_children):
        """ Returns record end. """
        return self.visit_record_member(node, visited_children)

      def generic_visit(self, node, visited_children):
        """ The generic visit method. """
        return visited_children or node

    visitor = KeyValueVisitor()
    return visitor.visit(document_tree)

  @staticmethod
  def init(parsing_spec, **params):
    log.info("Starting parser for {} ({}) data".format(
              parsing_spec['data']['source'], parsing_spec['data']['format']))
    try:
      parsing_spec['grammar'] = Grammar(parsing_spec['data']['parsing']['grammar']['rules'])
    except Exception as e:
      log.error(e)
      return False

    return True

  @staticmethod
  @pluginlib.abstractmethod
  def can_parse(parsing_spec, dataset_info, document_info, document_line, **params):
    return parsing_spec['grammar']['record_start'].parse(document_line)

  @staticmethod
  @pluginlib.abstractmethod
  def buffer_restart(parsing_spec, dataset_info, document_info, document_line, **params):
    return document_line

  @staticmethod
  def process(parsing_spec, dataset_info, document_info, **params):
    """Parscival parse a text buffer using a PEG grammar

    Args:

    Returns:
      Tree: a parse tree on document_info['buffer']
    """
    try:
      document_tree = parsing_spec['grammar'].parse(document_info['buffer'])

    except ParseError as e:
      ## e.g. malformed document (line 227717)
      log.warning("[cyan]{}[/cyan] - malformed document (line {})".format(
                                        dataset_info['filename'],
                                        document_info['line']['start']))

      # e.g. rule: 'record_end' didn't match (line 227754, column 1)
      log.debug("[cyan]{}[/cyan] - rule: '{}' didn't match "
                "(line {}, column {})".format(
                           dataset_info['filename'],
                           e.expr.name,
                          (e.line() + document_info['line']['start'] - 1),
                           e.column()))
      return False

    except Exception as e:
      log.error(e)
      return False

    if document_tree is not None:
      dataset_info['documents'].append(
        Parser.process_tree(parsing_spec,
                            dataset_info,
                            document_info,
                            document_tree)[0]
      )
      return True

    return False
