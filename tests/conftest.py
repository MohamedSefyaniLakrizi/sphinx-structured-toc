from __future__ import annotations

import logging
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
import sphinx.util.logging as sphinx_logging

pytest_plugins = "sphinx.testing.fixtures"


@pytest.fixture
def build_app(tmp_path: Path, make_app: Callable[..., Any]) -> Callable[..., Any]:
    """Build an in-memory Sphinx project from rST source.

    Returns a callable accepting the rST source of ``index.rst`` and
    returning a built Sphinx test application. The project loads only
    ``sphinx_structured_toc``.
    """

    def build(
        rst: str,
        *,
        docs: dict[str, str] | None = None,
    ) -> Any:
        src = tmp_path / "src"
        src.mkdir()
        # ``keep_warnings = True`` keeps ``system_message`` nodes in the
        # built doctree so error-detection tests can find them via
        # ``findall(nodes.system_message)``. Sphinx strips them by default.
        src.joinpath("conf.py").write_text(
            "extensions = ['sphinx_structured_toc']\n" "keep_warnings = True\n",
            encoding="utf-8",
        )
        src.joinpath("index.rst").write_text(rst, encoding="utf-8")
        for rel_path, content in (docs or {}).items():
            target = src / rel_path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
        app = make_app(srcdir=src, buildername="html")

        # doctree-resolved fires during build with a doctree that is then
        # discarded; the pickled doctree that env.get_doctree() returns was
        # saved before the transform ran. Capture each document's transformed
        # doctree so tests can inspect post-transform node attributes.
        app._transformed_doctrees = {}  # type: ignore[attr-defined]

        def capture(_app, doctree, docname) -> None:
            app._transformed_doctrees[docname] = doctree  # type: ignore[attr-defined]

        app.connect("doctree-resolved", capture)

        # Sphinx's namespace logger (``sphinx``) has ``propagate = False``
        # after ``make_app``, so pytest's ``caplog`` (root-logger based)
        # does not see its records. Attach a handler that collects warning
        # records onto the app so tests can inspect them.
        app._warning_records = []  # type: ignore[attr-defined]

        class _Collector(logging.Handler):
            def emit(self, record: logging.LogRecord) -> None:
                app._warning_records.append(record)  # type: ignore[attr-defined]

        sphinx_logger = logging.getLogger(sphinx_logging.NAMESPACE)
        handler = _Collector(level=logging.WARNING)
        sphinx_logger.addHandler(handler)
        try:
            app.build()
        finally:
            sphinx_logger.removeHandler(handler)

        # Cache the rendered HTML for the index page so HTML-level tests
        # can use BeautifulSoup without re-reading from disk.
        index_html = Path(app.outdir) / "index.html"
        app._index_html = index_html.read_text(encoding="utf-8")  # type: ignore[attr-defined]
        return app

    return build
