# -*- coding: utf-8 -*-
# module worker.py
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
import logging                                    #
# ---------------------------------------------------------------------------
from cerberus import Validator, TypeDefinition

import semver
from pathlib import Path                          #
# ---------------------------------------------------------------------------
from parscival.utils.logging import logging_decorator, logging_set_context
_alias_ = 'validate.dogma'
_version_ = '1.0.0'
logging_default_context = f"|{_alias_}:{_version_}         |"
# ---------------------------------------------------------------------------
log = logging.getLogger(__name__)                 #
# ---------------------------------------------------------------------------
class DogmaValidator(Validator):
  def __init__(self, *args, **kwargs):
    kwargs.setdefault("require_all", False)
    super(DogmaValidator, self).__init__(*args, **kwargs)

  def _check_with_conditional_required_fields(self, field, value):
    """
    Validate 'qualifier: conditional' fields in a dict (like 'args' or 'time_granularity').
    Called at schema-level via 'check_with'.
    """
    if not isinstance(value, dict):
      # only validate nested dicts
      return

    schema = self.schema.get(field, {}).get("schema", {})
    if not schema:
      return

    for subfield, rules in schema.items():
      if rules.get("qualifier") != "conditional":
        continue

      required_if = rules.get("required_if")
      if not required_if:
        self._error(field, "'required_if' must be defined when 'qualifier' is 'conditional'")
        return

      condition_validator = self._get_child_validator(schema=required_if, allow_unknown=True)

      if condition_validator.validate(value):
        if subfield not in value:
          self._error(f"{field}.{subfield}", f"'{subfield}' is required when condition {required_if} is met")

  def _validate_one_of_members(self, constraint, field, value):
    """ Validate that at least one specified field is present.
    The rule's arguments are validated against this schema:
    {'type': 'list', 'schema': {'type': 'string'}}
    """
    if not isinstance(constraint, list):
      self._error(field, "The 'one_of_members' rule must be a list of fields")
      return

    present_fields = None

    if value:
      present_fields = [f for f in constraint if f in value]

    if not present_fields:
      self._error(field, f"At least one of the fields {constraint} must be present")

  def _validate_qualifier(self, qualifier_value, field, value):
    """
    Custom rule: qualifier

    Supports:
      - 'required': enforces that the field must be present in the document.
      - 'optional': handled via default behavior (field may be missing).
      - 'conditional': validated via 'check_with' at schema level.

    The rule's arguments are validated against this schema:
    {'type': 'string', 'allowed': ['required', 'optional', 'conditional']}
    """
    if qualifier_value != "required":
      return

    is_missing = (
      field not in self.document
      or (self.document.get(field) is None and self.ignore_none_values)
    )
    if is_missing:
      self._error(field, "Required field missing")

  def _validate_required_if(self, value, field, rule_value):
    """
    Dummy validator for 'required_if'.

    The rule's arguments are validated against this schema:
    {'type': 'dict'}
    """
    pass

  def _validate_type_semver(self, value):
    """ Validate that the value is a valid semantic version.
    The rule's arguments are validated against this schema:
    {'type': 'string'}
    """
    if not isinstance(value, str):
      self._error('type', 'Must be a string')
      return False

    try:
      semver.VersionInfo.parse(value)
      return True
    except ValueError:
      self._error('type', 'Must be a valid semantic version')
      return False

  def _validate_type_any(self, value):
    """ Validate that the value is a any
    {'type': 'string'}
    """

    if not isinstance(value, object):
      self._error('type', 'Must be any value')
      return False

    return True


