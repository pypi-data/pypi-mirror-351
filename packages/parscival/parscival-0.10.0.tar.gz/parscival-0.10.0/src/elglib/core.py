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
import logging                                    #
log = logging.getLogger(__name__)                 #
# ---------------------------------------------------------------------------
from pathlib import Path                          #
import subprocess                                 #
import shutil                                     #
import tempfile                                   #
import re                                         #
from .utils import md5sum, md5sum_combine, srmdir  #
# ---------------------------------------------------------------------------
def guess_platform():
  """
  Identifies the platform and returns a string based on the system architecture
  and operating system.

  Returns:
      str: One of the following strings:
          - 'linux-i686'
          - 'linux-x86_64'
          - 'osx'
          - 'win32'
          - 'win64'
          - 'unknown'
  """
  system = platform.system().lower()
  machine = platform.machine().lower()

  # check if the system is linux
  if system == 'linux':
    if 'x86_64' in machine:
      return 'linux-x86_64'
    elif 'i386' in machine or 'i686' in machine:
      return 'linux-i686'
  # check if the system is mac os x
  elif system == 'darwin':
    return 'osx'
  # check if the system is windows
  elif system == 'windows':
    if sys.maxsize > 2**32:
      return 'win64'
    else:
      return 'win32'

  # return unknown if the platform is not identified
  return 'unknown'

def elg_get_binary():
  # get the path to the binary file
  relative_path = os.path.join('engine', 'platform', guess_platform(), 'elg-unitex')
  elg_binary = pkg_resources.resource_filename('elglib', relative_path)
  # checks if the elg binary exists and is executable
  if os.path.exists(elg_binary) and os.access(elg_binary, os.X_OK):
    return elg_binary

  log.error(f"ELG binary not found in '{os.path.join('elglib',relative_path)}'")
  # return false
  return False

def create_cache_dir(cash_name, **params):
  cache_dir = params['cache'].get('dir', '/tmp')
  cache_dir = os.path.join(cache_dir, cash_name)
  # create cache directory if it does not exist
  os.makedirs(cache_dir, exist_ok=True)
  return cache_dir

def get_from_cache(cash_name, file_hashname, use_type, **params):
  """
  Get the result from cache based on the data filename and parameters.

  Args:
    data_filename (str): the path to the data file.
    **params (dict): additional parameters for cache configuration.

  Returns:
    str or bool: the cached result if it exists, False otherwise.
  """
  if params.get('cache', {}).get(use_type, False):
    cache_dir = params['cache'].get('dir', '/tmp')
    cache_path = os.path.join(cache_dir, cash_name, file_hashname)
    if os.path.exists(cache_path):
      return cache_path
  return False

def setup_params(registry_filename, **params):
  """
  Setup and return the parameters dictionary, merging default values with provided parameters.

  Args:
    **params: Arbitrary keyword arguments for parameter values.

  Returns:
    dict: A dictionary with parameters, including default values for missing ones.
  """
  default_params = {
    'filter_mode': 'relaxed',
    'matches': {
      'ambiguous_policy': 'warn',
      'ambiguous_delimiter': ' *** '
    },
    'cache': {
      'dir': '/tmp',
      'store_compiled': True,
      'store_result': True,
      'use_cached_registry': True,
      'use_cached_result': True
    },
    'verbose': 'error'
  }

  # Update default parameters with provided parameters
  def recursive_update(d, u):
    for k, v in u.items():
      if isinstance(v, dict):
        d[k] = recursive_update(d.get(k, {}), v)
      else:
        d[k] = v
    return d

  params = recursive_update(default_params, params)

  cache_dir = params['cache']['dir']

  # Check if cache_dir is an absolute path
  if not os.path.isabs(cache_dir):
    # Make the relative path absolute relative to the parent of the registry_filename
    parent_dir = os.path.dirname(os.path.abspath(registry_filename))
    cache_dir = os.path.join(parent_dir, cache_dir)
    params['cache']['dir'] = os.path.normpath(os.path.abspath(cache_dir))

  # create cache directory if it does not exist
  os.makedirs(cache_dir, exist_ok=True)

  return params

