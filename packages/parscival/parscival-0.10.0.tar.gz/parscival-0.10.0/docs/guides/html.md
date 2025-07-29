# HTML document processing with Parscival

## Introduction

This document provides a guide to writing a specification for processing HTML documents using Parscival. The examples provided are based on the Europresse HTML specification, but the principles can be applied to any HTML document. Parscival uses a flexible YAML-based specification to define how to extract and transform data from HTML documents.

By following the structure and examples provided, you can adapt this specification to parse and process data from any HTML source, not just Europresse. The flexibility of the descriptive specification and the power of Parscival's plugins make it a robust solution for HTML parsing and processing tasks.

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
- **Parsing**: Defines how to extract data from the HTML.
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
description: 'Europresse HTML parscival specification'
source: 'europresse'
schema: 'markup'
format: 'html'
version: '1.0.0'
author: 'martinec'
```

### Fields
- **parscival_spec_version**: The version of the Parscival specification.
- **description**: A brief description of the specification.
- **source**: The source of the data.
- **schema**: The type of data structure being used.
- **format**: The format of the specification (key-value pairs).
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
  # only keep parsed keys listed under 'keys:'
  only_requested_keys: true
  # indicates whether the temporary directories should
  # be cleaned up after processing
  remove_transient: true
```

### Fields
- **only_requested_keys**: If true, only the keys listed under `keys.parsing` will be processed.

- **remove_transient**: Indicates whether the temporary directories should
be cleaned up after processing.

## Keys

The keys section defines the data keys to be parsed and mapped. It is divided into two subsections: `parsing` and `mapping`. It is suggested the use of two-, three-, four-character uppercase variable names.

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

The `parsing` subsection defines the keys to be extracted from the HTML document.

```yaml
# defines the data keys to be parsed and mapped
keys:
  # list of keys to be used during parsing
  # it is suggested the use of two-, three-, four-character uppercase variable names
  parsing:
    AU:  # Author
      type: string
      qualifier: optional
    AN:  # Aside notes
      type: string
      qualifier: optional
    AB:  # Content
      type: string
      qualifier: required
    DS:  # Copyright info
      type: string
      qualifier: optional
    HD:  # Header
      type: string
      qualifier: optional
    IB:  # Info Box (encadré)
      type: string
      qualifier: optional
    PID: # Publication ID
      type: string
      qualifier: required
    SC:  # Publication source code
      type: string
      qualifier: optional
    SD:  # Other source date
      type: string
      qualifier: optional
    SN:  # Other source name
      type: string
      qualifier: optional
    SO:  # Journal Title
      type: string
      qualifier: required
    ST:  # Subtitle
      type: string
      qualifier: optional
    TI:  # Title
      type: string
      qualifier: required
```

### Fields
- **type**: The data type of the key (e.g., string, integer).
- **qualifier**: Indicates whether the key is required or optional.

### Mapping Keys

The `mapping` subsection defines the keys to be mapped from the parsed keys.

```yaml
# defines the data keys to be mapped
keys:
  # list of keys to be used during mapping
  mapping:
    # Unique identifier for the article
    ArticleID:
      type: string
    # Name(s) of the author(s) of the article
    Author:
      type: string
    # Main content/body of the article
    Content:
      type: string
    # Header information of the article
    Header:
      type: string
    # Unique identifier used within the system
    ID:
      type: string
    # Additional information or summary box
    InfoBox:
      type: string
    # Publication date in ISI format
    ISIpubdate:
      type: integer
    # Name of the journal or publication
    Journal:
      type: string
    # Legal or copyright information
    LegalInfo:
      type: string
    # Additional notes or comments
    Notes:
      type: string
    # Release date of the other source
    OtherSourceDate:
      type: string
    # Name of the other source
    OtherSourceName:
      type: string
    # Classification of the publication: 'news', 'report', 'web',...
    PubClass:
      type: string
    # Publication date
    PubDate:
      type: string
    # Type of the publication, fixed to 'J'
    PubType:
      type: string
    # Source of the publication, fixed to 'Europresse'
    PubSource:
      type: string
    # Year of publication
    PubYear:
      type: string
    # Identifier of the source
    SourceID:
      type: string
    # Code representing the source
    SourceCode:
      type: string
    # Subtitle of the article
    Subtitle:
      type: string
    # Title of the article
    Title:
      type: string
    # Volume number of the journal or publication
    Volume:
      type: string
```

