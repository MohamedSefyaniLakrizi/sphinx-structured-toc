from __future__ import annotations

import logging
from textwrap import dedent

_DOCS = {
    "models/introduction.rst": "Introduction\n============\n",
    "models/fields.rst": "Field types\n===========\n",
    "queries/introduction.rst": "Introduction\n============\n",
    "queries/fields.rst": "Field types\n===========\n",
}


def has_ambiguity_warning(records: list[logging.LogRecord]) -> bool:
    return any(
        "ambigu" in rec.getMessage().lower() or "ambiguous" in rec.getMessage().lower()
        for rec in records
    )


def test_same_slice_same_visible_text_warns_unmarked(build_app):
    app = build_app(
        dedent("""
            The model layer
            ===============

            .. domain::

               .. slice:: Models

                  :doc:`Introduction <models/introduction>`
                  :doc:`Introduction <queries/introduction>`
            """),
        docs=_DOCS,
    )
    assert has_ambiguity_warning(app._warning_records)


def test_same_slice_same_visible_text_warns_even_when_marked(build_app):
    app = build_app(
        dedent("""
            The model layer
            ===============

            .. domain::

               .. slice:: Models

                  :doc:`Introduction <models/introduction>` slice domain
                  :doc:`Introduction <queries/introduction>` slice domain
            """),
        docs=_DOCS,
    )
    assert has_ambiguity_warning(app._warning_records)


def test_cross_slice_same_text_unmarked_warns(build_app):
    app = build_app(
        dedent("""
            The model layer
            ===============

            .. domain::

               .. slice:: Models

                  :doc:`Introduction <models/introduction>`

               .. slice:: Queries

                  :doc:`Introduction <queries/introduction>`
            """),
        docs=_DOCS,
    )
    assert has_ambiguity_warning(app._warning_records)


def test_cross_slice_same_text_both_marked_slice_no_warning(build_app):
    app = build_app(
        dedent("""
            The model layer
            ===============

            .. domain::

               .. slice:: Models

                  :doc:`Introduction <models/introduction>` slice

               .. slice:: Queries

                  :doc:`Introduction <queries/introduction>` slice
            """),
        docs=_DOCS,
    )
    assert not has_ambiguity_warning(app._warning_records)


def test_cross_slice_same_text_marked_domain_only_warns_same_domain(build_app):
    app = build_app(
        dedent("""
            The model layer
            ===============

            .. domain::

               .. slice:: Models

                  :doc:`Introduction <models/introduction>` domain

               .. slice:: Queries

                  :doc:`Introduction <queries/introduction>` domain
            """),
        docs=_DOCS,
    )
    assert has_ambiguity_warning(app._warning_records)


def test_cross_domain_same_text_both_marked_domain_no_warning(build_app):
    app = build_app(
        dedent("""
            .. domain:: French

               .. slice:: Verbs

                  :doc:`Introduction <models/introduction>` domain

            .. domain:: German

               .. slice:: Verbs

                  :doc:`Introduction <queries/introduction>` domain
            """),
        docs=_DOCS,
    )
    assert not has_ambiguity_warning(app._warning_records)


def test_cross_domain_same_text_marked_slice_domain_no_warning(build_app):
    app = build_app(
        dedent("""
            .. domain:: French

               .. slice:: Verbs

                  :doc:`Introduction <models/introduction>` slice domain

            .. domain:: German

               .. slice:: Nouns

                  :doc:`Introduction <queries/introduction>` slice domain
            """),
        docs=_DOCS,
    )
    assert not has_ambiguity_warning(app._warning_records)


def test_cross_domain_same_text_unmarked_warns(build_app):
    app = build_app(
        dedent("""
            .. domain:: French

               .. slice:: Verbs

                  :doc:`Introduction <models/introduction>`

            .. domain:: German

               .. slice:: Verbs

                  :doc:`Introduction <queries/introduction>`
            """),
        docs=_DOCS,
    )
    assert has_ambiguity_warning(app._warning_records)


def test_truly_distinct_items_no_warning(build_app):
    app = build_app(
        dedent("""
            The model layer
            ===============

            .. domain::

               .. slice:: Models

                  :doc:`Introduction <models/introduction>`
                  :doc:`Field types <models/fields>`

               .. slice:: Queries

                  :doc:`Lookup expressions <queries/fields>`
            """),
        docs={
            "models/introduction.rst": "Introduction\n============\n",
            "models/fields.rst": "Field types\n===========\n",
            "queries/fields.rst": "Lookup expressions\n=================\n",
        },
    )
    assert not has_ambiguity_warning(app._warning_records)
