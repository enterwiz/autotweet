import json
import os


def load_config():
    if os.path.exists("config.json"):
        with open("config.json", "r") as f:
            return json.load(f)
    return {}


def save_config(config):
    with open("config.json", "w") as f:
        json.dump(config, f)
