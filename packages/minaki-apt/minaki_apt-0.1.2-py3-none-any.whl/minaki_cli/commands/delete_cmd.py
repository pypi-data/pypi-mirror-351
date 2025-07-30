import click
import requests
from minaki_cli.utils.config_utils import load_config  # ← assumes you moved load_config here

@click.command()
@click.argument("package")
@click.argument("version")
@click.argument("arch")
def delete_cmd(package, version, arch):
    """Delete a .deb package from the repo."""
    config = load_config()
    url = f"{config['base_url']}/apt/delete-deb/{package}/{version}/{arch}"
    headers = {"apikey": config["apikey"]}
    try:
        res = requests.delete(url, headers=headers)
        res.raise_for_status()
        click.secho(f"✅ Deleted: {package} {version}", fg="green")
    except Exception as e:
        click.secho(f"⚠️ Failed to delete: {e}", fg="red")
