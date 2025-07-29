import ast
import pathlib
import re
from typing import List, Optional


def parse_directory(
    directory_path: str = None,
    incl_ext: Optional[List[str]] = None,
    excl_dir: Optional[List[str]] = None,
) -> List[pathlib.Path]:
    path = pathlib.Path(directory_path).resolve() if directory_path else pathlib.Path.cwd()
    if not path.exists():
        raise FileNotFoundError(f"No such file or directory: {path}")
    if not path.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {path}")

    files = [item for item in path.rglob("*") if item.is_file()]

    if excl_dir:
        exclude_set = {name.lower() for name in excl_dir}
        files = [
            f for f in files if not any(parent.name.lower() in exclude_set for parent in f.parents)
        ]
    if incl_ext:
        pattern = r"^\.[a-zA-Z]+"
        if not all(re.match(pattern, ext) for ext in incl_ext):
            raise ValueError("Extensions must start with '.' followed by alphabetic characters")

        ext_set = {ext.lower() for ext in incl_ext}
        files = [f for f in files if f.suffix.lower() in ext_set]

    return files


def parse_ast(path: pathlib.Path) -> ast.AST:
    if not path.is_file() or path.suffix != ".py":
        raise ValueError(f"Path must be a Python file: {path}")

    with open(path, "rb") as f:
        rv = ast.parse(f.read(), filename=path)

    return rv
