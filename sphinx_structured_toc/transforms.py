"""Post-transform resolution for the sphinx-structured-toc extension."""

from __future__ import annotations

from docutils import nodes
from sphinx.util.logging import getLogger

from .nodes import Domain, Slice, SliceItem

_logger = getLogger(__name__)


def nearest_section(node: nodes.Node) -> nodes.section | None:
    """Return the nearest enclosing ``nodes.section`` for ``node``, or ``None``."""
    parent = node.parent
    while parent is not None:
        if isinstance(parent, nodes.section):
            return parent
        parent = parent.parent
    return None


def section_title(section: nodes.section) -> str:
    """Return the text of a section's first ``nodes.title`` child, or ``""``."""
    title = section.next_node(nodes.title)
    return title.astext() if title is not None else ""


def section_id(section: nodes.section) -> str:
    """Return the section's first id, or ``""`` when it has none."""
    ids = section.get("ids", [])
    return ids[0] if ids else ""


def visible_text(item: SliceItem) -> str:
    """Return the visible text of a SliceItem's resolved ``:doc:`` reference."""

    from docutils import nodes as _nodes

    for child in item.children:
        if isinstance(child, _nodes.reference):
            return child.astext()
    return ""


def accessible_name(item: SliceItem, slice_node: Slice, domain: Domain) -> str:
    """Return the accessible name of a marked item."""

    parts: list[str] = [visible_text(item)]
    if item.get("mark_slice"):
        parts.append(slice_node["name"])
    if item.get("mark_domain"):
        parts.append(domain["name"])
    return " ".join(parts)


def check_ambiguity(doctree) -> None:
    """Warn at each occurrence of repeated visible text with identical accessible names."""

    # Group items by visible text across the whole page, recording the
    # accessible name and the slice/domain each came from so the
    # same-slice special case can be detected.
    occurrences: dict[str, list[tuple[SliceItem, Slice, Domain]]] = {}
    for domain in doctree.findall(Domain):
        if domain.get("suppress_warnings", False):
            continue
        for slice_node in domain.findall(Slice):
            for item in slice_node.children:
                if not isinstance(item, SliceItem):
                    continue
                text = visible_text(item)
                if not text:
                    continue
                occurrences.setdefault(text, []).append((item, slice_node, domain))

    for text, group in occurrences.items():
        if len(group) < 2:
            continue

        # Same-slice special case: any two items in the same slice
        # instance with the same visible text always warn.
        for i, (item_i, slice_i, _dom_i) in enumerate(group):
            for j, (item_j, slice_j, _dom_j) in enumerate(group):
                if j <= i:
                    continue
                if slice_i is slice_j:
                    _logger.warning(
                        "ambiguous link text %r: repeated within slice %r",
                        text,
                        slice_i["name"],
                    )
                    continue
                # Cross-slice: warn unless accessible names differ.
                name_i = accessible_name(item_i, slice_i, _dom_i)
                name_j = accessible_name(item_j, slice_j, _dom_j)
                if name_i == name_j:
                    _logger.warning(
                        "ambiguous link text %r: identical accessible "
                        "name %r across slices %r and %r",
                        text,
                        name_i,
                        slice_i["name"],
                        slice_j["name"],
                    )


def unique_id(base: str, used: set[str]) -> str:
    """Return ``base`` if unused, else ``base-2``, ``base-3``, ... on clash."""

    candidate = base
    counter = 2
    while candidate in used:
        candidate = f"{base}-{counter}"
        counter += 1
    used.add(candidate)
    return candidate


def resolve_domains(_app, doctree, _docname) -> None:
    """``doctree-resolved`` handler: fill in name/section_id and assign ids."""
    used_ids: set[str] = set()

    # Seed with ids already present on the page (section heading ids,
    # etc.) so generated ids never collide with existing ones.
    for node in doctree.findall(nodes.Element):
        for existing in node.get("ids", []):
            used_ids.add(existing)

    for domain in doctree.findall(Domain):
        section = nearest_section(domain)
        overridden = domain.get("overridden", False)
        if section is not None:
            domain["section_id"] = section_id(section)
            if not overridden:
                domain["name"] = section_title(section)
        else:
            domain["section_id"] = ""
            if not overridden:
                # No name available from anywhere: an unlabelled landmark
                # is worse for screen reader users than no landmark at all,
                # so fail the build rather than degrading to a nameless
                # container.
                _logger.error(
                    "domain directive requires an explicit name argument "
                    "or an enclosing section heading to derive one from"
                )
                continue

        section_slug = domain["section_id"]

        if domain.get("overridden", False):
            name_slug = nodes.make_id(domain["name"])
            domain["domain_span_id"] = unique_id(f"{name_slug}-domain", used_ids)

        for slice_node in domain.findall(Slice):
            slice_slug = nodes.make_id(slice_node["name"])
            if section_slug:
                base = f"{section_slug}-{slice_slug}"
            else:
                base = slice_slug
            slice_node["label_id"] = unique_id(base, used_ids)

            for item in slice_node.children:
                if not isinstance(item, SliceItem):
                    continue
                if not (item.get("mark_slice") or item.get("mark_domain")):
                    continue
                link_text = visible_text(item)
                if not link_text:
                    continue
                link_slug = nodes.make_id(link_text)
                base = f"{slice_node['label_id']}-{link_slug}"
                item["item_id"] = unique_id(base, used_ids)

    check_ambiguity(doctree)
