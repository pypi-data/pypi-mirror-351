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
from pathlib import Path
from typing import Any, Mapping, Protocol

from pdm.termui import UI  # type: ignore


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


class CoreLike(Protocol):  # pylint: disable=R0903
    """"""

    ui: UI


class ProjectLike(ConfigHolder, Protocol):  # pylint: disable=R0903
    """"""

    root: Path
    core: CoreLike
    PYPROJECT_FILENAME: str
