# Plain text key-value document processing with Parscival

## Introduction

This document provides a guide to writing a specification for processing plain text
key-value documents using Parscival. The examples provided are based on the PubMed NBIB
specification, but the principles can be applied to any key-value based document.
Parscival uses a flexible YAML-based specification to define how to extract and
transform data from textual documents.

By following the structure and examples provided, you can adapt this specification
to parse and process data from any key-value based source, not just PubMed nbib.
The flexibility of the descriptive specification and the power of Parscival's
plugins make it a robust solution for document parsing and processing tasks.

## Specification Overview

```eval_rst
.. warning::

   This documentation refers to Parscival specification **version 2.1** and may be outdated. Please check the latest documentation to confirm current specifications.
```

The specification is divided into several sections:

```eval_rst
.. mermaid::
  :align: center

  %%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#4d4d4d', 'primaryTextColor': '#ffffff', 'secondaryColor': '#bfbfbf', 'secondaryTextColor': '#000000', 'tertiaryColor': '#e6e6e6', 'tertiaryTextColor': '#000000', 'lineColor': '#7f7f7f', 'edgeLabelBackground':'#c6c6c6', 'fontFamily': 'Liberation Mono', 'fontSize': '13px'}}}%%
  flowchart TD
      A[Parscival Specification] --> B[Metadata]
      A --> C[Options]
      A --> D[Keys]
      A --> E[Parsing]
      A --> F[Mapping]
      A --> G[Curating]
      A --> H[Storing]
```

- **Metadata**: General information about the specification.
- **Options**: General options.
- **Keys**: Defines the data keys to be parsed and mapped.
- **Parsing**: Defines how to extract data from the NBIB.
- **Mapping**: Defines how to transform parsed data into output data.
- **Curating**: Additional processing steps.
- **Storing**: Defines how to store the processed data.

## Metadata

The metadata section provides general information about the specification.

```eval_rst
.. mermaid::
  :align: center

  %%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#4d4d4d', 'primaryTextColor': '#ffffff', 'secondaryColor': '#bfbfbf', 'secondaryTextColor': '#000000', 'tertiaryColor': '#e6e6e6', 'tertiaryTextColor': '#000000', 'lineColor': '#7f7f7f', 'edgeLabelBackground':'#c6c6c6', 'fontFamily': 'Liberation Mono', 'fontSize': '13px'}}}%%
  classDiagram
    class Metadata {
      parscival_spec_version
      description
      source
      schema
      format
      version
      author
    }
```

```yaml
parscival_spec_version: '2.1.0'
description: 'PubMed nbib parscival specification'
source: 'pubmed'
schema: 'nbib'
format: 'key-value'
version: '1.1.0'
author: 'martinec'
```

### Fields
- **parscival_spec_version**: The version of the Parscival specification.
- **description**: A brief description of the specification.
- **source**: The source of the data.
- **schema**: The type of data structure being used.
- **format**: The format of the specification.
- **version**: The version of the specification.
- **author**: The author of the specification.

## Options

The options section defines settings that affect the parsing process.

```eval_rst
.. mermaid::
  :align: center

  %%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#4d4d4d', 'primaryTextColor': '#ffffff', 'secondaryColor': '#bfbfbf', 'secondaryTextColor': '#000000', 'tertiaryColor': '#e6e6e6', 'tertiaryTextColor': '#000000', 'lineColor': '#7f7f7f', 'edgeLabelBackground':'#c6c6c6', 'fontFamily': 'Liberation Mono', 'fontSize': '13px'}}}%%
  classDiagram
    class Options {
      only_requested_keys [true|false]
      remove_transient [true|false]
    }
```

```yaml
# general options
options:
  # only process keys listed under 'keys:'
  only_requested_keys: true
  # indicates whether the temporary directories should
  # be cleaned up after processing
  remove_transient: true
```

### Fields
- **only_requested_keys**: If true, only the keys listed under `keys.parsing`
  will be processed.
- **remove_transient**: Indicates whether the temporary directories should be
  cleaned up after processing.

## Keys

The keys section defines the data keys to be parsed and mapped. It is divided into
two subsections: `parsing` and `mapping`. 

