import json
from pathlib import Path
import xdg.BaseDirectory


class ConfigManager:
    def __init__(self):
        self.config_dir = Path(xdg.BaseDirectory.save_config_path("vodka"))
        self.config_file = self.config_dir / "config.json"
        self.default_config = {
            "wine_default": "NONE",
            "prefixes_path": str(Path.home() / ".local/share/vodka/prefixes"),
            "download_path": str(Path.home() / ".local/share/vodka/downloads")
        }

    def load(self):
        if self.config_file.exists():
            with open(self.config_file) as f:
                return json.load(f)
        return self.save(self.default_config)

    def save(self, config):
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=4)
        return config
