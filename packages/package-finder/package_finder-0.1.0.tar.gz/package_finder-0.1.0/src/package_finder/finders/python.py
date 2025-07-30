import os
import json
import ast
import tomllib  # Python 3.11+; use `tomli` for earlier versions

from tqdm import tqdm
from tqdm import tqdm
import os

IGNORED_DIRS = {
    "node_modules", "dist", "build", ".git",
    ".venv", "env", "__pycache__", ".cache"
}


def find_python_project_files(root):
    found = 0
    with tqdm(desc="Scanning folders", unit="dir") as pbar:
        for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
            # Skip ignored dirs and symlinks
            dirnames[:] = [
                d for d in dirnames
                if d not in IGNORED_DIRS and not os.path.islink(os.path.join(dirpath, d))
            ]

            pbar.update(1)

            for filename in filenames:
                if filename in {"pyproject.toml", "setup.py"}:
                    found += 1
                    pbar.set_postfix_str(f"found: {found}")
                    yield os.path.join(dirpath, filename)

    tqdm.write(f"Found {found} Python project files.")


def parse_pyproject_toml(path):
    try:
        with open(path, "rb") as f:
            data = tomllib.load(f)
        if "project" in data:
            return data["project"].get("name"), data["project"].get("version")
        elif "tool" in data and "poetry" in data["tool"]:
            poetry = data["tool"]["poetry"]
            return poetry.get("name"), poetry.get("version")
    except Exception as e:
        print(f"Failed to parse {path}: {e}")
    return None, None


def parse_setup_py(path):
    try:
        with open(path, "r") as f:
            tree = ast.parse(f.read(), filename=path)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and getattr(node.func, 'id', '') == 'setup':
                kwargs = {kw.arg: ast.literal_eval(kw.value) for kw in node.keywords}
                return kwargs.get("name"), kwargs.get("version")
    except Exception as e:
        print(f"Failed to parse {path}: {e}")
    return None, None
