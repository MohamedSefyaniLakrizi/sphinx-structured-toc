from __future__ import annotations

import subprocess
from pathlib import Path

import pytest


@pytest.mark.slow
def test_package_docs_build(tmp_path: Path):
    project_root = Path(__file__).parents[2]
    build_dir = tmp_path / "html"

    subprocess.run(
        [
            "sphinx-build",
            "-b",
            "html",
            "-W",
            str(project_root / "docs"),
            str(build_dir),
        ],
        check=True,
    )
