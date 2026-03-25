"""19 VPN Client — Configuration and storage."""

import os
import json

APP_NAME = "19 VPN"
APP_VERSION = "2.0.0"

CONFIG_DIR = os.path.expanduser("~/.19vpn")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
PROFILES_DIR = os.path.join(CONFIG_DIR, "profiles")

DEFAULT_CONFIG = {
    "api_url": "",
    "api_key": "",
    "auto_connect": False,
    "kill_switch": True,
    "dns": "1.1.1.1, 8.8.8.8",
    "active_profile": None,
    "last_connected": None,
}


def ensure_dirs():
    os.makedirs(CONFIG_DIR, mode=0o700, exist_ok=True)
    os.makedirs(PROFILES_DIR, mode=0o700, exist_ok=True)


def load_config() -> dict:
    ensure_dirs()
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()
    with open(CONFIG_FILE) as f:
        return json.load(f)


def save_config(config: dict):
    ensure_dirs()
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def list_profiles() -> list[str]:
    ensure_dirs()
    profiles = []
    for f in os.listdir(PROFILES_DIR):
        if f.endswith(".conf"):
            profiles.append(f.replace(".conf", ""))
    return sorted(profiles)


def save_profile(name: str, config_text: str):
    ensure_dirs()
    path = os.path.join(PROFILES_DIR, f"{name}.conf")
    with open(path, "w") as f:
        f.write(config_text)
    os.chmod(path, 0o600)


def load_profile(name: str) -> str | None:
    path = os.path.join(PROFILES_DIR, f"{name}.conf")
    if os.path.exists(path):
        with open(path) as f:
            return f.read()
    return None


def delete_profile(name: str) -> bool:
    path = os.path.join(PROFILES_DIR, f"{name}.conf")
    if os.path.exists(path):
        os.remove(path)
        return True
    return False
