Developer reference
===================

``__init__.py`` is the extension's entry point, providing the ``setup(app)`` that Sphinx looks for in any extension it loads.

``setup(app)`` registers various components of the extension with Sphinx.

The three nodes that make up a ``structured-toc`` directive's output:

* ``Domain``: the outer container; one per ``.. domain::`` block
* ``Slice``: the inner container; one per ``.. slice:: <name>`` block inside a  ``Domain``
* ``SliceItem``: a single entry within a ``Slice``


The two directive classes in ``directives.py`` that correspond to ``.. domain`` and ``.. slice``. ``DomainDirective`` takes a ``.. domain`` and breaks it into parsed components, including one or more child slices handled by the ``SliceDirective``.

Conventions
-----------

Commit messages are in the past tense.
