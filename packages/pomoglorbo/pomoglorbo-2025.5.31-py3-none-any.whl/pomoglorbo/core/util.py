# SPDX-FileCopyrightText: 2021-2023 Bhatihya Perera
# SPDX-FileCopyrightText: 2023 Justus Perlwitz
# SPDX-FileCopyrightText: 2024 Justus Perlwitz
#
# SPDX-License-Identifier: MIT
import time
from collections.abc import Callable
from typing import Literal

from pomoglorbo.cli.util import gettext_lazy as _

from .states import RunningState, State, TaskStatus


def cur_time() -> int:
    return int(time.time())


def every(delay: int, task: Callable[[], None]) -> None:
    start_time = cur_time()
    next_time = start_time + delay
    while True:
        time.sleep(max(0, next_time - cur_time()))
        task()
        next_time = next_time + delay


def calc_remainder(state: RunningState) -> int:
    cur = cur_time()
    return max(state.started_at + state.time_period - cur, 0)


Style = Literal["fancy", "plain"]


def format_time(state: State, remainder: int, style: Style = "fancy") -> str:
    minutes, seconds = divmod(remainder, 60)
    match style:
        case "fancy":
            if state.status == TaskStatus.STARTED:
                progress = next(state.progress) + " "
            else:
                progress = ""

            return _("{}{minutes}min {seconds:02}s remaining").format(
                progress,
                minutes=minutes,
                seconds=seconds,
            )
        case "plain":
            return _("{minutes:02}:{seconds:02}").format(
                minutes=minutes, seconds=seconds
            )
