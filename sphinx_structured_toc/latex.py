from __future__ import annotations

from sphinx.writers.latex import LaTeXTranslator

from .nodes import Domain, Slice, SliceItem


def visit_domain(_translator: LaTeXTranslator, _node: Domain) -> None:
    return None


def depart_domain(_translator: LaTeXTranslator, _node: Domain) -> None:
    return None


def visit_slice(translator: LaTeXTranslator, node: Slice) -> None:
    name = translator.encode(node.get("name", ""))
    translator.body.append(f"\n\n\\textbf{{{name}:}}\n\n\\begin{{itemize}}\n")


def depart_slice(translator: LaTeXTranslator, _node: Slice) -> None:
    translator.body.append("\\end{itemize}\n")


def visit_slice_item(translator: LaTeXTranslator, _node: SliceItem) -> None:
    translator.body.append("\\item ")


def depart_slice_item(translator: LaTeXTranslator, _node: SliceItem) -> None:
    translator.body.append("\n")
