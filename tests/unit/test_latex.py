from __future__ import annotations

from pathlib import Path
from textwrap import dedent
from typing import Any

_DOCS = {
    "models/introduction.rst": "Introduction\n============\n",
}


def build_latex(
    make_app: Any,
    tmp_path: Path,
    rst: str,
    docs: dict[str, str] | None = None,
) -> Any:
    src = tmp_path / "src"
    src.mkdir()
    src.joinpath("conf.py").write_text(
        "extensions = ['sphinx_structured_toc']\n",
        encoding="utf-8",
    )
    src.joinpath("index.rst").write_text(rst, encoding="utf-8")
    for rel_path, content in (docs or {}).items():
        target = src / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    return make_app(srcdir=src, buildername="latex")


def tex_contents(app: Any) -> str:
    tex_files = sorted(Path(app.outdir).glob("*.tex"))
    assert tex_files, "expected at least one .tex file in the latex output"
    return "\n".join(path.read_text(encoding="utf-8") for path in tex_files)


def test_latex_build_succeeds_without_domain(tmp_path, make_app):
    app = build_latex(
        make_app,
        tmp_path,
        dedent("""
            The model layer
            ===============

            Some plain text.
            """),
    )
    app.build()
    assert "Some plain text." in tex_contents(app)


def test_latex_build_succeeds_with_domain_and_slices(tmp_path, make_app):
    app = build_latex(
        make_app,
        tmp_path,
        dedent("""
            The model layer
            ===============

            .. domain::

               .. slice:: Models

                  :doc:`Introduction <models/introduction>`
            """),
        docs=_DOCS,
    )
    app.build()


def test_latex_output_contains_slice_labels_and_items(tmp_path, make_app):
    app = build_latex(
        make_app,
        tmp_path,
        dedent("""
            The model layer
            ===============

            .. domain::

               .. slice:: Models

                  :doc:`Introduction <models/introduction>`
            """),
        docs=_DOCS,
    )
    app.build()
    tex = tex_contents(app)
    assert "Models" in tex
    assert "Introduction" in tex
