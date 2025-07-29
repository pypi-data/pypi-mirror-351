Parscival
=========

.. toctree::
    :caption: Getting started
    :maxdepth: 1
    :hidden:

    Introduction <self>
    Overview <overview>
    Installation <readme>

.. toctree::
    :caption: Guides
    :maxdepth: 2
    :hidden:

    HTML <guides/html>
    Key-Value <guides/key-value>

.. toctree::
    :caption: Plugins
    :maxdepth: 2
    :hidden:

    Parsing  <plugins/parsing/index>
    Mapping  <plugins/mapping/index>
    Curating <plugins/curating/index>
    Storing  <plugins/storing/index>

.. toctree::
    :caption: Sources
    :maxdepth: 2
    :hidden:

    Europresse (.html) <sources/europresse-html>
    Pubmed (.nbib)     <sources/pubmed-nbib>

.. toctree::
    :caption: Development
    :maxdepth: 1
    :hidden:

    contributing
    license
    authors
    api/modules

Parscival is a modular framework designed for efficiently ingesting, parsing, mapping,
curating, and validating textual data sources, offering flexible
conversion and storage of results in multiple formats.

.. grid:: 1 1 2 2
    :gutter: 2
    :padding: 0
    :class-container: surface

    .. grid-item-card:: :octicon:`database` Data Processing
        :link: #

        Parscival allows to process textual data inputs and export them
        to any arbitrary format, ensuring flexibility and adaptability to parse and
        process any kind of information.

    .. grid-item-card:: :octicon:`code` YAML Specification
        :link: #

        Define your parsing, mapping, curating, validating and storing rules
        using easy-to-write YAML specifications, making it straightforward to set
        up and customize for your specific needs.

    .. grid-item-card:: :octicon:`stack` Multiple Input Formats
        :link: #

        Supports various input formats (``html``, ``key-value``, more coming).
        New formats can be adopted via plugins.

    .. grid-item-card:: :octicon:`goal` Ready-to-process sources
        :link: #

        Ready-to-process sources for various types of data,
        including scientific, technological, and media (e.g., ``Europresss``,
        ``PubMed``, with more coming soon).

    .. grid-item-card:: :octicon:`sign-out` Multiple Output Formats
        :link: #

        Supports custom output formats like ``JSON`` and ``SQLite``. New formats can be easily
        described using a simple template syntax ensuring compatibility with a wide range of
        data sources and destinations.

    .. grid-item-card:: :octicon:`gear` Plugin Architecture
        :link: #

        Implements a lightweight plugin architecture to define custom tasks for all
        data lyfecycle: parsing, mapping, curating, validating, tranforming...
        Customize and extend functionality with ease.

    .. grid-item-card:: :octicon:`rocket` High Performance
        :link: #

        Utilizes HDF5 for fast I/O storage, enabling efficient handling
        of large, complex, and heterogeneous data sets.

    .. grid-item-card:: :octicon:`sync` Parallel Processing ready
        :link: #

        Integrates with the Klepto library to enable parallel (on-the-fly) access to the
        HDF5 data produced, improving performance for large-scale data processing tasks.