```eval_rst
.. mermaid::
  :align: center

  %%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#4d4d4d', 'primaryTextColor': '#ffffff', 'secondaryColor': '#bfbfbf', 'secondaryTextColor': '#000000', 'tertiaryColor': '#e6e6e6', 'tertiaryTextColor': '#000000', 'lineColor': '#7f7f7f', 'edgeLabelBackground':'#c6c6c6', 'fontFamily': 'Liberation Mono', 'fontSize': '13px'}}}%%
  classDiagram
    class Keys {
      parsing
      mapping
    }
```

### Parsing Keys

The `parsing` subsection defines the keys to be extracted from the key-value document.
These keys MUST corresponds to real keys in the document.


```yaml
keys:
  # list of keys to be used during parsing
  # these keys must match the keys found in the input document
  parsing:
    AB: # Abstract
      type: string
      qualifier: optional
    AD: # Affiliation
      type: string
      qualifier: repeated
    AU: # Author
      type: string
      qualifier: repeated
    AID: # Article Identifier
      type: string
      qualifier: repeated
    CRDT: # Create Date
      type: string
      qualifier: optional
    DCOM: # Date Completed
      type: string
      qualifier: optional
    DP: # Date of Publication
      type: date
      qualifier: optional
    FAU: # Full Author
      type: string
      qualifier: repeated
    GR: # Grant Number
      type: string
      qualifier: optional
    IP: # Issue
      type: string
      qualifier: optional
    IS: # ISSN
      type: string
      qualifier: repeated
    JT: # Journal Title
      type: string
      qualifier: optional
    LA: # Language
      type: string
      qualifier: optional
    MH: # MeSH Terms
      type: string
      qualifier: repeated
    PG: # Pagination
      type: string
      qualifier: optional
    PMID: # PubMed Unique Identifier
      type: string
      qualifier: required
    PT: # Publication Type
      type: string
      qualifier: repeated
    RN: # Registry Number/EC Number
      type: string
      qualifier: repeated
    TA: # Journal Title Abbreviation
      type: string
      qualifier: optional
    TI: # Title
      type: string
      qualifier: required
    VI: # Volume
      type: string
      qualifier: optional
    OT: # Other Term
      type: string
      qualifier: optional
```

### Fields
- **type**: The data type of the key (e.g., string, integer).
- **qualifier**: Indicates whether the key is required, optional, or repeated.

### Mapping Keys

The `mapping` subsection defines the keys to be mapped from the parsed keys.

```yaml
# defines the data keys to be mapped
keys:
  # list of keys to be used during mapping
  mapping:
    Abstract:
      type: string
    Affiliation:
      type: string
    ArticleTitle:
      type: string
    Author:
      type: string
    Author_firstname:
      type: string
    Author_name:
      type: string
    Chemical:
      type: string
    DateCompleted:
      type: string
    DateCreated:
      type: string
    doi:
      type: string
    Grant:
      type: string
    ISIpubdate:
      type: integer
    ISOAbbreviation:
      type: string
    ISSN:
      type: string
    ISSNLinking:
      type: string
    Issue:
      type: string
    Journal:
      type: string
    Keywords:
      type: string
    Language:
      type: string
    MedlinePgn:
      type: string
    MeshHeading:
      type: string
    MeshHeading_Description:
      type: string
    NameOfSubstance:
      type: string
    PMID:
      type: string
    PubDate:
      type: string
    PublicationType:
      type: string
    Volume:
      type: string
```

## Parsing

The parsing section defines how to extract data from the key-value documents, in
this case using the Parsing Expression Grammars (PEGs) plugin.

```eval_rst
.. mermaid::
  :align: center

  %%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#4d4d4d', 'primaryTextColor': '#ffffff', 'secondaryColor': '#bfbfbf', 'secondaryTextColor': '#000000', 'tertiaryColor': '#e6e6e6', 'tertiaryTextColor': '#000000', 'lineColor': '#7f7f7f', 'edgeLabelBackground':'#c6c6c6', 'fontFamily': 'Liberation Mono', 'fontSize': '13px'}}}%%
  classDiagram
    class Parsing {
      parser_category
    }
```

