==================================================
darca-file-utils - Robust File & Directory Utils
==================================================

**darca-file-utils** is a Python utility library providing robust, reusable helpers for file and directory manipulation. It includes safe wrappers for common operations like reading, writing, copying, moving, renaming, and deleting files and directories, with rich exception handling and structured logging using the `darca` framework.

Features
--------

- ✅ File utilities: check, read, write, remove, rename, move, and copy
- 📁 Directory utilities: create, list, move, rename, remove, and copy
- 🚨 Structured error handling via `DarcaException`
- 🧪 100% test coverage with `pytest`, `coverage`, and parallel test execution
- 🧹 Integrated pre-commit hooks for consistent code quality
- 📦 Isolated virtual environment and Poetry setup

Installation
------------

Clone the repository and install dependencies using the Makefile:

.. code-block:: bash

    make install

This will set up Poetry in an isolated virtual environment at ``/tmp/darca-log-venv``.

Quickstart
----------

.. code-block:: python

    from darca_file_utils.file_utils import FileUtils
    from darca_file_utils.directory_utils import DirectoryUtils

    FileUtils.write_file("example.txt", "Hello world!")
    print(FileUtils.read_file("example.txt"))

    DirectoryUtils.create_directory("test_folder")

Running Tests
-------------

.. code-block:: bash

    make test

- Generates full coverage reports in terminal, HTML, and JSON.
- Creates a coverage badge (``coverage.svg``) saved to ``docs/source/_static``.

Check Everything
----------------

Run all checks before committing:

.. code-block:: bash

    make check

This runs formatting, pre-commit, and tests in sequence.

Documentation
-------------

To build the Sphinx documentation locally:

.. code-block:: bash

    make docs

Output is generated in ``docs/build/html``.

Continuous Integration
----------------------

GitHub Actions uses:

.. code-block:: bash

    make ci

This target is optimized for CI/CD environments and runs pre-commit, tests, and docs builds.

License
-------

MIT License. See LICENSE for details.

Author
------

Roel Kist
