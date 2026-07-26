from __future__ import annotations

from docutils import nodes

from sphinx_structured_toc.nodes import Slice, SliceItem


def get_slice(app) -> Slice:
    doctree = app.env.get_doctree("index")
    ss = list(doctree.findall(Slice))
    assert len(ss) == 1, f"expected one slice, found {len(ss)}"
    return ss[0]


def items(slice_node: Slice) -> list[SliceItem]:
    return [c for c in slice_node.children if isinstance(c, SliceItem)]


def assert_plain(item: SliceItem) -> None:
    assert item.get("mark_slice") is not True
    assert item.get("mark_domain") is not True


def test_slice_keyword_alone_sets_mark_slice(build_app):
    app = build_app(
        """
        .. domain::

           .. slice:: Models

              :doc:`Introduction <models/introduction>` slice
        """,
        docs={"models/introduction.rst": "Introduction\n============\n"},
    )

    its = items(get_slice(app))
    assert len(its) == 1
    assert its[0]["mark_slice"] is True
    assert its[0].get("mark_domain") is not True


def test_domain_keyword_alone_sets_mark_domain(build_app):
    app = build_app(
        """
        .. domain::

           .. slice:: Models

              :doc:`Introduction <models/introduction>` domain
        """,
        docs={"models/introduction.rst": "Introduction\n============\n"},
    )

    its = items(get_slice(app))
    assert len(its) == 1
    assert its[0].get("mark_slice") is not True
    assert its[0]["mark_domain"] is True


def test_both_keywords_slice_then_domain(build_app):
    app = build_app(
        """
        .. domain::

           .. slice:: Models

              :doc:`Introduction <models/introduction>` slice domain
        """,
        docs={"models/introduction.rst": "Introduction\n============\n"},
    )

    its = items(get_slice(app))
    assert len(its) == 1
    assert its[0]["mark_slice"] is True
    assert its[0]["mark_domain"] is True


def test_both_keywords_domain_then_slice(build_app):
    app = build_app(
        """
        .. domain::

           .. slice:: Models

              :doc:`Introduction <models/introduction>` domain slice
        """,
        docs={"models/introduction.rst": "Introduction\n============\n"},
    )

    its = items(get_slice(app))
    assert len(its) == 1
    assert its[0]["mark_slice"] is True
    assert its[0]["mark_domain"] is True


def test_neither_keyword_leaves_plain_item(build_app):
    app = build_app(
        """
        .. domain::

           .. slice:: Models

              :doc:`Introduction <models/introduction>`
        """,
        docs={"models/introduction.rst": "Introduction\n============\n"},
    )

    its = items(get_slice(app))
    assert len(its) == 1
    assert_plain(its[0])


def test_unrecognised_trailing_token_is_fatal(build_app):
    app = build_app(
        """
        .. domain::

           .. slice:: Models

              :doc:`Introduction <models/introduction>` banana
        """,
        docs={"models/introduction.rst": "Introduction\n============\n"},
    )

    doctree = app.env.get_doctree("index")
    messages = list(doctree.findall(nodes.system_message))
    assert any("unrecognised" in m.astext() for m in messages)


def test_extra_whitespace_around_keywords_is_tolerated(build_app):
    app = build_app(
        """
        .. domain::

           .. slice:: Models

              :doc:`Introduction <models/introduction>`    slice     domain
        """,
        docs={"models/introduction.rst": "Introduction\n============\n"},
    )

    its = items(get_slice(app))
    assert len(its) == 1
    assert its[0]["mark_slice"] is True
    assert its[0]["mark_domain"] is True


def test_keyword_repeated_on_line_is_fatal(build_app):
    app = build_app(
        """
        .. domain::

           .. slice:: Models

              :doc:`Introduction <models/introduction>` slice slice
        """,
        docs={"models/introduction.rst": "Introduction\n============\n"},
    )

    doctree = app.env.get_doctree("index")
    messages = list(doctree.findall(nodes.system_message))
    assert any("unrecognised" in m.astext() for m in messages)
