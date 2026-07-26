from __future__ import annotations

import logging
from textwrap import dedent

from sphinx_structured_toc.nodes import Domain


def domain(app) -> Domain:
    doctree = app._transformed_doctrees["index"]
    ds = list(doctree.findall(Domain))
    assert len(ds) == 1, f"expected one domain, found {len(ds)}"
    return ds[0]


def test_argument_overrides_heading(build_app):
    app = build_app(
        dedent("""
            The model layer
            ===============

            .. domain:: Override name

               .. slice:: Models

                  :doc:`Introduction <models/introduction>`
            """),
        docs={"models/introduction.rst": "Introduction\n============\n"},
    )
    d = domain(app)
    assert d["name"] == "Override name"
    assert d["overridden"] is True


def test_name_from_nearest_enclosing_section(build_app):
    app = build_app(
        dedent("""
            The model layer
            ===============

            .. domain::

               .. slice:: Models

                  :doc:`Introduction <models/introduction>`
            """),
        docs={"models/introduction.rst": "Introduction\n============\n"},
    )
    d = domain(app)
    assert d["name"] == "The model layer"
    assert d["overridden"] is False
    assert d["section_id"] == "the-model-layer"


def test_fatal_error_when_no_section_and_no_argument(build_app):
    app = build_app(
        dedent("""
            .. domain::

               .. slice:: Models

                  :doc:`Introduction <models/introduction>`
            """),
        docs={"models/introduction.rst": "Introduction\n============\n"},
    )
    errors = [r for r in app._warning_records if r.levelno >= logging.ERROR]
    assert errors, "expected a fatal error for a domain with no name and no section"
    msg = errors[0].getMessage()
    assert "domain" in msg.lower()
    assert "name" in msg.lower() or "section" in msg.lower()


def test_nested_sections_pick_nearest_enclosing(build_app):
    app = build_app(
        dedent("""
            Top section
            ===========

            Inner section
            -------------

            .. domain::

               .. slice:: Models

                  :doc:`Introduction <models/introduction>`
            """),
        docs={"models/introduction.rst": "Introduction\n============\n"},
    )
    d = domain(app)
    assert d["name"] == "Inner section"
    assert d["overridden"] is False
    assert d["section_id"] == "inner-section"
