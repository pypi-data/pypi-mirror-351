# SPDX-FileCopyrightText: 2021-2023 Bhatihya Perera
# SPDX-FileCopyrightText: 2023 Justus Perlwitz
# SPDX-FileCopyrightText: 2024 Justus Perlwitz
#
# SPDX-License-Identifier: MIT
import argparse
import ast
import configparser
import os
import pathlib
from collections.abc import Mapping
from dataclasses import replace
from importlib import metadata

from pomoglorbo.cli.util import gettext_lazy as _
from pomoglorbo.types import Configuration, InAppResource, PathOrResource
from pomoglorbo.xdg_base_dirs import xdg_config_home, xdg_state_home

# File is located in '~/.config/pomoglorbo/config.ini' or the location
# specified by POMOGLORBO_CONFIG_FILE environment variable
DEFAULT_CONFIG_FILE = xdg_config_home() / "pomoglorbo/config.ini"
CONFIG_FILE = pathlib.Path(
    os.environ.get("POMOGLORBO_CONFIG_FILE", DEFAULT_CONFIG_FILE)
)
STATE_FILE_PATH = pathlib.Path(xdg_state_home() / "pomoglorbo" / "state.pomoglorbo")


DEFAULT_CONFIG: Mapping[str, Mapping[str, str]] = {
    "General": {
        "no_sound": "false",
        "audio_file": "",
    },
    "Ipc": {},
    "Time": {
        "tomatoes_per_set": "4",
        "work_minutes": "25",
        "small_break_minutes": "5",
        "long_break_minutes": "15",
    },
    "KeyBindings": {
        "focus_previous": "s-tab,up,left,h,k",
        "focus_next": "tab,right,down,l,j",
        "exit_clicked": "q",
        "start": "s",
        "pause": "p",
        "reset": "r",
        "reset_all": "a",
        "help": "?,f1",
    },
    "Trigger": {
        "work_state_cmd": "None",
        "work_paused_state_cmd": "None",
        "work_resumed_state_cmd": "None",
        "long_break_state_cmd": "None",
        "small_break_state_cmd": "None",
        "break_over_cmd": "None",
        "exit_cmd": "None",
    },
}


def get_argument_parser() -> argparse.ArgumentParser:
    """Create argument parser."""
    parser = argparse.ArgumentParser(
        "pomoglorbo",
        description=_("Pomoglorbo: TUI Pomodoro Technique Timer"),
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=_("""Please refer to the terms of the LICENSES included with Pomoglorbo.

Curious about how to use Pomoglorbo? Read my blog post: https://www.justus.pw/posts/2024-06-18-try-pomoglorbo.html

Stay up to date with changes: https://codeberg.org/justusw/Pomoglorbo

Reach out to me if you have any questions: justus@jwpconsulting.net
"""),
    )
    parser.add_argument("--no-sound", help=_("Mute alarm"), action="store_true")
    parser.add_argument(
        "--audio-check", help=_("Play alarm and exit"), action="store_true"
    )
    parser.add_argument(
        "-v",
        "--version",
        help=_("Display version and exit"),
        action="version",
        version=metadata.version("pomoglorbo"),
    )
    parser.add_argument(
        "--audio-file",
        metavar="path",
        help=_("Custom audio file for alarm"),
        type=pathlib.Path,
    )
    parser.add_argument(
        "--config-file",
        help=_(
            "Use a different config file. "
            "Overrides POMOGLORBO_CONFIG_FILE environment variable. "
            'Default is "$XDG_CONFIG_HOME/pomoglorbo/config.ini".'
        ),
        default=CONFIG_FILE,
        type=pathlib.Path,
        metavar="path",
    )
    parser.add_argument(
        "--work-state-cmd-suffix",
        nargs="+",
        help=_(
            "Append these arguments to external command invocation "
            "when starting the next Pomodoro"
        ),
        metavar="suffix",
    )
    return parser


def create_default_ini(conf: configparser.ConfigParser, path: pathlib.Path) -> None:
    """Creates default ini configuration file."""
    path.parent.mkdir(exist_ok=True)
    with path.open("w+") as configfile:
        conf.write(configfile)


def ini_parse(conf: configparser.ConfigParser, path: pathlib.Path) -> None:
    """Parse configuration file."""
    if not path.exists():
        create_default_ini(conf, path)
    conf.read(path)


def get_config_parser() -> configparser.ConfigParser:
    """Create configuration parser."""
    conf = configparser.ConfigParser()
    conf.update(DEFAULT_CONFIG)
    return conf


def parse_configuration(path: pathlib.Path) -> Configuration:
    """Parse configuration from ini file."""
    conf = get_config_parser()
    ini_parse(conf, path)
    audio_file: PathOrResource
    if audio_file_conf := conf.get("General", "audio_file", fallback=None):
        audio_file = pathlib.Path(audio_file_conf)
    else:
        audio_file = InAppResource("b15.wav")
    return Configuration(
        no_sound=conf.getboolean("General", "no_sound"),
        audio_file=audio_file,
        state_file=pathlib.Path(
            conf.get("Ipc", "state_file", fallback=STATE_FILE_PATH)
        ),
        tomatoes_per_set=conf.getint("Time", "tomatoes_per_set"),
        work_minutes=conf.getfloat("Time", "work_minutes"),
        small_break_minutes=conf.getfloat("Time", "small_break_minutes"),
        long_break_minutes=conf.getfloat("Time", "long_break_minutes"),
        key_bindings={
            "focus_previous": conf.get("KeyBindings", "focus_previous"),
            "focus_next": conf.get("KeyBindings", "focus_next"),
            "exit_clicked": conf.get("KeyBindings", "exit_clicked"),
            "start": conf.get("KeyBindings", "start"),
            "pause": conf.get("KeyBindings", "pause"),
            "reset": conf.get("KeyBindings", "reset"),
            "reset_all": conf.get("KeyBindings", "reset_all"),
            "help": conf.get("KeyBindings", "help"),
        },
        work_state_cmd_suffix=ast.literal_eval(
            conf.get("Trigger", "work_state_cmd_suffix", fallback="None")
        ),
        work_state_cmd=ast.literal_eval(conf.get("Trigger", "work_state_cmd")),
        work_paused_state_cmd=ast.literal_eval(
            conf.get("Trigger", "work_paused_state_cmd")
        ),
        small_break_state_cmd=ast.literal_eval(
            conf.get("Trigger", "small_break_state_cmd")
        ),
        long_break_state_cmd=ast.literal_eval(
            conf.get("Trigger", "long_break_state_cmd")
        ),
        work_resumed_state_cmd=ast.literal_eval(
            conf.get("Trigger", "work_resumed_state_cmd")
        ),
        break_over_cmd=ast.literal_eval(conf.get("Trigger", "break_over_cmd")),
        exit_cmd=ast.literal_eval(conf.get("Trigger", "exit_cmd")),
    )


def merge_config_and_cli_args(
    configuration: Configuration, cli_args: argparse.Namespace
) -> Configuration:
    """
    Loads the command line arguments

    Command line arguments override file configurations.
    """
    return replace(
        configuration,
        no_sound=(cli_args.no_sound or configuration.no_sound),
        work_state_cmd_suffix=cli_args.work_state_cmd_suffix or [],
        audio_check=cli_args.audio_check,
        audio_file=cli_args.audio_file or configuration.audio_file,
    )


def create_configuration() -> Configuration:
    cli_args = get_argument_parser().parse_args()
    config = parse_configuration(cli_args.config_file)
    config = merge_config_and_cli_args(config, cli_args)
    return config