def elg_clean_dictionary_cache(registry_cache_name, **params):
  # global cache directory
  cache_dir = params['cache']['dir']
  # cache directory for this register
  registry_cache_dir = os.path.join(cache_dir, registry_cache_name)
  # remove any previous cached files for this register
  srmdir(registry_cache_dir)
  # return the name of the delete directory
  return registry_cache_dir

def elg_make_dictionary(ELG_BINARY,registry_filename,
                        registry_hashname,
                        registry_cache_name,
                        stdout_descriptor=subprocess.DEVNULL,
                        stderr_descriptor=subprocess.DEVNULL,
                        **params):

  if not registry_cache_name.strip():
    return { 'valid':  False}

  # clean any previous cache
  registry_cache_dir = elg_clean_dictionary_cache(registry_cache_name, **params)

  # prepare the name to store the dic version of the register
  dictionary_dic = os.path.join(registry_cache_dir, registry_hashname) + '.dic'

  # create cache directory for this register if not already exists
  os.makedirs(registry_cache_dir, exist_ok=True)

  # regex to find multiple spaces
  collapse_spaces  = re.compile(r'\s+')
  # regex to find '{', and '}'
  sanitize_special = re.compile(r'[}{]')
  # regex to find '-'
  sanitize_dash = re.compile(r'\s+-\s+')
  # regex to find unescaped ., ,, and +
  flexional_special = re.compile(r'(?<!\\)([.,+])')
  # regex to find unescaped ., ,, and +
  lemma_special = re.compile(r'(?<!\\)([.,+])')
  # main lexical category
  lexical_entry_code = 'N'


  def make_dictionary_entries(line, line_number):
    nonlocal collapse_spaces, sanitize_special
    nonlocal flexional_special, lemma_special

    #  sanitize special characters
    line = sanitize_special.sub(' ', line)

    # collapse multiple spaces
    line = collapse_spaces.sub(' ', line)

    # remove leading and trailing whitespace
    line = line.strip()

    # ignore empty or comment lines
    if line.startswith('/') or not line:
      return ''

    # try to split into the flexional and canonical forms
    forms = line.split(';')
    if len(forms) != 2:
      log.warning("'{}:{}' - Ignoring invalid registry entry : '{}'".format(
          params['registry'], line_number, line
      ))
      return ''

    # replace unescaped characters with their escaped versions
    flexional = flexional_special.sub(r'\\\1', forms[0])
    flexional = sanitize_dash.sub(' ', flexional)
    # replace unescaped characters with their escaped versions
    lemma     = lemma_special.sub(r'\\\1', forms[1])

    # create the lexical entry
    lexical_entry = "{},{}.{}".format(flexional,lemma,lexical_entry_code)

    return lexical_entry + '\n'

  # track line number for logging purposes
  line_number = 1
  def make_dictionary_entries_with_tracking(line):
    nonlocal line_number
    processed_entry = make_dictionary_entries(line, line_number)
    line_number += 1
    return processed_entry

  # convert registry into DELAF format
  edit_file_lines(dictionary_dic,
                  make_dictionary_entries_with_tracking,
                  registry_filename)

  dictionary_bin = os.path.join(registry_cache_dir, registry_hashname) + '.bin'

  def compile_dictionary(dictionary_dic, dictionary_bin):
    nonlocal ELG_BINARY, stdout_descriptor, stderr_descriptor
    ELG_RESOURCES  = os.getenv('ELG_RESOURCES',
                     pkg_resources.resource_filename('elglib', 'engine/graphs'))

    compress_args = [ELG_BINARY, 'Compress', f"{dictionary_dic}", f"-o{dictionary_bin}"] + \
                    ['-qutf8-no-bom']
    # debug argguments
    log.trace("\",\n\"".join(compress_args) + "\"")
    try:
      subprocess.run(compress_args, check=True,
                     stdout=stdout_descriptor,
                     stderr=stderr_descriptor)
    except subprocess.CalledProcessError as e:
      log.error('Compress command failed.')
      return False

    return True

  # try to compile the created dictionary
  if compile_dictionary(dictionary_dic, dictionary_bin):
    # os.remove(dictionary_dic)
    return { 'valid':  True, 'file': dictionary_bin}

  os.remove(dictionary_dic)
  return { 'valid':  False}