## Parsing

The parsing section defines how to extract data from the HTML document using query selectors.

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
# parse a HTML document by specifying the query selectors needed to extract
# the keys defined on 'keys.parsing'
parsing:
  # name of the parsing category
  lquery:
    # name of the parsing plugin
    type: 'htmlq'
    # the beginning of each document
    record_separator: '<article>'
    # the end of each document
    record_finalizer: '</article>'
    keys:
      AU:  # Author
        selectors:
          # Example:
          # <div class="docAuthors">John Doe</div>
          # try to use .docAuthors to find the author
          - query: 'div.docAuthors'
            type: 'text'
          # alternatively, use the last .sm-margin-bottomNews element
          - query: '.sm-margin-bottomNews'
            chain:
              # select only the last item
              - method: 'eq'
                params: -1
            type: 'text'
      AN:  # Aside Notes
        selectors:
          # Example:
          # <aside>
          #   <div>Note(s): This is an important aside note.</div>
          # </aside>
          - query: 'aside'
            chain:
              # select those contains the string 'Note'
              - method: 'filter'
                params: ':contains("Note")'
              # keep only the first element
              - method: 'eq'
                params: 0
            type: 'text'
      AB:  # Content
        selectors:
          # Example:
          # <div class="DocText">
          #   <p>At the beginning of the COVID-19 ...</p>
          # </div>
          # try to use .DocText
          - query: 'div.DocText'
            type: 'text'
          # alternatively, .docOcurrContainer
          - query: 'div.docOcurrContainer'
            type: 'text'
      DS:  # Copyright info
        selectors:
          # Example:
          # <div class="Doc-LegalInfo">
          #   <small>© 2022 Acme University. All rights reserved.</small>
          # </div>
          - query: 'div.Doc-LegalInfo small'
            chain:
              # select only the first element
              - method: 'eq'
                params: 0
            type: 'text'
      HD:  # Header
        selectors:
          # Example:
          # <div class="rdp__DocHeader">
          #   <span class="DocHeader">Thursday, December 22, 2022 13887 mots, p. 819(40)</span>
          # </div>
          - query: '.DocHeader'
            type: 'text'
      IB:  # Info Box
        selectors:
          # Example:
          # <div class="rdp__newsdoc">
          #   Information box content here
          # </div>
          - query: 'div.rdp__newsdoc'
            type: 'text'
      PID: # Publication ID
        selectors:
          # Example:
          # <div class="publiC-lblNodoc">news·20221222·XXXXX·000000000</div>
          - query: '.publiC-lblNodoc'
            type: 'text'
      SC:  # Code of the source
        selectors:
          # Example:
          # <span sourcecode="XXXXX"></span>
          - query: 'span[sourcecode]'
            # we specify that we need the attribute 'sourcecode' instant of
            # the content of the element 'span'
            type: 'attr'
            attribute: 'sourcecode'
      SD:  # Other source date
        selectors:
          # Example:
          # <div class="apd-sources-date">2022-12-22</div>
          - query: '.apd-sources-date'
            # for a single document, having multiple results for this selector
            # each item retrieved is preserved in a list
            type: 'list_text'
      SN:  # Other source name
        selectors:
          # Example:
          # <div class="apd-sources-date">2022-12-22</div>
          # <td>
          #   <div class="source-name-APD">Source Name 1</div>
          #   <div class="source-name-APD">Source Name 2</div>
          # </td>
          # <div class="apd-sources-date">2022-12-23</div>
          # <td>
          #   <div class="source-name-APD">Source Name 3</div>
          # </td>
          - query: '.apd-sources-date'
            # for a single document, having multiple results for this selector
            # each item retrieved is preserved in a list
            type: 'list_text'
            # for each item retrieved, the following chain of actions is performed
            item_chain:
              # select the closest parent 'td' element
              - method: 'closest'
                params: 'td'
              # move to the next sibling 'td' element
              - method: 'next_all'
                params: 'td'
              # find all elements with the class '.source-name-APD' within the
              # current context
              - method: 'find'
                params: '.source-name-APD'
      SO:  # Publication Name
        selectors:
          # Example:
          # <div class="rdp__DocPublicationName">
          #   <span class="DocPublicationName">Acme Law Review, Vol. 14, no 4</span>
          # </div>
          - query: '.DocPublicationName'
            type: 'text'
      ST:  # Subtitle
        selectors:
          # Example:
          # <div class="rdp__subtitle">Subtitle goes here</div>
          - query: '.rdp__subtitle'
            type: 'text'
      TI:  # Title, use the first non empty text found
        selectors:
          # Example:
          # <div class="titreArticle">
          #   <p class="titreArticleVisu">Title goes here</p>
          # </div>
          # try to use .titreArticle
          - query: '.titreArticle'
            type: 'text'
          # alternatively, .grandTitre
          - query: '.grandTitre'
            type: 'text'
          # as last-chance, .titreArticleVisu
          - query: '.titreArticleVisu'
            type: 'text'