```yaml
# parse a NBIB document by specifying the grammar needed to extract
# the keys defined on 'keys.parsing'
parsing:
  grammar:
    type: 'PEG'
    record_separator: 'PMID-'
    rules: |
      dataset   =  document+
      document  =  newline*
                   record_start
                   record_member+
                   record_end

      record_start  = key_start  key_sep value
      record_member = key_member key_sep value
      record_end    = key_end    key_sep value

      key_start   = 'PMID'
      key_member  = !key_start !key_end ~'[A-Z]+'
      key_end     = 'SO'

      key_sep     = whitespace? '-' whitespace?

      value       = value_data
                   (newline+ space value_data)*
                    newline+

      value_data  = ~'[^\r\n]+'

      space       = ~' +'
      whitespace  = ~'\s*'
      newline     = ~'\r\n' / ~'\n'
```

### Fields
- **type**: The type of parser plugin used (e.g., `PEG`).
- **record_separator**: The string that marks the beginning of each document.
- **rules**: The grammar rules used to parse the document.

## Mapping

The mapping section defines how the parsed keys are transformed into output keys.

```eval_rst
.. mermaid::
  :align: center

  %%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#4d4d4d', 'primaryTextColor': '#ffffff', 'secondaryColor': '#bfbfbf', 'secondaryTextColor': '#000000', 'tertiaryColor': '#e6e6e6', 'tertiaryTextColor': '#000000', 'lineColor': '#7f7f7f', 'edgeLabelBackground':'#c6c6c6', 'fontFamily': 'Liberation Mono', 'fontSize': '13px'}}}%%
  classDiagram
    class Mapping {
      source_targets
      target_template
    }
```

### Mapping Source-Targets

Allow mappings from a single key source to multiple key targets.

