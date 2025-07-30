#
# SPDX-License-Identifier: MIT
#
# Copyright (c) 2021-2025 Carsten Igel.
#
# This file is part of pdm-pfsc
# (see https://github.com/carstencodes/pdm-pfsc).
#
# This file is published using the MIT license.
# Refer to LICENSE for more information
#
""""""
import sys
from abc import ABC, abstractmethod
from collections import ChainMap
from collections.abc import Iterable, Mapping
from dataclasses import fields
from enum import Enum, IntEnum, auto
from functools import cached_property
from pathlib import Path
from types import SimpleNamespace
from typing import (
    Any,
    Final,
    Generic,
    Optional,
    OrderedDict,
    Protocol,
    TypeVar,
    cast,
)

from pdm.project.config import ConfigItem
from pyproject_metadata import StandardMetadata

from .logging import logger, traced_function

if sys.version_info >= (3, 11, 0):
    # suspicious mypy behavior
    from tomllib import load as load_toml  # type: ignore
else:
    # Python 3.11 -> mypy will not recognize this
    from tomli import load as load_toml  # type: ignore


class ConfigMapping(dict[str, Any]):
    """"""

    @staticmethod
    def _create_from_chain_map(chain_map: ChainMap) -> "ConfigMapping":
        dict_from_chain_map = {
            key: chain_map[key] for key in list(chain_map) if key in chain_map
        }

        return ConfigMapping(dict_from_chain_map)

    @traced_function
    def get_config_value(
        self,
        *keys: str,
        default_value: Optional[Any] = None,
        store_default: bool = False,
        readonly: bool = True,
    ) -> Optional[Any]:
        """

        Parameters
        ----------
        *keys: str :

        default_value: Optional[Any] :
             (Default value = None)

        store_default: bool:
            (Default value = False)

        readonly: bool:
            (Default value = True)

        Returns
        -------

        """
        key: str = ".".join(keys)
        logger.debug("Searching for '%s' in configuration", key)
        logger.debug("Configuration is set to: \n%s", self)

        front: str
        config: ConfigMapping = self
        if len(keys) > 1:
            front = keys[0]
            if front in config.keys():
                logger.debug("Found configuration section %s", front)
                cfg = ConfigMapping(cast(dict[str, Any], config[front]))
                if not readonly:
                    config[front] = cfg
                return cfg.get_config_value(
                    *tuple(keys[1:]),
                    default_value=default_value,
                    store_default=store_default,
                    readonly=readonly,
                )

            logger.debug("Could not find configuration section %s.", front)
            if not readonly and store_default:
                config[front] = default_value
            return default_value

        front = keys[0]

        is_default: bool = front not in config.keys()
        result = default_value if is_default else config[front]
        logger.debug("Found value at '%s' is: %s", key, result)

        if ConfigMapping.__is_primitive(result):
            if not readonly and is_default and store_default:
                config[front] = result
            return result

        result = ConfigMapping(cast(dict[str, Any], result))
        if not readonly:
            config[front] = result

        return result

    @staticmethod
    def __is_primitive(value: Any) -> bool:
        return isinstance(value, (bool, str, int, float, type(None)))

    @traced_function
    def set_config_value(self, value: Any, *keys: str) -> None:
        """

        Parameters
        ----------
        value: Any :

        *keys: str :


        Returns
        -------

        """
        front: str

        key: str = ".".join(keys)
        logger.debug("Setting '%s' to '%s'", key, value)

        config = self
        while len(keys) > 1:
            front = keys[0]
            if front not in config.keys():
                logger.debug(
                    "Key '%s' was not found. Adding empty configuration", front
                )
                config[front] = {}
            config = config[front]
            keys = tuple(keys[1:])

        front = keys[0]
        config[front] = value


# Justification: Minimal protocol
class ConfigHolder(Protocol):  # pylint: disable=R0903
    """"""

    root: Path
    PYPROJECT_FILENAME: str

    @property
    def config(self) -> Mapping[str, Any]:
        """"""
        # Method empty: Only a protocol stub
        raise NotImplementedError()


class _StringEnum(str, Enum):
    """"""

    # Justification: Zen of python: Explicit is better than implicit
    pass  # pylint: disable=W0107


class ConfigSection(IntEnum):
    """"""

    ROOT = auto()
    METADATA = auto()
    PLUGIN_CONFIG = auto()
    BUILD_SYSTEM = auto()
    TOOL_CONFIG = auto()
    PLUGINS = auto()


