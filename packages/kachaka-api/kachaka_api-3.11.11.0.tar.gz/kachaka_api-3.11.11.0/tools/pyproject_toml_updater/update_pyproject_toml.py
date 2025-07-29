import argparse
from pathlib import Path
import re
from typing import Any

import tomli
import tomlkit


def validate_version(version: str) -> bool:
    """
    Validate that the version string is in the format x.x.x.x

    Args:
        version: Version string to validate

    Returns:
        True if the version is valid, False otherwise
    """
    pattern = r"^\d+\.\d+\.\d+\.\d+$"
    return bool(re.match(pattern, version))


def update_pyproject_toml(
    source_toml_path: Path, target_toml_path: Path, new_version: str
) -> None:
    """
    Update target pyproject.toml with dependencies from source and set a new version

    Args:
        source_toml_path: Path to the source pyproject.toml to extract dependencies from
        target_toml_path: Path to the target pyproject.toml to update
        new_version: New version to set in the target pyproject.toml

    Raises:
        ValueError: If the new_version is not in the format x.x.x.x
    """
    # Validate version format
    if not validate_version(new_version):
        raise ValueError(
            f"Invalid version format: {new_version}. Expected format: x.x.x.x (e.g., 1.2.3.4)"
        )

    # Read source toml file to extract dependencies
    with source_toml_path.open("rb") as f:
        source_data: dict[str, Any] = tomli.load(f)

    # Get dependencies from source
    source_dependencies: list[str] = source_data.get("project", {}).get(
        "dependencies", []
    )

    # Read target toml file using tomlkit to preserve formatting and comments
    with target_toml_path.open("r") as f:
        target_doc = tomlkit.parse(f.read())

    # Update version
    target_doc["project"]["version"] = new_version

    # Update dependencies
    target_doc["project"]["dependencies"] = tomlkit.array(source_dependencies)

    # Write updated toml
    with target_toml_path.open("w") as f:
        f.write(tomlkit.dumps(target_doc))

    print(
        f"Updated {target_toml_path} with new version {new_version} and dependencies from {source_toml_path}"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Update pyproject.toml with dependencies from another toml file"
    )
    parser.add_argument("source_toml", help="Path to source pyproject.toml")
    parser.add_argument("target_toml", help="Path to target pyproject.toml")
    parser.add_argument("new_version", help="New version to set (format: x.x.x.x)")

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    try:
        update_pyproject_toml(
            Path(args.source_toml), Path(args.target_toml), args.new_version
        )
    except ValueError as e:
        print(f"エラー: {e}")
        exit(1)


if __name__ == "__main__":
    main()
