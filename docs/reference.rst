Reference
=============

The extension can only apply ARIA attributes to HTML output. For PDF,  links are generated but without any additional context.

Basic rendering
---------------

When ``.. domain::`` is given without an argument, the domain label is taken from the nearest enclosing section heading (the ``<nav>`` is labelled via an ``aria-labelledby`` attribute that refers to the heading's ``id``).

..  code-block:: rst

    The model layer
    ---------------

    ..  domain::

        ..  slice:: Models

            :doc:`Reference <models/reference>`

The example above renders as:

..  code-block:: html

     <nav aria-labelledby="the-model-layer">
      <ul>
        <li>
          <span id="the-model-layer-models" class="domain-list-label">Models</span>:
          <ul>
            <li>
              <a class="reference internal" href="models/reference">
                <span class="doc">Reference</span>
              </a>
            </li>
          </ul>
        </li>
      </ul>
    </nav>

The ``id``\s are automatically generated as required.


ARIA labelling
--------------

Here's an example that includes accessibility labelling via the ``slice`` and ``domain`` options. There are three links in the slice:

* *Introduction* (to the Model layer, via the ``domain`` option)
* *Reference* (for Models, via the ``slice`` option)
* *Custom fields*

..  code-block:: rst

    The model layer
    ...............

    ..  domain::

        ..  slice:: Models

            :doc:`Introduction </demo-targets/field-types-reference>` domain
            :doc:`Reference </demo-targets/model-reference>` slice
            :doc:`Custom fields </demo-targets/custom-fields-how-to>`

The HTML output below has been simplified by removing some elements, classes and other attributes.

In the HTML you can see the ``aria-labelledby`` attribute on various items.

The ``id``\s an ``aria-labelledby`` attribute refers to will give a screen reader an accessible name for that element.

For example, there is an ``<a id="the-model-layer-models-reference">`` (the last highlighted link) that is "labelled by" two other ``id``\s: ``the-model-layer-models-reference`` and ``the-model-layer-models``.

You can identify the text associated with those two ``id``\s; the screenreader will find them and render the accessible name *Reference, Models*.


..  code-block:: html
    :emphasize-lines: 1, 2, 5, 9, 10, 16, 17

    <nav aria-labelledby="model-layer-domain">
      <span id="model-layer-domain">Model layer</span>
      <ul>
        <li>
          <span id="the-model-layer-models">Models</span>:
          <ul>
            <li>
              <a
                id="the-model-layer-models-introduction"
                aria-labelledby="the-model-layer-models-introduction model-layer-domain">
                <span>Introduction</span>
                </a>
              </li>
              <li>
                <a
                  id="the-model-layer-models-reference"
                  aria-labelledby="the-model-layer-models-reference the-model-layer-models">
                  <span>Reference</span>
                </a>
              </li>
              <li><a>Custom fields</a></li>
            </ul>
          </li>
        </ul>
      </nav>


Explicitly named domains
~~~~~~~~~~~~~~~~~~~~~~~~

When domain *is* supplied with an argument, it overrides the heading-derived name:

..  code-block:: rst

    The model layer
    ---------------

    ..  domain:: Model layer

        ..  slice:: Models

            :doc:`Reference <models/reference>`


..  code-block:: html

    <nav aria-labelledby="model-layer-domain">
      <span id="model-layer-domain" class="domain-aria-target">Model layer</span>
      [...]


The ``domain`` directive
------------------------

A ``domain`` contains one or more ``slice`` directives.

Syntax
~~~~~~

..  code-block:: rst

    ..  domain:: [<name>]
        [:suppress-warnings:]

        ..  slice:: <slice name>

            :doc:`<item>` [<keyword> ...]


Arguments and options
~~~~~~~~~~~~~~~~~~~~~

* The optional ``<name>`` argument supplies the domain name. When present, it overrides the name that would otherwise be derived from the nearest enclosing section heading.
* The ``:suppress-warnings:`` flag silences ambiguity warnings for every item inside this domain.


The ``slice`` directive
-----------------------

A ``slice`` is used inside a ``domain``, and contains one or more ``:doc:`` links, each on a single line.

Syntax
~~~~~~

..  code-block:: rst

    ..  slice:: <slice name>

        :doc:`<item>` [<keyword> ...]


Arguments
~~~~~~~~~

The ``<slice name>`` argument is required.

Each item in a slice can take optional ``slice`` or ``domain`` keywords.

* ``slice``: appends the slice name to the link's accessible name.
* ``domain``: appends the domain name to the link's accessible name.

Accessible name order
---------------------

For an item marked with ``slice`` and/or ``domain``, the accessible name is built by appending the marked context names to the item's own visible text, in the fixed order:

* the item's own visible text (always)
* the slice name (when ``slice`` is marked)
* the domain name (when ``domain`` is marked)

So an item ``:doc:`Reference <models/reference>` slice domain`` whose slice is *Models* and whose domain is *Model layer* has the accessible name *Reference, Models, Model layer*, while its visible text remains *Reference*.

The keyword order on the source line is irrelevant; the output order is always *item, slice, domain*.


CSS
---

The extension ships a minimal CSS file, ``domain-list.css``, that is automatically copied into the build's ``_static`` directory and linked from every page. It provides only the inline flow for the nested per-slice list and a default separator between adjacent items via ``border-left: 1px solid currentColor`` on nested list items. It does not suppress bullets, set spacing, typography, or layout — those are the responsibility of the theme.
