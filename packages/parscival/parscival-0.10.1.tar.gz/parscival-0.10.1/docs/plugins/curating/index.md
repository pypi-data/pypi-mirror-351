# Curating

Curation plugins defines additional tasks before ingesting,
parsing, mapping, storing or finishing the processing of inputs.

List of available plugins:

```eval_rst
.. contents::
   :depth: 1
   :local:
```

## ``encode::convert``

### Overview

The `convert` plugin is designed to perform encoding conversions and newline character standardizations on files before they are ingested. This plugin ensures that all files meet the specified encoding and newline requirements, making them consistent and compliant for further processing.

### Configuration

The `convert` plugin can be configured with various parameters to control its behavior. Below is a detailed explanation of each configuration option.

### Example Configuration

Below is an example configuration for the `convert` plugin:

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
```

#### Encoding Conversion

The `convert` plugin performs encoding conversion on the specified files. It can automatically detect the source encoding if the value `'guess'` is used for the `from` parameter. The target encoding is specified using the `to` parameter.

##### from

- **Description**: The source encoding of the files. The value `'guess'` will attempt to detect the encoding automatically.
- **Type**: String
- **Valid Values**: Any valid encoding name, or `'guess'`
- **Default**: `'guess'`

##### to

- **Description**: The target encoding to convert the files to.
- **Type**: String
- **Valid Values**: Any valid encoding name
- **Default**: `'utf-8'`

#### Policy

The `policy` parameter determines which files will be processed. The value `'only-non-complaint'` means that only files that do not already meet the specified encoding and newline criteria will be processed.

- **Description**: The policy to apply for processing files. The value `'only-non-complaint'` means only files that don't meet the expected encoding and newline criteria will be processed.
- **Type**: String
- **Valid Values**: `'only-non-complaint'`
- **Default**: `'only-non-complaint'`

#### Newline Character Standardization

The plugin ensures that all files have a consistent newline character as specified by the `newline` parameter. The valid values for this parameter are:

- **`'LF'`**: Line Feed (Unix-style newlines)
- **`'CR'`**: Carriage Return (Mac-style newlines)
- **`'CRLF'`**: Carriage Return and Line Feed (Windows-style newlines)

- **Description**: The newline character to use in the output files.
- **Type**: String
- **Valid Values**: `'LF'`, `'CR'`, `'CRLF'`
- **Default**: `'LF'`

#### Transient Directory

The plugin uses a temporary directory for intermediate processing steps. The `basedir` parameter specifies the base directory for creating these temporary directories. If `cleanable` is set to `true`, these temporary directories will be cleaned up after processing.

##### basedir

- **Description**: The base directory for creating temporary directories.
- **Type**: String
- **Default**: `'/tmp'`

##### cleanable

- **Description**: Indicates whether the temporary directories should be cleaned up after processing.
- **Type**: Boolean
- **Default**: `true`

#### Enabling/Disabling the Plugin

The `enabled` parameter can be used to enable or disable the plugin. If set to `false`, the plugin will not perform any actions.

- **Description**: Enable or disable this plugin.
- **Type**: Boolean
- **Default**: `true`

### Usage

To use the `convert` plugin, include it in the `before_ingesting` section of your Parscival specification file with the desired parameters. This will ensure that all files are processed according to the specified encoding and newline requirements before they are ingested.

## ``encode::time_granularity`` <sup>≥v0.9</sup>

### Overview

The `time_granularity` plugin standardizes and encodes time granularity for specified data mappings. It converts timestamp or date fields into discrete periods (e.g., yearly, quarterly, monthly) and assigns sequential numerical indices starting from a specified base. This plugin is useful for normalizing and grouping temporal data consistently across datasets.

### Configuration

The `time_granularity` plugin is customizable through several configuration parameters outlined below.

### Example Configuration

Here's a sample YAML configuration for the `time_granularity` plugin:

```yaml
curating:
  # curation actions to be taken after mapping data
  after_mapping:
    plugins:
      # list of plugins to be executed
      - encode: 'time_granularity'
        params:
          # name of the node to process
          node: 'ISIpubdate'
          # 'mixed' or valid date string format
          input_date_format: mixed
          # 'timelapse', 'bins' or 'dateint'
          output_time_format: timelapse
          # 'years', 'quarters', 'months',  'weeks',
          # 'days' , 'hours'   , 'minutes', 'seconds',
          # 'milliseconds', 'microseconds', 'nanoseconds'
          granularity: years
          # assign sequential numbers starting from start_from
          start_from: 1
          # enable or disable this plugin
          enabled: true

