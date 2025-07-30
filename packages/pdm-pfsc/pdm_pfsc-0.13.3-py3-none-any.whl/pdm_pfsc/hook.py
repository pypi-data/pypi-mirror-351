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

from abc import ABC, abstractmethod
from argparse import ArgumentParser, Namespace
from collections.abc import Generator, Iterable
from dataclasses import dataclass, field
from typing import Generic, Protocol, TypeVar, runtime_checkable

from .logging import traced_function

_TPreHookContext = TypeVar("_TPreHookContext")
_TPostHookContext = TypeVar("_TPostHookContext")


class HookBase(ABC, Generic[_TPreHookContext, _TPostHookContext]):
    """"""

    @abstractmethod
    @traced_function
    def pre_action_hook(
        self, context: _TPreHookContext, args: Namespace
    ) -> None:
        """

        Parameters
        ----------
            context :

            args :


        Returns
        -------

        """
        raise NotImplementedError()

    @abstractmethod
    @traced_function
    def post_action_hook(
        self, context: _TPostHookContext, args: Namespace
    ) -> None:
        """

        Parameters
        ----------
            context :

            args :

        Returns
        -------

        """
        raise NotImplementedError()

    @classmethod
    @traced_function
    # Justification: Protocol definition
    # pylint: disable=W0613
    def configure(cls, parser: ArgumentParser) -> None:
        """

        Parameters
        ----------
            parser:

        Returns
        -------

        """
        return  # NOSONAR


@dataclass(frozen=True)
class HookInfo:
    """"""

    hook_type: type[HookBase] = field()

    @traced_function
    def update_parser(self, parser: ArgumentParser) -> None:
        """

        Parameters:
        -----------
            parser: ArgumentParser :

        Returns:
        --------
        """
        self.hook_type.configure(parser)

    @traced_function
    def create_hook(self) -> HookBase:
        """

        Returns:
        --------
        """
        return self.hook_type()


@runtime_checkable
class HookGenerator(Protocol):  # pylint: disable=R0903
    # Justification: Just a protocol
    """"""

    @classmethod
    def generate_hook_infos(cls) -> Generator[HookInfo, None, None]:
        """

        Returns:
        --------

        """
        raise NotImplementedError()


_THookContext = TypeVar("_THookContext")


class HookExecutorBase(ABC, Generic[_THookContext]):
    """"""

    def __init__(self) -> None:
        """

        Parameters:
        -----------
            hunk_source: HunkSource :
            vcs_provider: VcsProvider :

        Returns:
        --------

        """
        self.__hooks: list[HookBase] = []

    @traced_function
    @abstractmethod
    def run(
        self,
        context: _THookContext,
        args: Namespace,
        dry_run: bool = False,
    ) -> None:
        """

        Parameters:
        -----------
            context: _THookContext :
            args: Namespace :
            dry_run: bool :

        Returns:
        --------

        """
        raise NotImplementedError()

    @property
    def _hooks(self) -> Iterable[HookBase]:
        """"""
        return self.__hooks

    @traced_function
    def register(self, hook: HookBase) -> None:
        """

        Parameters:
        -----------
            hook: Hook :

        Returns:
        --------

        """
        self.__hooks.append(hook)