```yaml
# specifies how to convert the parsed keys into output keys
mapping:
  # a single key target from an an arbitrary string template
  source_targets:
    # AB |-> Abstract
    AB:
      - target: 'Abstract'
    # AD |-> Affiliation
    AD:
      - target: 'Affiliation'
        rank: 'Author_name'
        plugins:
          # remove email addresses from affiliations
          - transform: 'regex_sub'
            params:
              regex: "\\s(Electronic address:?)?\
                      \\s([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@\
                      [A-Za-z0-9-]+\
                      (\\.[A-Z|a-z-]{2,})+"
              repl: ''
          # split by ',' while increasing the parserank
          - transform: 'regex_parseranker'
            params:
              regex: '\s*,\s*'
          # trim trailing dots of each parsed rank
          - transform: 'regex_sub'
            params:
              regex: '\s*\.+\s*$'
              repl: ''
    # AU |-> Author
    AU:
      - target: 'Author'
    # AID |-> doi
    AID:
      - target: 'doi'
        plugins:
          # map only string values ending with '[doi]' and if a value
          # match, then keep the value without the '[doi]' tag
          - transform: 'regex_match_filter'
            params:
              regex: '^(.*)\s\[doi\]$'
              value: '{{_[0]}}'
    # CRDT |-> DateCreated
    CRDT:
      - target: 'DateCreated'
        plugins:
          # parse string as year with century as a decimal number (i.e YYYY)
          - transform: 'date_format'
            params:
              format: '%Y'
    # DCOM |-> DateCompleted
    DCOM:
      - target: 'DateCompleted'
        plugins:
          # parse string as year with century as a decimal number (i.e YYYY)
          - transform: 'date_format'
            params:
              format: '%Y'
    # DP |-> { PubDate }
    DP:
      - target: 'PubDate'
        plugins:
          # convert invalid date strings of type 'YYYY Mth-Mth' e.g '2016 Sep-Oct'
          # into 'YYYY Mth-Mth' e.g '2016 Sep'
          - transform: 'regex_format'
            params:
              regex: '\b([0-9]{4}\s[A-Z][a-z]{2})-[A-Z][a-z]{2}\b'
              value: '{{_[0]}}'
          # parse string as year with century as a decimal number (i.e YYYY)
          - transform: 'date_format'
            params:
              format: '%Y'
              # as fallback keep only the first 4 characters
              fallback: '{{ _[0][0:4] }}'
    # FAU |-> { Author_firstname, Author_name }
    FAU:
      - target: 'Author_firstname'
        plugins:
          # this assumes that everything before the ',' is equal to
          # the author's first name
          - transform: 'regex_format'
            params:
              regex: '^([^,]+),\s*(.*)$'
              value: '{{_[0]}}'
      - target: 'Author_name'
    # GR |-> Grant
    GR:
      - target: 'Grant'
    # IP |-> Issue
    IP:
      - target: 'Issue'
    # IS |-> { ISSN, ISSNLinking }
    IS:
      - target: 'ISSN'
      - target: 'ISSNLinking'
    # JT |-> Journal
    JT:
      - target: 'Journal'
    # LA |-> Language
    LA:
      - target: 'Language'
    # MH |-> { MeshHeading, MeshHeading_Description }
    MH:
      - target: 'MeshHeading'
        plugins:
          # put the most significant term, identified with an asterisk (*), at the
          # head of the list. Note that the resulting string is in lower case
          - transform: 'regex_format'
            params:
              enabled: false
              regex: '^([^\*]*?)(/)?(\*[^/]+)?([^\*]*)$'
              value: '{{_[2].lower()}}{{_[1]}}{{_[0].lower()}}{{_[3].lower()}}'
          # split by '/' while increasing the parserank
          - transform: 'regex_parseranker'
            params:
              regex: '/'
      - target: 'MeshHeading_Description'
        plugins:
          # put the most significant term, identified with an asterisk (*), at the
          # head of the list. Note that the resulting string is in lower case
          - transform: 'regex_format'
            params:
              enabled: false
              regex: '^([^\*]*?)(/)?(\*[^/]+)?([^\*]*)$'
              value: '{{_[2].lower()}}{{_[1]}}{{_[0].lower()}}{{_[3].lower()}}'
          # split by '/' while increasing the parserank
          - transform: 'regex_parseranker'
            params:
              regex: '/'
    # PG |-> MedlinePgn
    PG:
      - target: 'MedlinePgn'
    # PMID |-> PMID
    PMID:
      - target: 'PMID'
    # PT |-> PublicationType
    PT:
      - target: 'PublicationType'
    # RN |-> { Chemical, NameOfSubstance }
    RN:
      - target: 'Chemical'
        plugins:
        # map 'ID (Substance Name)' as 'ID', where ID is the unique
        # 10-digit Unique Ingredient Identifiers (UNIIs) or the 5- to
        # 9-digit number assigned by the Chemical Abstracts Service (CAS)
        # Note that according to the MEDLINE/PubMed documentation, a ID equal
        # to zero (0) is a valid value when an actual number cannot be located
        # or is not yet available
        - transform: 'regex_match_filter'
          params:
            regex: '^([^\(]+) \((.+)\)$'
            value: '{{_[0]}}'
      - target: 'NameOfSubstance'
        plugins:
        # map 'ID (Substance Name)' as 'Substance Name'
        - transform: 'regex_match_filter'
          params:
            regex: '^([^\(]+) \((.+)\)$'
            value: '{{_[1]}}'
    # TA |-> ISOAbbreviation
    TA:
      - target: 'ISOAbbreviation'
    # TI |-> ArticleTitle
    TI:
      - target: 'ArticleTitle'
    # VI |-> Volume
    VI:
      - target: 'Volume'
    # OT |-> Keywords
    OT:
      - target: 'Keywords'
  # a single key target from a string template
  target_template:
    # |-> ISIpubdate
    ISIpubdate:
      # template with a dynamic variable
      template: '{{PubDate}}'
```

### Fields
- **source_targets**: Maps parsed keys to output keys with optional plugins.
- **target_template**: Defines templates for output keys using mapped data.

### Plugins
- **regex_sub**: Performs a regex substitution.
- **regex_match_filter**: Filters data based on a regex match.
- **regex_format**: Formats data using a regex.
- **date_format**: Formats date strings.
- **data_ranker**: Ranks data items.

### Examples

- **Mapping AU (Author) to Author**:
  ```yaml
  AU:
    - target: 'Author'
      plugins:
        - transform: 'regex_sub'
          params:
            regex: "\\s+\\[?email protected\\]?"
            repl: ''
  ```

