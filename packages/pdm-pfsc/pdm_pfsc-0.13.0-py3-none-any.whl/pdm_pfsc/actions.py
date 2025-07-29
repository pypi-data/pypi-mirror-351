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
from collections.abc import Mapping
from typing import Callable, Generic, Protocol, TypeVar, cast

from .hook import HookGenerator


# Justification: Just a protocol
class _HasAddSubParser(Protocol):  # pylint: disable=R0903
    """"""

    def add_parser(self, name, **kwargs) -> ArgumentParser:
        """

        Parameters
        ----------
        name :

        **kwargs :


        Returns
        -------

        """
        raise NotImplementedError()


class _ArgumentParserFactoryMixin:
    """"""

    name: str
    description: str

    @classmethod
    def _update_command(cls, sub_parser: ArgumentParser) -> None:
        """

        Parameters
        ----------
        sub_parser: ArgumentParser :


        Returns
        -------

        """
        # Justification: Zen of Python: Explicit is better than implicit
        # Must be implemented if necessary
        pass  # pylint: disable=W0107

    @classmethod
    def get_allowed_arguments(cls) -> set[str]:
        """"""
        return set()

    @classmethod
    def create_command(
        cls, sub_parser_collection: _HasAddSubParser, **kwargs
    ) -> ArgumentParser:
        """

        Parameters
        ----------
        sub_parser_collection: _HasAddSubParser :

        **kwargs :


        Returns
        -------

        """
        aliases: list[str] = []

        if "aliases" in vars(cls):
            aliases = list(getattr(cls, "aliases"))

        exit_on_error = True
        if "exit_on_error" in kwargs:
            exit_on_error = bool(kwargs.pop("exit_on_error"))

        parser = sub_parser_collection.add_parser(
            cls.name,
            description=cls.description,
            aliases=aliases,
            exit_on_error=exit_on_error,
        )

        parser.add_argument(
            "--dry-run",
            "-n",
            action="store_true",
            dest="dry_run",
            help="Do not perform any action, just check if it would work.",
        )

        cls._update_command(parser)

        return parser


_TResult = TypeVar("_TResult")


class ActionBase(ABC, Generic[_TResult], _ArgumentParserFactoryMixin):
    """"""

    def __init__(self, **kwargs) -> None:
        # Just to ignore key word arguments
        pass

    @abstractmethod
    def run(self, dry_run: bool = False) -> _TResult:
        """

        Parameters
        ----------
        dry_run: bool :
             (Default value = False)

        Returns
        -------

        """
        raise NotImplementedError()

    @classmethod
    def create_from_command(cls, **kwargs) -> "ActionBase":
        """

        Parameters
        ----------
        **kwargs :


        Returns
        -------

        """
        instance: "ActionBase" = cls(**kwargs)

        return instance


_TContext = TypeVar("_TContext")


class ActionRegistry(ABC, Generic[_TContext]):
    """"""

    def __init__(self) -> None:
        self.__items: dict[str, type[ActionBase]] = {}

    def register(self) -> Callable:
        """"""

        def decorator(clazz: type[ActionBase]):
            """

            Parameters
            ----------
            clazz: type[ActionBase] :


            Returns
            -------

            """
            if not issubclass(clazz, ActionBase):
                raise ValueError(
                    f"{clazz.__name__} is not an sub-type of "
                    f"{ActionBase.__name__}"
                )
            self.__items[clazz.name] = clazz

            return clazz

        return decorator

    def update_parser(self, parser: ArgumentParser) -> None:
        """

        Parameters
        ----------
        parser: ArgumentParser :


        Returns
        -------

        """
        parsers: _HasAddSubParser = parser.add_subparsers(  # type: ignore
            dest="selected_command",
            description="Either the part of the version to bump "
            + "according to PEP 440:"
            + " major.minor.micro, "
            + "or VCS based actions to take.",
            required=True,
        )
        parser.add_help = True
        keys = list(self.__items.keys())
        keys.sort()
        exit_on_error = False
        if "exit_on_error" in vars(parser):
            exit_on_error = getattr(parser, "exit_on_error")

        for key in keys:
            clazz = self.__items[key]
            child_parser: ArgumentParser = clazz.create_command(
                parsers, exit_on_error=exit_on_error
            )
            if issubclass(clazz, HookGenerator):
                hook_generator: type[HookGenerator] = cast(
                    type[HookGenerator], clazz
                )
                for hook_info in hook_generator.generate_hook_infos():
                    hook_info.update_parser(child_parser)

    @property
    def _items(self) -> Mapping[str, type[ActionBase]]:
        return self.__items

    @abstractmethod
    def execute(  # pylint: disable=R0913
        self,
        /,
        args: Namespace,
        context: _TContext,
    ) -> None:
        """

        Parameters
        ----------
        / :

        args: Namespace :

        context: _TContext :


        Returns
        -------

        """
        raise NotImplementedError()
