#
# SPDX-License-Identifier: MIT
#
# Copyright (c) 2021-2024 Carsten Igel.
#
# This file is part of pdm-pfsc
# (see https://github.com/carstencodes/pdm-pfsc).
#
# This file is published using the MIT license.
# Refer to LICENSE for more information
#
""""""


from os import environ, pathsep
from pathlib import Path
from subprocess import run as stdlib_run_process
from shutil import which as shutil_which
from sys import platform
from typing import Optional, Protocol, Union, cast

from pdm.project import Project
from pdm.environments import BaseEnvironment

from .logging import logger


class _CompletedProcessLike(Protocol):
    """"""

    @property
    def returncode(self) -> int:
        """"""
        raise NotImplementedError()

    @property
    def stdout(self) -> str:
        """"""
        raise NotImplementedError()

    @property
    def stderr(self) -> str:
        """"""
        raise NotImplementedError()


class _ProcessRunningCallable(Protocol):  # pylint: disable=R0903
    """"""

    def __call__(
        self,
        cmd: list[str],
        *,
        check: bool,
        capture_output: bool,
        cwd: Optional[Union[str, Path]],
        encoding: str = "utf-8",
        env: "Optional[dict[str, str]]" = None,
    ) -> _CompletedProcessLike:
        raise NotImplementedError()


class ProcessRunner:
    """"""

    run_process: Optional[_ProcessRunningCallable] = None

    def _run_process(
        self,
        cmd: list[str],
        *,
        check: bool,
        capture_output: bool,
        cwd: Optional[Union[str, Path]],
        encoding: str = "utf-8",
        env: "Optional[dict[str, str]]" = None,
    ) -> _CompletedProcessLike:
        """

        Parameters
        ----------
        cmd: list[str] :

        * :

        check: bool :

        capture_output: bool :

        cwd: Optional[Union[str, Path]] :

        encoding: str :
             (Default value = "utf-8")

        Returns
        -------

        """
        if self.run_process is not None:
            run_proc: _ProcessRunningCallable = cast(
                _ProcessRunningCallable, self.run_process
            )
            return run_proc(
                cmd,
                check=check,
                capture_output=capture_output,
                cwd=cwd,
                encoding=encoding,
                env=env,
            )

        return stdlib_run_process(
            cmd,
            check=check,
            capture_output=capture_output,
            cwd=cwd,
            encoding=encoding,
            env=env,
        )


class CliRunnerMixin(ProcessRunner):
    """"""

    def _which(
        self, exec_name: str, extension: Optional[str] = None, project: Optional[Project] = None
    ) -> Optional[Path]:
        """

        Parameters
        ----------
        exec_name: str :

        extension: Optional[str] :
             (Default value = None)

        project: Optional[Project] :
             (Default value = None)

        Returns
        -------

        """
        file_path: "Optional[Path]" = None
        if extension is None:
            if project is not None:
                project_env = project.environment
                found_path = project_env.which(exec_name)
            else:
                found_path = shutil_which(exec_name)

            if found_path is not None:
                return Path(found_path)

        search_path = environ["PATH"]
        logger.debug(
            "Searching for executable '%s' using search path '%s'",
            exec_name,
            search_path,
        )
        if search_path is None or len(search_path) == 0:
            return None

        extension = ".exe" if extension is None and platform == "win32" else ""
        executable_full_name = exec_name + extension
        paths = search_path.split(pathsep)
        for path in [Path(p) for p in paths]:
            logger.debug(
                "Searching for '%s' in '%s'", executable_full_name, path
            )
            file_path = path / executable_full_name
            if file_path.is_file():
                logger.debug("Found %s", file_path)
                return file_path

        logger.debug("Could not find %s", executable_full_name)
        return None

    def run(
        self,
        /,
        executable: Path,
        args: tuple[str, ...],
        *,
        raise_on_exit: bool = False,
        cwd: Optional[Path] = None,
        env: Optional[dict[str, str]] = None,
    ) -> tuple[int, str, str]:
        """

        Parameters
        ----------
        / :

        executable: Path :

        args: tuple[str, ...] :

        * :

        raise_on_exit: bool :
             (Default value = False)
        cwd: Optional[Path] :
             (Default value = None)

        Returns
        -------

        """
        cmd = []
        cmd.append(str(executable))
        for arg in args:
            cmd.append(arg)

        logger.debug(
            "Running command '%s' with args [%s]",
            str(executable),
            args,
        )

        completed: _CompletedProcessLike = self._run_process(
            cmd,
            check=False,
            capture_output=True,
            cwd=cwd,
            encoding="utf-8",
            env=env,
        )

        logger.debug("Process exited with code %d", completed.returncode)
        logger.debug(
            "Process wrote the following to stdout: \n%s", completed.stdout
        )
        logger.debug(
            "Process wrote the following to stderr: \n%s", completed.stderr
        )

        if raise_on_exit and completed.returncode != 0:
            raise SystemError(
                completed.returncode, completed.stdout, completed.stderr
            )

        return (
            completed.returncode,
            completed.stdout,
            completed.stderr,
        )

