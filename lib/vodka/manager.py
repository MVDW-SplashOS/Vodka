import json
import os
import tarfile
import urllib.request
from pathlib import Path


class VodkaManager:
    def __init__(self, base_dir=None):
        self.base_dir = Path(base_dir) if base_dir else Path.home() / ".vodka"
        self.versions_file = self.base_dir / "versions.json"
        self.default_link = self.base_dir / "default"
        self.base_dir.mkdir(exist_ok=True)

    def download_versions(self):
        """Download the versions list from the repository."""
        versions_url = "https://raw.githubusercontent.com/MVDW-Java/vodka/refactor/data/wine.json"
        try:
            urllib.request.urlretrieve(versions_url, self.versions_file)
            return True
        except Exception as e:
            raise Exception(f"Error downloading versions: {e}")

    def load_versions(self):
        """Load and return the versions list."""
        if not self.versions_file.exists():
            self.download_versions()
        with open(self.versions_file) as f:
            data = json.load(f)
            # Flatten versions from all categories into a single list
            versions = []
            for category_versions in data['versions'].values():
                versions.extend(category_versions)
            return versions

    def is_installed(self, version_name):
        """Check if a specific version is installed."""
        return (self.base_dir / version_name).exists()

    def is_default(self, version_name):
        """Check if a specific version is set as default."""
        if not self.default_link.exists() or not self.is_installed(version_name):
            return False
        try:
            return (self.base_dir / version_name).samefile(self.default_link)
        except FileNotFoundError:
            return False

    def set_default(self, version_name):
        """Set a specific version as default."""
        if not self.is_installed(version_name):
            raise Exception(f"Version {version_name} is not installed")

        if self.default_link.exists():
            self.default_link.unlink()
        self.default_link.symlink_to(self.base_dir / version_name)
        return True

    def install_version(self, version_name):
        """Install a specific version."""
        version = self.find_version(version_name)
        if not version:
            raise Exception(f"Version {version_name} not found")

        install_dir = self.base_dir / version["name"]
        if install_dir.exists():
            return False  # Already installed

        # Download and extract
        tar_path = self.base_dir / f"{version['name']}.tar.gz"
        try:
            print(f"Downloading {version['name']}...")
            urllib.request.urlretrieve(version["uri"], tar_path)

            print(f"Extracting {version['name']}...")
            with tarfile.open(tar_path) as tar:
                tar.extractall(self.base_dir)
            tar_path.unlink()

            # Set as default if it's the only version
            installed_versions = [
                d for d in self.base_dir.iterdir() if d.is_dir()]
            if len(installed_versions) == 1:
                self.set_default(version["name"])

            return True
        except Exception as e:
            # Clean up on failure
            if tar_path.exists():
                tar_path.unlink()
            if install_dir.exists():
                import shutil
                shutil.rmtree(install_dir)
            raise Exception(f"Installation failed: {e}")

    def get_versions(self):
        """Get a list of all versions with their status."""
        versions = self.load_versions()
        return [{
            "name": version["name"],
            "installed": self.is_installed(version["name"]),
            "is_default": self.is_default(version["name"])
        } for version in versions]

    def find_version(self, version_name):
        """Find a version in any category by name"""
        try:
            with open(self.versions_file) as f:
                data = json.load(f)

            # Search through all categories
            for category_versions in data['versions'].values():
                for version in category_versions:
                    # Case insensitive comparison of the full version string
                    if version['name'].lower() == version_name.lower():
                        return version
            return None
        except Exception as e:
            raise Exception(f"Error finding version: {e}")