```

### Fields
- **type**: The type of parser plugin used (e.g., `htmlq`).
- **record_separator**: The HTML tag that marks the beginning of each document.
- **record_finalizer**: The HTML tag that marks the end of each document.
- **keys**: The keys to be parsed, each with a list of selectors and optional chain methods.

### Selectors
- **selectors**: Defines the query selectors to extract data.
- **query**: The CSS selector used to find elements.
- **type**: The type of data to extract: `text`, `attr`, `list_text`, `list_attr`.
- **attribute**: The attribute to extract if `type` is `attr` or `list_attr`.
- **chain**: A sequence of methods to further refine the selection.
  - **method**: The method to apply (e.g., `eq`, `filter`, `closest`, `next_all`, `find`).
  - **params**: Parameters for the method.

### Chain Methods

The `chain` section within a selector defines a sequence of methods to further refine the selection process in the HTML document. These methods are applied in order and allow for precise targeting of elements. Below are the available methods, along with meaningful examples.

#### Available Methods

1. **closest**
1. **eq**
1. **filter**
1. **find**
1. **next_all**
1. **next_until**
1. **not_**
1. **parents**
1. **children**
1. **is_**
1. **prev_all**
1. **siblings**

#### Method Descriptions and Examples

1. **closest**

   The `closest` method finds the closest ancestor element that matches the specified selector.

   ```yaml
   - query: '.child-element'
     chain:
       - method: 'closest'
         params: '.parent-element'
   ```

   **Example:**
   ```html
   <div class="parent-element">
     <div class="intermediate-element">
       <div class="child-element">Content</div>
     </div>
   </div>
   ```

   This chain will select the `.parent-element` for each `.child-element`.

1. **eq**

   The `eq` method selects the element at the specified index. Negative index are related to the inverse order.

   ```yaml
   - query: '.list-item'
     chain:
       - method: 'eq'
         params: 1
   ```

   **Example:**
   ```html
   <ul>
     <li class="list-item">Item 1</li>
     <li class="list-item">Item 2</li>
     <li class="list-item">Item 3</li>
   </ul>
   ```

   This chain will select the second `.list-item` (index 1).

1. **filter**

   The `filter` method reduces the set of matched elements to those that match the specified selector.

   ```yaml
   - query: '.list-item'
     chain:
       - method: 'filter'
         params: ':contains("Item 2")'
   ```

   **Example:**
   ```html
   <ul>
     <li class="list-item">Item 1</li>
     <li class="list-item">Item 2</li>
     <li class="list-item">Item 3</li>
   </ul>
   ```

   This chain will select the `.list-item` containing the text "Item 2".

1. **find**

   The `find` method searches for descendants of each matched element that match the specified selector.

   ```yaml
   - query: '.parent-element'
     chain:
       - method: 'find'
         params: '.child-element'
   ```

   **Example:**
   ```html
   <div class="parent-element">
     <div class="child-element">Content</div>
   </div>
   ```

   This chain will select the `.child-element` within each `.parent-element`.

1. **next_all**

   The `next_all` method gets all following siblings of each element, optionally filtered by a selector.

   ```yaml
   - query: '.list-item'
     chain:
       - method: 'next_all'
         params: '.other-items'
   ```

   **Example:**
   ```html
   <ul>
     <li class="list-item">Item 1</li>
     <li class="other-items">Item 2</li>
     <li class="other-items">Item 3</li>
   </ul>
   ```

   This chain will select all `.other-items` that follow each `.list-item`.

1. **next_until**

   The `next_until` method gets all following siblings up to but not including the element matched by the selector.

   ```yaml
   - query: '.start'
     chain:
       - method: 'next_until'
         params: '.end'
   ```

   **Example:**
   ```html
   <div class="start">Start</div>
   <div class="middle">Middle 1</div>
   <div class="middle">Middle 2</div>
   <div class="end">End</div>
   ```

   This chain will select all elements with the class `middle` between `start` and `end`.

1. **not_**

   The `not_` method removes elements from the set of matched elements that match the specified selector.

   ```yaml
   - query: '.list-item'
     chain:
       - method: 'not_'
         params: ':contains("Item 2")'
   ```

   **Example:**
   ```html
   <ul>
     <li class="list-item">Item 1</li>
     <li class="list-item">Item 2</li>
     <li class="list-item">Item 3</li>
   </ul>
   ```

   This chain will select all `.list-item` elements except the one containing "Item 2".

1. **parents**

   The `parents` method gets the ancestors of each element in the current set of matched elements, optionally filtered by a selector.

   ```yaml
   - query: '.child-element'
     chain:
       - method: 'parents'
         params: '.parent-element'
   ```

   **Example:**
   ```html
   <div class="grandparent-element">
     <div class="parent-element">
       <div class="child-element">Content</div>
     </div>
   </div>
   ```

   This chain will select the `.parent-element` for each `.child-element`.

1. **children**

    The `children` method filters elements that are direct children of the matched element, optionally filtered by a selector.

    ```yaml
    - query: '.parent-element'
      chain:
        - method: 'children'
          params: '.child-element'
    ```

    **Example:**
    ```html
    <div class="parent-element">
      <div class="child-element">Child 1</div>
      <div class="child-element">Child 2</div>
    </div>
    ```

    This chain will select all direct children of the `.parent-element` that have the class `.child-element`.

1. **is_**

    The `is_` method checks if any elements in the set match the selector.

    ```yaml
    - query: '.list-item'
      chain:
        - method: 'is_'
          params: '.highlight'
    ```

    **Example:**
    ```html
    <ul>
      <li class="list-item">Item 1</li>
      <li class="list-item highlight">Item 2</li>
      <li class="list-item">Item 3</li>
    </ul>
    ```

    This chain will return `true` if any `.list-item` has the class `.highlight`.

1. **prev_all**

    The `prev_all` method gets all preceding siblings of each element, optionally filtered by a selector.

    ```yaml
    - query: '.list-item'
      chain:
        - method: 'prev_all'
          params: '.previous-items'
    ```

    **Example:**
    ```html
    <ul>
      <li class="previous-items">Item 0</li>
      <li class="list-item">Item 1</li>
      <li class="list-item">Item 2</li>
      <li class="list-item">Item 3</li>
    </ul>
    ```

    This chain will select all `.previous-items` that precede each `.list-item`.

1. **siblings**

    The `siblings` method gets all sibling elements of each element in the set of matched elements, optionally filtered by a selector.

    ```yaml
    - query: '.selected-item'
      chain:
        - method: 'siblings'
          params: '.sibling-items'
    ```

    **Example:**
    ```html
    <ul>
      <li class="sibling-items">Item 1</li>
      <li class="selected-item">Item 2</li>
      <li class="sibling-items">Item 3</li>
    </ul>
    ```

    This chain will select all `.sibling-items` that are siblings of each `.selected-item`.

### Examples

- **AU (Author)**:
  ```yaml
  AU:  # Author
    selectors:
      # Example:
      # <div class="docAuthors">John Doe</div>
      - query: 'div.docAuthors'
        type: 'text'
      # alternatively, use the last .sm-margin-bottomNews element
      - query: '.sm-margin-bottomNews'
        chain:
          # select only the last item
          - method: 'eq'
            params: -1
        type: 'text'
  ```

- **AN (Aside Notes)**:
  ```yaml
  AN:  # Aside Notes
    selectors:
      # Example:
      # <aside>
      #   <div>Note: This is an important aside note.</div>
      # </aside>
      - query: 'aside'
        chain:
          # select those contains the string 'Note'
          - method: 'filter'
            params: ':contains("Note")'
          # keep only the first element
          - method: 'eq'
            params: 0
        type: 'text'
  ```

- **AB (Content)**:
  ```yaml
  AB:  # Content
    selectors:
      # Example:
      # <div class="DocText">
      #   <p>At the beginning of the COVID-19 ...</p>
      # </div>
      # try to use .DocText
      - query: 'div.DocText'
        type: 'text'
      # alternatively, .docOcurrContainer
      - query: 'div.docOcurrContainer'
        type: 'text'
  ```

- **SN (Other source name)**:
  ```yaml
  SN:  # Other source name
    selectors:
      # Example:
      # <div class="apd-sources-date">2022-12-22</div>
      # <td>
      #   <div class="source-name-APD">Source Name 1</div>
      #   <div class="source-name-APD">Source Name 2</div>
      # </td>
      # <div class="apd-sources-date">2022-12-23</div>
      # <td>
      #   <div class="source-name-APD">Source Name 3</div>
      # </td>
      - query: '.apd-sources-date'
        # for a single document, having multiple results for this selector
        # each item retrieved is preserved in a list
        type: 'list_text'
        # for each item retrieved, the following chain of actions is performed
        item_chain:
          # select the closest parent 'td' element
          - method: 'closest'
            params: 'td'
          # move to the next sibling 'td' element
          - method: 'next_all'
            params: 'td'
          # find all elements with the class '.source-name-APD' within the
          # current context
          - method: 'find'
            params: '.source-name-APD'
  ```

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
  # from a single key source to multiple key targets
  source_targets:
    # AU |-> Author
    AU:
      - target: 'Author'
        plugins:
          # remove "email protected" from Author text
          - transform: 'regex_sub'
            params:
              regex: "\\s+\\[?email protected\\]?"
              repl: ''
    # AN |-> Notes
    AN:
      - target: 'Notes'
        plugins:
          # replace 1 or more new lines by a space
          - transform: 'regex_sub'
            params:
              regex: "\\s+"
              repl: ' '
          # from Aside Notes, keep only them starting by the string 'Note(s)'
          - transform: 'regex_match_filter'
            params:
              regex: '^Note(\(s\)\s*:\s*)?(.*)$'
              value: '{{_[1]}}'
    # AB |-> Content
    AB:
      - target: 'Content'
        plugins:
          # replace 1 or more new lines by a space
          - transform: 'regex_sub'
            params:
              regex: "\\s+"
              repl: ' '
    # DS |-> LegalInfo
    DS:
      - target: 'LegalInfo'
    # IB |-> InfoBox
    IB:
      - target: 'InfoBox'
        plugins:
          # replace 1 or more new lines by a space
          - transform: 'regex_sub'
            params:
              regex: "\\s+"
              repl: ' '
    # HD |-> Header
    HD:
      - target: 'Header'
    # SO |-> Journal
    SO:
      - target: 'Journal'
        plugins:
          # select Journal name
          - transform: 'regex_format'
            params:
              regex: '^([^,]+)\s*,?\s*(.*)$'
              value: '{{_[0]}}'
      - target: 'Volume'
        plugins:
          # select Volume
          - transform: 'regex_format'
            params:
              regex: '^([^,]+)\s*,\s*(.*[Vv]ol.*)$'
              value: '{{_[1]}}'
              ignore_unmatch: true
              fallback: ''
    # PID |-> ID, PubClass, PubDate, SourceID, ArticleID
    PID:
      - target: 'ID'
      - target: 'PubClass'
        plugins:
          # convert PID in the form 'foo\u00b720231019\u00b7bar\u00b7zaz'
          # into 'fo'
          - transform: 'regex_format'
            params:
              regex: '\b([^·]+)·([^·]+)·([^·]+)·([^·]+)\b'
              value: '{{_[0]}}'
      - target: 'PubDate'
        plugins:
          # convert PID in the form 'foo\u00b720231019\u00b7bar\u00b7zaz'
          # into 'YYYY/MM/dd'
          - transform: 'regex_format'
            params:
              regex: '\b([^·]+)·([^·]+)·([^·]+)·([^·]+)\b'
              value: '{{_[1]}}'
          # parse string as year-month-day (e.g. 2023-10-19)
          - transform: 'date_format'
            params:
              format: '%Y-%m-%d'
              # as fallback keep only the first 4 characters
              fallback: '{{ _[0][0:4] }}'
      - target: 'SourceID'
        plugins:
          # convert PID in the form 'foo\u00b720231019\u00b7bar\u00b7zaz'
          # into 'bar'
          - transform: 'regex_format'
            params:
              regex: '\b([^·]+)·([^·]+)·([^·]+)·([^·]+)\b'
              value: '{{_[2]}}'
      - target: 'ArticleID'
        plugins:
          # convert PID in the form 'foo\u00b720231019\u00b7bar\u00b7zaz'
          # into 'bar:zaz'
          - transform: 'regex_format'
            params:
              regex: '\b([^·]+)·([^·]+)·([^·]+)·([^·]+)\b'
              value: '{{_[2]}}:{{_[3]}}'
    # SC |-> SourceCode
    SC:
      - target: 'SourceCode'
    # SD |-> OtherSourceDate
    SD:
      - target: 'OtherSourceDate'
        plugins:
          # each item on the parsed SD increases the rank
          - transform: 'data_ranker'
    # SN |-> OtherSourceName
    SN:
      - target: 'OtherSourceName'
        plugins:
          # each item on the parsed SN increases the rank
          - transform: 'data_ranker'
            params:
              # each subitem on the parsed SN increases the parserank
              parserank: true
    # ST |-> SubTitle
    ST:
      - target: 'Subtitle'
    # TI |-> Title
    TI:
      - target: 'Title'
```

