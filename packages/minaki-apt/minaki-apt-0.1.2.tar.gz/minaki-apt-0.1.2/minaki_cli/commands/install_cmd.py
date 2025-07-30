import click
import os
from pathlib import Path

@click.command()
def install_cmd():
    """Install bash autocompletion for minaki-cli."""
    home = str(Path.home())
    script_path = os.path.join(home, ".minaki_cli_complete.sh")

    # Generate autocompletion script
    click.echo(f"🔧 Generating completion script at: {script_path}")
    os.system(f"_MINAKI_CLI_COMPLETE=source_bash minaki-cli > {script_path}")

    # Add to .bashrc if not already added
    bashrc_path = os.path.join(home, ".bashrc")
    source_line = f"source {script_path}"
    with open(bashrc_path, "a+") as f:
        f.seek(0)
        contents = f.read()
        if source_line not in contents:
            f.write(f"\n# Minaki CLI autocomplete\n{source_line}\n")
            click.echo(f"✅ Added autocompletion to {bashrc_path}")
        else:
            click.echo("ℹ️ Autocompletion already present in .bashrc")

    click.echo("💡 Reload your shell or run: `source ~/.bashrc` to enable.")
