# Storing

Storing plugins define how to convert the mapped data into output files.
They can transform data into various formats such as JSON, SQLite, etc., using
specified templates and scripts.

List of available plugins:

```eval_rst
.. contents::
   :depth: 1
   :local:
```

## `plain::render_template`

### Overview

The `plain::render_template` plugin is designed to transform mapped data into
various output formats using a specified template. This plugin uses templates
to render the data into formats like JSON, SQLite script, etc., based on the provided
template file.

### Configuration

The `plain::render_template` plugin can be configured with various parameters
to control its behavior. Below is a detailed explanation of each configuration
option.

#### Template

- **template**: The template file used for rendering the output.
  - **Type**: String
  - **Default**: None

#### Example

Below is an example configuration used to create a JSON file:

```yaml
# specifies how to convert the mapped data into output files
storing:
  # create a .json file
  cortext.json:
    plugins:
      # apply the 'render_template' plugin to transform the data using
      # the specified template
      - plain: 'render_template'
        params:
          # template file to be used for rendering the JSON output
          template: 'cortext.json.tpl'
```

### Usage

To use the `plain::render_template` plugin, include it in the `storing` section
of your Parscival specification file with the desired parameters. This will
ensure that data is rendered into the specified format using the provided template.

### Template Designer Documentation

Template engine allows for generating text-based formats (HTML, XML, CSV, LaTeX, etc.)
through templates that contain **variables**, **expressions**, and **tags**.

This synopsis provides a quick reference for the main aspects of Jinja2, the template
engine used by the plugin ``plain::render_template``, including syntax, template
inheritance, control structures, and more.

#### Template Syntax

- **Variables**: Inserted using `{{ variable }}`.
- **Expressions**: Evaluated and printed using `{{ expression }}`.
- **Tags**: Control logic using `{% tag %}`.

#### Default Delimiters

| Delimiter | Purpose              |
|-----------|----------------------|
| `{% %}`   | Statements           |
| `{{ }}`   | Expressions          |
| `{# #}`   | Comments             |

#### Key Components

##### Variables

Variables are defined by the context dictionary passed to the template and can
be accessed using dot notation (`foo.bar`) or subscript notation (`foo['bar']`).
If a variable does not exist, it returns an undefined value.

##### Filters

Filters modify variables and are applied using a pipe symbol (`|`). Filters can
be chained and accept arguments.

| Example                    | Description                        |
|----------------------------|------------------------------------|
| `{{ name|striptags|title }}` | Removes HTML tags and title-cases |

##### Tests

Tests check variables against common expressions using `is`. 

| Example                              | Description                      |
|--------------------------------------|----------------------------------|
| `{% if loop.index is divisibleby 3 %}` | Checks if index is divisible by 3 |

##### Comments

Comments are added using `{# comment #}` and are not included in the output.

##### Whitespace Control

- `trim_blocks`: Removes the first newline after a block.
- `lstrip_blocks`: Strips tabs and spaces from the beginning of a line to the start of a block.
- Use `-{` or `}-` to manually strip whitespace.

##### Escaping

To include raw Jinja syntax, use `{% raw %}{% endraw %}`. For literals, use `{{ '{{' }}`.

#### Template Inheritance

##### Base Template

Defines a common structure for child templates.

```html
<!DOCTYPE html>
<html lang="en">
<head>
    {% block head %}{% endblock %}
</head>
<body>
    {% block content %}{% endblock %}
</body>
</html>
```

##### Child Template

Extends the base template and fills in the blocks.

```html
{% extends "base.html" %}
{% block content %}
    <h1>Index</h1>
{% endblock %}
```

##### Blocks

Blocks can be nested and scoped to access variables within them.

##### Required Blocks

Marked as `required`, these must be overridden in child templates.

#### Control Structures

##### For Loop

Loops over sequences and provides special loop variables.

| Variable      | Description                                    |
|---------------|------------------------------------------------|
| `loop.index`  | Current iteration (1 indexed)                  |
| `loop.first`  | True if first iteration                        |
| `loop.length` | Number of items in the sequence                |

