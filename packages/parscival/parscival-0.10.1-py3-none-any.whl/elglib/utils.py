# -*- coding: utf-8 -*-
# module core.py
#
# Copyright (c) 2015-2024  Cogniteva SAS
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
# Minimal port of the ELG functionality from Cogniteva's Wolfish Record
# Linkage (WRL) Library
# ---------------------------------------------------------------------------
import pkg_resources                              #
import subprocess                                 #
import sys                                        #
import os                                         #
import platform                                   #
import hashlib                                    #
import shutil                                     #
import logging                                    #
log = logging.getLogger(__name__)                 #
# ---------------------------------------------------------------------------


def md5sum(filename):
  """
  Compute the MD5 checksum of a file.

  Args:
    filename (str): the path to the file for which the MD5 checksum is computed.

  Returns:
    str: the hexadecimal representation of the MD5 checksum.
  """
  # compute the md5 checksum
  md5_hash = hashlib.md5()
  with open(filename, 'rb') as f:
    for byte_block in iter(lambda: f.read(4096), b''):
      md5_hash.update(byte_block)

  # hexadecimal representation
  filename_md5 = md5_hash.hexdigest()
  return filename_md5
# ---------------------------------------------------------------------------

def md5sum_combine(md5_1, md5_2):
  """
  Combine two MD5 checksums into a single string of the length of one MD5 checksum.

  Args:
    md5_1 (str): the first MD5 checksum in hexadecimal.
    md5_2 (str): the second MD5 checksum in hexadecimal.

  Returns:
    str: the combined MD5 checksum in hexadecimal.
  """
  # Convert the hex strings to bytes
  bytes_1 = bytes.fromhex(md5_1)
  bytes_2 = bytes.fromhex(md5_2)

  # XOR the bytes together
  combined_bytes = bytes(a ^ b for a, b in zip(bytes_1, bytes_2))

  # Convert the combined bytes back to a hex string
  return combined_bytes.hex()
# ---------------------------------------------------------------------------


def srmdir(path, whitelist=None, blacklist=None):
  """
  Safely remove a directory, ensuring it's not a system directory.

  Args:
    path (str): The directory path to remove.
    whitelist (list): Directories allowed to be removed.
    blacklist (list): Directories not allowed to be removed.

  Raises:
    ValueError: If an attempt is made to delete a protected or root directory.
  """

  # ensure the directory is not root
  if path == "/":
    raise ValueError("attempt to delete root directory is not allowed.")

  # normalize the path to avoid issues with trailing slashes
  path = os.path.normpath(path)

  # set default whitelists and blacklists if not provided
  if whitelist is None:
    whitelist = []
  if blacklist is None:
    blacklist = ["/", "/bin", "/boot", "/dev", "/etc", "/home", "/lib",
                 "/proc", "/root", "/sys", "/usr", "/var"]

  # check if path is in the blacklist
  if path in blacklist:
    raise ValueError(f"Attempt to delete a protected directory is not allowed: {path}")

  # if a whitelist is provided, ensure the path is within the whitelist
  if whitelist and path not in whitelist:
    raise ValueError(f"attempt to delete a directory not in the whitelist: {path}")

  # check if the directory exists before attempting to delete
  if os.path.exists(path):
    shutil.rmtree(path)


def is_buffer(obj):
  """Check if the object is a buffer."""
  return isinstance(obj, (bytes, bytearray))


def key_identity(key):
  """Identity function for keys."""
  return key

# @source https://github.com/hughsk/flat


def flatten(target, delimiter='.', max_depth=None, transform_key=None, safe=False):
  """Flatten a nested dictionary."""
  if transform_key is None:
    transform_key = key_identity

  def step(object_, prev_key='', current_depth=1, output=None):
    if output is None:
      output = {}

    for key, value in object_.items():
      new_key = f"{prev_key}{delimiter}{transform_key(key)}" if prev_key else transform_key(
          key)
      if isinstance(value, dict) and (max_depth is None or current_depth < max_depth):
        step(value, new_key, current_depth + 1, output)
      else:
        output[new_key] = value

    return output

  return step(target)

# @source https://github.com/hughsk/flat


def unflatten(target, delimiter='.', overwrite=False, transform_key=None):
  """Unflatten a dictionary."""
  if transform_key is None:
    transform_key = key_identity

  def get_key(key):
    try:
      return int(key) if '.' not in key else key
    except ValueError:
      return key

  result = {}

  for key, value in target.items():
    keys = key.split(delimiter)
    keys = [transform_key(k) for k in keys]
    d = result

    for k in keys[:-1]:
      k = get_key(k)
      if k not in d or not isinstance(d[k], dict):
        d[k] = {}
      d = d[k]

    k = get_key(keys[-1])
    if overwrite or k not in d:
      d[k] = value

  return result