def parse_named_arguments(named_args_str):
  if named_args_str:
    named_args = named_args_str.split(';')
    for arg in named_args:
      key, _, value = arg.partition('=')
      log.trace(f"Parsed param: {key}={value}")
      os.environ[key] = value

def elg_dic_tagger(ELG_BINARY, input_file, output_file=None, temp_prefix='tmp',
                   named_arguments_string=None, sentence_fst2=None,
                   dictionaries=None, matching_mode = 'longest_matches',
                   matching_overlaps_policy = 'allow_overlap_matches',
                   apply_options=None, protect_empty_lines=False,
                   stdout_descriptor=subprocess.DEVNULL,
                   stderr_descriptor=subprocess.DEVNULL):

    ELG_RESOURCES  = os.getenv('ELG_RESOURCES', pkg_resources.resource_filename('elglib', 'engine/graphs'))
    ELG_BUILD      = os.getenv('ELG_BUILD', pkg_resources.resource_filename('elglib', 'engine/graphs/build'))
    ELG_EXTENSIONS = os.getenv('ELG_EXTENSIONS', pkg_resources.resource_filename('elglib', 'engine/elg'))

    # Make sure the ELG_BINARY, RESOURCES and BUILD directories exist
    for required_path in [ELG_BINARY, ELG_RESOURCES, ELG_BUILD]:
        if not os.path.exists(required_path):
            log.error(f"Required resource does not exist: {required_path}")
            return False

    if not os.path.exists(input_file):
        log.error(f"'{input_file}' file not found")
        return False

    # Check if dictionaries are provided
    if not dictionaries:
        log.error('No dictionaries provided. At least one dictionary is required.')
        return False

    dictionaries_with_extension = []
    for dict_name in dictionaries:
        if not os.path.isabs(dict_name):
          dict_name = os.path.join(ELG_BUILD, dict_name)
        name, ext = os.path.splitext(dict_name)
        if ext:  # If there's an extension, don't add '.bin'
            dictionaries_with_extension.append(f"{dict_name}")
        else:  # If there's no extension, add '.bin'
            dictionaries_with_extension.append(f"{dict_name}.bin")

    dictionaries = dictionaries_with_extension
    log.trace(f"{dictionaries}")
    # Check if all dictionaries exist
    missing_dictionaries = [dict_name for dict_name in dictionaries if not os.path.isfile(dict_name) ]
    if missing_dictionaries:
      log.error(f"The following dictionaries are missing: {', '.join(missing_dictionaries)}")
      return False

    # Use the provided Sentence.fst2 path or the default one
    sentence_fst2_path = sentence_fst2 if sentence_fst2 is not None else f"{ELG_RESOURCES}/Sentence.fst2"

    parse_named_arguments(named_arguments_string)

    create_cache = os.getenv('create_cache', '0') == '1'
    use_cache = os.getenv('use_cache', '0') == '1'
    cache_dir = os.getenv('cache_dir', '')
    task_name = os.getenv('task_name', '')
    task_compile = os.getenv('task_compile', '0') == '1'

    if task_name == '':
      log.error('TASK_NAME environment variable is not set.')
      return False

    if ELG_BUILD is None or not os.path.isfile(f"{ELG_BUILD}/{task_name}.fst2"):
      log.error(f"File doesn't exist: {ELG_BUILD}/{task_name}.fst2")
      return False

    if use_cache and not os.path.isdir(cache_dir):
      if not cache_dir:
        log.error(f"Use cache requested, but cache_dir is unset")
      else:
        log.error(f"Use cache requested, but cache_dir={cache_dir} is not a directory")
      return False

    if not use_cache:
      # create a temporary file and copy the input file content to it
      with tempfile.NamedTemporaryFile(prefix=temp_prefix, delete=False, dir='/tmp', mode='w+', encoding='utf-8') as temp_file:
        shutil.copyfile(input_file, temp_file.name)
        temp_file_path = temp_file.name

      if protect_empty_lines:
        # Read through each line and check if it contains only spaces
        with open(temp_file_path, 'r', encoding='utf-8') as file:
          lines = file.readlines()

        modified_lines = ['[[]]\n' if line.isspace() else line.replace('\\n', ' ') for line in lines]

        with open(temp_file_path, 'w', encoding='utf-8') as file:
          file.writelines(modified_lines)

      input_file = temp_file_path

    # Path manipulations
    dirname = os.path.dirname(input_file)
    filename = os.path.basename(input_file)
    filename_without_ext, extension = os.path.splitext(filename)
    corpus_dsnt = os.path.join(dirname, f"{filename_without_ext}_snt")
    corpus_snt = os.path.join(dirname, f"{filename_without_ext}.snt")
    output_file = output_file or f"{dirname}/{filename_without_ext}.tag"

    if use_cache and corpus_dsnt != cache_dir:
      log.error(f"Using cache but {corpus_dsnt} and {cache_dir} differs")
      return False

    if use_cache and not os.path.isfile(corpus_snt):
      log.error(f"Using cache but {corpus_snt} doesn't exist")
      return False

    log.trace((corpus_dsnt,corpus_snt,output_file))
    os.makedirs(corpus_dsnt, exist_ok=True)

    if ELG_BINARY is None or ELG_RESOURCES is None:
      log.error('ELG_BINARY or RESOURCES environment variable is not set.')
      return False

    if not use_cache or not os.path.isfile(corpus_snt):
      # Replace with actual ELG Engine commands and appropriate paths
      normalize_args = [ELG_BINARY, 'Normalize', input_file, f"-r{ELG_RESOURCES}/Norm.txt", '-qutf8-no-bom']
      log.trace("\",\n\"".join(normalize_args) + "\"")
      subprocess.run(normalize_args, stdout=stdout_descriptor, stderr=stderr_descriptor)


      fst2txt_args = [ELG_BINARY, 'Fst2Txt', f"-t{corpus_snt}", f"{sentence_fst2_path}", f"-a{ELG_RESOURCES}/Alphabet.txt", '-M', '-qutf8-no-bom']
      log.trace("\",\n\"".join(fst2txt_args) + "\"")
      subprocess.run(fst2txt_args, stdout=stdout_descriptor, stderr=stderr_descriptor)

      tokenize_args = [ELG_BINARY, 'Tokenize', corpus_snt, f"-a{ELG_RESOURCES}/Alphabet.txt", '-qutf8-no-bom']
      log.trace("\",\n\"".join(tokenize_args) + "\"")
      subprocess.run(tokenize_args, stdout=stdout_descriptor, stderr=stderr_descriptor)

    # Dicos have changed
    # note DICOS_HAVE_CHANGED is default to use_cache
    dicos_have_changed = os.getenv('DICOS_HAVE_CHANGED', '1') == '1' and not use_cache
    if dicos_have_changed:
      if task_compile:
        for dict_name in dictionaries:
          if dict_name.endswith('.fst2'):
            dict_name_without_extension = dict_name[:-5]
            log.trace(f"Compiling dictionary graph {dict_name_without_extension}.grf")
            try:
              grf2fst_args = [ELG_BINARY, 'Grf2Fst2', f"{dict_name_without_extension}.grf", '-y' ] + \
                             [f"-a{ELG_RESOURCES}/Alphabet.txt", '-qutf8-no-bom']
              log.trace("\",\n\"".join(grf2fst_args) + "\"")
              subprocess.run(grf2fst_args, check=True, stdout=stdout_descriptor, stderr=stderr_descriptor)
            except subprocess.CalledProcessError as e:
              log.error('Grf2Fst2 command failed.')
              return False

      log.trace(f"Applying dictionaries")
      # Modified list comprehension to create pairs of command line arguments
      dicos_to_apply  = [
        [f"-P{apply_options[i]}", f"{dict_name}"] if apply_options and apply_options[i] else [f"{dict_name}"]
        for i, dict_name in enumerate(dictionaries)
      ]

      # Flatten the list to get individual command line arguments
      flattened_dicos_to_apply_list = [item for sublist in dicos_to_apply for item in sublist]

      # replaced by policy -Pbin:m
      # [f"-m{BUILD}/{dict_name}" for dict_name in dictionaries if dict_name.endswith('.bin')] + \

      dico_args = [ELG_BINARY, 'Dico', f"-t{corpus_snt}", f"-a{ELG_RESOURCES}/Alphabet.txt"] + \
                  flattened_dicos_to_apply_list   + \
                  ['-qutf8-no-bom']
      # log.trace(" ".join(dico_args))
      log.trace("\",\n\"".join(dico_args) + "\"")
      try:
        subprocess.run(dico_args, check=True, stdout=stdout_descriptor, stderr=stderr_descriptor)
      except subprocess.CalledProcessError as e:
        log.error('Dico command failed.')
        return False

    if task_compile:
      try:
        log.trace(f"Compiling graph {ELG_BUILD}/{task_name}.grf")
        grf2fst_args = [ELG_BINARY, 'Grf2Fst2', f"{ELG_BUILD}/{task_name}.grf", '-y' ] + \
                       [f"-a{ELG_RESOURCES}/Alphabet.txt", '-qutf8-no-bom']
        log.trace("\",\n\"".join(grf2fst_args) + "\"")
        subprocess.run(grf2fst_args, check=True, stdout=stdout_descriptor, stderr=stderr_descriptor)
      except subprocess.CalledProcessError as e:
        log.error('Grf2Fst2 command failed.')
        return False

    # Locate patterns using ELG Engine
    try:
      log.trace(f"Running {ELG_BUILD}/{task_name}.fst2")
      # Add matching mode argument before '-R'
      matching_modes = {
        'shortest_matches': '-S',
        'longest_matches': '-L',
        'all_matches': '-A'
      }

      matching_overlap_policies = {
        'allow_overlap_matches': '-O',
        'filter_overlap_matches': '-F'
      }

      # Retrieve the matching mode argument from the user input
      user_matching_mode = matching_modes.get(matching_mode)
      user_matching_overlap_policy = matching_overlap_policies.get(matching_overlaps_policy)

      # --stack_max=N: set max exploration step to save stack (default: 1000)
      stack_max=5000
      # --max_errors=N: set max number of error to display before exit (default: 50)
      max_errors=1000
      # --max_matches_per_subgraph=N: set max matches per subgraph (default: 200)
      max_matches_per_subgraph=10000
      # --max_matches_at_token_pos=N: set max matches per token (default: 400)
      max_matches_at_token_pos=700
      locate_dictionaries = dictionaries
      locate_args = [ELG_BINARY, 'Locate', f"-t{corpus_snt}", f"-a{ELG_RESOURCES}/Alphabet.txt"] + \
                    [f"-m{dict_name}" for dict_name in locate_dictionaries if dict_name.endswith('.bin')] + \
                    [f"{ELG_BUILD}/{task_name}.fst2", user_matching_mode, user_matching_overlap_policy, '-R', '--all',
                      '-b', '-Y', f"--max_errors={max_errors}", f"--max_matches_per_subgraph={max_matches_per_subgraph}",
                      f"--stack_max={stack_max}" , f"--max_matches_at_token_pos={max_matches_at_token_pos}",
                      f"--elg_extensions_path={ELG_EXTENSIONS}", '-qutf8-no-bom']
      log.trace("\",\n\"".join(locate_args) + "\"")
      subprocess.run(locate_args, check=True, stdout=stdout_descriptor, stderr=stderr_descriptor)
    except subprocess.CalledProcessError as e:
      log.error('Locate command failed.')
      # delete output file if exists
      if Path(output_file).exists() and Path(output_file).is_file():
          log.trace(f"Removing {output_file}")
          Path(output_file).unlink()
      return False

    # Concordance generation using ELG Engine
    try:
      subprocess.run([
          ELG_BINARY, 'Concord',
          f"{corpus_dsnt}/concord.ind",
          f"-m{output_file}",
          '-qutf8-no-bom'
      ], check=True, stdout=stdout_descriptor, stderr=stderr_descriptor)
    except subprocess.CalledProcessError as e:
      log.error('Concord command failed.')
      return False

    # Check if the file exists
    concord_n_file = Path(corpus_dsnt) / 'concord.n'
    if concord_n_file.exists():
      # Read the first line from the file
      with concord_n_file.open('r') as file:
          first_line = file.readline().strip()

      # Extract the number of matches before the first space
      number_of_matches = first_line.split(' ')[0]

      # Define the output file name
      output_file_n_matches_name = f"{os.path.splitext(output_file)[0]}.n"

      # Write the extracted part to the output file
      with open(output_file_n_matches_name, 'w') as output_file_n_matches:
          output_file_n_matches.write(number_of_matches)

    # Process QUOTE environment variable for text transformation
    quote = os.getenv('QUOTE', '1') == '1'
    if quote:
      sed_command = "sed -i 's|{S}||g ; s/\\r$// ; s|\"|\\\\\"|g ; s|^ \+||g ; s| \+$||g ; s|^|\"| ; s|$|\"|' " + output_file
    else:
      sed_command = "sed -i 's|{S}||g ; s/\\r$// ; s|^ \+||g ; s| \+$||g ;' " + output_file

    # Use shell=True to handle the pipe and redirection in the sed command
    try:
      subprocess.run(sed_command, shell=True, check=True, stdout=stdout_descriptor, stderr=stderr_descriptor)
    except subprocess.CalledProcessError as e:
      log.error('Process quotes failed.')
      return False

    log.trace(f"File directory: {dirname}")
    log.trace(f"Corpus directory: {corpus_dsnt}")
    if create_cache:
      log.trace(f"Cache directory: {corpus_dsnt}")
    log.trace(f"Result file: {output_file}")
    log.trace(f"Number of matches: {output_file_n_matches_name}")

    # Cleanup if not using cache
    if not create_cache and not use_cache and dirname != os.path.join(cache_dir, filename_without_ext):
      if Path(corpus_dsnt).exists() and Path(corpus_dsnt).is_dir():
        log.trace(f"Removing {corpus_dsnt}")
        srmdir(corpus_dsnt)
      if Path(corpus_snt).exists() and Path(corpus_snt).is_file():
        log.trace(f"Removing {corpus_snt}")
        Path(corpus_snt).unlink()

    return {
      'file': output_file,
      'input': input_file,
      # 'dir': dirname,
      'file_n_matches': output_file_n_matches_name,
      'n_matches': number_of_matches
    }

