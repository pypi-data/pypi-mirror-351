# -*- coding: utf-8 -*-
# module curating.py
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
import pluginlib                                  #
import logging                                    #
# ---------------------------------------------------------------------------
from parscival_plugins.utils.logging_mixin import LoggingMixin
# ---------------------------------------------------------------------------
log = logging.getLogger(__name__)                 #
# ---------------------------------------------------------------------------
@pluginlib.Parent('curating')
class Curator(LoggingMixin):
  """
  Base class for curating tasks with logging capabilities.
  """
  _alias_ = 'curating'
  _version_ = '1.0.1'

  @staticmethod
  @pluginlib.abstractmethod
  def process(parsing_spec: dict, parsing_data: dict, **params) -> bool:
    """
    Abstract method to be implemented by subclasses for data processing.

    Args:
    - parsing_spec (dict): Specifications for data parsing.
    - parsing_data (dict): Data to be parsed and processed.
    - **params: Additional keyword arguments for processing.

    Returns:
    - bool: True if processing is successful, False otherwise.
    """
    pass
