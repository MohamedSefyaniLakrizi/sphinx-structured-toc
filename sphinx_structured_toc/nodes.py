from docutils import nodes


class Domain(nodes.General, nodes.Element):
    """Outer container for a ``.. domain::`` block."""


class Slice(nodes.General, nodes.Element):
    """A single named slice within a ``Domain``."""


class SliceItem(nodes.General, nodes.TextElement):
    """A single link entry within a ``Slice``."""
