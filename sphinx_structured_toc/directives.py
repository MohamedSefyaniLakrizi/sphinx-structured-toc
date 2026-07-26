from __future__ import annotations

from typing import ClassVar

from docutils import nodes
from docutils.parsers.rst.directives import flag
from sphinx.addnodes import pending_xref
from sphinx.util.docutils import SphinxDirective
from sphinx.util.typing import OptionSpec

from .nodes import Domain, Slice, SliceItem


class DomainDirective(SphinxDirective):
    """Outer directive: ``.. domain::`` with an optional name argument."""

    optional_arguments = 1
    final_argument_whitespace = True  # allow whitespace in the name
    has_content = True  # has content that will need to be parsed
    option_spec: ClassVar[OptionSpec] = {"suppress-warnings": flag}

    def run(self) -> list[nodes.Node]:
        """Parse nested content and validate that only Slice children result."""
        overridden = bool(self.arguments)

        # if not supplied the name will need to be resolved later
        name = self.arguments[0] if overridden else ""

        nested = nodes.Element()
        # parse the inner content
        self.state.nested_parse(self.content, self.content_offset, nested)

        # if slice parsing fails, forward the first error
        messages = [c for c in nested.children if isinstance(c, nodes.system_message)]
        if messages:
            return [messages[0]]

        slices = [child for child in nested.children if isinstance(child, Slice)]
        non_slice = [child for child in nested.children if not isinstance(child, Slice)]

        if non_slice:
            return [self.emit_error("domain may only contain 'slice' blocks")]

        if not slices:
            return [self.emit_error("domain must contain at least one slice")]

        # create the node, pass its attributes, add the slices
        domain_node = Domain()
        if overridden:
            domain_node["name"] = name
        domain_node["overridden"] = overridden
        if "suppress-warnings" in self.options:
            domain_node["suppress_warnings"] = True
        domain_node.extend(slices)
        return [domain_node]

    def emit_error(self, msg: str) -> nodes.system_message:
        return self.state_machine.reporter.error(
            msg,
            nodes.literal_block(self.block_text, self.block_text),
            line=self.lineno,
        )


class SliceDirective(SphinxDirective):
    """Inner directive: ``.. slice:: <name>`` with item lines as content."""

    required_arguments = 1
    final_argument_whitespace = True
    has_content = True
    option_spec: dict = {}

    def run(self) -> list[nodes.Node]:
        """Build a Slice node from the directive content."""

        name = self.arguments[0]

        slice_node = Slice()
        slice_node["name"] = name

        # adds parsed lines into the slice_node
        for offset, line in enumerate(self.content):
            if not line.strip():
                continue
            lineno = self.lineno + self.content_offset + offset
            item = self.parse_item(line, lineno)
            if isinstance(item, nodes.system_message):
                return [item]
            slice_node.append(item)

        if not slice_node.children:
            return [self.emit_error(f"slice '{name}' has no items")]

        return [slice_node]

    def parse_item(self, line: str, lineno: int) -> nodes.Node:
        role_text, mark_slice, mark_domain, err = self.parse_line(line)
        if err is not None:
            return self.emit_error(err, lineno=lineno)

        nodes_list, messages = self.state.inline_text(role_text, lineno)

        if messages:
            return self.emit_error(
                f"slice item must be a :doc: role: {line!r}",
                lineno=lineno,
            )

        # each line should contain one and only cross-reference and nothing else
        xrefs = [n for n in nodes_list if isinstance(n, pending_xref)]
        non_xrefs = [
            n
            for n in nodes_list
            if not isinstance(n, pending_xref)
            and not (isinstance(n, nodes.Text) and not str(n).strip())
        ]

        if len(xrefs) != 1 or non_xrefs:
            return self.emit_error(
                f"slice item must be a :doc: role: {line!r}",
                lineno=lineno,
            )

        xref = xrefs[0]
        if xref.get("refdomain") != "std" or xref.get("reftype") != "doc":
            return self.emit_error(
                f"slice item must be a :doc: role: {line!r}",
                lineno=lineno,
            )

        # create a SliceItem from the line
        item = SliceItem(rawsource=line)
        if mark_slice:
            item["mark_slice"] = True
        if mark_domain:
            item["mark_domain"] = True
        item += xref
        return item

    def parse_line(self, line: str) -> tuple[str, bool, bool, str | None]:
        """Parses a line into its components"""

        mark_slice = mark_domain = False
        text = line.rstrip()
        parts = text.split()

        while parts and parts[-1] in ("slice", "domain"):
            marker = parts.pop()
            if marker == "slice" and not mark_slice:
                mark_slice = True
            elif marker == "domain" and not mark_domain:
                mark_domain = True
            else:
                parts.append(marker)  # duplicate, hand back to error path
                break

        if parts and parts[-1] in ("slice", "domain"):
            return (
                line,
                False,
                False,
                f"unrecognised trailing token in slice item: {line!r}",
            )

        role_text = " ".join(parts)
        return role_text, mark_slice, mark_domain, None

    def emit_error(self, msg: str, lineno: int | None = None) -> nodes.system_message:
        return self.state_machine.reporter.error(
            msg,
            nodes.literal_block(self.block_text, self.block_text),
            line=lineno if lineno is not None else self.lineno,
        )
