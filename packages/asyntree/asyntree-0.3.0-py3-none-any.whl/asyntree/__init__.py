"""asyntree"""

import importlib.metadata

from asyntree.api import (
    describe,
    parse_ast,
    parse_directory,
    to_llm,
    to_requirements,
    to_tree,
)

__title__ = "asyntree"
__description__ = "Syntax trees and file utilities."

try:
    __version__ = importlib.metadata.version(__package__ or __title__)
except importlib.metadata.PackageNotFoundError:
    __version__ = "unknown"

__all__ = [
    "describe",
    "to_llm",
    "to_requirements",
    "to_tree",
    "parse_directory",
    "parse_ast",
    "__title__",
    "__description__",
    "__version__",
]
