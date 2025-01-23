from pathlib import Path
import json
import os


class ConfigManager:
    def __init__(self, base_dir=None):
        self.base_dir = Path(base_dir) if base_dir else Path.home() / ".vodka"
        self.config_file = self.base_dir / "config.json"
        self.default_config = {
            "wine_default": None,
            "prefixes_dir": str(self.base_dir / "prefixes"),
            "downloads_dir": str(self.base_dir / "downloads")
        }
        self.ensure_dirs()

    def ensure_dirs(self):
        """Ensure all required directories exist."""
        self.base_dir.mkdir(exist_ok=True)
        Path(self.default_config["prefixes_dir"]).mkdir(exist_ok=True)
        Path(self.default_config["downloads_dir"]).mkdir(exist_ok=True)

    def load(self):
        """Load configuration from file."""
        if not self.config_file.exists():
            return self.save(self.default_config)

        try:
            with open(self.config_file) as f:
                config = json.load(f)
                return {**self.default_config, **config}
        except Exception:
            return self.default_config

    def save(self, config):
        """Save configuration to file."""
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=4)
        return config

    def get(self, key, default=None):
        """Get a configuration value."""
        config = self.load()
        return config.get(key, default)

    def set(self, key, value):
        """Set a configuration value."""
        config = self.load()
        config[key] = value
        self.save(config)
