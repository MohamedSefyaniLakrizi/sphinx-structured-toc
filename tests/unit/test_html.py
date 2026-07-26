from __future__ import annotations

from textwrap import dedent

from bs4 import BeautifulSoup

_DOCS = {
    "models/introduction.rst": "Introduction\n============\n",
    "models/fields.rst": "Field types\n===========\n",
    "models/custom-fields.rst": "Custom fields\n=============\n",
    "models/reference.rst": "Reference\n=========\n",
    "queries/introduction.rst": "Introduction\n============\n",
    "queries/lookup-expressions.rst": "Lookup expressions\n=================\n",
    "queries/queryset-operations.rst": "Queryset operations\n==================\n",
    "queries/reference.rst": "Reference\n=========\n",
}


def soup(app) -> BeautifulSoup:
    return BeautifulSoup(app._index_html, "html.parser")


def get_nav(app) -> BeautifulSoup:
    s = soup(app)
    nav = s.find("nav", class_="domain-list")
    assert nav is not None, 'expected a <nav class="domain-list">'
    return nav


def test_nav_aria_labelledby_when_domain_from_heading(build_app):
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
    nav = get_nav(app)
    assert nav.get("aria-labelledby") == "the-model-layer"
    assert "aria-label" not in nav.attrs


def test_nav_aria_label_and_hidden_span_when_domain_overridden(build_app):
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
    nav = get_nav(app)
    assert nav.get("aria-label") == "Override name"
    assert "aria-labelledby" not in nav.attrs
    span = nav.find("span", id="override-name-domain")
    assert span is not None
    assert span.get_text() == "Override name"
    assert span.get("class") is not None


def test_nav_aria_label_when_overridden_and_no_section(build_app):
    app = build_app(
        dedent("""
            .. domain:: Override name

               .. slice:: Models

                  :doc:`Introduction <models/introduction>`
            """),
        docs=_DOCS,
    )
    nav = get_nav(app)
    assert nav.get("aria-label") == "Override name"
    span = nav.find("span", id="override-name-domain")
    assert span is not None
    assert span.get_text() == "Override name"


def test_slice_label_has_id_and_text(build_app):
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
    nav = get_nav(app)
    span = nav.find("span", class_="domain-list-label")
    assert span is not None
    assert span.get("id") == "the-model-layer-models"
    assert span.get_text() == "Models"


def test_colon_and_space_outside_span(build_app):
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
    nav = get_nav(app)
    li = nav.find("li")
    assert li is not None
    direct_text = "".join(str(c).strip() for c in li.children if isinstance(c, str))
    assert ": " in direct_text or direct_text.endswith(":")


def test_marked_slice_link_has_id_and_aria_labelledby(build_app):
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
    nav = get_nav(app)
    a = nav.find("a", href="models/introduction.html")
    assert a is not None
    assert a.get("id") == "the-model-layer-models-introduction"
    labelledby = a.get("aria-labelledby")
    assert labelledby is not None
    ids = labelledby.split()
    assert ids == [
        "the-model-layer-models-introduction",
        "the-model-layer-models",
    ]


def test_marked_domain_link_uses_section_id(build_app):
    app = build_app(
        dedent("""
            The model layer
            ===============

            .. domain::

               .. slice:: Models

                  :doc:`Introduction <models/introduction>` domain
            """),
        docs=_DOCS,
    )
    nav = get_nav(app)
    a = nav.find("a", href="models/introduction.html")
    assert a is not None
    assert a.get("id") == "the-model-layer-models-introduction"
    ids = a.get("aria-labelledby", "").split()
    assert ids == [
        "the-model-layer-models-introduction",
        "the-model-layer",
    ]


def test_marked_slice_domain_link_order(build_app):
    app = build_app(
        dedent("""
            The model layer
            ===============

            .. domain::

               .. slice:: Models

                  :doc:`Introduction <models/introduction>` slice domain
            """),
        docs=_DOCS,
    )
    nav = get_nav(app)
    a = nav.find("a", href="models/introduction.html")
    assert a is not None
    ids = a.get("aria-labelledby", "").split()
    assert ids == [
        "the-model-layer-models-introduction",
        "the-model-layer-models",
        "the-model-layer",
    ]


def test_marked_domain_link_uses_hidden_span_when_overridden(build_app):
    app = build_app(
        dedent("""
            The model layer
            ===============

            .. domain:: Override name

               .. slice:: Models

                  :doc:`Introduction <models/introduction>` domain
            """),
        docs=_DOCS,
    )
    nav = get_nav(app)
    a = nav.find("a", href="models/introduction.html")
    assert a is not None
    ids = a.get("aria-labelledby", "").split()
    assert ids == [
        "the-model-layer-models-introduction",
        "override-name-domain",
    ]


def test_unmarked_link_has_no_id_or_aria(build_app):
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
    nav = get_nav(app)
    a = nav.find("a", href="models/introduction.html")
    assert a is not None
    assert "id" not in a.attrs
    assert "aria-labelledby" not in a.attrs


def test_no_separator_punctuation_in_html(build_app):
    app = build_app(
        dedent("""
            The model layer
            ===============

            .. domain::

               .. slice:: Models

                  :doc:`Introduction <models/introduction>`
                  :doc:`Field types <models/fields>`
                  :doc:`Custom fields <models/custom-fields>`
            """),
        docs=_DOCS,
    )
    nav = get_nav(app)
    text = nav.get_text()
    for sep in ("|", "·", "/"):
        assert sep not in text


def test_top_level_ul_contains_slice_lis(build_app):
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
    nav = get_nav(app)
    top_ul = nav.find("ul", recursive=True)
    assert top_ul is not None
    slice_lis = top_ul.find_all("li", recursive=False)
    assert len(slice_lis) == 2
    for li in slice_lis:
        span = li.find("span", class_="domain-list-label", recursive=False)
        assert span is not None
        nested_ul = li.find("ul", recursive=False)
        assert nested_ul is not None
