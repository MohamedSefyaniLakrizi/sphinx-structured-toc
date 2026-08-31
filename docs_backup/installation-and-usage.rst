Installation and usage
======================

Installation
------------

``sphinx-structured-toc`` is available on `PyPI <https://pypi.org/project/sphinx-structured-toc/>`_. Install it with ``pip``:

..  code-block:: console

    pip install sphinx-structured-toc

or with ``uv``:

..  code-block:: console

    uv add sphinx-structured-toc

The extension requires Python 3.10 or later, Sphinx 7.x, and docutils 0.21.2 or later.

Add ``sphinx_structured_toc`` to the ``extensions`` list in ``conf.py``:

..  code-block:: python

    extensions = ["sphinx_structured_toc"]

No other configuration is required. The extension ships a small CSS file that is automatically copied into your build's ``_static`` directory and linked from every page.

A minimal example
-----------------

A ``domain`` contains one or more ``slice`` blocks. Each ``slice`` contains one or more ``:doc:`` item lines, one per line:

..  code-block:: rst

    The model layer
    ~~~~~~~~~~~~~~~

    ..  domain::

        ..  slice:: Models

            :doc:`Field types <demo-targets/field-types-reference>`
            :doc:`Custom fields <demo-targets/custom-fields-how-to>`

        ..  slice:: Queries

            :doc:`Lookup expressions <demo-targets/lookup-expressions-how-to>`
            :doc:`Queryset operations <demo-targets/queryset-operations-how-to>`

This renders as a single ``<nav>`` representing the domain. It contains one list of two slices.

Each slice begins with its name, followed by a list of links with CSS separators:

..  domain::

    ..  slice:: Models

        :doc:`Field types <demo-targets/field-types-reference>`
        :doc:`Custom fields <demo-targets/custom-fields-how-to>`

    ..  slice:: Queries

        :doc:`Lookup expressions <demo-targets/lookup-expressions-how-to>`
        :doc:`Queryset operations <demo-targets/queryset-operations-how-to>`

The struture of each domain is a nested list::

  ul: the domain
      li: the slice
          ul:
              li: link
              li: link


Disambiguating repeated link text
---------------------------------

Screen reader users can't tell multiple links apart if they have the same name. Even a single link might have an uninformative name, whose meaning is immediately clear to visual users from its context but not to someone using a screen reader.

The ``slice`` and ``domain`` trailing keywords add the slice name and/or the domain name to a link's accessible name. The additional context is always added in the order *item, slice, domain*:

..  code-block:: rst
    :emphasize-lines: 5, 9

    ..  domain::

        ..  slice:: Models

            :doc:`Reference <models/reference>` slice

        ..  slice:: Queries

            :doc:`Reference <queries/reference>` slice

Here the two *Reference* links get accessible names *Reference, Models* and *Reference, Queries*. The visible text remains *Reference* in both cases.

``domain`` can be used as well as or instead of ``slice`` when ``slice`` alone is not sufficient to provide the required context:

.. _verbs:

..  code-block:: rst
    :emphasize-lines: 5, 11

    ..  domain:: French verbs

        ..  slice:: Conjugation

            :doc:`Reference <french/conjugation/reference>` domain

    ..  domain:: German verbs

        ..  slice:: Conjugation

            :doc:`Reference <german/conjugation/reference>` domain

The accessible names become *Reference, French verbs* and *Reference, German verbs*.

Ambiguity warnings
------------------

The extension emits a warning for link names that collide. This can be suppressed per particular domain with ``:suppress-warnings:`` flag:

..  code-block:: rst
    :emphasize-lines: 2

    ..  domain::
        :suppress-warnings:
