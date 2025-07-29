import json
from pathlib import Path

from pydantic import ValidationError

from data.c_cpp_properties import Model


def parse_c_cpp_properties(
    file: Path,
) -> tuple[Model, None] | tuple[None, str | ValidationError]:

    if not Path.exists(file):
        return (None, f"File {file} doesn't exist")

    with Path.open(file) as f:
        data = json.load(f)

        try:
            model = Model.model_validate(
                data,
                strict=False,
            )
            return (model, None)
        except ValidationError as e:
            return (None, e)
