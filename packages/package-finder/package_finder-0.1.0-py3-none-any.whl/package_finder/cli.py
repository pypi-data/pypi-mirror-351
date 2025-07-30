import json
import os

import click
from tqdm import tqdm

from package_finder.finders.node import find_node_project_files, parse_package_json, detect_package_manager
from package_finder.finders.python import parse_pyproject_toml, find_python_project_files, parse_setup_py


@click.group()
def cli():
    """Project metadata scanner CLI."""


@cli.command()
@click.argument("root_dir", type=click.Path(exists=True, file_okay=False))
@click.argument("output_json", type=click.Path(writable=True))
def python(root_dir, output_json):
    """Scan Python projects in ROOT_DIR and save to OUTPUT_JSON."""
    paths = list(find_python_project_files(root_dir))
    results = []

    for path in tqdm(paths, desc="Scanning Python projects"):
        base_folder = os.path.dirname(path)
        if path.endswith("pyproject.toml"):
            name, version = parse_pyproject_toml(path)
            project_format = "pyproject.toml"
        else:
            name, version = parse_setup_py(path)
            project_format = "setup.py"

        if name and version:
            results.append({
                "base_folder": base_folder,
                "project_format": project_format,
                "name": name,
                "version": version
            })

    with open(output_json, "w") as f:
        json.dump(results, f, indent=2)
    click.echo(f"Saved {len(results)} Python projects to {output_json}")


@cli.command()
@click.argument("root_dir", type=click.Path(exists=True, file_okay=False))
@click.argument("output_json", type=click.Path(writable=True))
def node(root_dir, output_json):
    """Scan Node.js projects in ROOT_DIR and save to OUTPUT_JSON."""
    print(f"finding projects at {root_dir}")
    paths = list(find_node_project_files(root_dir))
    results = []

    for path in tqdm(paths, desc="Scanning Node.js projects"):
        base_folder = os.path.dirname(path)
        name, version = parse_package_json(path)
        if name and version:
            results.append({
                "base_folder": base_folder,
                "project_format": "package.json",
                "name": name,
                "version": version,
                "package_manager": detect_package_manager(base_folder)
            })

    with open(output_json, "w") as f:
        json.dump(results, f, indent=2)
    click.echo(f"Saved {len(results)} Node.js projects to {output_json}")


if __name__ == "__main__":
    cli()