def edit_file_lines(output_name, func, input_name=None):
  """
  Edits lines in a file by applying a given function to each line.

  Args:
    output_name (str): The name of the output file.
    func (function): The function to apply to each line.
    input_file (str): Optional; the name of the input file to read from. If not provided, output_name will be used.
  """
  input_name = input_name if input_name else output_name

  with tempfile.NamedTemporaryFile(delete=False, mode='w') as temp_file:
    try:
      with open(input_name, 'r') as f:
        for line in f:
          temp_file.write(func(line))
      temp_file.close()
      shutil.move(temp_file.name, output_name)
    except OSError as e:
      log.error(f"Error while replacing file: {e}")
      raise
    except Exception as e:
      log.error(f"Unexpected error: {e}")
      raise
    finally:
      # Clean up temp file in case of an error
      if os.path.exists(temp_file.name):
        os.remove(temp_file.name)

def elg_matches_remove_duplicates(input_list):
    """
    Remove duplicates from a matching list while maintaining the order of the elements.

    Args:
        input_list (list): The list from which to remove duplicates. The list can contain any type of elements, including strings.

    Returns:
        list: A new list with duplicates removed, preserving the original order of elements.

    Example:
        >>> input_list = ['apple', 'banana', 'apple', 'orange', 'banana', 'grape']
        >>> remove_duplicates(input_list)
        ['apple', 'banana', 'orange', 'grape']
    """
    seen = set()
    result = []
    for item in input_list:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result

