from __future__ import annotations

from textwrap import dedent

from sphinx_structured_toc.nodes import Domain, Slice, SliceItem

_DOCS = {
    "models/introduction.rst": "Introduction\n============\n",
    "models/fields.rst": "Field types\n===========\n",
    "queries/introduction.rst": "Introduction\n============\n",
}


def domain(app) -> Domain:
    doctree = app._transformed_doctrees["index"]
    ds = list(doctree.findall(Domain))
    assert len(ds) == 1, f"expected one domain, found {len(ds)}"
    return ds[0]


def slices(app) -> list[Slice]:
    doctree = app._transformed_doctrees["index"]
    return list(doctree.findall(Slice))


def items(slice_node: Slice) -> list[SliceItem]:
    return [c for c in slice_node.children if isinstance(c, SliceItem)]


def test_slice_id_with_enclosing_section(build_app):
    app = build_app(
        dedent("""
            The model layer
            ===============

            .. domain::

               .. slice:: Models

                  :doc:`Introduction <models/introduction>`
            """),
        docs=_DOCS,
    )
    s = slices(app)[0]
    assert s["label_id"] == "the-model-layer-models"


def test_slice_id_without_enclosing_section(build_app):
    app = build_app(
        dedent("""
            .. domain:: Override name

               .. slice:: Models

                  :doc:`Introduction <models/introduction>`
            """),
        docs=_DOCS,
    )
    s = slices(app)[0]
    assert s["label_id"] == "models"


def test_marked_item_id_with_enclosing_section(build_app):
    app = build_app(
        dedent("""
            The model layer
            ===============

            .. domain::

               .. slice:: Models

                  :doc:`Introduction <models/introduction>` slice
            """),
        docs=_DOCS,
    )
    it = items(slices(app)[0])[0]
    assert it["item_id"] == "the-model-layer-models-introduction"


def test_marked_item_id_without_enclosing_section(build_app):
    app = build_app(
        dedent("""
            .. domain:: Override name

               .. slice:: Models

                  :doc:`Introduction <models/introduction>` slice
            """),
        docs=_DOCS,
    )
    it = items(slices(app)[0])[0]
    assert it["item_id"] == "models-introduction"


def test_unmarked_item_has_no_item_id(build_app):
    app = build_app(
        dedent("""
            The model layer
            ===============

            .. domain::

               .. slice:: Models

                  :doc:`Introduction <models/introduction>`
            """),
        docs=_DOCS,
    )
    it = items(slices(app)[0])[0]
    assert "item_id" not in it


def test_domain_span_id_present_when_overridden_with_section(build_app):
    app = build_app(
        dedent("""
            The model layer
            ===============

            .. domain:: Override name

               .. slice:: Models

                  :doc:`Introduction <models/introduction>`
            """),
        docs=_DOCS,
    )
    d = domain(app)
    assert d["domain_span_id"] == "override-name-domain"


def test_domain_span_id_present_when_overridden_without_section(build_app):
    app = build_app(
        dedent("""
            .. domain:: Override name

               .. slice:: Models

                  :doc:`Introduction <models/introduction>`
            """),
        docs=_DOCS,
    )
    d = domain(app)
    assert d["domain_span_id"] == "override-name-domain"


def test_domain_span_id_absent_when_not_overridden(build_app):
    app = build_app(
        dedent("""
            The model layer
            ===============

            .. domain::

               .. slice:: Models

                  :doc:`Introduction <models/introduction>`
            """),
        docs=_DOCS,
    )
    d = domain(app)
    assert "domain_span_id" not in d


def test_collision_counter_appended_on_slice_id_clash(build_app):
    app = build_app(
        dedent("""
            .. domain:: Override name

               .. slice:: Models

                  :doc:`Introduction <models/introduction>`

               .. slice:: Models

                  :doc:`Field types <models/fields>`
            """),
        docs=_DOCS,
    )
    ss = slices(app)
    assert len(ss) == 2
    assert ss[0]["label_id"] == "models"
    assert ss[1]["label_id"] == "models-2"


def test_collision_counter_appended_on_item_id_clash(build_app):
    app = build_app(
        dedent("""
            .. domain:: Override name

               .. slice:: Models

                  :doc:`Introduction <models/introduction>` slice
                  :doc:`Introduction <queries/introduction>` slice
            """),
        docs=_DOCS,
    )
    its = items(slices(app)[0])
    assert len(its) == 2
    assert its[0]["item_id"] == "models-introduction"
    assert its[1]["item_id"] == "models-introduction-2"


def test_different_sections_produce_distinct_slice_ids_without_counter(build_app):
    app = build_app(
        dedent("""
            Section A
            =========

            .. domain::

               .. slice:: Models

                  :doc:`Introduction <models/introduction>`

            Section B
            =========

            .. domain::

               .. slice:: Models

                  :doc:`Introduction <models/introduction>`
            """),
        docs=_DOCS,
    )
    ss = slices(app)
    assert len(ss) == 2
    assert ss[0]["label_id"] == "section-a-models"
    assert ss[1]["label_id"] == "section-b-models"
