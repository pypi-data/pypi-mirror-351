import os
import subprocess
from enum import Enum
from logging import Logger
from pathlib import Path
from typing import Optional

from typing_extensions import Self

from arguments import ParserResult
from data import c_cpp_properties
from data.compilation_database import Arguments, Directory, File, Model
from logger import get_logger

logger: Logger = get_logger()


def read_file(file: Path) -> list[str]:
    with Path.open(file) as f:
        return [line.rstrip("\n") for line in f]


class ArgResolver:
    __prefix: Optional[Path]

    def __init__(self) -> None:
        self.__prefix = None

    def resolve(self: Self, arg: str) -> list[str]:
        if arg.startswith("@"):
            intermediate = read_file(Path(arg.removeprefix("@")))
            return [res for a in intermediate for res in self.resolve(a)]

        if arg.startswith("-iprefix"):
            self.__prefix = Path(arg.removeprefix("-iprefix"))
            return [arg]

        if arg.startswith("-iwithprefixbefore"):
            if self.__prefix is None:
                logger.warning("tried resolving prefix, but no '-iprefix' was given")
                return [arg]

            path = arg.removeprefix("-iwithprefixbefore")
            if path.startswith("/"):
                path = path.removeprefix("/")

            final_path = (self.__prefix / path).absolute()
            return [f"-I{final_path}"]

        return [arg]


def resolve_used_config(
    configs: c_cpp_properties.Configurations,
) -> Optional[c_cpp_properties.Configuration]:
    if len(configs.root) == 0:
        return None
    # TODO: correctly choose one, based on e.g. name and cli args
    # TODO: allow multipel configurations to also map for languages, e.g. g++ for cpp and gcc for c
    return configs.root[0]


def resolve_sources(root: Path, source: str) -> list[Path]:
    raw_folders = source.split("|")

    raw_list: list[Path] = []
    for raw_folder in raw_folders:
        path = Path(raw_folder)
        if not path.exists():
            logger.info(f"Skipped folder {path} since it doesn't exist")
            continue

        if not path.is_dir():
            logger.info(f"Skipped folder {path} since it isn't a folder")
            continue

        raw_list.append(path)

    result: list[Path] = []

    for raw_folder in raw_list:
        root_local = root / raw_folder
        for root_arg, _dirs, files in os.walk(root_local):
            result.extend(Path(root_arg) / file for file in files)

    return result


class Language(Enum):
    c = "c"
    cpp = " cpp"


def classify_language(name: Path) -> Optional[Language]:
    match name.suffix:
        case ".cpp":
            return Language.cpp
        case ".c":
            return Language.c
        case _:
            return None


class ArgumentsObject:
    arguments: list[str]
    conditional_args: dict[Language, list[str]]
    compiler: str

    def __init__(self, compiler: str) -> None:
        self.arguments = []
        self.conditional_args = {Language.c: [], Language.cpp: []}
        self.compiler = compiler


def parse_search_list(inp: str) -> list[str]:

    result: list[str] = []

    is_in_search_mode = False

    for line in inp.split("\n"):
        if line == "#include <...> search starts here:":
            is_in_search_mode = True

        if line == '#include "..." search starts here:':
            is_in_search_mode = True

        if line == "End of search list.":
            is_in_search_mode = True

        if is_in_search_mode:
            path = Path(line.removeprefix(" "))
            if path.exists():
                result.append(str(path.absolute().resolve()))

    return result


def get_standard_include_paths(language: Language, compiler: str) -> list[str]:
    try:
        language_str = "c" if language == Language.c else "c++"

        # TODO. also support clang and detect compiler based on string
        result = subprocess.run(  # noqa: S603
            [compiler, f"-x{language_str}", "-E", "-v", "-"],
            check=True,
            capture_output=True,
            input="",
        )

        if result.returncode != 0:
            msg = f"Invalid Return code f{result.returncode}"
            raise RuntimeError(msg)  # noqa: TRY301

        res = result.stderr.decode()

        return parse_search_list(res)

    except Exception as e:  # noqa: BLE001
        logger.info(e)
        return []


def get_arguments_object(
    args: ParserResult,
    config: c_cpp_properties.Configuration,
) -> ArgumentsObject:
    # TODO resolve $CC or $CXX env vraibale, if nothing was given
    compiler = "g++" if config.compilerPath is None else config.compilerPath

    arguments = ArgumentsObject(compiler)

    include_paths = [] if config.includePath is None else config.includePath

    for include_path in include_paths:
        if include_path == "":
            continue

        arguments.arguments.append(f"-I{include_path}")

    defines = [] if config.defines is None else config.defines

    for define in defines:
        if define == "":
            continue

        arguments.arguments.append(f"-D{define}")

    compiler_args = [] if config.compilerArgs is None else config.compilerArgs

    resolver = ArgResolver()

    for arg in compiler_args:
        arguments.arguments.extend(resolver.resolve(arg))

    if config.cppStandard is not None:
        arguments.conditional_args[Language.cpp].append(
            f"--std={config.cppStandard.value}",
        )

    if config.cStandard is not None:
        arguments.conditional_args[Language.c].append(f"--std={config.cStandard.value}")

    if args.cross:
        for language in list(Language):
            standard_include_paths = get_standard_include_paths(language, compiler)
            for include_path in standard_include_paths:
                if include_path == "":
                    continue

                arguments.conditional_args[language].append(f"-I{include_path}")

    return arguments


CompilationResult = tuple[list[Model], None] | tuple[None, str]


def create_compilation_database_from_v4(
    args: ParserResult,
    model: c_cpp_properties.Model,
) -> CompilationResult:
    config = resolve_used_config(model.configurations)

    if config is None:
        return (None, "No valid configurations entry in file")

    arguments_object = get_arguments_object(args, config)

    root = Path().absolute()

    sources = resolve_sources(root, args.sources)

    result: list[Model] = []

    for file in sources:
        language = classify_language(file)
        if language is None:
            continue

        arguments: list[str] = [arguments_object.compiler]

        arguments.extend(arguments_object.arguments)
        arguments.extend(arguments_object.conditional_args[language])

        new_model = Model(
            directory=Directory(str(root.absolute())),
            file=File(str(file.absolute())),
            arguments=Arguments(arguments),
        )
        result.append(new_model)

    return (result, None)


def create_compilation_database(
    args: ParserResult,
    model: c_cpp_properties.Model,
) -> CompilationResult:

    version = model.version

    match version.root:
        case 4:
            return create_compilation_database_from_v4(args, model)
        case _:
            return (None, f"Unsupported c_cpp_properties version: {version.root}")
