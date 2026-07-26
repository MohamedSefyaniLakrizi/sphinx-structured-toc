"""Documentation configuration for sphinx-structured-toc."""

from __future__ import annotations

import pathlib
import sys

project_root = pathlib.Path(__file__).parents[1].resolve()
sys.path.insert(0, str(project_root))

project = "sphinx-structured-toc"
author = "sphinx-structured-toc contributors"

extensions = ["sphinx_structured_toc"]

html_theme = "furo"
html_title = project