class Config(Protocol):  # pylint: disable=R0903
    """"""

    @cached_property
    @traced_function
    def pyproject_file(self) -> Path:
        """"""
        raise NotImplementedError()


class ConfigAccessor(ABC):
    """"""

    def __init__(self, config: Config, cfg_holder: ConfigHolder) -> None:
        self.__config = config
        self.__mapping = ConfigMapping._create_from_chain_map(cfg_holder.config)

    def get_config_section_path(
        self, section: ConfigSection
    ) -> tuple[str, ...]:
        """"""
        section_key: tuple[str, ...] = tuple()
        if section in (
            ConfigSection.TOOL_CONFIG,
            ConfigSection.PLUGIN_CONFIG,
        ):
            sk: list[str] = ["tool", "pdm"]
            if ConfigSection.PLUGIN_CONFIG == section:
                logger.warning("ConfigSection '%s' is deprecated", section)
                sk.extend(self.plugin_config_name)
            section_key = tuple(sk)
        elif ConfigSection.PLUGINS == section:
            keys: list[str] = ["plugin"]
            keys.extend(self.plugin_config_name)
            section_key = tuple(keys)
        elif ConfigSection.BUILD_SYSTEM == section:
            section_key = ("build-system",)
        elif ConfigSection.METADATA == section:
            section_key = ("project",)

        return section_key

    @property
    @abstractmethod
    def plugin_config_name(self) -> Iterable[str]:
        """"""
        raise NotImplementedError()

    @property
    def pyproject_file(self) -> Path:
        """"""
        return self.__config.pyproject_file

    @traced_function
    def get_config_value(self, *keys: tuple[str, ...]) -> Optional[Any]:
        """

        Parameters
        ----------
        *keys: tuple[str, ...] :


        Returns
        -------

        """
        return self.__mapping.get_config_value(*keys)

    @traced_function
    def get_config_or_pyproject_value(
        self, *keys: tuple[str, ...]
    ) -> Optional[Any]:
        """

        Parameters
        ----------
        *keys: tuple[str, ...] :


        Returns
        -------

        """
        pdm_config: ConfigMapping = self.__mapping
        project_config: ConfigMapping = self.get_pyproject_config(
            ConfigSection.PLUGIN_CONFIG
        )

        return pdm_config.get_config_value(
            *keys
        ) or project_config.get_config_value(*keys)

    @traced_function
    def get_pyproject_config(self, section: ConfigSection) -> ConfigMapping:
        """

        Parameters
        ----------
        section: _ConfigSection :


        Returns
        -------

        """
        project_data: ConfigMapping = self._read_config()
        section_key: Iterable[str]
        if ConfigSection.ROOT == section:
            return project_data or ConfigMapping({})

        section_key = self.get_config_section_path(section)
        data = project_data.get_config_value(
            *section_key, default_value=ConfigMapping({})
        )

        return cast(ConfigMapping, data)

    @traced_function
    def _read_config(self) -> ConfigMapping:
        """"""
        project_file = self.pyproject_file
        with open(project_file, "rb") as file_pointer:
            return ConfigMapping(load_toml(file_pointer))

    @traced_function
    def get_pyproject_metadata(self, *keys: str) -> Optional[Any]:
        """

        Parameters
        ----------
        *keys: tuple[str, ...] :


        Returns
        -------

        """
        config: ConfigMapping = self.get_pyproject_config(
            ConfigSection.METADATA
        )
        return config.get_config_value(*keys)

    @traced_function
    def get_pyproject_tool_config(self, *keys: str) -> Optional[Any]:
        """

        Parameters
        ----------
        *keys: tuple[str, ...] :


        Returns
        -------

        """
        config: ConfigMapping = self.get_pyproject_config(
            ConfigSection.TOOL_CONFIG
        )
        return config.get_config_value(*keys)

    @cached_property
    @traced_function
    def meta_data(self) -> StandardMetadata:
        """"""
        data: ConfigMapping = self.get_pyproject_config(ConfigSection.ROOT)
        meta: StandardMetadata = StandardMetadata.from_pyproject(data)
        return meta


class _SupportsAddConfig(Protocol):  # noqa: R0903
    """"""
    def add_config(self, name: str, item: "ConfigItem") -> None: ...
    """"""


