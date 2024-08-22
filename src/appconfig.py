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


def save_consumer_token(consumer_key, consumer_secret):
    config = load_config()
    config["consumer_key"] = consumer_key
    config["consumer_secret"] = consumer_secret
    save_config(config)


def load_consumer_token():
    config = load_config()
    consumer_key = config.get("consumer_key")
    consumer_secret = config.get("consumer_secret")
    return consumer_key, consumer_secret


def save_request_token(key, secret):
    config = load_config()
    config["resource_owner_key"] = key
    config["resource_owner_secret"] = secret
    save_config(config)


def load_request_token():
    config = load_config()
    key = config.get("resource_owner_key")
    secret = config.get("resource_owner_secret")
    return key, secret


def save_access_token(key, secret):
    config = load_config()
    config["access_token"] = key
    config["access_token_secret"] = secret
    save_config(config)


def load_access_token():
    config = load_config()
    key = config.get("access_token")
    secret = config.get("access_token_secret")
    return key, secret