def dogma_to_cerberus_schema(dogma_schema):
  """
  Translates a Dogma schema to a Cerberus schema.

  Args:
      dogma_schema (dict): The Dogma schema to translate.

  Returns:
      dict: The translated Cerberus schema.

  Raises:
      ValueError: If reserved words are used improperly or 'array' is not defined as a list.
  """
  # reserved keywords in Dogma
  dogma_reserved = set([
      'items', 'valuesrules', 'dict'
  ])

  # attributes recognized in Dogma schema
  dogma_attributes = set([
      'allof', 'allow_unknown', 'allowed', 'anyof', 'check_with', 'coerce',
      'contains', 'default', 'default_setter', 'dependencies', 'empty',
      'excludes', 'forbidden', 'keysrules', 'max', 'maxlength', 'meta',
      'min', 'minlength', 'noneof', 'nullable', 'oneof', 'purge_unknown',
      'readonly', 'regex', 'rename', 'rename_handler', 'require_all',
      'required', 'schema', 'type',
      'one_of_members', 'qualifier', 'required_if'
  ])

  def update_schema(node, parent_key=None):
    """
    Recursively prepares the schema:
    - Sets 'qualifier' to 'optional' if not present.
    - Translates qualifier to Cerberus-native 'required' where applicable.
    - Injects 'check_with: conditional_required_fields' into dicts containing conditional fields.
    """
    if isinstance(node, dict):
      new_node = {}
      for key, value in node.items():
        new_node[key] = update_schema(value, parent_key=key)

      #cCheck if current node is a dict-like structure with nested fields
      is_struct = node.get("type") in ("record", "dict", "map")
      has_members = "members" in node or "schema" in node

      # check for any 'qualifier: conditional' in child members/schema
      members = node.get("members") or node.get("schema")
      if is_struct and has_members and isinstance(members, dict):
        found_conditional = any(
          isinstance(field_def, dict) and field_def.get("qualifier") == "conditional"
          for field_def in members.values()
        )

        if found_conditional and "check_with" not in node:
          new_node["check_with"] = "conditional_required_fields"

      # apply qualifier rules
      is_valid_field = (
        'type' in node and
        parent_key not in (
          'schema', 'valuesrules', 'items', 'keysrules', 'definitions', 'members'
        ) and
        parent_key != 'qualifier'
      )

      if is_valid_field:
        qualifier = node.get('qualifier')

        if qualifier in (None, 'optional'):
          new_node['qualifier'] = 'optional'
          new_node['required'] = False
        elif qualifier == 'required':
          new_node['required'] = True

      return new_node

    elif isinstance(node, list):
      return [update_schema(item, parent_key=parent_key) for item in node]

    else:
      return node

  def translate_node(node):
    """
    Recursively translates the Dogma schema nodes to Cerberus schema nodes.
    """
    if isinstance(node, dict):
      translated = {}
      for key, value in node.items():
        if key == 'one_of_members':
          pass
        if key == 'type' and isinstance(value, str) and value in dogma_reserved:
          raise ValueError(f"'type: {value}' is unknown")
        elif key in dogma_reserved:
          raise ValueError(f"Key '{key}' is reserved word")
        elif key in dogma_attributes:
          translated[key] = value
        elif key == 'members':
          if translated.get('type') == 'record':
            translated['type'] = 'dict'
            translated['schema'] = translate_node(value)
          elif translated.get('type') == 'map':
            translated['type'] = 'dict'
            translated['valuesrules'] = translate_node(value)
          elif translated.get('type') == 'array':
            # ensure 'array' are defined as a list
            if not isinstance(value, list):
              raise ValueError(
                  f"Expected 'array' to be a list, got {type(value).__name__}")
            translated['type'] = 'list'
            translated['items'] = [translate_node(item) for item in value] if isinstance(
                value, list) else translate_node(value)
          elif translated.get('type') == 'collection':
            translated['type'] = 'list'
            translated['schema'] = translate_node(value)
        else:
          translated[key] = translate_node(value)

      # handle cases where `members` is missing
      if 'type' in translated:
        type_value = translated['type']
        if type_value == 'record':
          translated['type'] = 'dict'
          if 'schema' not in translated:
            translated['schema'] = {}
        elif type_value == 'map':
          translated['type'] = 'dict'
          if 'valuesrules' not in translated:
            translated['valuesrules'] = {}
        elif type_value == 'array':
          translated['type'] = 'list'
          if 'items' not in translated:
            translated['items'] = []
        elif type_value == 'collection':
          translated['type'] = 'list'
          if 'schema' not in translated:
            translated['schema'] = {}

      return translated

  # update the schema and then translate it
  updated_schema = update_schema(dogma_schema)
  cerberus_schema = translate_node(updated_schema)
  return cerberus_schema

@logging_decorator(logging_default_context)
def dogma_schema_normalize(document, schema):
  def strip_unused_conditionals(document, schema, validator_cls=DogmaValidator):
    """
    Recursively remove fields from `document` that are marked as
    'qualifier: conditional' but whose `required_if` condition is NOT met.

    Args:
      document (dict): The data to clean.
      schema (dict): The matching Cerberus (Dogma) schema.
      validator_cls: Validator class to use (default: DogmaValidator)

    Returns:
      dict: Cleaned document with unused conditionals removed.
    """
    if not isinstance(document, dict) or not isinstance(schema, dict):
      return document

    cleaned = {}
    schema_fields = schema.get("schema", schema)

    for key, value in document.items():
      field_schema = schema_fields.get(key, {})

      # recurse into nested dicts
      if field_schema.get("type") == "dict" and isinstance(value, dict):
        sub_cleaned = strip_unused_conditionals(value, field_schema, validator_cls=validator_cls)
        if sub_cleaned:
          # keep only if not empty
          cleaned[key] = sub_cleaned
        continue

      # check for conditional removal
      if field_schema.get("qualifier") == "conditional":
        required_if = field_schema.get("required_if")
        if required_if:
          validator = validator_cls(required_if, allow_unknown=True)
          if not validator.validate(document):
            log.warning(f"Skipping configuration '{key}':'{value}', condition NOT met: {required_if})")
            continue

      # keep this field
      cleaned[key] = value

    return cleaned


  # parse the dot notation schema
  try:
    schema = dogma_to_cerberus_schema(schema)
  except Exception as e:
    raise e

  # create a DogmaValidator with the parsed schema
  try:
    v = DogmaValidator(schema)
  except Exception as e:
    raise e

  # normalize the document (applies defaults, coercion, etc.)
  document_normalized =  v.normalized(document)

  # strip unused conditional fields (based on the final normalized values)
  document_normalized = strip_unused_conditionals(document_normalized, schema)

  return document_normalized

@logging_decorator(logging_default_context)
def dogma_schema_validate(document, schema):
  # parse the dot notation schema
  try:
    schema = dogma_to_cerberus_schema(schema)
  except Exception as e:
    raise e

  try:
    # create a DogmaValidator with the parsed schema
    v = DogmaValidator(schema)
  except Exception as e:
    raise e

  # validate the spec against the schema
  if not v.validate(document):
    log.error("Schema is invalid")
    log.error(v.errors)
    return False

  return True