### Mapping Target Template

Allow mappings of single key target from an arbitrary string template

```yaml
# specifies how to convert the parsed keys into output keys
mapping:
  # a single key target from a string template
  target_template:
    # PubDateSource:
    #   template: '{{OtherSourceDate}}: {{OtherSourceName}}'
    # |-> ISIpubdate
    ISIpubdate:
      # template with a dynamic variable
      template: '{{PubDate}}'
    # |-> PubType
    PubType:
      # template with a literal value for all nodes
      template: 'J'
    # |-> PubSource
    PubSource:
      # template with a literal value for all nodes
      template: 'Europresse'
    # |-> PubYear
    PubYear:
      # template with a dynamic variable, followed by a
      # mapping plugin able to parse and format dates
      template: '{{PubDate}}'
      plugins:
        # parse string as year (e.g. 2023)
        - transform: 'date_format'
          params:
            format: '%Y'
            # as fallback keep only the first 4 characters
            fallback: '{{ _[0][0:4] }}'
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

The curating section defines additional tasks before ingesting,
parsing, mapping, storing or finishing the processing of inputs.

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
# ingesting, parsing, mapping, storing or finishing
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

  # curation actions to be taken after mapping data
  after_mapping:
    plugins:
      - match: 'elg_node_matcher'
        params:
          # name of the node to process
          node: 'OtherSourceName'
          # path to the registry file
          registry: 'europresse-journal-name.csv'
          # strict: clear non fully matched nodes
          # moderate: keep partially matched nodes
          # relaxed: keep non matched nodes
          filter_mode: 'relaxed'
          # normalize functions to be applied on each node item before matching
          normalize:
            # lowercase item data
            - lowercase: true
            # collapse multiple spaces
            - collapse: true
            # remove leading and trailing whitespace
            - trim: true
          # cache options
          cache:
            # directory for cache storage
            dir: './cache'
            # store the compiled registry in the cache
            store_compiled_registry: true
            # store the match results in the cache
            store_result: false
            # use the cached compiled registry
            use_cached_registry: true
            # use the cached match results
            use_cached_result: false
          # match options
          matches:
            # policy for handling ambiguous matches
            # options: keep, warn, ignore
            ambiguous_policy: 'warn'
            # delimiter for separating ambiguous matches
            ambiguous_delimiter: ' *** '
          # verbosity level
          # options: info, error, none
          verbose: 'error'
          # enable or disable the plugin
          enabled: true

  # curation actions to be taken before storing mapped data
  before_storing:
    plugins:
      - deduplicate: 'hash_key_deduplicator'
        params:
          hash_key: '{{ID}}'
```

### Fields
- **before_ingesting**: Defines steps to run before ingesting.
- **before_parsing**: Defines steps to run before parsing.
- **before_mapping**: Defines steps to run before mapping.
- **before_storing**: Defines steps to run before storing.
- **before_finishing**: Defines steps to run before finishing.

Following are ``after_`` aliases:

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
          template: 'cortext.json.tpl'

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

### Fields
- **cortext.json**: Defines the output as a JSON file.
- **cortext.sqlite**: Defines the output as an SQLite database.

### Plugins
- **render_template**: Renders data using a template.
- **execute_sqlite_script**: Executes an SQLite script to create a sqlite database.
