# SPDX-FileCopyrightText: 2023 Justus Perlwitz
# SPDX-FileCopyrightText: 2024 Justus Perlwitz
#
# SPDX-License-Identifier: MIT

from importlib import resources
from pathlib import Path

from playsound3 import playsound

from pomoglorbo.types import PathOrResource

from .. import core


def play(path: PathOrResource, block: bool) -> None:
    match path:
        case Path():
            playsound(str(path), block=block)
        case str():
            with resources.path(core, path) as file:
                playsound(str(file), block=block)
