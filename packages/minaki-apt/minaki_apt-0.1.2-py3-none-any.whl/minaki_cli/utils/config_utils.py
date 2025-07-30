import os
import json
import click

CONFIG_PATH = os.path.expanduser("~/.minaki/config.json")

def load_config():
    if not os.path.exists(CONFIG_PATH):
        click.secho("❌ Config file not found. Run `minaki config` first.", fg="red")
        exit(1)
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)

def save_config(apikey, base_url):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, 'w') as f:
        json.dump({"apikey": apikey, "base_url": base_url}, f)
    click.secho("✅ Config saved!", fg="green")
