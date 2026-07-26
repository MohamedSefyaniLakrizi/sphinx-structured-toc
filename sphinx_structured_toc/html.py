"""HTML visitors for sphinx-structured-toc nodes (Phase 8).

Renders the annotated doctree as semantic HTML:

* ``Domain`` becomes ``<nav aria-labelledby="...">`` referencing either the
  enclosing section's heading id (when the domain name is derived from a
  section heading) or a visually-hidden ``<span id="..." class="domain-
  aria-target">`` holding the name (when the domain name is overridden).
  The nameless case (no argument and no enclosing section) is a fatal
  build error, raised in ``transforms.py`` before rendering.
* ``Slice`` becomes a ``<li>`` containing the slice label ``<span>`` plus
  ``": "`` and a nested ``<ul>`` of items.
* ``SliceItem`` becomes a ``<li>`` containing the resolved ``<a>``.

For items marked ``slice`` and/or ``domain``, the ``<a>`` element
receives ``id`` and ``aria-labelledby``. The ``<a>`` is emitted by
Sphinx's own ``visit_reference``; this extension overrides that visitor
(globally, via ``app.add_node(..., override=True)``) so that when the
reference's parent is a ``SliceItem`` with the relevant flags set, the
aria/id attributes are injected. All other references fall through to
Sphinx's default behaviour.
"""

from __future__ import annotations

from typing import Any

from docutils import nodes


def visit_domain(translator: Any, node: Any) -> None:
    """Open the outer container for a Domain.

    Emits ``<nav aria-labelledby="{section_id}">`` when the domain name
    is derived from a section heading (not overridden), or
    ``<nav aria-labelledby="{domain_span_id}">`` referencing a
    visually-hidden ``<span id="{domain_span_id}" class="domain-aria-
    target">{name}</span>`` when overridden. The nameless case (no
    argument and no enclosing section) is a fatal build error raised in
    ``transforms.py`` and never reaches the visitor.
    """
    overridden = bool(node.get("overridden", False))
    section_id = node.get("section_id", "")
    name = node.get("name", "")

    if overridden:
        # aria-labelledby on the nav points at a visually-hidden span
        # inside, which is the single source of truth for the name and
        # is also referenced by aria-labelledby on marked items.
        span_id = node.get("domain_span_id", "")
        translator.body.append(
            f'<nav class="domain-list" aria-labelledby="{span_id}">'
        )
        # "domain-aria-target" visually hides the span while keeping it
        # in the accessibility tree (styles in domain-list.css).
        translator.body.append(
            f'<span id="{span_id}" class="domain-aria-target">'
            f'{translator.attval(name)}</span>'
        )
    else:
        translator.body.append(
            f'<nav class="domain-list" aria-labelledby="{section_id}">'
        )

    # One top-level <ul> for the slices.
    translator.body.append("<ul>")


def depart_domain(translator: Any, node: Any) -> None:
    """Close the outer container for a Domain."""
    translator.body.append("</ul>")
    translator.body.append("</nav>")


def visit_slice(translator: Any, node: Any) -> None:
    """Open a slice as a <li> containing the label <span> and a nested <ul>.

    The colon and trailing space sit in the parent <li>, after the
    ``<span>``; not inside the span, not in CSS.
    """
    label_id = node.get("label_id", "")
    name = node.get("name", "")
    translator.body.append("<li>")
    translator.body.append(
        f'<span id="{label_id}" class="domain-list-label">'
        f"{translator.attval(name)}</span>: "
    )
    translator.body.append("<ul>")


def depart_slice(translator: Any, node: Any) -> None:
    """Close a slice's nested <ul> and the slice <li>."""
    translator.body.append("</ul></li>")


def visit_slice_item(translator: Any, node: Any) -> None:
    """Open a slice item as a <li>.

    The ``<a>`` itself is emitted by Sphinx's ``visit_reference`` (which
    we override to inject ``id``/``aria-labelledby`` when the parent
    ``SliceItem`` is marked). Here we only open the wrapping ``<li>``.
    """
    translator.body.append("<li>")


def depart_slice_item(translator: Any, node: Any) -> None:
    """Close a slice item's <li>."""
    translator.body.append("</li>")


def make_reference_visitor(app: Any) -> tuple[Any, Any]:
    """Build ``visit``/``depart`` overrides for ``docutils.nodes.reference``.

    Returns ``(visit_reference, depart_reference)``. The visit function
    delegates to Sphinx's original ``visit_reference`` for any reference
    whose parent is not a marked ``SliceItem``. For marked ``SliceItem``
    parents it injects ``id`` and ``aria-labelledby`` onto the ``<a>``
    before delegating, so the rest of Sphinx's reference handling
    (classes, href, secnumber, etc.) is preserved.

    The override is registered globally via
    ``app.add_node(docutils.nodes.reference, html=(...), override=True)``.
    """
    from sphinx.writers.html5 import HTML5Translator

    from .nodes import SliceItem

    original_visit = HTML5Translator.visit_reference
    original_depart = getattr(HTML5Translator, "depart_reference", None)

    def visit_reference(self: Any, node: nodes.reference) -> None:
        parent = node.parent
        if isinstance(parent, SliceItem) and (
            parent.get("mark_slice") or parent.get("mark_domain")
        ):
            item_id = parent.get("item_id", "")
            slice_node = parent.parent
            domain_node = slice_node.parent if slice_node is not None else None
            labelledby: list[str] = []
            if item_id:
                labelledby.append(item_id)
            if parent.get("mark_slice") and slice_node is not None:
                slice_label_id = slice_node.get("label_id", "")
                if slice_label_id:
                    labelledby.append(slice_label_id)
            if parent.get("mark_domain") and domain_node is not None:
                if domain_node.get("overridden", False):
                    domain_id = domain_node.get("domain_span_id", "")
                else:
                    domain_id = domain_node.get("section_id", "")
                if domain_id:
                    labelledby.append(domain_id)
            if item_id:
                # ``starttag`` will emit the id from ``node['ids']``.
                node.setdefault("ids", []).append(item_id)
            # Delegate to Sphinx's visit_reference, then patch the
            # opening tag it emitted to add aria-labelledby (Sphinx does
            # not emit aria-* attributes on references by default).
            mark = len(self.body)
            original_visit(self, node)
            if labelledby:
                inject_aria_labelledby(self.body, mark, " ".join(labelledby))
            return

        original_visit(self, node)

    def depart_reference(self: Any, node: nodes.reference) -> None:
        if original_depart is not None:
            original_depart(self, node)

    return visit_reference, depart_reference


def inject_aria_labelledby(body: list[str], since: int, value: str) -> None:
    """Inject ``aria-labelledby="..."`` into the most recent ``<a ...>`` tag.

    Sphinx's ``visit_reference`` appends the opening ``<a>`` tag as a
    single string via ``self.starttag``. We locate that string in
    ``body`` (searching backwards from the end, starting at ``since``)
    and insert the attribute before the closing ``>``.
    """
    for i in range(len(body) - 1, since - 1, -1):
        chunk = body[i]
        if "<a " in chunk or chunk.startswith("<a"):
            # Insert before the closing ">" of the opening tag.
            idx = chunk.rfind(">")
            if idx == -1:
                continue
            body[i] = chunk[:idx] + f' aria-labelledby="{value}"' + chunk[idx:]
            return
