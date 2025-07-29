import pathlib
import sys
from typing import Any, Dict, List, Optional, Set

from rich.filesize import decimal
from rich.text import Text
from rich.tree import Tree

from asyntree.parser import parse_ast, parse_directory
from asyntree.visitor import ImportVisitor, Visitor


def describe(
    directory_path: pathlib.Path,
    *,
    incl_ext: Optional[List[str]] = None,
    excl_dir: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """Print the ast nodes of all python files."""

    visitor = Visitor()
    output = []

    file_paths = parse_directory(directory_path, incl_ext=incl_ext, excl_dir=excl_dir)

    for file_path in file_paths:
        file_ast = parse_ast(file_path)
        file_ast_metrics = dict(visitor.run(file_ast))
        output.append({"path": file_path.name, "ast": file_ast_metrics})

    return output


def to_tree(
    directory_path: pathlib.Path,
    *,
    incl_ext: Optional[List[str]] = None,
    excl_dir: Optional[List[str]] = None,
) -> Tree:
    """Print the tree structure of the directory."""

    file_paths = parse_directory(directory_path, incl_ext=incl_ext, excl_dir=excl_dir)

    if not file_paths:
        return None

    nodes: Dict[pathlib.Path, Tree] = {}

    root_node = Tree(Text(directory_path.name))
    nodes[directory_path] = root_node

    for path in sorted(file_paths, key=lambda p: p.parts):
        if path.name.startswith("."):
            continue

        relative_path = path.relative_to(directory_path)
        current = root_node
        current_parent = directory_path

        for part in relative_path.parts[:-1]:
            current_path = current_parent / part
            if current_path not in nodes:
                nodes[current_path] = current.add(Text(part, "yellow bold"))
            current = nodes[current_path]
            current_parent = current_path

        file_size = path.stat().st_size
        text_filename = Text(path.name, "green")
        text_filename.append(f" ({decimal(file_size)})", "blue")
        current.add(text_filename)

    return root_node


def to_llm(
    directory_path: pathlib.Path,
    *,
    incl_ext: Optional[List[str]] = None,
    excl_dir: Optional[List[str]] = None,
    output_file: str = "llm.txt",
) -> pathlib.Path:
    """Generate (and export) the llm.txt file."""

    file_paths = parse_directory(directory_path, incl_ext=incl_ext, excl_dir=excl_dir)

    if not file_paths:
        return None

    file_paths = sorted(file_paths)

    content_list = []

    content_list.append("<<<--- File Paths --->>>\n\n")
    for file_path in file_paths:
        relative_path = file_path.relative_to(directory_path.parent)
        content_list.append(f"{relative_path}\n")

    content_list.append("\n<<<--- File Contents --->>>\n\n")
    for file_path in file_paths:
        relative_path = file_path.relative_to(directory_path.parent)
        try:
            with open(file_path, encoding="utf-8") as f:
                file_content = f.read()

            content_list.append(f'<file path="{relative_path}">\n')
            content_list.append(file_content)
            content_list.append("\n</file>\n\n")
        except Exception as e:
            content_list.append(f'<file path="{relative_path}">\n')
            content_list.append(f"Could not read file: {e}\n")
            content_list.append("</file>\n\n")

    output_path = pathlib.Path(output_file)
    with open(output_path, "w", encoding="utf-8") as f:
        f.writelines(content_list)

    return output_path


def to_requirements(
    directory_path: pathlib.Path,
    *,
    incl_ext: Optional[List[str]] = None,
    excl_dir: Optional[List[str]] = None,
    output_file: str = "llm.txt",
) -> pathlib.Path:
    """Generate (and export) the requirements.txt file."""

    file_paths = parse_directory(directory_path, incl_ext=incl_ext, excl_dir=excl_dir)

    if not file_paths:
        return None

    imports = _extract_imports(file_paths)

    external_deps = []
    for dep in sorted(imports):
        if not dep.startswith(".") and dep not in sys.stdlib_module_names:
            root_module = dep.split(".")[0]
            if root_module not in sys.stdlib_module_names:
                external_deps.append(root_module)

    unique_deps = sorted(list(set(external_deps)))

    output_path = pathlib.Path(output_file)
    with open(output_path, "w", encoding="utf-8") as f:
        f.writelines(f"{dep}\n" for dep in unique_deps)

    return output_path


def _extract_imports(paths: List[pathlib.Path]) -> Set[str]:
    all_imports = set()
    visitor = ImportVisitor()

    for file_path in paths:
        ast_tree = parse_ast(file_path)
        imports = visitor.run(ast_tree)
        all_imports.update(imports)

    return all_imports
