# Parsing

Parsing plugins defines how to extract specific data from documents.

List of available plugins:

```eval_rst
.. contents::
   :depth: 1
   :local:
```
  
## ``lquery::htmlq``

### Overview

The `lquery::htmlq` plugin is designed to parse HTML documents by specifying
query selectors needed to extract data for the keys defined in the `keys.parsing`
configuration. This plugin allows for precise extraction of data from HTML
elements using CSS selectors and optional chain methods to refine the selection.

### Configuration

The `lquery::htmlq` plugin can be configured with various parameters to control
its behavior.

### Example Configuration

Below is an example configuration for the `lquery::htmlq` plugin:

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

#### Parsing Category

- **lquery**: The name of the parsing category.
  
#### Parser Type

- **type**: Specifies the parser plugin used.
  - **Type**: String
  - **Valid Values**: `htmlq`
  - **Default**: None

#### Record Separator

- **record_separator**: The string that marks the beginning of each document.
  - **Type**: String

#### Record Finalizer

- **record_finalizer**: The string that marks the end of each document.
  - **Type**: String

#### Keys

- **keys**: The keys to be parsed, each with a list of selectors and optional chain methods.
  - **Type**: Dictionary
  - **Default**: None

### Fields

- **type**: The type of parser plugin used (here: `htmlq`).
- **record_separator**: The HTML tag that marks the beginning of each document.
- **record_finalizer**: The HTML tag that marks the end of each document.
- **keys**: The keys to be parsed, each with a list of selectors and optional chain methods.

### Selectors

Selectors define the query selectors to extract data from the HTML document.

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

### Usage

To use the `lquery::htmlq` plugin, include it in the `parsing` section of your
Parscival specification file with the desired parameters. This will ensure
that data is extracted from the HTML documents according to the specified
query selectors and chain methods.

## ``grammar::PEG``

### Overview

Parsing Expression Grammars (PEGs) are a type of formal grammar that are used
to define the syntax of a language in a straightforward and unambiguous way.
Unlike traditional context-free grammars, PEGs use a top-down parsing approach
and prioritize order, making them deterministic and free from ambiguities.
This characteristic makes PEGs particularly useful for parsing complex and
nested structures found in many document formats.

The `grammar::PEG` plugin leverages parsimonious PEGs to parse documents,
extracting data based on defined grammar rules. This plugin can handle various
document structures, including nested and hierarchical data.

### Configuration

#### Parsing Category

- **grammar**: The name of the parsing category.

#### Parser Type

- **type**: Specifies the parser plugin used.
  - **Type**: String
  - **Valid Values**: `PEG`

#### Record Separator

- **record_separator**: The string that marks the beginning of each document.
  - **Type**: String
  - **Default**: `None`

#### Rules

- **rules**: The grammar rules used to parse the document.
  - **Type**: String
  - **Default**: None

### Example Configuration

Below is an example configuration designed to parse a NBIB document:

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

### Example Document

A PubMed nbib document recognized by the grammar above is given below:

```
PMID- 32598326
OWN - NLM
STAT- MEDLINE
DCOM- 20200924
LR  - 20200924
IS  - 2191-0308 (Electronic)
IS  - 0048-7554 (Linking)
VI  - 35
IP  - 3
DP  - 2020 Sep 25
TI  - Impact of pesticide exposure in childhood.
PG  - 221-227
LID - 10.1515/reveh-2020-0011 [doi]
AB  - Pesticides represent a wide variety of chemicals presented as different formulations 
      and concentrations and used in different settings: agriculture, animal sanitary 
      bath, domestic use, and vector control. Lack of awareness, poor agricultural 
      practices, and inappropriate disposal of containers will increase the exposure and 
      risk of health effects during childhood. The concern about children's exposure to 
      pesticides is based on their toxic properties and the special vulnerability to the 
      exposure, which may occur in different stages, from the prenatal period to infancy. 
FAU - Pascale, Antonio
AU  - Pascale A
AD  - Department of Toxicology, School of Medicine, University of the Republic, 
      Montevideo, Uruguay.
FAU - Laborde, Amalia
AU  - Laborde A
AD  - Department of Toxicology, School of Medicine, University of the Republic, 
      Montevideo, Uruguay.
LA  - eng
PT  - Journal Article
PT  - Review
PL  - Germany
TA  - Rev Environ Health
JT  - Reviews on environmental health
JID - 0425754
RN  - 0 (Pesticides)
SB  - IM
MH  - Adolescent
MH  - Child
MH  - Child, Preschool
OTO - NOTNLM
OT  - children
OT  - diseases
OT  - exposure
AID - 10.1515/reveh-2020-0011 [doi]
PST - ppublish
SO  - Rev Environ Health. 2020 Sep 25;35(3):221-227. doi: 10.1515/reveh-2020-0011.
```

### Usage

To use the `grammar::PEG` plugin, include it in the `parsing` section of your
Parscival specification file with the desired parameters. This will ensure
that data is extracted from the documents according to the specified grammar
rules.

### Syntax Reference

The `grammar::PEG` plugin uses a specific syntax for defining grammar rules.
Below is a reference for the syntax elements used in parsimonious PEGs:

| Syntax                | Description                                                                                                      |
|-----------------------|------------------------------------------------------------------------------------------------------------------|
| `"some literal"`      | Used to quote literals.                                                                                          |
| `b"some literal"`     | A bytes literal.                                                                                                 |
| [space]               | Sequences are made out of space- or tab-delimited things.                                                        |
| `a / b / c`           | Alternatives. The first to succeed of `a / b / c` wins.                                                          |
| `thing?`              | An optional expression. This is greedy, always consuming `thing` if it exists.                                   |
| `&thing`              | A lookahead assertion. Ensures `thing` matches at the current position but does not consume it.                  |
| `!thing`              | A negative lookahead assertion. Matches if `thing` isn't found here. Doesn't consume any text.                   |
| `things*`             | Zero or more things. This is greedy, always consuming as many repetitions as it can.                             |
| `things+`             | One or more things. This is greedy, always consuming as many repetitions as it can.                              |
| `~r"regex"ilmsuxa`    | Regexes have `~` in front and are quoted like literals.                                                          |
| `~br"regex"`          | A bytes regex; required if your grammar parses bytestrings.                                                      |
| `(things)`            | Parentheses are used for grouping, like in every other language.                                                 |
| `thing{n}`            | Exactly `n` repetitions of `thing`.                                                                              |
| `thing{n,m}`          | Between `n` and `m` repetitions (inclusive.)                                                                     |
| `thing{,m}`           | At most `m` repetitions of `thing`.                                                                              |
| `thing{n,}`           | At least `n` repetitions of `thing`.                                                                             |
