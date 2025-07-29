#!/usr/bin/env python3

import json
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from arguments import parse_arguments
from compilation_database import create_compilation_database
from logger import setup_custom_logger
from properties_parser import parse_c_cpp_properties

if TYPE_CHECKING:
    from logging import Logger


def main() -> int:
    args = parse_arguments()

    logger: Logger = setup_custom_logger(args.level)

    model, err = parse_c_cpp_properties(Path(args.file))

    if model is None or err is not None:
        logger.error(f"An error occured while parsing the input file: {err}")
        return 1

    compilation_database, err2 = create_compilation_database(args, model)

    if compilation_database is None or err2 is not None:
        logger.error(
            f"An error occured while crreating the complation database: {err2}",
        )
        return 1

    final_output_file = Path(args.output) / "compile_commands.json"

    if not final_output_file.parent.exists():
        final_output_file.parent.mkdir(exist_ok=True, parents=True)

    with Path.open(final_output_file, "w") as f:
        data = [c.model_dump(exclude_none=True) for c in compilation_database]
        json.dump(data, f, indent=2)

    return 0


if __name__ == "__main__":
    result = main()
    sys.exit(result)