```

#### Parameters

Below is the description of each configurable parameter for the plugin:

##### node

- **Description**: Name of the node in the data mappings containing date or timestamp fields to encode.
- **Type**: String
- **Required**: Yes
- **Example**: `'ISIpubdate'`

##### granularity

- **Description**: The time granularity for encoding timestamps/dates.
- **Type**: String
- **Valid Values**:
  - `'year'`, `'years'`, `'yearly'`
  - `'quarter'`, `'quarters'`, `'quarterly'`
  - `'month'`, `'months'`, `'monthly'`
  - `'week'`, `'weeks'`, `'weekly'`
  - `'business day'`, `'business days'`
  - `'day'`, `'days'`, `'calendar day'`, `'calendar days'`
  - `'hour'`, `'hours'`, `'hourly'`
  - `'minute'`, `'minutes'`, `'minutely'`
  - `'second'`, `'seconds'`, `'secondly'`
  - `'millisecond'`, `'milliseconds'`
  - `'microsecond'`, `'microseconds'`
  - `'nanosecond'`, `'nanoseconds'`
- **Default**: `'years'`

##### input_date_format

- **Description**: Format specification of the `node` input. Use `'mixed'` if dates have varying formats and require automatic detection.
- **Type**: String
- **Valid Values**: Any valid date format string or `'mixed'`
- **Default**: `'mixed'`

Here are common valid date format directives:

| Directive | Meaning                           | Example           |
|-----------|-----------------------------------|-------------------|
| `%Y`      | Four-digit year                   | `2024`            |
| `%y`      | Two-digit year                    | `24`              |
| `%m`      | Zero-padded month (01-12)         | `03` (for March)  |
| `%d`      | Zero-padded day (01-31)           | `09`              |
| `%H`      | Hour in 24-hour clock (00-23)     | `14`              |
| `%I`      | Hour in 12-hour clock (01-12)     | `02`              |
| `%M`      | Minutes (00-59)                   | `35`              |
| `%S`      | Seconds (00-59)                   | `59`              |
| `%f`      | Microseconds (000000-999999)      | `123456`          |
| `%p`      | AM/PM                             | `AM`, `PM`        |
| `%z`      | UTC offset                        | `+0100`, `-0530`  |
| `%Z`      | Time zone name                    | `EST`, `UTC`      |
| `%a`      | Abbreviated weekday name          | `Mon`, `Tue`      |
| `%A`      | Full weekday name                 | `Monday`          |
| `%b`      | Abbreviated month name            | `Jan`, `Feb`      |
| `%B`      | Full month name                   | `January`         |
| `%j`      | Day of the year (001-366)         | `365`             |
| `%W`      | Week number (00-53)               | `52`              |
| `%U`      | Week number (Sunday first) (00-53)| `52`              |
| `%c`      | Locale’s appropriate date/time    | `Tue Aug 16 21:30:00 2024` |
| `%x`      | Locale’s appropriate date         | `08/16/24`        |
| `%X`      | Locale’s appropriate time         | `21:30:00`        |

##### Examples

| Date Example             | `input_date_format`          |
|--------------------------|------------------------------|
| `2024-03-20`             | `%Y-%m-%d`                   |
| `20/03/2024`             | `%d/%m/%Y`                   |
| `03-20-24`               | `%m-%d-%y`                   |
| `March 20, 2024`         | `%B %d, %Y`                  |
| `2024-03-20 14:25:30`    | `%Y-%m-%d %H:%M:%S`          |
| `03/20/2024 02:25 PM`    | `%m/%d/%Y %I:%M %p`          |

##### output_time_format

- **Description**: Defines how the encoded time values should be represented.
- **Type**: String
- **Valid Values**:
  - **`bins`** → Assigns sequential numbers for each unique time period.
  - **`timelapse`** → Computes the time difference from the earliest available period.
  - **`dateint`** → Converts dates into an integer representation based on the `granularity` format.
- **Default**: `'timelapse'`


##### Examples

###### `bins`

| node: 'ISIpubdate' | years | months | days |
|--------------------|-------|--------|------|
| **enabled**       | "true" | "true"  | "true"  |
| **input_date_format** | "mixed" | "mixed" | "mixed" |
| **starting_from** | 1 | 1 | 1 |
| **output_time_format** | "bins" | "bins" | "bins" |
| **2022-12-22**    | 3 | 3 | 3 |
| **2022-12-28**    | 3 | 3 | 4 |
| **2023-10-19**    | 4 | 4 | 5 |
| **1989-10-25**    | 1 | 1 | 1 |
| **2020-10-06**    | 2 | 2 | 2 |


###### `timelapse`

| node: 'ISIpubdate' | years | months | days |
|--------------------|-------|--------|------|
| **enabled**       | "true" | "true"  | "true"  |
| **input_date_format** | "mixed" | "mixed" | "mixed" |
| **starting_from** | 0 | 0 | 0 |
| **output_time_format** | "timelapse" | "timelapse" | "timelapse" |
| **2022-12-22**    | 33  | 398  | 12111  |
| **2022-12-28**    | 33  | 398  | 12117  |
| **2023-10-19**    | 34  | 408  | 12412  |
| **1989-10-25**    | 0   | 0    | 0  |
| **2020-10-06**    | 31  | 372  | 11304  |


###### `dateint`

| node: 'ISIpubdate' | years | months | days |
|--------------------|-------|--------|------|
| **enabled**       | "true" | "true"  | "true"  |
| **input_date_format** | "mixed" | "mixed" | "mixed" |
| **starting_from** | not_used | not_used | not_used |
| **output_time_format** | "dateint" | "dateint" | "dateint" |
| **2022-12-22**    | 2022  | 202212  | 20221222  |
| **2022-12-28**    | 2022  | 202212  | 20221228  |
| **2023-10-19**    | 2023  | 202310  | 20231019  |
| **1989-10-25**    | 1989  | 198910  | 19891025  |
| **2020-10-06**    | 2020  | 202010  | 20201006  |

##### start_from

- **Description**: The initial number for sequential indexing of encoded time periods.
- **Type**: Integer (≥ 0)
- **Default**: `1`

##### enabled

- **Description**: Controls whether the plugin executes its processing logic.
- **Type**: Boolean
- **Valid Values**: `true` or `false`
- **Default**: `true`

### Usage

To apply the `time_granularity` plugin, include it in the appropriate `curating` section (e.g., `after_mapping`) of your Parscival specification YAML. Provide the necessary parameters to specify the target node, granularity, and other preferences.

## ``match::elg_node_matcher``

### Overview

The  ELG Node Matcher (`elg_node_matcher`) plugin is designed to effiently apply matching and replacement over the data of a specified mapped node using a registry (or authoritative list) in CSV format. This plugin ensures that all entries are standardized according to the provided registry.

The registry list can contain hundreds of thousands of entries. The file is automatically compiled into an efficient representation and then applied to the node using an Extended Local Grammar engine. For more information, refer to the thesis *Extended Local Grammars: Principles, Implementation and Applications for Information Retrieval* (Martinez C., Université Paris-Est, 2017).

### Example Registry

Below is an example of a registry used to normalize publication names:

```
avis financiers les echos;les echos
finances les echos;les echos
les echos avis financiers (english);les echos
les echos avis financiers (français);les echos
les echos avis financiers;les echos
les echos finances;les echos
lesechos.fr;les echos
les echos le cercle;les echos
les echos le cercle (site web);les echos
les echos;les echos
lesechos;les echos
```

### Configuration

The plugin can be configured with various parameters to control its behavior. Below is a detailed explanation of each configuration option.

### Example Configuration

Below is an example configuration for the `elg_node_matcher` plugin:

```yaml
# Specifies curating tasks to be done after/before
# ingesting, parsing, mapping, storing or finishing
curating:
  # Curation actions to be taken after mapping data
  after_mapping:
    plugins:
      # List of plugins to be executed after mapping
      - match: 'elg_node_matcher'
        # Parameters for the node matcher plugin
        params:
          # Name of the node to process
          node: 'OtherSourceName'
          # Path to the registry file
          registry: 'europresse-journal-name.csv'
          # Filter mode for processing nodes
          filter_mode: 'relaxed'
          # Normalize functions to be applied on each node item before matching
          normalize:
            # Lowercase item data
            - lowercase: true
            # Collapse multiple spaces
            - collapse: true
            # Remove leading and trailing whitespace
            - trim: true
          # Cache options
          cache:
            # Directory for cache storage
            dir: './cache'
            # Store the compiled registry in the cache
            store_compiled_registry: true
            # Store the match results in the cache
            store_result: false
            # Use the cached compiled registry
            use_cached_registry: true
            # Use the cached match results
            use_cached_result: false
          # Match options
          matches:
            # Policy for handling ambiguous matches
            ambiguous_policy: 'warn'
            # Delimiter for separating ambiguous matches
            ambiguous_delimiter: ' *** '
          # Verbosity level
          verbose: 'error'
          # Enable or disable the plugin
          enabled: true
