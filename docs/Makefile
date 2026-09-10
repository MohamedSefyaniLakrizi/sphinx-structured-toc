# Minimal makefile for Sphinx documentation
#
# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SPHINXAUTOBUILD ?= sphinx-autobuild
SOURCEDIR     = .
BUILDDIR      = _build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile livehtml pdf

# Catch-all target: route all unknown targets through Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

run:
	@$(SPHINXAUTOBUILD) "$(SOURCEDIR)" "$(BUILDDIR)/html" $(SPHINXOPTS) $(O)

# Build a PDF with the standard LaTeX toolchain (latexmk + xelatex, as used
# by the sphinx-docs-starter-pack). The finished PDF is moved to $(BUILDDIR).
# `-Q` quiets Sphinx; LATEXMKOPTS quiets the latexmk/xelatex passes (it
# propagates via the environment to the Makefile that `-M latexpdf` runs).
pdf:
	@LATEXMKOPTS=-silent $(SPHINXBUILD) -M latexpdf "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) -Q $(O)
	@find "$(BUILDDIR)/latex" -name '*.pdf' -exec mv {} "$(BUILDDIR)"/ \;
	@echo "Output can be found in ./$(BUILDDIR)"