##### If Statement

Similar to Python's if statement, it checks conditions and supports `elif` and `else`.

#### Macros

Macros are reusable blocks of code similar to functions.

```html
{% macro input(name, value='', type='text') %}
    <input type="{{ type }}" name="{{ name }}" value="{{ value }}">
{% endmacro %}
```

#### Importing

Templates and macros can be imported from other files.

```html
{% import 'forms.html' as forms %}
{{ forms.input('username') }}
```

#### Expressions and Operators

Supports literals, math operations, comparisons, and logical operators similar to Python.

#### Extensions

Extensions provide additional functionalities like i18n, loop controls, and
autoescaping overrides.

#### Built-in Functions and Filters

Provides a comprehensive set of built-in filters, tests, and global functions.

##### Common Filters

| Filter       | Description                       |
|--------------|-----------------------------------|
| `escape`     | Escapes HTML characters           |
| `length`     | Returns the length of a sequence  |
| `default`    | Provides a default value          |

##### Common Tests

| Test         | Description                       |
|--------------|-----------------------------------|
| `defined`    | Checks if a variable is defined   |
| `even`       | Checks if a number is even        |
| `odd`        | Checks if a number is odd         |

#### Examples

##### ``cortext.json.tpl``

```
{# CorText Graph json template -#}
{{ parsing_data['mappings'] | tojson(indent=2) }}
```

##### ``cortext.sqlite.tpl``

```
{# CorText Graph DB template -#}
PRAGMA synchronous = OFF;
PRAGMA journal_mode = MEMORY;

-- CorText Graph tables
{% for table_name in parsing_data['mappings'] %}
DROP TABLE IF EXISTS [{{table_name}}];
CREATE TABLE [{{table_name}}] (
  file text,
  id integer,
  rank integer,
  parserank integer,
  {% if table_name == 'ISIpubdate' -%}
  data integer
  {% else -%}
  data text
  {% endif -%}
);
{% endfor %}

-- CorText Graph table values
BEGIN TRANSACTION;
{% for table_name in parsing_data['mappings'] -%}
{% for record in parsing_data['mappings'][table_name] -%}
{% if table_name == 'ISIpubdate' -%}
{% set data = record.data -%}
{% else -%}
{% set data = "'" ~ record.data | replace("'", "''") ~ "'" -%}
{% endif -%}
INSERT INTO [{{table_name}}] VALUES ('{{record.file}}', {{record.id}}, {{record.rank}}, {{record.parserank}}, {{data}});
{% endfor %}
{% endfor -%}
END TRANSACTION;
```

## `binary::execute_sqlite_script`

### Overview

The `binary::execute_sqlite_script` plugin is designed to execute SQLite
scripts to create and manipulate SQLite databases. This plugin takes a
rendered SQLite script and executes it to generate the SQLite database files.

### Configuration

The `binary::execute_sqlite_script` plugin does not require any specific
parameters. It simply executes the provided SQLite script.

### Example Configuration

Below is an example configuration for the `binary::execute_sqlite_script`
plugin, used to create an SQLite database:

```yaml
# specifies how to convert the mapped data into output files
storing:
  # create both .sqlite and .db files
  cortext.sqlite:
    plugins:
      # apply the 'render_template' plugin to transform the data using
      # the specified template
      - plain: 'render_template'
        params:
          # template file to be used for rendering the SQLite script
          template: 'cortext.sqlite.tpl'
      # apply the 'execute_sqlite_script' plugin to execute the rendered
      # SQLite script
      - binary: 'execute_sqlite_script'
```

### Usage

To use the `binary::execute_sqlite_script` plugin, include it in the `storing`
section of your Parscival specification file after the `plain::render_template`
plugin. This will ensure that the rendered SQLite script is executed to generate
the SQLite database.

### Fields

- **cortext.json**: Defines the output as a JSON file.
- **cortext.sqlite**: Defines the output as an SQLite database.

### Plugins

- **render_template**: Renders data using a template.
- **execute_sqlite_script**: Executes an SQLite script to create a SQLite database.
