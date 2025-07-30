# SPDX-FileCopyrightText: 2023 Justus Perlwitz
# SPDX-FileCopyrightText: 2024 Justus Perlwitz
# SPDX-FileCopyrightText: 2021-2023 Bhatihya Perera
#
# SPDX-License-Identifier: MIT
"""Provide utilities for CLI."""

from gettext import gettext


def gettext_lazy(message: str) -> str:
    return gettext(message)
