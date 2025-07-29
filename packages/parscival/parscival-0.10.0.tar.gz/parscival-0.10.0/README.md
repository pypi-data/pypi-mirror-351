# Parscival
![Parscival](https://gitlab.com/cortext/cortext-methods/parscival/-/raw/master/docs/_static/logo.png)

## Description

Parscival is a modular framework designed to ingest, parse, map, curate, validate, and store heterogeneous textual data. It's especially tailored to handle Scientific and Technical Sources (STS) and can output them into any arbitrary format, such as JSON, SQLite, or custom templates.

Parscival is not limited to parsing; it empowers a complete, adaptative orchestration of the data lifecycle. From ingestion to transformation, curation to validation, and finally to structured export.

Data parsing and transforming is performed according to an experimental specification
described in a YAML file. For an example see [here](https://gitlab.com/cortext/cortext-methods/parscival/-/blob/master/src/parscival_specs/pubmed/pubmed-nbib.yaml).

The output data is saved by default using the
[HDF5](https://www.hdfgroup.org/solutions/hdf5/) binary data format. HDF5
is an open source file format that supports large, complex, heterogeneous data.
It is designed for fast I/O processing and storage.

To enable parallel (on-the-fly) access to the HDF5 data produced, Parscival
uses [klepto](https://github.com/uqfoundation/klepto), a python library that
provides fast and flexible access to large amounts of storage.

In order to define how to transform the data into an arbitrary output
format, Parscival implements a lightweight plugin architecture. For example, by using
the [render-template](https://gitlab.com/cortext/cortext-methods/parscival/-/blob/master/src/parscival_plugins/storing/plain/render_template.py) plugin, the output
result can be simple described as a [Jinja](https://jinja.palletsprojects.com/en/3.0.x/)
template. For an example on how to transform the data into ``json``
see [here](https://gitlab.com/cortext/cortext-methods/parscival/-/blob/master/src/parscival_specs/default/assets/cortext.json.tpl).

## Install

```console
pip install parscival
```

## Usage

```console
usage: parscival [-h] [--job-id JOB_ID] [--version] [--with-config [CONFIGURATION_FILES ...]] [-v] [-vv] [-vvv] FILE_PARSER_SPEC FILE_OUTPUT FILE_DATASET [FILE_DATASET ...]

A modular framework for ingesting, parsing, mapping, curating, validating and storing data

positional arguments:
  FILE_PARSER_SPEC      parscival specification
  FILE_OUTPUT           processed data output
  FILE_DATASET          input dataset

options:
  -h, --help            show this help message and exit
  --job-id JOB_ID       job identifier for logging
  --version             show program's version number and exit
  --with-config [CONFIGURATION_FILES ...]
                        YAML configuration files
  -v, --verbose         set loglevel to INFO
  -vv, --very-verbose   set loglevel to DEBUG
  -vvv, --very-very-verbose
                        set loglevel to TRACE
```

### Examples

```console
# converts documents from pesticides-s.nbib into pesticides.cortext.json as described by pubmed-nbib.yaml
parscival -v src/parscival_specs/pubmed/pubmed-nbib.yaml /tmp/pesticides.cortext.json tests/datasets/pesticides-s.nbib

# converts documents from both pesticides-s.nbib and hetercat-s.nbib into pesticides.db as described by pubmed-nbib.yaml
parscival -v src/parscival_specs/pubmed/pubmed-nbib.yaml /tmp/pesticides.cortext.db tests/datasets/pesticides-s.nbib tests/datasets/hetercat-s.nbib

# converts documents from the HTML dataset file europresse-sample1.html into JSON output file /tmp/test.cortext.json
# uses the parsing specification file europresse-html.yaml
# additionally, loads supplementary YAML configuration `(--with-config)` from the file europress-args.yaml
parscival --with-config tests/datasets/europresse-html/europress-args.yaml -v src/parscival_specs/europresse/europresse-html.yaml /tmp/test.cortext.json tests/datasets/europress/europresse-sample1.html
```

## Supported formats

### Sources

- ``PubMed (.nbib)`` : PubMed is a free search engine accessing primarily the MEDLINE
database of references and abstracts on life sciences and biomedical topics. The
parsing spec is avalaible [here](https://gitlab.com/cortext/cortext-methods/parscival/-/blob/master/src/parscival_specs/pubmed/pubmed-nbib.yaml). You can find a more
detailed description in the related [documentation](https://gitlab.com/cortext/cortext-methods/parscival/-/blob/master/docs/guides/key-value.md).

- ``Europresse (.html)`` : Europresse is a comprehensive database providing access
to a vast range of news and information from various sources. The [parsing specification](https://gitlab.com/cortext/cortext-methods/parscival/-/blob/master/src/parscival_specs/europresse/europresse-html.yaml)
allows for extracting structured data from Europresse HTML files.

### Intermediate data

The intermediate data is stored usign the CorText Graph format:

| Field       | Value                                | Type             | Description              |
| ----------- | ------------------------------------ | ---------------- | ------------------------ |
| `file`      | `sourceFile(fieldName)`              | `text`           | source file for the data |
| `id`        | `fieldName.doc[0,n-1]`               | `integer`        | ID of each document      |
| `rank`      | `fieldName.doc[id][0,m-1]`           | `integer`        | field cardinal index     |
| `parserank` | `fieldName.doc[id][rank][0,p-1]`     | `integer`        | parsed cardinal index    |
| `data`      | `fieldName.doc[id][rank][parserank]` | `[text,integer]` | parsed data              |

### Output

- ``cortext.json``: intermediate data is converted to ``json`` using the [cortext.json template](https://gitlab.com/cortext/cortext-methods/parscival/-/blob/master/src/parscival_specs/default/assets/cortext.json.tpl)

- ``cortext.sqlite``: intermediate data is converted to a ``sqlite`` script using
the [cortext.sqlite template](https://gitlab.com/cortext/cortext-methods/parscival/-/blob/master/src/parscival_specs/default/assets/cortext.sqlite.tpl). If requested by the
processing spec, the resulting ``sqlite`` script can be intepreted and thus converted
to a binary database.

## Requirements

Parscival has been set up using PyScaffold, a project generator for
bootstrapping high-quality Python packages. For details and usage information
on PyScaffold see <https://pyscaffold.org>.

This project uses PyScaffold in combination with Tox, a generic virtualenv management
and test command line tool acting as frontend to Continuous Integration servers.
A list with all the available tasks is obtained via the ``tox -av`` command.

To prepare your environment you will need to install the following dependencies:

```console
pip install -U pip setuptools
pip install -U tox
```

## Development

To facilitate development, you can use Docker to run Parscival and set up a
[remote debugging environment](https://learn.microsoft.com/en-us/visualstudio/python/debugging-python-code-on-remote-linux-machines).

### Running the Docker Container

You can run the Docker container with the following command:

```sh
docker run -it \
    -v ./test:/tmp/test \
    parscival
```

This command will:

- Start an interactive terminal session within the Docker container.
- Mount the `./test` directory from your host machine to `/tmp/test` in the container.

### Building Documentation

To build the project documentation inside the docker using `tox`, you can execute
the following command from your host machine:

```sh
docker run -it \
    -v ./docs/_build/html:/app/parscival/docs/_build/html \
    parscival \
    tox -e docs
```

This command will:

- Start an interactive terminal session within the Docker container.
- Mount the `./docs/_build/html` directory from your host machine to `/app/parscival/docs/_build/html` in the container.

## Deployment

```console
virtualenv .venv
source .venv/bin/activate
# ... if needed, edit setup.cfg to add dependencies ...
pip install .
tox

# to build distribution
tox -e build
```

## Documentation

In order to compile the Parscival documentation you must type:

```console
tox -e docs
```

## Dependences

- ``libhdf5-dev``: Provides the development files for the HDF5 (Hierarchical Data
Format version 5) library. HDF5 is designed to store and organize large amounts
of data, making it suitable for high-performance data processing applications.

- ``Python >= 3.9``: Ensures compatibility with ``Parscival >= 0.7``. This version
supports the necessary libraries and features used in the project.

## Environment variables

- ``PARSCIVAL_PLUGINS_PATHS``: Specifies the directories where Parscival should
    look for plugins.

- ``PARSCIVAL_PLUGIN_RENDER_TEMPLATE_DIR``: Specifies the directory where Parscival
    should look for default rendering templates used by plugins.

- ``PARSCIVAL_LOG_PATH`` Specifies the directory where Parscival should keep the logging
    activity.

## Learn more

To learn more about Parscival, compile the documentation by executing the following command: ``tox -e docs``

Alternatively, you may directly refer to some raw documentation pages linked below:

### General

- [How to process HTML documents with Parscival](https://gitlab.com/cortext/cortext-methods/parscival/-/blob/master/docs/guides/html.md)
- [How to process plain text key-value documents with Parscival](https://gitlab.com/cortext/cortext-methods/parscival/-/blob/master/docs/guides/key-value.md)

### Plugins

- [Parsing](https://gitlab.com/cortext/cortext-methods/parscival/-/blob/master/docs/plugins/parsing/index.md)
- [Mapping](https://gitlab.com/cortext/cortext-methods/parscival/-/blob/master/docs/plugins/mapping/index.md)
- [Curating](https://gitlab.com/cortext/cortext-methods/parscival/-/blob/master/docs/plugins/curating/index.md)
- [Storing](https://gitlab.com/cortext/cortext-methods/parscival/-/blob/master/docs/plugins/storing/index.md)

### Parscival specification examples

- [Europresse (.html)](https://gitlab.com/cortext/cortext-methods/parscival/-/blob/master/src/parscival_specs/europresse/europresse-html.yaml)
- [Pubmed (.nbib)](https://gitlab.com/cortext/cortext-methods/parscival/-/blob/master/src/parscival_specs/pubmed/pubmed-nbib.yaml)

## Credits

Parscival is being developed by the [CorTexT Platform](https://www.cortext.net) and
[Cogniteva SAS](https://cogniteva.com).
