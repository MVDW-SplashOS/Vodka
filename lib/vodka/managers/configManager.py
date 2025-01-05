import xdg.BaseDirectory
import json
import os

config_path = os.path.join(xdg.BaseDirectory.save_config_path("vodka"), "config.json");
default_config = {
    "wine_default": "NONE"
}

def getConfiguration():
    if os.path.exists(config_path):
        with open(config_path, 'r') as conf:
            return json.load(conf)
    else:
        return saveConfiguration(default_config);

def saveConfiguration(data):
    with open(config_path, 'w') as conf:
        json.dump(data, conf, indent=4)
    return data
