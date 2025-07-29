# Mapping

Mapping plugins are used for transforming, filtering and validating data during
the mapping process.

List of available plugins:

```eval_rst
.. contents::
   :depth: 1
   :local:
```

## ``transform::regex_sub``

### Overview

The `regex_sub` plugin performs a regular expression substitution on the input text.

### Usage

Use `regex_sub` when you need to clean or modify text by replacing specific
patterns with another string.

### Configuration

- **regex**: The regular expression pattern to search for.
- **repl**: The replacement string.

#### Example

```yaml
plugins:
  - transform: 'regex_sub'
    params:
      regex: "\\s+\\[?email protected\\]?"
      repl: ''
```

This example removes the string ``email protected`` from the text.

## ``transform::regex_match_filter``

### Overview

The `regex_match_filter` plugin filters text based on a regular expression match.

### Usage

Use `regex_match_filter` to selectively keep or modify parts of the text that
match a specific pattern.

### Configuration

- **regex**: The regular expression pattern to match.
- **value**: The value to use when the pattern matches.

#### Example

```yaml
plugins:
  - transform: 'regex_match_filter'
    params:
      regex: '^Note(\(s\)\s*:\s*)?(.*)$'
      value: '{{_[1]}}'
```

This example filters texts, keeping only those starting with the string 'Note'
and capturing the relevant part.

## ``transform::regex_format``

### Overview

The `regex_format` plugin formats text based on a regular expression pattern.

### Usage

Use `regex_format` to extract and format parts of the text based on a pattern.

### Configuration

- **regex**: The regular expression pattern to match.
- **value**: The formatted value to use when the pattern matches.
- **ignore_unmatch**: (Optional) Whether to ignore unmatched patterns. Default is `false`.
- **fallback**: (Optional) A fallback value to use if the pattern does not match.

#### Example

```yaml
plugins:
  - transform: 'regex_format'
    params:
      regex: '^([^,]+)\s*,?\s*(.*)$'
      value: '{{_[0]}}'
```

This example selects the journal name from a string of the form ``journal name,other data``
by capturing the part before the first comma.


## ``transform::date_format``

### Overview

The `date_format` plugin parses and formats dates.

### Usage

Use `date_format` to convert text to date formats or to extract date information.

### Configuration

- **format**: The date format string.
- **fallback**: (Optional) A fallback value to use if matching fails.

#### Example

```yaml
plugins:
  - transform: 'date_format'
    params:
      format: '%Y-%m-%d'
      fallback: '{{ _[0][0:4] }}'
```

This example parses dates in the format 'YYYY-MM-DD' and falls back to the
first four characters if matching fails.


## ``transform::regex_parseranker``

### Overview

The `regex_parseranker` plugin parses text and increases its rank based on
regular expression matches.

### Configuration

- **regex**: The regular expression pattern to parse.

### Usage

Use `regex_parseranker` to split text into components and rank them based on
specific patterns.

#### Example

```yaml
plugins:
  - transform: 'regex_parseranker'
    params:
      regex: '\s*,\s*'
```

This example splits text by commas and increases the rank of each parsed item.

## ``transform::data_ranker``

### Overview

The `data_ranker` plugin ranks data based on the number of items or subitems.

### Configuration

- **parserank**: (Optional) Whether to increase the rank based on subitems.
Default is `false`.

### Usage

Use `data_ranker` to prioritize or rank data items based on their quantity.

#### Example

```yaml
plugins:
  - transform: 'data_ranker'
    params:
      parserank: true
```

This example increases the rank based on the number of subitems of a key.
