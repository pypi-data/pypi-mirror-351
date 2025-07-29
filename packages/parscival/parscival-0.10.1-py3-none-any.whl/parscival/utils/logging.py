# -*- coding: utf-8 -*-
# module utils.py
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
import logging                                    #
import inspect                                    #
import os                                         #
from types import SimpleNamespace                 #
# ---------------------------------------------------------------------------
from functools import wraps                       #
# ---------------------------------------------------------------------------
log = logging.getLogger(__name__)
# ---------------------------------------------------------------------------


def logging_set_context(logger, value):
  """
  Traverse the logger hierarchy and set the context for each handler that supports it.

  Args:
  - logger: The logger instance to start from.
  - value: The context value to set.

  Note:
  - This function will ignore handlers that do not have a set_context method.
  """
  current_logger = logger
  while current_logger:
    for handler in current_logger.handlers:
      if hasattr(handler, 'set_context'):
        try:
          handler.set_context(value)
        except AttributeError:
          # ignore handlers without a set_context method
          pass
    if current_logger.propagate:
      current_logger = current_logger.parent
    else:
      current_logger = None
# ---------------------------------------------------------------------------


def logging_decorator(prefix: str):
  """
  Decorator to add and remove a logging filter around a function call.
  """
  def decorator(func):
    """
    Actual decorator function that wraps `func` with logging filters.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
      # Store previous context
      previous_context = None
      if hasattr(logging.root.handlers[0], 'context'):
        previous_context = logging.root.handlers[0].context

      # Set the new context
      if hasattr(logging.root.handlers[0], 'set_context'):
        logging.root.handlers[0].set_context(prefix)
      try:
        return func(*args, **kwargs)
      except Exception as e:
        details = {
          'filename': os.path.basename(inspect.getfile(func)),
          'line_number' : inspect.currentframe().f_lineno,
          'function_name': func.__name__
        }
        e.details = SimpleNamespace(**details)
        raise e
      finally:
        # Restore previous context
        if hasattr(logging.root.handlers[0], 'set_context'):
          logging.root.handlers[0].set_context(previous_context)

    # Preserve the original function's signature
    wrapper.__signature__ = inspect.signature(func)
    return wrapper

  return decorator
