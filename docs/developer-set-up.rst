Development set-up
======================

Having cloned the repository, build with ``make install`` (at the root; there's a completely unrelated ``Makefile`` for the ``docs`` directory).

``make setup-tests`` is a lighter-weight alternative if you want to run tests but need less of the tooling.

There's some complexity in this; it will opt for ``homebrew`` or ``apt`` to install components.


Testing
-------

``make test`` runs ``uv run pytest``. There's a slow test that can be skipped: ``make test-fast``.

Use ``make test`` to run rests, and ``make test-coverage`` for a coverage report.


Running the documentation
-------------------------

In ``docs``: ``make run`` to launch the documentation site on port 8000.

Changes to the extension code will be picked up live.
