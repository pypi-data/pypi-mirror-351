# -*- coding: utf-8 -*-

"""
Document Build and Deploy Automation for Python Projects.
"""

import typing as T
import shutil
import dataclasses
import subprocess

from .vendor.emoji import Emoji
from .vendor.os_platform import OPEN_COMMAND

from .logger import logger
from .helpers import print_command

if T.TYPE_CHECKING:  # pragma: no cover
    from .define import PyWf


@dataclasses.dataclass
class PyWfDocs:
    """
    Namespace class for document related automation.
    """

    @logger.emoji_block(
        msg="Build Documentation Site Locally",
        emoji=Emoji.doc,
    )
    def _build_doc(
        self: "PyWf",
        real_run: bool = True,
        quiet: bool = False,
    ):
        """
        Use sphinx doc to build documentation site locally. It set the
        necessary environment variables so that the ``make html`` command
        can build the HTML successfully.

        Run:

        .. code-block:: bash

            sphinx-build -M html docs/source docs/build
        """
        if real_run:
            shutil.rmtree(
                f"{self.dir_sphinx_doc_build}",
                ignore_errors=True,
            )
            shutil.rmtree(
                f"{self.dir_sphinx_doc_source_python_lib}",
                ignore_errors=True,
            )

        args = [
            f"{self.path_venv_bin_sphinx_build}",
            "-M",
            "html",
            f"{self.dir_sphinx_doc_source}",
            f"{self.dir_sphinx_doc_build}",
        ]
        self.run_command(args, real_run)

    def build_doc(
        self: "PyWf",
        real_run: bool = True,
        verbose: bool = True,
    ):  # pragma: no cover
        with logger.disabled(not verbose):
            return self._build_doc(
                real_run=real_run,
                quiet=not verbose,
            )

    build_doc.__doc__ = _build_doc.__doc__

    @logger.emoji_block(
        msg="View Documentation Site Locally",
        emoji=Emoji.doc,
    )
    def _view_doc(
        self: "PyWf",
        real_run: bool = True,
        quiet: bool = False,
    ):
        """
        View documentation site built locally in web browser.

        It is usually at the ``${dir_project_root}/build/html/index.html``

        Run:

        .. code-block:: bash

            # For MacOS / Linux
            open build/html/index.html
            # For Windows
            start build/html/index.html
        """
        args = [OPEN_COMMAND, f"{self.path_sphinx_doc_build_index_html}"]
        self.run_command(args, real_run)

    def view_doc(
        self: "PyWf",
        real_run: bool = True,
        verbose: bool = True,
    ):  # pragma: no cover
        with logger.disabled(not verbose):
            return self._view_doc(
                real_run=real_run,
                quiet=not verbose,
            )

    view_doc.__doc__ = _view_doc.__doc__

    @logger.emoji_block(
        msg="Convert Jupyter Notebook to Markdown",
        emoji=Emoji.doc,
    )
    def _notebook_to_markdown(
        self: "PyWf",
        real_run: bool = True,
    ):
        """
        Convert Jupyter notebooks to Markdown files so they can be
        more efficiently included in the AI knowledge base.
        """
        for path_notebook in self.dir_sphinx_doc_source.glob("**/*.ipynb"):
            if ".ipynb_checkpoints" in str(path_notebook):  # pragma: no cover
                continue
            path_markdown = path_notebook.parent / "index.md"
            args = [
                f"{self.path_venv_bin_bin_jupyter}",
                "nbconvert",
                "--to",
                "markdown",
                str(path_notebook),
                "--output",
                str(path_markdown),
            ]
            self.run_command(args, real_run)

    def notebook_to_markdown(
        self: "PyWf",
        real_run: bool = True,
        verbose: bool = True,
    ):
        with logger.disabled(not verbose):
            return self._notebook_to_markdown(
                real_run=real_run,
            )

    notebook_to_markdown.__doc__ = _notebook_to_markdown.__doc__
