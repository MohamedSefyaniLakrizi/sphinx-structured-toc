Approaches and best practices
=============================

In all information usability practice, too much information can be as damaging as not enough. That's especially the case when it comes to accessibility and non-visual users, for whom ignoring useless information can be even more of an effort.

A sighted reader might be able to skip over unwanted information with the flick of an eye; the screen reader user will often have to pick through it much more laboriously.

Designing your tables of contents
---------------------------------

It's worth repeating that ``sphinx-structured-toc``\s tables of contents are independent of Sphinx ``toctree``\s. They are nothing to do with each other.

Making use of context
~~~~~~~~~~~~~~~~~~~~~

The job of your table of contents is to present as much information as possible in a small space, in such a way that relationships between pages of information are intuited from the organisation of the table.

This means allowing the context of links to be provided by adjacent headings and markers – the HTML heading before a domain, or the slice name at the start of a line of links.

Longer page titles can be reduced this way. If the domain is "the model layer" and the slice is about querysets, *Reference* in that slice is clearly about querysets, and not, say, model fields: we don't need to say "Model queryset reference" in the table, even if that is the actual title of the page we're linking to.


Thinking non-visually
~~~~~~~~~~~~~~~~~~~~~

Accessibility means providing the same cues and clues through other mechanisms.

We need to be aware of what the non-visual user loses and of the way information behaves. For example, the user of a screen reader can't take in a screenful of information in one act. A visually close heading could be much further away for a screen reader.


Approaches
----------

``sphinx-structured-toc`` makes some decisions based on best practice, while others are left to the user.


Built-in patterns
~~~~~~~~~~~~~~~~~

The accessible link name for a link *Reference*, that refers to the "Model queryset reference" page, is "Reference, Querysets". The order is always outwards, from the immediate context to the parent context.

The accessible name always contains the visible name ("Reference").


Decisions for the author
~~~~~~~~~~~~~~~~~~~~~~~~

It's up to the user to decide whether for example "Reference, Querysets" is enough.

Querysets only make sense in the context of models, so probably it is. Appending "Model layer" would make the name unnecessarily verbose.

Or it might be the case that the better context for clarification is not the surrounding context of the link's slice, but its wider domain, as in the :ref:`example of verb reference <verbs>`.
