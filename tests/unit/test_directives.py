from __future__ import annotations

from io import StringIO
from textwrap import dedent

from docutils import nodes
from docutils.core import publish_doctree
from docutils.parsers.rst import directives as rst_directives

from sphinx_structured_toc.directives import DomainDirective, SliceDirective
from sphinx_structured_toc.nodes import Domain, Slice, SliceItem


def parse_rst(source: str) -> nodes.document:
    # Register directives per-call. A Sphinx test app built earlier in the
    # same session replaces docutils' global directive entries for these
    # names; re-registering keeps these structural tests independent of
    # ordering.
    rst_directives.register_directive("domain", DomainDirective)
    rst_directives.register_directive("slice", SliceDirective)
    return publish_doctree(
        dedent(source),
        settings_overrides={
            "halt_level": 6,
            "report_level": 5,
            "warning_stream": StringIO(),
        },
    )


def domains(doctree: nodes.document) -> list[Domain]:
    return list(doctree.findall(Domain))


def slices(doctree: nodes.document) -> list[Slice]:
    return list(doctree.findall(Slice))


def items(slice_node: Slice) -> list[SliceItem]:
    return [child for child in slice_node.children if isinstance(child, SliceItem)]


# --- domain containing one slice with one item ---------------------------


def test_domain_with_one_slice_with_one_item(build_app):
    app = build_app(
        """
        .. domain::

           .. slice:: Models

              :doc:`Introduction <models/introduction>`
        """,
        docs={"models/introduction.rst": "Introduction\n============\n"},
    )

    ds = domains(app.env.get_doctree("index"))
    assert len(ds) == 1
    ss = slices(app.env.get_doctree("index"))
    assert len(ss) == 1
    assert ss[0]["name"] == "Models"
    its = items(ss[0])
    assert len(its) == 1


# --- domain with one slice with multiple items ---------------------------


def test_domain_with_one_slice_with_multiple_items(build_app):
    app = build_app(
        """
        .. domain::

           .. slice:: Models

              :doc:`Introduction <models/introduction>`
              :doc:`Field types <models/fields>`
              :doc:`Custom fields <models/custom>`
        """,
        docs={
            "models/introduction.rst": "Introduction\n============\n",
            "models/fields.rst": "Field types\n===========\n",
            "models/custom.rst": "Custom fields\n=============\n",
        },
    )

    ss = slices(app.env.get_doctree("index"))
    assert len(ss) == 1
    its = items(ss[0])
    assert len(its) == 3


# --- slice name with spaces ----------------------------------------------


def test_slice_name_may_contain_spaces(build_app):
    app = build_app(
        """
        .. domain::

           .. slice:: Model instances and relations

              :doc:`Instance methods <models/instances>`
        """,
        docs={"models/instances.rst": "Instance methods\n================\n"},
    )

    ss = slices(app.env.get_doctree("index"))
    assert len(ss) == 1
    assert ss[0]["name"] == "Model instances and relations"


# --- empty slice errors --------------------------------------------------


def test_empty_slice_errors():
    doctree = parse_rst(
        """
        .. domain::

           .. slice:: Models
        """,
    )

    messages = list(doctree.findall(nodes.system_message))
    assert any("slice 'Models' has no items" in m.astext() for m in messages)


# --- empty domain (no slices) errors -------------------------------------


def test_empty_domain_errors():
    doctree = parse_rst(
        """
        .. domain::
        """,
    )

    messages = list(doctree.findall(nodes.system_message))
    assert any("domain must contain at least one slice" in m.astext() for m in messages)


# --- domain with non-slice content errors --------------------------------


def test_domain_rejects_non_slice_content():
    doctree = parse_rst(
        """
        .. domain::

           This is not a slice.
        """,
    )

    messages = list(doctree.findall(nodes.system_message))
    assert any("domain may only contain 'slice' blocks" in m.astext() for m in messages)


# --- domain with optional name argument ----------------------------------


def test_domain_accepts_optional_name_argument(build_app):
    app = build_app(
        """
        .. domain:: Model layer

           .. slice:: Models

              :doc:`Introduction <models/introduction>`
        """,
        docs={"models/introduction.rst": "Introduction\n============\n"},
    )

    ds = domains(app.env.get_doctree("index"))
    assert len(ds) == 1
    assert ds[0]["name"] == "Model layer"
    assert ds[0]["overridden"] is True


def test_domain_without_name_argument_has_no_name(build_app):
    app = build_app(
        """
        .. domain::

           .. slice:: Models

              :doc:`Introduction <models/introduction>`
        """,
        docs={"models/introduction.rst": "Introduction\n============\n"},
    )

    ds = domains(app.env.get_doctree("index"))
    assert len(ds) == 1
    assert "name" not in ds[0]
    assert ds[0]["overridden"] is False
