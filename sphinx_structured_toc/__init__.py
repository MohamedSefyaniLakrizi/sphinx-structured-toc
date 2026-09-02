from pathlib import Path

from sphinx.application import Sphinx
from sphinx.util.typing import ExtensionMetadata

from .directives import DomainDirective, SliceDirective
from .html import (
    depart_domain,
    depart_slice,
    depart_slice_item,
    visit_domain,
    visit_slice,
    visit_slice_item,
)
from .nodes import Domain, Slice, SliceItem
from .transforms import resolve_domains

_CSS_DIR = str(Path(__file__).parent)

try:
    from ._version import __version__
except ImportError:  # pragma: no cover
    from importlib.metadata import PackageNotFoundError, version

    try:
        __version__ = version("sphinx-structured-toc")
    except PackageNotFoundError:
        __version__ = "dev"

def visit_transparent(translator: object, node: object) -> None:
    """Render structured TOC nodes transparently for LaTeX output."""


def depart_transparent(translator: object, node: object) -> None:
    """Finish rendering a transparent structured TOC node."""

def setup(app: Sphinx) -> ExtensionMetadata:
    # register various components

    # nodes
    app.add_node(
        Domain,
        html=(visit_domain, depart_domain),
        latex=(visit_transparent, depart_transparent),
    )
    app.add_node(
        Slice,
        html=(visit_slice, depart_slice),
        latex=(visit_transparent, depart_transparent),
    )
    app.add_node(
        SliceItem,
        html=(visit_slice_item, depart_slice_item),
        latex=(visit_transparent, depart_transparent),
    )

    # directives
    app.add_directive("domain", DomainDirective)
    app.add_directive("slice", SliceDirective)

    # transform
    app.connect("doctree-resolved", resolve_domains)

    # static asset shipping
    app.connect("builder-inited", add_static_dir)

    # reference override (decorates <a> emitted for marked slice items)
    app.connect("builder-inited", install_reference_override)

    app.add_css_file("domain-list.css")

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }


def add_static_dir(app: Sphinx) -> None:
    """Add the extension package directory to ``html_static_path``."""

    if _CSS_DIR not in app.config.html_static_path:
        app.config.html_static_path.append(_CSS_DIR)


def install_reference_override(app: Sphinx) -> None:
    """Override ``docutils.nodes.reference`` HTML visitors."""

    from docutils import nodes as docutils_nodes

    from .html import make_reference_visitor

    visit, depart = make_reference_visitor(app)
    app.add_node(
        docutils_nodes.reference,
        html=(visit, depart),
        override=True,
    )


__all__ = ["__version__", "setup"]
