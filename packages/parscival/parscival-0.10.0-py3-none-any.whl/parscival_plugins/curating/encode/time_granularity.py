# -*- coding: utf-8 -*-
# module convert.py
#
# Copyright (c) 2024  Cogniteva SAS
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
import pandas as pd
import datetime
# ---------------------------------------------------------------------------
class TimeGranularityEncoder(parscival_plugins.curating.Curator):
  """
  Encodes time granularity for given data mappings.
  """

  _alias_ = 'curating.encode.time_granularity'
  _version_ = '1.0.0'

  # Update default parameters with provided parameters
  @staticmethod
  def update_plugin_params(d: dict, u: dict) -> dict:
    for k, v in u.items():
      if isinstance(v, dict):
        d[k] = TimeGranularityEncoder.update_plugin_params(d.get(k, {}), v)
      else:
        d[k] = v
    return d

  @staticmethod
  def get_default_params() -> dict:
    """
    Update default parameters with provided parameters.

    Args:
      d (dict): Default parameters.
      u (dict): User-provided parameters.

    Returns:
      dict: Updated parameters.
    """
    default_params = {
      'input_date_format': 'mixed',
      'output_time_format': 'timelapse',
      'granularity': 'years'
    }

    return default_params

  @staticmethod
  def get_granularity_code(granularity: str) -> str:
    """
    Convert granularity string to period code.

    Args:
      granularity (str): Granularity string.

    Returns:
      str: Corresponding period code.

    Raises:
      ValueError: If the granularity is not recognized.
    """
    granularity_to_code = {
      'yearly':         'Y',
      'year':           'Y',
      'years':          'Y',
      'quarterly':      'Q',
      'quarters':       'Q',
      'quarter':        'Q',
      'monthly':        'M',
      'months':         'M',
      'month':          'M',
      'weekly':         'W',
      'weeks':          'W',
      'week':           'W',
      'business day':   'B',
      'business days':  'B',
      'calendar day':   'D',
      'calendar days':  'D',
      'day':            'D',
      'days':           'D',
      'hourly':         'h',
      'hours':          'h',
      'hour':           'h',
      'minutely':       'min',
      'minutes':        'min',
      'minute':         'min',
      'secondly':       's',
      'seconds':        's',
      'second':         's',
      'milliseconds':   'ms',
      'millisecond':    'ms',
      'microseconds':   'us',
      'microsecond':    'us',
      'nanoseconds':    'ns',
      'nanosecond':     'ns'
    }

    if not granularity in granularity_to_code:
      raise ValueError(f"Granularity '{granularity}' not recognized")

    return granularity_to_code[granularity]

  @staticmethod
  def get_date_format(granularity_code: str) -> str:
    """
    Convert granularity code to a corresponding date format.

    Args:
      granularity_code (str): Granularity code from get_granularity_code.

    Returns:
      str: Corresponding date format.
    """

    date_format_mapping = {
      'Y': '%Y',
      'Q': '%YQ%q',
      'M': '%Y%m',
      'W': '%Y%U',
      'B': '%Y%m%d',
      'D': '%Y%m%d',
      'h': '%Y%m%d%H',
      'min': '%Y%m%d%H%M',
      's': '%Y%m%d%H%M%S',
      'ms': '%Y%m%d%H%M%S%f',
      'us': '%Y%m%d%H%M%S%f',
      'ns': '%Y%m%d%H%M%S%f'
    }

    if not granularity_code in date_format_mapping:
      raise ValueError(f"Granularity code '{granularity_code}' not recognized")

    return date_format_mapping[granularity_code]

  @staticmethod
  def assign_granularity(df: pd.DataFrame, params: dict) -> None:
    """
    Assign time granularity to the data.

    Args:
      df (pd.DataFrame): DataFrame containing the data.
      params (dict): Parameters for granularity assignment.
    """
    # validate start_from
    if 'start_from' in params:
      log.error(params['start_from'])
      if not isinstance(params['start_from'], int) or params['start_from'] < 0:
        raise ValueError(f"start_from '{params['start_from']}' must be a positive integer")

    # validate output_time_format
    valid_output_formats = {'bins', 'timelapse', 'dateint'}
    output_time_format = params.get('output_time_format', 'timelapse')
    if output_time_format not in valid_output_formats:
      raise ValueError(f"output_time_format '{output_time_format}' must be one of {valid_output_formats}")

    # extract parameter values
    granularity_code = TimeGranularityEncoder.get_granularity_code(params['granularity'])
    input_date_format = params['input_date_format']  # 'mixed' or date format string

    # convert the 'data' column from string to datetime
    df['data'] = pd.to_datetime(df['data'], format=input_date_format)

    if output_time_format == 'bins':
      start_from = params['start_from']
      # convert according to the specified granularity
      df['data'] = df['data'].dt.to_period(granularity_code)
      unique_periods = sorted(df['data'].unique())
      period_mapping = {period: idx + start_from for idx, period in enumerate(unique_periods)}
      df['data'] = df['data'].map(period_mapping)
    elif output_time_format == 'timelapse':
      # Compute timelapse index based on earliest date
      min_period = df['data'].dt.to_period(granularity_code).min()
      df['data'] = df['data'].dt.to_period(granularity_code).apply(lambda x: x.ordinal - min_period.ordinal)
    elif output_time_format == 'dateint':
      # mapping of granularity code to date format
      date_format_mapping = TimeGranularityEncoder.get_date_format(granularity_code)
      # Format datetime using granularity-specific format
      df['data'] = df['data'].apply(lambda x: int(x.strftime(date_format_mapping)))

    # ensure integers in output
    df['data'] = df['data'].astype(int)

  @staticmethod
  def process(parsing_spec: dict, parsing_data: dict, **params) -> bool:
    """
    Process the given data to encode time granularity.

    Args:
      parsing_spec (dict): Parsing specifications.
      parsing_data (dict): Data to be parsed.
      **params: Additional parameters.

    Returns:
      bool: True if processing is successful, False otherwise.
    """
    # check the mandatory params
    if not 'node' in params:
      log.warning("Param 'node' is required")
      return False

    # check if the node is available
    if not params['node'] in parsing_data['mappings']:
      # node is not available, but this must not be considered as an error
      return True

    # update params with the default values
    params = TimeGranularityEncoder.update_plugin_params(
            TimeGranularityEncoder.get_default_params(),
            params)

    try:
      # convert the node into a dataframe
      df = pd.DataFrame(parsing_data['mappings'].get(params['node'],{}))

      # assign the granularity according the given parameters
      TimeGranularityEncoder.assign_granularity(df, params)

      # convert back the dataframe to a node
      # records: each row in the dataframe should be converted to a dictionary,
      # and the resulting dictionaries should be stored in a list
      node = df.to_dict(orient='records')

      # and assign back to the original node
      # Using set() to handle new or existing entries
      parsing_data['mappings'][params['node']] = node
    except Exception as e:
      log.error("Error raised: {} ".format(e))
      raise e

    return True
