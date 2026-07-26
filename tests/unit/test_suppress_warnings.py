from __future__ import annotations

import logging
from textwrap import dedent

from docutils import nodes
from sphinx_structured_toc.nodes import Domain

_DOCS = {
    "models/introduction.rst": "Introduction\n============\n",
    "models/fields.rst": "Field types\n===========\n",
    "queries/introduction.rst": "Introduction\n============\n",
}


def has_ambiguity_warning(records: list[logging.LogRecord]) -> bool:
    return any("ambigu" in rec.getMessage().lower() for rec in records)


def get_domain(app, name: str | None = None) -> Domain:
    """Return the single domain (or one matching ``name``) in the index doctree."""
    doctree = app._transformed_doctrees["index"]  # type: ignore[attr-defined]
    matches = list(doctree.findall(Domain))
    if name is not None:
        matches = [d for d in matches if d.get("name") == name]
    assert len(matches) == 1, f"expected one domain, found {len(matches)}"
    return matches[0]


def test_suppress_warnings_silences_same_slice_duplicates(build_app):
    app = build_app(
        dedent("""
            .. domain:: Models
               :suppress-warnings:

               .. slice:: Models

                  :doc:`Introduction <models/introduction>`
                  :doc:`Introduction <queries/introduction>`
            """),
        docs=_DOCS,
    )
    assert not has_ambiguity_warning(app._warning_records)
    assert get_domain(app, "Models").get("suppress_warnings") is True


def test_suppress_warnings_silences_cross_slice_duplicates(build_app):
    app = build_app(
        dedent("""
            .. domain:: Models
               :suppress-warnings:

               .. slice:: Models

                  :doc:`Introduction <models/introduction>`

               .. slice:: Queries

                  :doc:`Introduction <queries/introduction>`
            """),
        docs=_DOCS,
    )
    assert not has_ambiguity_warning(app._warning_records)


def test_suppress_warnings_on_one_domain_does_not_silence_another(build_app):
    app = build_app(
        dedent("""
            .. domain:: French
               :suppress-warnings:

               .. slice:: Verbs

                  :doc:`Reference <models/introduction>`

            .. domain:: German

               .. slice:: Verbs

                  :doc:`Reference <queries/introduction>`
                  :doc:`Reference <models/introduction>`
            """),
        docs={
            "models/introduction.rst": "Introduction\n============\n",
            "queries/introduction.rst": "Introduction\n============\n",
        },
    )
    assert has_ambiguity_warning(app._warning_records)


def test_without_suppress_warnings_default_still_warns(build_app):
    app = build_app(
        dedent("""
            .. domain:: Models

               .. slice:: Models

                  :doc:`Introduction <models/introduction>`
                  :doc:`Introduction <queries/introduction>`
            """),
        docs=_DOCS,
    )
    assert has_ambiguity_warning(app._warning_records)
    domain = get_domain(app)
    assert domain.get("suppress_warnings") is not True


def test_unknown_option_on_domain_is_rejected(build_app):
    app = build_app(
        dedent("""
            .. domain:: Models
               :no-such-option:

               .. slice:: Models

                  :doc:`Introduction <models/introduction>`
            """),
        docs=_DOCS,
    )
    doctree = app._transformed_doctrees["index"]  # type: ignore[attr-defined]
    messages = list(doctree.findall(nodes.system_message))
    assert any("no-such-option" in m.astext() for m in messages)
