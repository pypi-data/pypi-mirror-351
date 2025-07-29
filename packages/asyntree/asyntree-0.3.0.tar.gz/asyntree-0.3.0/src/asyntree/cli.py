import pathlib
from typing import Annotated, List, Optional

import typer
from rich import print

from asyntree import api

app = typer.Typer(add_completion=False)


@app.command("describe")
def cli_describe(
    path: Annotated[pathlib.Path, typer.Argument(help="Input a directory path")],
    exclude: Annotated[
        Optional[List[str]], typer.Option("--exclude", "-e", help="Directory names to exclude")
    ] = None,
) -> None:
    """Print the ast nodes of all python files."""
    try:
        validated_path = _validate_path(path)
        cli_output = api.describe(validated_path, incl_ext=[".py"], excl_dir=exclude)
        print(cli_output)
    except Exception as e:
        print(f"Error: {e}")
        raise typer.Exit(1)


@app.command("to-tree")
def cli_to_tree(
    path: Annotated[pathlib.Path, typer.Argument(help="Input a directory path")],
    include: Annotated[
        Optional[List[str]], typer.Option("--include", "-i", help="File extensions to include")
    ] = None,
    exclude: Annotated[
        Optional[List[str]], typer.Option("--exclude", "-e", help="Directory names to exclude")
    ] = None,
) -> None:
    """Print the tree structure of the directory."""
    try:
        validated_path = _validate_path(path)
        cli_output = api.to_tree(validated_path, incl_ext=include, excl_dir=exclude)
        print(cli_output)
    except Exception as e:
        print(f"Error: {e}")
        raise typer.Exit(1)


@app.command("to-llm")
def cli_to_llm(
    path: Annotated[pathlib.Path, typer.Argument(help="Input a directory path")],
    include: Annotated[
        Optional[List[str]], typer.Option("--include", "-i", help="File extensions to include")
    ] = None,
    exclude: Annotated[
        Optional[List[str]], typer.Option("--exclude", "-e", help="Directory names to exclude")
    ] = None,
    output_file: Annotated[
        str, typer.Option("--output", "-o", help="Output file name")
    ] = "llm.txt",
) -> None:
    """Generate (and export) the llm.txt file."""
    try:
        validated_path = _validate_path(path)
        cli_output = api.to_llm(
            validated_path, incl_ext=include, excl_dir=exclude, output_file=output_file
        )
        print(f"Exported to: {cli_output}")
    except Exception as e:
        print(f"Error: {e}")
        raise typer.Exit(1)


@app.command("to-requirements")
def cli_to_requirements(
    path: Annotated[pathlib.Path, typer.Argument(help="Input a directory path")],
    exclude: Annotated[
        Optional[List[str]], typer.Option("--exclude", "-e", help="Directory names to exclude")
    ] = None,
    output_file: Annotated[
        str, typer.Option("--output", "-o", help="Output file name")
    ] = "requirements.txt",
) -> None:
    """Generate (and export) the requirements.txt file."""
    try:
        validated_path = _validate_path(path)
        cli_output = api.to_requirements(
            validated_path, incl_ext=[".py"], excl_dir=exclude, output_file=output_file
        )
        print(f"Exported to: {cli_output}")
    except Exception as e:
        print(f"Error: {e}")
        raise typer.Exit(1)


def _validate_path(value: str) -> pathlib.Path:
    path = pathlib.Path(value).resolve() if value else pathlib.Path.cwd()

    if not path.exists():
        raise FileNotFoundError(f"No such file or directory: {path}")
    if not path.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {path}")

    return path


# TODO: validate all inputs, add data structure for directory tree after filterings, add helpers in api, add colors
