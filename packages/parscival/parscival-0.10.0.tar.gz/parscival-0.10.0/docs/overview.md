# Overview

## Data processing flow

The following diagram provides a high-level overview of the data processing flow using the Parscival framework. It illustrates how different data sources are ingested, processed, and transformed through various stages defined in the Parscival specification, ultimately resulting in multiple output formats.

```eval_rst
.. mermaid::
  :align: center

  %%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#4d4d4d', 'primaryTextColor': '#ffffff', 'secondaryColor': '#bfbfbf', 'secondaryTextColor': '#000000', 'tertiaryColor': '#e6e6e6', 'tertiaryTextColor': '#000000', 'lineColor': '#7f7f7f', 'edgeLabelBackground':'#c6c6c6', 'fontFamily': 'Liberation Mono', 'fontSize': '13px'}}}%%
  flowchart TD
      subgraph "Heterogeneous Sources"
          direction TB
          A1["Europresse (.html)"]
          A2["PubMed (.nbib)"]
          A3["More coming"]
      end

      subgraph "Parscival Specification"
          direction TB
          B1["<b>Ingesting</b>"]
          B2["<b>Parsing</b>"]
          B3["<b>Mapping</b>"]
          B5["<b>Storing</b>"]
          B0["(before_ingesting)"]
          B4["(before_storing)"]
          B6["(before_parsing)"]
          B7["(before_mapping)"]
          B8["(before_finishing)"]
      end

      subgraph "Multiple Outputs"
          direction TB
          C1["JSON"]
          C2["SQLite"]
          C3["Other Formats"]
      end

      A1 --> B0
      A2 --> B0
      A3 --> B0
      B0 --> B1
      B1 --> B6
      B6 --> B2
      B2 --> B7
      B7 --> B3
      B3 --> B4
      B4 --> B5
      B5 --> B8
      B8 --> C1
      B8 --> C2
      B8 --> C3
```

- **Heterogeneous Sources**:
  - The process begins with data coming from a single or multiples files of a determined source:
    - **``Europresse (.html)``**: HTML formatted documents from Europresse.
    - **``PubMed (.nbib)``**: NBIB formatted documents from PubMed.
    - **More coming**: Additional data sources will be added in the future.

- **Parscival Specification**:
  - The data from these sources undergoes several processing stages as defined by the Parscival specification:
    - **``Ingesting``**: Initial ingestion of raw data from the sources.
    - **``Parsing``**: Extraction of structured information from the ingested raw data.
    - **``Mapping``**: Transformation of parsed data into a consistent format.
    - **``Curating``**: Additional processing steps to refine and enhance the data.
    - **``Storing``**: Final preparation and storage of the processed data in specified formats.

- **Multiple Outputs**:
  - The processed data is then stored in multiple output formats, making it accessible for various use cases:
    - **``JSON``**: A common format for data interchange.
    - **``SQLite``**: A lightweight, disk-based database.
    - **Other Formats**: Other output formats may be specified.


## Parscival Specification

A Parscival specification is a detailed and structured YAML document that defines
how to ingest, parse, map, curate, and store data from determinated sources.
The specification is divided on multiple sections, each addressing a particular phase
of the data lifecycle.

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

By organizing the workflow into clearly defined sections, it allows to customize
and extend  data processing capabilities to meet diverse requirements. The modular
nature of Parscival, combined with its plugin architecture, ensures that it can
handle a wide variety of data sources and formats efficiently.

Below is a general overview of these sections.

```yaml
parscival_spec_version: '2.1.0'
description: ''
source: ''
schema: ''
format: ''
version: ''
author: ''

# general options
options:

# defines the data keys to be parsed and mapped
keys:
  # list of keys to be used during parsing
  parsing:

  # list of keys to be used during mapping
  mapping:

# parsing approach needed to extract the keys defined on 'keys.parsing'
parsing:

# specifies how to convert the parsed keys into output keys
mapping:
  # from a single key source to multiple key targets
  source_targets:

  # a single key target from a string template
  target_template:

# specifies curating tasks to be done before
# ingesting, parsing, mapping, storing or finishing processing
curating:
  # tasks to run before ingesting
  before_ingesting:

  # tasks to run before parsing
  before_parsing:

  # tasks to run before mapping
  before_mapping:

  # tasks to run before storing
  before_storing:

  # tasks to run before finishing
  before_finishing:

# specifies how to convert the mapped data into output files
storing:
```

1. **Metadata**: Provides general information about the specification, such as the
version, description, source, schema, format, and author. This section ensures that
the specification is well-documented and identifiable.

2. **Options**: Contains general settings that influence the overall processing
behavior. For example, options can specify whether to only process listed keys or
whether to remove temporary directories after processing.

3. **Keys**: Defines the data keys to be parsed and mapped. This section is subdivided into:

   - **Parsing Keys**: Lists the keys to be extracted from the source documents, along
     with their types and qualifiers (e.g., required or optional).

   - **Mapping Keys**: Specifies how the parsed keys should be transformed into
      output keys, including their types and any necessary qualifiers.

4. **Parsing**: Details the methods and rules for extracting data from source documents.
This section can use different available parsing plugins, such as Parsing Expression
Grammars (PEGs) or HTLMq query selectors, to accurately capture the desired data.

5. **Mapping**: Describes how the parsed data should be converted. This involves defining
source-target mappings, where parsed keys are transformed into mapped keys using various
transformation plugins (e.g., regex substitutions, date formatting).

6. **Curating**: Defines additional processing steps to be executed before or after various
stages of the data lifecycle, such as ingesting, parsing, mapping, or storing. Curating
tasks can include encoding conversions, data normalization, and deduplication.

7. **Storing**: Specifies how the processed data should be stored in the desired output
format. This section includes plugins to render data into specific formats, such as
JSON or SQLite, and outlines the templates or scripts required for the rendering process.

## Learn more

Whether you're installing and using Parscival for the first time or exploring its
advanced functionality through its various plugins, the resources below will guide
you through every step. Learn how to process different types of documents and
get inspired by real examples of Parscival specifications.

### General

- [How to install and use Parscival](readme)
- [How to process HTML documents with Parscival](guides/html)
- [How to process plain text key-value documents with Parscival](guides/key-value)

### Plugins

- [Parsing](plugins/parsing/index)
- [Mapping](plugins/mapping/index)
- [Curating](plugins/curating/index)
- [Storing](plugins/storing/index)

### Parscival specification examples

- [Europresse (.html)](sources/europresse-html)
- [Pubmed (.nbib)](sources/pubmed-nbib)

