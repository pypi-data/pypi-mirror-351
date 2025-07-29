# Asyntree

Syntax trees and file utilities.

## Usage

### As a CLI

Installation:

```shell
uv install tool asyntree
```

Usage:

```shell
>>> asyntree --help

 Usage: asyntree [OPTIONS] COMMAND [ARGS]...

╭─ Options ───────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                             │
╰─────────────────────────────────────────────────────────────────────────╯
╭─ Commands ──────────────────────────────────────────────────────────────╮
│ to-tree           Print the tree structure of the directory.            │
│ to-llm            Generate (and export) the llm.txt file.               │
│ to-requirements   Generate (and export) the requirements.txt file.      │
╰─────────────────────────────────────────────────────────────────────────╯
```

Configuration:

```shell
# asyntree to-tree --include <file_extension> --exlcude <directory>
asyntree to-tree . -i .py -i .r -e .venv -e .git

# asyntree to-llm --include <file_extension> --exlcude <directory> --output <file>
asyntree to-llm . -i .py -i .r -e .venv -e .git -o llm.txt

# asyntree to-requirements --exlcude <directory> --output <file>
asyntree to-requirements . -e .venv -o requirements.txt
```

### As a Library

Installation:

```shell
uv add asyntree
```

Usage:

```python
import asyntree as atree

atree.to_requirements("requirements.txt")
atree.to_llm("llm.txt")
```

## Development

The `Makefile` contains relevant commands to get the development environment configured (ie `make init`, `make test`, `make lint`, `make format`, `make deps`).
