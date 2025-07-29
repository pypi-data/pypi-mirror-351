import argparse
from typing import cast

from logger import LogLevel


class ParserResult:
    file: str
    output: str
    cross: bool
    level: LogLevel
    sources: str


def parse_arguments() -> ParserResult:
    parser = argparse.ArgumentParser(
        prog="cpp-to-compile-commands",
        description="Convert Micorsoft cpp file to compilation database",
    )

    parser.add_argument(
        "-f",
        "--file",
        dest="file",
        required=False,
        default="./.vscode/c_cpp_properties.json",
        help="The c_cpp file to use",
    )

    parser.add_argument(
        "-o",
        "--output",
        dest="output",
        required=False,
        default="build",
        help="The output directory",
    )

    parser.add_argument(
        "-c",
        "--cross",
        dest="cross",
        required=False,
        default=False,
        action="store_true",
        help="Whether this is a cross compile or not",
    )

    loglevel_choices: list[LogLevel] = [
        LogLevel.CRITICAL,
        LogLevel.ERROR,
        LogLevel.WARNING,
        LogLevel.INFO,
        LogLevel.DEBUG,
        LogLevel.NOTSET,
    ]
    loglevel_default: LogLevel = LogLevel.INFO
    parser.add_argument(
        "-l",
        "--level",
        choices=loglevel_choices,
        default=loglevel_default,
        dest="level",
        type=lambda s: LogLevel.from_str(s) or cast(LogLevel, s.lower()),
        help="The loglevel to use",
    )

    parser.add_argument(
        "-s",
        "--sources",
        dest="sources",
        required=False,
        default="src|test",
        help="The source file to scan and add, can be a list, that is seperated by |",
    )

    return cast(ParserResult, parser.parse_args())
