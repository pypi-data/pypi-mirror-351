import click
from minaki_cli.utils.config_utils import save_config

@click.command()
@click.argument("apikey")
@click.argument("base_url")
def config_cmd(apikey, base_url):
    """Save API key and base URL"""
    save_config(apikey, base_url)
