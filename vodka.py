#!/usr/bin/env python3
import json
import os
import sys
import subprocess
import tarfile
import urllib.request
from pathlib import Path

VODKA_DIR = Path.home() / ".vodka"
VERSIONS_FILE = VODKA_DIR / "versions.json"
DEFAULT_LINK = VODKA_DIR / "default"

def download_versions():
    versions_url = "https://raw.githubusercontent.com/MVDW-Java/vodka/main/versions.json"
    try:
        urllib.request.urlretrieve(versions_url, VERSIONS_FILE)
        print("Successfully downloaded versions list")
    except Exception as e:
        print(f"Error downloading versions: {e}")
        return False
    return True

def load_versions():
    if not VERSIONS_FILE.exists():
        if not download_versions():
            return []

    with open(VERSIONS_FILE) as f:
        return json.load(f)

def is_installed(version_name):
    return (VODKA_DIR / version_name).exists()

def is_default(version_name):
    if not DEFAULT_LINK.exists() or not is_installed(version_name):
        return False
    try:
        return (VODKA_DIR / version_name).samefile(DEFAULT_LINK)
    except FileNotFoundError:
        return False

def set_default(version_name):
    if not is_installed(version_name):
        print(f"Error: Version {version_name} is not installed")
        return False

    if DEFAULT_LINK.exists():
        DEFAULT_LINK.unlink()
    DEFAULT_LINK.symlink_to(VODKA_DIR / version_name)
    print(f"Set {version_name} as default")
    return True

def install_version(version_name):
    versions = load_versions()
    version = next((v for v in versions if v["name"].lower() == version_name.lower()), None)

    if not version:
        print(f"Error: Version {version_name} not found")
        return False

    install_dir = VODKA_DIR / version["name"]
    if install_dir.exists():
        print(f"Version {version_name} is already installed")
        return True

    print(f"Downloading {version['name']}...")
    tar_path = VODKA_DIR / f"{version['name']}.tar.gz"

    urllib.request.urlretrieve(version["uri"], tar_path)

    print("Extracting...")
    with tarfile.open(tar_path) as tar:
        tar.extractall(VODKA_DIR)

    tar_path.unlink()  # Clean up tar file

    # If this is the only version installed, set it as default
    installed_versions = [d for d in VODKA_DIR.iterdir() if d.is_dir()]
    if len(installed_versions) == 1:
        set_default(version["name"])

    print(f"Successfully installed {version['name']}")
    return True

def list_versions():
    versions = load_versions()
    print("Available versions:")
    print("------------------")
    for version in versions:
        status = "installed" if is_installed(version["name"]) else "not installed"
        default = " (default)" if is_default(version["name"]) else ""
        print(f"{version['name']}: {status}{default}")

def main():
    # Create vodka directory if it doesn't exist
    VODKA_DIR.mkdir(exist_ok=True)

    if len(sys.argv) < 2:
        print("Usage: vodka <command> [args]")
        print("Commands:")
        print("  install <version>   - Install a specific version")
        print("  default <version>   - Set default version")
        print("  list               - List all available versions")
        print("  refresh            - Refresh versions list")
        return

    command = sys.argv[1].lower()

    if command == "install" and len(sys.argv) == 3:
        install_version(sys.argv[2])
    elif command == "default" and len(sys.argv) == 3:
        set_default(sys.argv[2])
    elif command == "list":
        list_versions()
    elif command == "refresh":
        download_versions()
    else:
        print("Invalid command")

if __name__ == "__main__":
    main()
