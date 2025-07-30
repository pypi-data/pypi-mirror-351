import click

from minaki_cli.commands.config_cmd import config_cmd
from minaki_cli.commands.push_cmd import push_cmd
from minaki_cli.commands.list_cmd import list_cmd
from minaki_cli.commands.delete_cmd import delete_cmd
from minaki_cli.commands.install_cmd import install_cmd

@click.group()
def cli():
    """Minaki APT CLI Tool"""
    pass

cli.add_command(config_cmd, name="config")
cli.add_command(push_cmd, name="push")
cli.add_command(list_cmd, name="list")
cli.add_command(delete_cmd, name="delete")
cli.add_command(install_cmd, name="install")

if __name__ == '__main__':
    cli()
