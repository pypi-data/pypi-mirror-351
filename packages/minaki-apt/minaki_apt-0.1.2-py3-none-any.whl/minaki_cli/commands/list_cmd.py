import click
import requests
from minaki_cli.utils.config_utils import load_config  # assumes this exists

@click.command(name="list")
def list_cmd():
    """List all available .deb packages in the APT repo."""
    config = load_config()
    url = f"{config['base_url']}/apt/list-debs/"
    headers = {"apikey": config["apikey"]}
    try:
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        data = res.json()
        click.echo("📦 Available packages:")
        for p in data["packages"]:
            click.echo(f"- {p['package']} {p['version']} ({p['arch']})")
    except Exception as e:
        click.secho(f"⚠️ Failed to fetch package list: {e}", fg="red")
