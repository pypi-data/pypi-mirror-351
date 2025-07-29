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
from pathlib import Path                                    #
import os                                                   #
import tempfile                                             #
import shutil                                               #
import contextlib                                           #
import codecs                                               #
import mmap                                                 #
from chardet.universaldetector import UniversalDetector     #
from collections import Counter                             #
# ---------------------------------------------------------------------------
class Converter(parscival_plugins.curating.Curator):

  _alias_ = 'curating.encode.convert'
  _version_ = '1.0.0'

  @staticmethod
  def detect_encoding(file_obj):
    """
    Detect the encoding of a file using chardet.

    Parameters:
      file_obj (file): The file object to detect encoding for.

    Returns:
      str: The detected encoding.
    """
    detector = UniversalDetector()
    with contextlib.closing(
      mmap.mmap(file_obj.fileno(), 0, access=mmap.ACCESS_READ)) as mm:
      for line in iter(mm.readline, b""):
        detector.feed(line)
        if detector.done:
          break
      detector.close()
    # reset file pointer after reading
    file_obj.seek(0)
    return detector.result['encoding']

  @staticmethod
  def detect_newline(file_obj, encoding, num_lines=100):
    """
    Detect the most common newline character in a file.

    Parameters:
      file_obj (file): The file object to detect newline characters for.
      encoding (str): The encoding of the file.
      num_lines (int): The number of lines to read for detection.

    Returns:
      str: The most common newline character.
    """
    newline_counter = Counter()

    # size of chunks to read
    chunk_size = 1024

    total_lines = 0

    with contextlib.closing(
      mmap.mmap(file_obj.fileno(), 0, access=mmap.ACCESS_READ)) as mm:
      buffer = b""
      while total_lines < num_lines:
        data = mm.read(chunk_size)
        if not data:
          break
        buffer += data
        try:
          text = buffer.decode(encoding)
        except UnicodeDecodeError:
          continue
        buffer = b""

        # split the decoded text into lines while keeping the end characters
        lines = text.splitlines(keepends=True)
        for line in lines:
          if line.endswith('\r\n'):
            newline_counter['\r\n'] += 1
          elif line.endswith('\r'):
            newline_counter['\r'] += 1
          elif line.endswith('\n'):
            newline_counter['\n'] += 1
          total_lines += 1
          if total_lines >= num_lines:
            break

      # determine the most common newline character
      if newline_counter:
        most_common_newline = max(newline_counter, key=newline_counter.get)
      else:
        most_common_newline = '\n'

    # reset file pointer after reading
    file_obj.seek(0)
    return most_common_newline

  @staticmethod
  def encode_file(file_obj, dest_path, from_encode, to_encode, old_newline, new_newline):
    """
    Encode a file from one encoding to another and replace newlines.

    Parameters:
      file_obj (file): The file object to read from.
      dest_path (Path): The path to the destination file.
      from_encode (str): The encoding to convert from.
      to_encode (str): The encoding to convert to.
      old_newline (str): The old newline character to replace.
      new_newline (str): The new newline character to replace with.

    Returns:
      bool: True if the encoding and newline replacement is successful, False otherwise.
    """
    # size of chunks to read
    BLOCKSIZE = 1048576

    try:
      # obtain the file descriptor from the file object
      file_descriptor = file_obj.fileno()

      with contextlib.closing(mmap.mmap(file_descriptor, 0, access=mmap.ACCESS_READ)) as mm:
        with codecs.open(dest_path, 'w', to_encode) as target_file:
          offset = 0
          leftover = ''
          while offset < mm.size():
            end = min(offset + BLOCKSIZE, mm.size())
            data = mm[offset:end]
            offset = end

            # decode the data, handling any leftover from the previous block
            contents = leftover + data.decode(from_encode)

            # if the contents end with a partial newline sequence, save it for the next block
            if contents.endswith(old_newline[0]) and old_newline != new_newline:
              leftover = contents[-len(old_newline):]
              contents = contents[:-len(old_newline)]
            else:
              leftover = ''

            # replace old newlines with new newlines in chunks if necessary
            if old_newline != new_newline:
              contents = contents.replace(old_newline, new_newline)

            # write the converted data to the target file
            target_file.write(contents)

          # handle any leftover data
          if leftover and old_newline != new_newline:
            leftover = leftover.replace(old_newline, new_newline)
          target_file.write(leftover)

      return True
    except Exception as e:
      log.error(f"Error encoding file: {e}")
      return False

  # Update default parameters with provided parameters
  @staticmethod
  def update_plugin_params(d, u):
    for k, v in u.items():
      if isinstance(v, dict):
        d[k] = Converter.update_plugin_params(d.get(k, {}), v)
      else:
        d[k] = v
    return d

  @staticmethod
  def process(parsing_spec, parsing_data, **params):
    """
    Process the files according to the specified parameters.

    Parameters:
      parsing_spec (dict): Specifications for parsing (not used in this function).
      parsing_data (dict): Data for parsing, including file descriptors and transient data.
      params (dict): Parameters for processing, including encoding, policy, and newline options.

    Returns:
      bool: True if processing is successful, False otherwise.
    """
    default_params = {
      'encode': {
        'from': 'guess',
        'to': 'utf-8',
      },
      'policy': 'only-non-complaint',
      'newline': 'LF',
      'transient': {
        'basedir': '/tmp',
        'cleanable': True
      }
    }

    # update params with the default values
    params = Converter.update_plugin_params(default_params, params)

    # setup newline character mappings
    newline_type = {
      '\n': 'LF',
      '\r\n': 'CRLF',
      '\r': 'CR'
    }

    newline_char = {
      'LF': '\n',
      'CRLF': '\r\n',
      'CR': '\r'
    }

    # determine the new newline character and type
    new_newline = newline_char[params['newline']] if params['newline'] in newline_char else '\n'
    new_newline_type = newline_type[new_newline]

    # files to process
    file_datasets = parsing_data['files']

    # create a temporary directory with the suffix 'parscival-transient-' in the provided
    # base directory or system temp directory
    base_dir = (params['transient']['basedir']
                if os.path.exists(params['transient']['basedir'])
                else tempfile.gettempdir())
    temp_dir  = tempfile.mkdtemp(prefix='parscival-transient-', dir=base_dir)
    temp_path = Path(temp_dir)

    # add temporary path to transient if cleanable
    if params['transient']['cleanable']:
      parsing_data['transient']['directories'].append(temp_path)

    # loop over each of the open descriptors in file_datasets
    for index, f in enumerate(file_datasets):
      try:
        file_path = Path(f.name)
        filename  = file_path.name
        encoded_file_path = temp_path / filename

        # detect encoding if from_encode is 'guess'
        if params['encode']['from'] == 'guess':
          from_encode = Converter.detect_encoding(f)
          if from_encode is None:
            log.error(f"Encoding detection failed for file: '{f}'")
            continue
          else:
            log.debug(f"Detected encoding for '{filename}': '{from_encode}'")
        else:
          from_encode = params['encode']['from']
          log.debug(f"Using encoding for '{filename}': '{from_encode}'")

        # detect the current newline character
        current_newline = Converter.detect_newline(f, from_encode)
        current_newline_type = newline_type[current_newline]
        log.debug(f"Detected newline for '{filename}': '{current_newline_type}'")

        # if both the encoding and line endings are already as expected there
        # is not nothing more to do
        if (params['policy']  == 'only-non-complaint' and
            params['newline'] == current_newline_type and
            params['encode']['to'] == from_encode):
          log.debug(f"File '{filename}' already has the expected encoding and line endings")
          continue

        # policy implies to always copy to the temporary directory
        if (params['newline'] == current_newline_type and
            params['encode']['to'] == from_encode):
          # Open the destination file in write-binary mode
          with open(encoded_file_path, 'wb') as out_file:
            # Copy the content of the source file to the destination file
            shutil.copyfileobj(f, out_file)
        else:
          to_encode = params['encode']['to']

          # log the encoding details
          log.info("Encoding '{}' from '{}:{}' to '{}:{}'".format(
            filename,
            from_encode, current_newline_type,
            to_encode, new_newline_type))

          # try to encode the file
          if not Converter.encode_file(f,
                                encoded_file_path,
                                from_encode,
                                to_encode,
                                current_newline,
                                new_newline):
            log.error("Encoding failed")
            continue

        # close the original file object
        f.close()

        # open the encoded file in read-write binary mode and update
        # the file object in file_datasets
        encoded_file_obj = open(encoded_file_path, 'r+b')
        file_datasets[index] = encoded_file_obj

        # add to global transient if cleanable
        if params['transient']['cleanable']:
          parsing_data['transient']['files'].append(encoded_file_path)

      # catch and log any exceptions that occur during processing
      except Exception as e:
        log.error(f"Error processing file '{filename}': '{e}'")

    return True