- **Mapping AB (Content) to Content**:
  ```yaml
  AB:
    - target: 'Content'
      plugins:
        - transform: 'regex_sub'
          params:
            regex: "\\s+"
            repl: ' '
  ```

## Curating

The curating section defines additional tasks before ingesting, parsing, mapping,
storing, or finishing the processing of inputs.

```eval_rst
.. mermaid::
  :align: center

  %%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#4d4d4d', 'primaryTextColor': '#ffffff', 'secondaryColor': '#bfbfbf', 'secondaryTextColor': '#000000', 'tertiaryColor': '#e6e6e6', 'tertiaryTextColor': '#000000', 'lineColor': '#7f7f7f', 'edgeLabelBackground':'#c6c6c6', 'fontFamily': 'Liberation Mono', 'fontSize': '13px'}}}%%
  classDiagram
    class Curating {
      before_ingesting
      before_parsing
      before_mapping
      before_storing
      before_finishing
    }
```

```yaml
# specifies curating tasks to be done after/before
# ingesting, parsing, mapping or storing
curating:
  # curation actions to be taken before ingesting data
  before_ingesting:
    plugins:
      # list of plugins to be executed before ingesting
      - encode: 'convert'
        # parameters for the encoding plugin
        params:
          # encoding settings
          encode:
            # source encoding. 'guess' will attempt to detect
            # the encoding
            from: 'guess'
            # target encoding to convert the files to
            to: 'utf-8'
          # policy to apply. 'only-non-complaint' means only files
          # that don't meet the expected encoding and newline
          # criteria will be processed
          policy: 'only-non-complaint'
          # newline character to use in the output files. 'LF'
          # stands for Line Feed (Unix-style newlines)
          # valid values are [LF|CR|CRLF]
          newline: 'LF'
          # temporary directory settings
          transient:
            # base directory for creating temporary directories
            basedir: '/tmp'
            # indicates whether the temporary directories should
            # be cleaned up after processing
            cleanable: true
          # enable or disable this plugin
          enabled: true

  before_storing:
    plugins:
      - deduplicate: 'hash_key_deduplicator'
        params:
          hash_key: '{{PMID}}'
```

### Fields

- **before_ingesting**: Defines steps to run before ingesting.
- **before_parsing**: Defines steps to run before parsing.
- **before_mapping**: Defines steps to run before mapping.
- **before_storing**: Defines steps to run before storing.
- **before_finishing**: Defines steps to run before finishing.

Following are `after_` aliases:

- **after_initializing**: **before_ingesting**
- **after_ingesting**: **before_parsing**
- **after_parsing**: **before_mapping**
- **after_mapping**: **before_storing**
- **after_storing**: **before_finishing**

### Plugins

See plugins section.

## Storing

The storing section defines how to output the processed data.

```eval_rst
.. mermaid::
  :align: center

  %%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#4d4d4d', 'primaryTextColor': '#ffffff', 'secondaryColor': '#bfbfbf', 'secondaryTextColor': '#000000', 'tertiaryColor': '#e6e6e6', 'tertiaryTextColor': '#000000', 'lineColor': '#7f7f7f', 'edgeLabelBackground':'#c6c6c6', 'fontFamily': 'Liberation Mono', 'fontSize': '13px'}}}%%
  classDiagram
    class Storing {
      file_extension
    }
```

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
          filename: 'cortext.json.tpl'

  # create both .sqlite and .db files
  cortext.sqlite:
    plugins:
      # apply the 'render_template' plugin to transform the data using
      # the specified template
      - plain: 'render_template'
        params:
          # template file to be used for rendering the SQLite script
          filename: 'cortext.sqlite.tpl'
      # apply the 'execute_sqlite_script' plugin to execute the rendered
      # SQLite script
      - binary: 'execute_sqlite_script'
```

### Fields
- **cortext.json**: Defines the output as a JSON file.
- **cortext.sqlite**: Defines the output as an SQLite database.

### Plugins
- **render_template**: Renders data using a template.
- **execute_sqlite_script**: Executes an SQLite script to create a sqlite database.
