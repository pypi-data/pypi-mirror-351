# Package Finder CLI

A command-line tool to recursively scan a directory for Node.js and Python projects. It extracts basic metadata (`name` and `version`) from project files like `package.json`, `pyproject.toml`, and `setup.py`, and outputs the results to a JSON file.

---

## ✨ Features

- ✅ Supports **Node.js** (`package.json`) with package manager detection (`npm`, `yarn`, `pnpm`)
- ✅ Supports **Python** (`pyproject.toml`, `setup.py`)
- ✅ Ignores unnecessary folders like `node_modules/`, `.git/`, `.venv/`, `dist/`, etc.
- ✅ Skips symlinked directories to avoid cycles and unnecessary traversal
- ✅ Displays real-time progress using `tqdm`
- ✅ Built with `click` for a clean subcommand-based CLI

---

## 🚀 Installation

```shell
pip install package-finder
```

## 📦 Usage

```shell
# Scan Python projects
find-package python <input_folder> <output.json>

# Scan Node.js projects
find-package node <input_folder> <output.json>
```