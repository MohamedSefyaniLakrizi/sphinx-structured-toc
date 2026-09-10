"""Documentation configuration for sphinx-structured-toc."""

from __future__ import annotations

import pathlib
import sys

project_root = pathlib.Path(__file__).parents[1].resolve()
sys.path.insert(0, str(project_root))

project = "sphinx-structured-toc"
author = "sphinx-structured-toc contributors"

extensions = [
    "sphinx_structured_toc",
    # Convert SVG images to PDF for LaTeX/PDF output
    "sphinxcontrib.cairosvgconverter",
]

html_theme = "furo"
html_title = project