def elg_process_output(tagged, **params):
  """
  Process the output file based on the given filter_mode and other parameters.

  Args:
    tagged (dict): A dictionary containing the 'file' key with the name of the output file to process.
    params (dict): A dictionary containing processing parameters like 'filter_mode' and 'matches'.

  Returns:
    bool: True if processing is successful.
  """
  output_name = tagged['file']

  # compile regex patterns for moderate and strict modes
  moderate_mode_pattern = re.compile(r'^"?[^\]]*"?$')
  strict_mode_pattern = re.compile(r'^"?([^\[\n][^\[\n][^\n]*|[^\n]*[^\]\n][^\]\n])"?$')

  # apply the appropriate filter mode
  if params['filter_mode'] == 'moderate':
    def moderate_mode(line):
      return moderate_mode_pattern.sub('""\n', line)
    edit_file_lines(output_name, moderate_mode)

  elif params['filter_mode'] == 'strict':
    def strict_mode(line):
      return strict_mode_pattern.sub('""', line)
    edit_file_lines(output_name, strict_mode)

  def process_lines(line, line_number):
    nonlocal params
    line = line.rstrip('\n')
    quoted = line.startswith('"') and line.endswith('"')

    if quoted:
      line = line[1:-1]

    matches = []
    match = ""
    on_match = 0

    # iterate over each character in the line
    # and add matches to the list
    for i in range(len(line)):
      char_prev = line[i-1] if i > 0 else ''
      char_current = line[i]
      char_next = line[i+1] if i < len(line) - 1 else ''

      if on_match == 0 and char_prev == '[' and char_current == '[':
        on_match = 1
      elif on_match == 1 and char_current == ']' and char_next == ']':
        on_match = 0
        matches.append(match)
        match = ""
      elif on_match == 1:
        match += char_current

    # remove duplicated matches
    if len(matches) > 1:
      matches = elg_matches_remove_duplicates(matches)

    # count the total of matches for this line
    n_true_matches = len(matches)

    # handle ambiguous matches based on policy
    if (params['matches']['ambiguous_policy'] in ['warn', 'ignore'] and
        n_true_matches > 1):
      if params['matches']['ambiguous_policy'] == 'warn':
        log.warning("Ambiguous matches on data index %d: '%s'", line_number, line)
      elif params['matches']['ambiguous_policy'] == 'ignore':
        matches = []
        n_true_matches = 0
        log.warning("Ignoring ambiguous matches on data index %d: '%s'", line_number, line)

    # in relaxed mode, keep unmatched lines
    if params['filter_mode'] == 'relaxed' and not matches:
      matches.append(line)

    # join matches using the ambiguous delimiter
    line = params['matches']['ambiguous_delimiter'].join(matches)

    # remove multiple spaces and trim begin and end
    line = re.sub(' +', ' ', line).strip()

    # add quotes back if the line was originally quoted
    if quoted:
      line = f'"{line}"'

    return line + '\n', n_true_matches

  # track line number for logging purposes
  line_number = 1
  line_matches = 0
  def process_lines_with_tracking(line):
    nonlocal line_number, line_matches
    processed_line, line_true_matches = process_lines(line, line_number)
    line_number += 1
    if line_true_matches > 0:
      line_matches += 1
    return processed_line

  edit_file_lines(output_name, process_lines_with_tracking)

  tagged['line_count'] = line_number - 1
  tagged['line_matches'] = line_matches
  return tagged

