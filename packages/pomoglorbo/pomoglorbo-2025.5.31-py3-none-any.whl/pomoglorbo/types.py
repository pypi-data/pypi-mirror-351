# SPDX-FileCopyrightText: 2023 Justus Perlwitz
# SPDX-FileCopyrightText: 2024 Justus Perlwitz
#
# SPDX-License-Identifier: MIT

from dataclasses import (
    dataclass,
)
from pathlib import Path
from typing import (
    Literal,
    NewType,
    Optional,
    TypedDict,
    Union,
)

from prompt_toolkit.layout import (
    Container,
    FormattedTextControl,
    Layout,
)

# Possible circular import?
from .core.states import State

OptionalCmd = Optional[list[str]]

InAppResource = NewType("InAppResource", str)
PathOrResource = Union[InAppResource, Path]


KeyBindingsCfg = TypedDict(
    "KeyBindingsCfg",
    {
        "focus_previous": str,
        "focus_next": str,
        "exit_clicked": str,
        "start": str,
        "pause": str,
        "reset": str,
        "reset_all": str,
        "help": str,
    },
)


@dataclass(kw_only=True, frozen=True)
class Configuration:
    no_sound: bool
    audio_file: PathOrResource
    tomatoes_per_set: int
    work_minutes: float
    small_break_minutes: float
    long_break_minutes: float
    key_bindings: KeyBindingsCfg
    work_state_cmd: OptionalCmd = None
    work_state_cmd_suffix: OptionalCmd = None
    work_paused_state_cmd: OptionalCmd = None
    small_break_state_cmd: OptionalCmd = None
    long_break_state_cmd: OptionalCmd = None
    work_resumed_state_cmd: OptionalCmd = None
    break_over_cmd: OptionalCmd = None

    exit_cmd: OptionalCmd = None

    audio_check: bool = False

    state_file: Path


@dataclass
class Tomato:
    state: State
    tomatoes = 0
    sets = 0
    config: Configuration
    show_help: bool
    last_warning: Optional[str] = None
    last_cmd_out: Optional[str] = None


@dataclass(frozen=True)
class TomatoRender:
    text: str
    show_help: bool


TomatoInput = Literal[
    "start",
    "pause",
    "reset",
    "reset_all",
    "update",
    "toggle_help",
]


MaybeCommand = Optional[list[str]]


@dataclass(frozen=True)
class TomatoInteraction:
    cmd: MaybeCommand
    play_alarm: bool
    new_state: State
    warning: Optional[str]
    show_help: Optional[bool]


@dataclass(frozen=True)
class TomatoLayout:
    layout: Layout
    text_area: FormattedTextControl
    warning_display: FormattedTextControl
    last_cmd_display: FormattedTextControl
    status: FormattedTextControl
    helpwindow: Container