```

#### Node Processing

The plugin processes a specific node in the data.

##### node

- **Description**: The name of the node to process.
- **Type**: String
- **Default**: None

#### Registry

The plugin uses a registry file in CSV format to standardize entries.

##### registry

- **Description**: The path to the registry file.
- **Type**: String
- **Default**: None

#### Filter Mode

The `filter_mode` parameter determines how unmatched or partially matched nodes are handled.

- **Description**: The filter mode to apply for processing nodes.
- **Type**: String
- **Valid Values**: `'strict'`, `'moderate'`, `'relaxed'`
- **Default**: `'relaxed'`

- **Options**:
  - **`'strict'`**: Clear non-fully matched nodes.
  - **`'moderate'`**: Keep partially matched nodes.
  - **`'relaxed'`**: Keep non-matched nodes.

#### Normalization

Normalization functions to be applied on each node item before matching.

##### normalize

- **Description**: A list of normalization functions to apply.
- **Type**: List of function names in order of application
- **Options**:
  - **`lowercase`**: Convert item data to lowercase.
  - **`collapse`**: Collapse multiple spaces.
  - **`trim`**: Remove leading and trailing whitespace.

#### Cache Options

Settings related to caching compiled registry and match results.

##### cache

###### dir

- **Description**: Directory for cache storage.
- **Type**: String
- **Default**: `'./cache'`

###### store_compiled_registry

- **Description**: Whether to store the compiled registry in the cache.
- **Type**: Boolean
- **Default**: `true`

###### store_result

- **Description**: Whether to store the match results in the cache.
- **Type**: Boolean
- **Default**: `false`

###### use_cached_registry

- **Description**: Whether to use the cached compiled registry.
- **Type**: Boolean
- **Default**: `true`

###### use_cached_result

- **Description**: Whether to use the cached match results.
- **Type**: Boolean
- **Default**: `false`

#### Match Options

Settings related to handling matches.

##### matches

###### ambiguous_policy

- **Description**: Policy for handling ambiguous matches.
- **Type**: String
- **Valid Values**: `'keep'`, `'warn'`, `'ignore'`
- **Default**: `'warn'`

###### ambiguous_delimiter

- **Description**: Delimiter for separating ambiguous matches.
- **Type**: String
- **Default**: `' *** '`

#### Verbosity

Controls the verbosity level of the plugin.

##### verbose

- **Description**: Verbosity level of the plugin.
- **Type**: String
- **Valid Values**: `'info'`, `'error'`, `'none'`
- **Default**: `'error'`

#### Enabling/Disabling the Plugin

The `enabled` parameter can be used to enable or disable the plugin.

##### enabled

- **Description**: Enable or disable this plugin.
- **Type**: Boolean
- **Default**: `true`

### Usage

To use the `elg_node_matcher` plugin, include it in the `after_mapping` section of your Parscival specification file with the desired parameters. This will ensure that all entries in the specified node are standardized according to the provided registry.


Certainly! Here’s the updated documentation for the `hash_key_deduplicator` plugin with the combined overview section:

## ``deduplicate::hash_key_deduplicator``

### Overview

The `hash_key_deduplicator` plugin is designed to identify and remove duplicate documents based on a templatized hash key. Two documents are considered duplicates if they share the same hash key. This plugin ensures that only unique documents are stored.

Document deduplication is a crucial step in data curation to ensure data quality and integrity. There are several techniques to achieve document deduplication, including but not limited to:

- **Hash-Based Deduplication**: Uses a hash key to identify duplicates. If two documents generate the same hash key, they are considered duplicates.
- **Content-Based Deduplication**: Compares the content of documents to identify duplicates. This can involve comparing text similarity, document structure, or even semantic content.
- **Metadata-Based Deduplication**: Utilizes metadata such as titles, dates, and authors to identify duplicate documents.
- **Author Name Disambiguation**: A specialized form of deduplication that resolves different names referring to the same author to avoid treating different name variations as separate entities.

The `hash_key_deduplicator` plugin specifically uses a hash key collision approach for deduplication. While this method is efficient and straightforward, other techniques such as content-based and metadata-based deduplication, as well as author name disambiguation, can be implemented in future steps by other plugins to create a comprehensive deduplication strategy.

### Configuration

### Example Configuration

Below is an example configuration for the `hash_key_deduplicator` plugin:

```yaml
# Specifies curating tasks to be done after/before
# ingesting, parsing, mapping, storing or finishing
curating:
  # Curation actions to be taken before storing mapped data
  before_storing:
    plugins:
      # List of plugins to be executed before storing
      - deduplicate: 'hash_key_deduplicator'
        # Parameters for the deduplication plugin
        params:
          # Templatized string used to generate the hash key
          hash_key: '{{ID}}'
```

#### Deduplication Key

The plugin uses a templatized hash key to identify duplicate documents.

##### hash_key

- **Description**: The templatized string used to generate the hash key. This string can use the names of the mapped nodes.
- **Type**: String
- **Default**: `None`

### Usage

To use the `hash_key_deduplicator` plugin, include it in the `before_storing` section of your Parscival specification file with the desired parameter. This will ensure that duplicate documents are identified and removed based on the specified hash key before the data is stored.

