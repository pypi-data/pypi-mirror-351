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
from parscival.utils.logging import logging_decorator
from parscival.utils.logging import logging_set_context
# ---------------------------------------------------------------------------
log = logging.getLogger(__name__)
# ---------------------------------------------------------------------------
class LoggingMixin:
  """
  Mixin class to provide logging capabilities to other classes.
  """
  _version_ = '1.0.1'

  @staticmethod
  def get_logging_prefix(cls):
    # ensure it has at least 30 characters with padding
    prefix = f"|{cls.__module__.split('.')[-1].lower()}:{cls._version_}"
    prefix = f"{prefix:<30}|"
    return prefix

  @classmethod
  def apply_logging_context(cls, func: callable) -> callable:
    """
    Apply logging context decorator with class-specific prefix.

    Args:
    - func: The function to decorate with logging context.

    Returns:
    - Decorated function with logging context applied.
    """
    return logging_decorator(LoggingMixin.get_logging_prefix(cls))(func)

  @staticmethod
  def set_context(value: str):
    """
    Set context for all logging handlers.

    This method traverses the logger hierarchy and applies the given context value to all
    handlers that support the set_context method.

    Args:
    - value (str): The context value to set.
    """
    logging_set_context(logging.getLogger(), value)

  def __init_subclass__(cls, **kwargs):
    """
    Automatically decorate the plugins abstract methods with logging context.
    """
    super().__init_subclass__(**kwargs)
    # list of methods to decorate
    methods_to_decorate = ['process', 'init']
    # decorate each method
    for method_name in methods_to_decorate:
      if method_name in cls.__dict__ and isinstance(cls.__dict__[method_name], staticmethod):
        original_method = cls.__dict__[method_name].__func__
        decorated_method = cls.apply_logging_context(original_method)
        setattr(cls, method_name, staticmethod(decorated_method))
# ---------------------------------------------------------------------------
