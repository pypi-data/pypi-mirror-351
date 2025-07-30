# SPDX-FileCopyrightText: 2021-2023 Bhatihya Perera
# SPDX-FileCopyrightText: 2023 Justus Perlwitz
# SPDX-FileCopyrightText: 2024 Justus Perlwitz
#
# SPDX-License-Identifier: MIT
from gettext import ngettext

from pomoglorbo.cli.util import gettext_lazy as _
from pomoglorbo.core.states import (
    InitialState,
    LongBreakState,
    SmallBreakState,
    State,
    WorkingState,
    WorkPausedState,
)
from pomoglorbo.core.util import calc_remainder, format_time
from pomoglorbo.types import Tomato, TomatoRender


def render_time_remaining(tomato: Tomato, state: State) -> str:
    """Give time remaining for this state."""
    match state:
        case SmallBreakState() | LongBreakState() | WorkingState():
            remainder = calc_remainder(state)
            return format_time(state, remainder)
        case WorkPausedState():
            return _("Press [start] to continue")
        case InitialState():
            return _("Press [start] to begin")


def render_tomato(tomato: Tomato) -> TomatoRender:
    set_message = ngettext(
        "1 set completed", "{sets} sets completed", tomato.sets
    ).format(sets=tomato.sets)

    time = render_time_remaining(tomato, tomato.state)

    tomatoes_per_set = tomato.config.tomatoes_per_set
    tomatoes_remaining = tomatoes_per_set - tomato.tomatoes % tomatoes_per_set
    ascii_tomato = "(`) "
    count = ascii_tomato * tomatoes_remaining

    ftext_lines = [
        tomato.state.name,
        "",
        time,
        count,
        set_message,
        "",
        tomato.last_warning or "",
        tomato.last_cmd_out or "",
    ]
    ftext: str = "\n".join(ftext_lines)

    return TomatoRender(
        text=ftext,
        show_help=tomato.show_help,
    )