class ConfigItems(OrderedDict):
    """"""

    __allowed_values = [f.name for f in fields(ConfigItem)]

    def __init__(self, accessor: "ConfigAccessor"):
        self.__accessor = accessor

    def add_config_value(self, name: str, **kwargs: Any) -> None:
        """"""
        use_env_var = kwargs.pop("use_env_var", False)
        if use_env_var:
            kwargs["env_var"] = self.__get_env_var_name(
                name, kwargs.pop("env_var_prefix", "PDM_PLUGINS")
            )
        for key in [k for k in kwargs if k not in self.__allowed_values]:
            logger.warning(
                (
                    "Cannot use '%s' as config item value. This is most "
                    "likely an authoring error. Only the following keys "
                    "are valid: %s"
                ),
                key,
                ",".join(self.__allowed_values),
            )
            kwargs.pop(key)

        config_key = f"{self.config_key_prefix}.{name}"
        self[config_key] = ConfigItem(**kwargs)

    @property
    def config_key_prefix(self) -> str:
        """"""
        keys = self.__accessor.get_config_section_path(ConfigSection.PLUGINS)
        key_value = ".".join(keys)
        return key_value

    def propagate(self, target: "_SupportsAddConfig") -> None:
        """"""
        for key, value in self.items():
            target.add_config(key, value)

    def to_namespace(self) -> "SimpleNamespace":
        """"""
        result = SimpleNamespace()
        for key in self:
            name = str(key)
            name = name.removeprefix(self.config_key_prefix).lstrip(".")
            if "." in name:
                continue
            result.__dict__[name] = self.__accessor.get_config_value(key)
        return result

    def __get_env_var_name(self, name: str, env_var_prefix: str) -> str:
        """"""
        path = [env_var_prefix]
        config_values = (
                           self.__accessor.get_config_section_path(ConfigSection.PLUGINS)
        )
        if len(config_values) > 1:
            config_values = config_values[1:]
        if len(config_values) == 1:
            config_values = [config_values[0]]
        if isinstance(config_values, str):
            config_values = [config_values]

        path.extend([c.upper() for c in config_values])
        path.append(name.upper())

        return "_".join(path)


class ConfigNamespace:
    """"""

    def __init__(
        self,
        namespace: str,
        accessor: ConfigAccessor,
        parent: "ConfigNamespace | None" = None,
    ) -> None:
        """
        Parameters
        ----------
        namespace: str :
        parent : _ConfigNamespace | None :


        Returns
        -------

        """
        self.__parent = parent
        self.__namespace = namespace
        self.__accessor = accessor

    @property
    def parent(self) -> "ConfigNamespace | None":
        """"""
        return self.__parent

    @property
    def namespace(self) -> tuple[str, ...]:
        """"""
        if self.__parent is None:
            return tuple([self.__namespace])
        return tuple(list(self.__parent.namespace) + [self.__namespace])

    def _get_value(self, name: str) -> Any:
        config_names: tuple[str, ...] = tuple(list(self.namespace) + [name])
        return self.__accessor.get_config_value(*config_names)


# pylint: disable=C0103
# Justification: TypeVar naming
_TConfigValue = TypeVar("_TConfigValue", bool, int, float, str)


class IsMissing(ABC):
    @abstractmethod
    def __int__(self) -> int:  # pylint: disable=R0801
        """"""
        raise NotImplementedError()

    @abstractmethod
    def __float__(self) -> float:  # pylint: disable=R0801
        """"""
        raise NotImplementedError()

    @abstractmethod
    def __bool__(self) -> bool:  # pylint: disable=R0801
        """"""
        raise NotImplementedError()

    @abstractmethod
    def __str__(self) -> str:  # pylint: disable=R0801
        """"""
        raise NotImplementedError()

    @abstractmethod
    def raw_value(self) -> Any:  # pylint: disable=R0801
        """"""
        raise NotImplementedError()


class MissingValue(Generic[_TConfigValue], IsMissing):
    """"""

    def __init__(self, value: _TConfigValue) -> None:
        self.__value: Final[_TConfigValue] = value

    @property
    def value(self) -> _TConfigValue:
        """"""
        return self.__value

    def __int__(self) -> int:
        """"""
        return int(self.__value)

    def __float__(self) -> float:
        """"""
        return float(self.__value)

    def __bool__(self) -> bool:
        """"""
        return bool(self.__value)

    def __str__(self) -> str:
        """"""
        return str(self.__value)

    def raw_value(self) -> Any:
        """"""
        return self.__value
