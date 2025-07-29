# -*- coding: utf-8 -*-
# module date_format.py
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
import dateutil.parser                            #
from pathlib import Path                          #
import jinja2                                     #
log = logging.getLogger(__name__)                 #
# ---------------------------------------------------------------------------
class DateFormat(parscival_plugins.mapping.Mapper):

  _alias_ = 'mapping.transform.date_format'
  _version_ = '1.0.0'

  @staticmethod
  def process(parsing_spec, parsing_data, mapping_nodes, **params):
    """try to parse a date and produce a mapped value in the given format

    Args:
      params (list): list of parameters to use within this plugin
        mandatory:
          - format: explicit format string. For a complete list of formatting
            directives, see strftime() and strptime() Behavior.

    Returns:
      Boolean: True if the process is successful, False otherwise
    """
    # check the mandatory params
    if not 'format' in params :
      log.warning("Param 'format' is required")
      return False

    template = None
    if 'fallback' in params:
      try:
        # prepare a template for the expected fallback value
        template = jinja2.Template(params['fallback'])
      except Exception as e:
        log.warning("Template error while executing plugin")
        return False

    # try to parse and format the data value
    try:
      for node in mapping_nodes:
        # try to parse the data sring as a date
        mapped_date = dateutil.parser.parse(node['data'])
        # format the parse string according the given format parameter
        mapped_value = mapped_date.strftime(params['format'])
        # reassign data string according the mapped value
        node['data'] = mapped_value
    except ValueError as e:
      if 'fallback' in params:
        context = [ node['data'] ]
        # use fallback value
        node['data'] = template.render(_ = context)
      else:
        log.warning("Invalid date string '{}'".format(node['data']))
        # clean the invalid date
        node['data'] = ''
        return False

    except Exception as e:
      log.warning("Error while executing plugin")
      # clean the invalid date
      node['data'] = ''
      return False

    return True
