import os
import json

from tqdm import tqdm

IGNORED_DIRS = {
    "node_modules", "dist", "build", ".git",
    ".venv", "env", "__pycache__", ".cache"
}


def find_node_project_files(root):
    found = 0
    with tqdm(desc="Scanning folders", unit="dir") as pbar:
        for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
            # Remove ignored dirs and symlinks from traversal
            dirnames[:] = [
                d for d in dirnames
                if d not in IGNORED_DIRS and not os.path.islink(os.path.join(dirpath, d))
            ]

            pbar.update(1)

            if "package.json" in filenames:
                found += 1
                pbar.set_postfix_str(f"found: {found}")
                yield os.path.join(dirpath, "package.json")

    tqdm.write(f"Found {found} Node.js project files.")


def detect_package_manager(folder):
    if os.path.exists(os.path.join(folder, "pnpm-lock.yaml")):
        return "pnpm"
    elif os.path.exists(os.path.join(folder, "yarn.lock")):
        return "yarn"
    elif os.path.exists(os.path.join(folder, "package-lock.json")):
        return "npm"
    return None


def parse_package_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("name"), data.get("version")
    except Exception as e:
        print(f"Failed to parse {path}: {e}")
    return None, None
