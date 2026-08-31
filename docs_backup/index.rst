Sphinx structured table of contents
===================================

``sphinx-structured-toc`` is an extension to help build structured, accessible tables of contents.

Tables of contents often rely on implicit relationships to convey information in compact forms, and that information isn't always readily available to users of screen readers. This extension makes ARIA attributes available when they're required.

Note that this is *independent* of Sphinx's ``toctree``\s. A ``toctree`` builds the site's page tree. This extension provides a way to display a thematic table of contents.

The *domains of concern* pattern
--------------------------------

.. _first-example:

Example
~~~~~~~

Below is a fragment of a table of contents.

----------

The model layer
...............

..  domain::
    :suppress-warnings:

    ..  slice:: Models

        :doc:`Field types <demo-targets/field-types-reference>`
        :doc:`Custom fields <demo-targets/custom-fields-how-to>`
        :doc:`Reference <demo-targets/model-reference>`

    ..  slice:: Queries

        :doc:`Lookup expressions <demo-targets/lookup-expressions-how-to>`
        :doc:`Queryset operations <demo-targets/queryset-operations-how-to>`
        :doc:`Reference <demo-targets/queries-reference>`

The view layer
..............

..  domain::
    :suppress-warnings:

    ..  slice:: Basics

        :doc:`View functions <demo-targets/view-functions-introduction>`
        :doc:`Reference <demo-targets/views-reference>`

----------

Each line is a slice of a thematic **domain of concern**.

It's an excellent pattern – it's compact and makes good use of implicit structural information, that saves space (see a real-life version of this pattern at a much larger scale in `Django's documentation <https://docs.djangoproject.com>`_).

It's obvious that the *Introduction* and *Reference* items in the *Models* line are in the models slice, whereas those in the *Queries* line are about queries.

The problem
~~~~~~~~~~~~

The problem is that it's only obvious to a sighted reader. The user of a screenreader can't take the structural relationships in at a glance. The information will only be available to them if they consume entire lines, sequentially.

The list of links on the page will be: "Field types, Custom fields, Reference, Lookup expressions, Queryset operations, Reference, View functions, Reference".

*Reference* appears three times.

What's obvious to the sighted reader is out of context and unclear to the screenreader user. In the case of the Django documentation, the link text *Overview* appears on the page almost 20 times. The screen reader user is entitled to ask, with some impatience, "Overview of *what*?".

Adding ARIA attributes for context
----------------------------------

``sphinx-structured-toc`` allows you to indicate the context (the domain and its slice) of a link that would otherwise be ambiguous, using ARIA attributes in the markup.

Specifically, an entire domain can be given an accessible label, so that the ``<nav>`` element announces its context. Then, each item in each slice can optionally add the slice label and/or the domain label to its link text to create an accessible name.

The example below is the same as the one above, with the addition of some *domain* and *slice* keywords to make the ambiguous links explicit.

There are two domains, *Model layer* and *View layer* (named explicitly, though a domain can also get its label automatically from the heading that precedes it, as they do in the :ref:`first example on this page <first-example>`).

*Reference* appears three times. The ``slice`` keyword on the first two disambiguates them with their slice names. Their accessible names become "Reference, Models" and "Reference, Queries".

The third *Reference* needs to be disambiguated by ``domain``, becoming "Reference, View layer".

..  code-block:: rst

    The model layer
    ~~~~~~~~~~~~~~~

    ..  domain:: Model layer

        ..  slice:: Models

            :doc:`Field types <demo-targets/field-types-reference>`
            :doc:`Custom fields <demo-targets/custom-fields-how-to>`
            :doc:`Reference <demo-targets/model-reference>` slice

        ..  slice:: Queries

            :doc:`Lookup expressions <demo-targets/lookup-expressions-how-to>`
            :doc:`Queryset operations <demo-targets/queryset-operations-how-to>`
            :doc:`Reference <demo-targets/queries-reference>` slice

    The view layer
    ~~~~~~~~~~~~~~

    ..  domain:: View layer

        ..  slice:: Basics

            :doc:`View functions <demo-targets/view-functions-introduction>`
            :doc:`Reference <demo-targets/views-reference>` domain


.. _in-this-documentation:

Accessible example
~~~~~~~~~~~~~~~~~~

The output looks no different, but provides the user of a screen reader with a better experience.

--------

The model layer
...............

..  domain:: Model layer
    :suppress-warnings:

    ..  slice:: Models

        :doc:`Field types <demo-targets/field-types-reference>`
        :doc:`Custom fields <demo-targets/custom-fields-how-to>`
        :doc:`Reference <demo-targets/model-reference>` slice

    ..  slice:: Queries

        :doc:`Lookup expressions <demo-targets/lookup-expressions-how-to>`
        :doc:`Queryset operations <demo-targets/queryset-operations-how-to>`
        :doc:`Reference <demo-targets/queries-reference>` slice

The view layer
..............

..  domain:: View layer
    :suppress-warnings:

    ..  slice:: Basics

        :doc:`View functions <demo-targets/view-functions-introduction>`
        :doc:`Reference <demo-targets/views-reference>` domain


..  toctree::
    :hidden:

    Home <self>
    installation-and-usage
    reference
    developer-reference
    approaches