def elg_log_output(log_file, log_level=logging.INFO):
  """
  Reads and logs the content of stdout_temp if it is not empty.

  Args:
      log_file (tempfile.NamedTemporaryFile): The temporary file containing the output.

  Returns:
      None
  """

  # read and log the content of stdout_temp if not empty
  with open(log_file.name, 'r') as f:
    log_content = f.read().strip()
    if log_content:
      log.log(log_level, f"{log_content}")

def elg_tagger(data_filename, data_line_count, registry_filename, temp_prefix, **params):
  # elg engine
  elg_binary = elg_get_binary()
  if not elg_binary:
    return False

  # setup optional params
  params = setup_params(registry_filename, **params)

  # prepare the default name of the dictionary cache
  dictionary_cache_name = os.path.splitext(os.path.basename(params['registry']))[0]
  dictionary_cache_name = re.sub(r'[^a-zA-Z0-9]+', '-', dictionary_cache_name).lower()

  # try to retrieve the results from the cache
  data_cache_name = params['node']
  data_cache_name = re.sub(r'[^a-zA-Z0-9]+', '-', data_cache_name).lower()
  data_cache_name = f"node--{data_cache_name}--{dictionary_cache_name}"
  data_hashname = md5sum(data_filename)
  registry_hashname = md5sum(registry_filename)
  data_result_filename = f"{md5sum_combine(data_hashname,registry_hashname)}.tag"
  data_cache_dir = create_cache_dir(data_cache_name, **params)

  # try to retrieve the results from the cache
  data_result = get_from_cache(data_cache_name, data_result_filename, 'use_cached_result', **params)

  # if the result was found return it
  if data_result:
    log.info("Using cached result of applying '{}' on '{}'".format(
      params['registry'], params['node']))
    # count the number of lines
    line_count = 0
    with open(data_result, 'rb') as f:
      line_count = sum(1 for _ in f)
    # return the information of the cached data
    return {
      'file': data_result,
      'line_count': line_count
    }

  dictionary_cached = f"{registry_hashname}.bin"
  dictionary_cached = get_from_cache(dictionary_cache_name, dictionary_cached, 'use_cached_registry', **params)

  # set default values for stdout and stderr
  stdout_temp = subprocess.DEVNULL
  stderr_temp = subprocess.DEVNULL
  stdout_file = None
  stderr_file = None

  # if verbose is 'info' or 'error', create a temporary file for stderr
  if params['verbose'] in ['info', 'error']:
    stderr_file = tempfile.NamedTemporaryFile(prefix="log-", delete=False)
    stderr_temp = stderr_file

  # if verbose is 'info', create a temporary file for stdout
  if params['verbose'] == 'info':
    stdout_file = tempfile.NamedTemporaryFile(prefix="log-", delete=False)
    stdout_temp = stdout_file


  dictionaries = []

  if dictionary_cached:
    log.info("Using cached compiled registry '{}'...".format(params['registry']))
    dictionaries.append(dictionary_cached)
  else:
    log.info("Compiling registry '{}'...".format(params['registry']))
    dictionary = elg_make_dictionary(elg_binary,
                                     registry_filename,
                                     registry_hashname,
                                     dictionary_cache_name,
                                     stdout_descriptor=stdout_temp,
                                     stderr_descriptor=stderr_temp,
                                     **params)
    if dictionary['valid']:
      dictionaries.append(dictionary['file'])
    else:
      log.error("Error compiling registry '{}'".format(
        params['registry']))
      return False

  # test if we have at least a single dictionary
  if not len(dictionaries):
    log.error("Unable to use compiled registry '{}'".format(
      params['registry']))
    return False

  # run the elg_dic_tagger with the specified parameters
  log.info("Using compiled registry for fast processing node '{}'".format(
            params['node']))
  tagged = elg_dic_tagger(
    elg_binary,
    data_filename,
    temp_prefix=temp_prefix,
    dictionaries=dictionaries,
    named_arguments_string=f"task_name=DicTaggerLemmas",
    stdout_descriptor=stdout_temp,
    stderr_descriptor=stderr_temp
  )

  processed = False

  if tagged:
    log.info("Processing {} string matches over {} data points".format(
             tagged.get('n_matches',0), data_line_count))
    processed = elg_process_output(tagged, **params)
    if processed:
      if data_line_count != processed['line_count']:
        # test if we still have the same number of lines
        log.error("Error applying ELG based on registry '{}', {} data points sent, {} data points retrieved".format(
          params['registry'], data_line_count, processed['line_count']
        ))
        processed = False
      else:
        log.info("Successfully updated {}/{} data points".format(
                 processed['line_matches'],tagged.get('line_count',0)))
        log.info("Finished successfully".format(
              params['node']))

  # if a temporary file for stdout was created, close it, log its output, and remove it
  if stdout_file:
    stdout_file.close()
    elg_log_output(stdout_file, logging.INFO)
    os.remove(stdout_file.name)

  # if a temporary file for stderr was created, close it, log its output, and remove it
  if stderr_file:
    stderr_file.close()
    elg_log_output(stderr_file, logging.ERROR)
    os.remove(stderr_file.name)

  # if requested, clear registry cache
  if not params['cache']['store_compiled_registry']:
    elg_clean_dictionary_cache(dictionary_cache_name, **params)

  # if requested, clear results cache
  if not params['cache']['store_result']:
    srmdir(data_cache_dir)
  else:
    # store results
    data_cache_result_filename = os.path.join(data_cache_dir, data_result_filename)
    shutil.move(processed['file'], data_cache_result_filename)
    processed['file'] = data_cache_result_filename

  return processed
