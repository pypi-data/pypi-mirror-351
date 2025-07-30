# -*- coding: utf-8 -*-

"""
Publish to Python repository related automation.
"""

import typing as T
import subprocess
import dataclasses
from textwrap import dedent

try:
    from github import (
        Github,
        GithubException,
        Repository,
        GitTag,
        GitRelease,
    )
except ImportError:  # pragma: no cover
    pass

from .vendor.emoji import Emoji
from .vendor.better_pathlib import temp_cwd

from .logger import logger
from .helpers import bump_version, print_command

if T.TYPE_CHECKING:  # pragma: no cover
    from .define import PyWf


@dataclasses.dataclass
class PyWfPublish:  # pragma: no cover
    """
    Namespace class for publishing to Python repository related automation.
    """

    def twine_upload(
        self: "PyWf",
        real_run: bool = True,
        quiet: bool = False,
    ):
        """
        Publish to PyPI repository using
        `twine upload <https://twine.readthedocs.io/en/stable/index.html>`_.
        """
        args = [
            f"{self.path_bin_twine}",
            "upload",
            f"{self.dir_dist}/*",
        ]
        print_command(args)
        if real_run:
            with temp_cwd(self.dir_project_root):
                subprocess.run(args, check=True)

    def poetry_publish(
        self: "PyWf",
        real_run: bool = True,
    ):
        """
        Publish to PyPI repository using
        `poetry publish <https://python-poetry.org/docs/libraries/#publishing-to-pypi>`_.`
        """
        args = [
            f"{self.path_bin_poetry}",
            "publish",
        ]
        print_command(args)
        if real_run:
            with temp_cwd(self.dir_project_root):
                subprocess.run(args, check=True)

    def bump_version(
        self: "PyWf",
        major: bool = False,
        minor: bool = False,
        patch: bool = False,
        minor_start_from: int = 0,
        micro_start_from: int = 0,
        real_run: bool = True,
    ):
        """
        Bump a semantic version. The current version has to be in x.y.z format,
        where x, y, z are integers.

        :param major: bump major version.
        :param minor: bump minor version.
        :param patch: bump patch version.
        :param minor_start_from: if bumping major version, minor start from this number.
        :param micro_start_from: if bumping minor version, micro start from this number.
        """
        new_version = bump_version(
            current_version=self.package_version,
            major=major,
            minor=minor,
            patch=patch,
            minor_start_from=minor_start_from,
            micro_start_from=micro_start_from,
        )

        # update _version.py file
        version_py_content = dedent(
            """
        __version__ = "{}"
    
        # keep this ``if __name__ == "__main__"``, don't delete!
        # this is used by automation script to detect the project version
        if __name__ == "__main__":  # pragma: no cover
            print(__version__)
        """
        ).strip()
        version_py_content = version_py_content.format(new_version)
        if real_run:
            self.path_version_py.write_text(version_py_content)

        # update pyproject.toml file
        if self.path_pyproject_toml.exists():
            if major:
                action = "major"
            elif minor:
                action = "minor"
            elif patch:
                action = "patch"
            else:  # pragma: no cover
                raise NotImplementedError
            with temp_cwd(self.dir_project_root):
                args = [
                    f"{self.path_bin_poetry}",
                    "version",
                    action,
                ]
                print_command(args)
                if real_run:
                    subprocess.run(args, check=True)

    @logger.emoji_block(
        msg="Publish to GitHub Release",
        emoji=Emoji.package,
    )
    def _publish_to_github_release(
        self: "PyWf",
        real_run: bool = True,
    ) -> T.Optional["GitRelease"]:
        """
        Create a GitHub Release using the current version based on main branch.

        :returns: a boolean flag to indicate whether the operation is performed.
        """
        logger.info(f"preview release at {self.github_versioned_release_url}")
        release_name = self.package_version
        repo = self.gh.get_repo(self.github_repo_fullname)

        # Check if release exists
        try:
            repo.get_release(release_name)
            logger.info(f"Release {release_name!r} already exists.")
            return None
        except GithubException as e:
            if e.status == 404:
                pass
            else:
                raise e
        except Exception as e:  # pragma: no cover
            raise e

        # Create Tag if not exists
        try:
            repo.get_git_ref(f"tags/{release_name}")
            logger.info(f"Tag {release_name!r} already exists.")
        except GithubException as e:
            if e.status == 404:
                if real_run:
                    default_branch = repo.default_branch
                    commit = repo.get_branch(default_branch).commit
                    commit_sha = commit.sha
                    tag = repo.create_git_tag(
                        tag=release_name,
                        message=f"Release {release_name}",
                        object=commit_sha,
                        type="commit",
                    )
                    repo.create_git_ref(
                        ref=f"refs/tags/{release_name}",
                        sha=tag.sha,
                    )
            else:  # pragma: no cover
                raise e
        except Exception as e:  # pragma: no cover
            raise e

        # Create Release
        if real_run:
            release = repo.create_git_release(
                tag=release_name,
                name=release_name,
                message=f"Release {release_name}",
            )
            return release
        else:
            return None

    def publish_to_github_release(
        self: "PyWf",
        real_run: bool = True,
        verbose: bool = True,
    ):
        with logger.disabled(not verbose):
            return self._publish_to_github_release(
                real_run=real_run,
            )

    publish_to_github_release.__doc__ = _publish_to_github_release.__doc__
