import os
from pathlib import Path
from ..manager import VodkaManager
from ..configManager import ConfigManager


class WineManager:
    def __init__(self):
        self.vodka = VodkaManager()
        self.config = ConfigManager()

    def install_version(self, version):
        return self.vodka.install_version(version)

    def set_default(self, version):
        return self.vodka.set_default(version)

    def get_versions(self):
        return self.vodka.get_versions()

    def refresh_versions(self):
        return self.vodka.download_versions()

    def execute(self, version, command):
        return self.vodka.execute(version, command)
