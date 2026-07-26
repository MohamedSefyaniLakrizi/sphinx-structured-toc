import pathlib
import sys

project_dir = pathlib.Path(__file__).parents[1].resolve()
sys.path.insert(0, str(project_dir.absolute()))

project = "Mockumentation"
author = "Tester"

html_title = project
html_theme = "furo"

extensions = [
    "sphinx_structured_toc",
]
