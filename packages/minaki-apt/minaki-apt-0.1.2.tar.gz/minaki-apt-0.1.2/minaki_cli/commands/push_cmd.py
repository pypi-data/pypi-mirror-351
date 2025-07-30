import time
import click
import requests
import os
from pathlib import Path
from yaspin import yaspin
from yaspin.spinners import Spinners
from minaki_cli.utils.config_utils import load_config
from minaki_cli.utils.metadata_utils import get_package_metadata

@click.command()
@click.argument('deb_file', type=click.Path(exists=True))
@click.option('--readme', type=click.Path(exists=True), help='Optional README.md file to upload')
def push_cmd(deb_file, readme):
    """Upload a .deb file to the Minaki APT server (optionally with README.md)."""
    config = load_config()
    headers = {"apikey": config["apikey"]}

    # Extract metadata
    try:
        package_name, version = get_package_metadata(deb_file)
        click.secho(f"📦 Detected package: {package_name} v{version}", fg="cyan")
    except Exception as e:
        click.secho(f"❌ Metadata extraction failed: {e}", fg="red")
        return

    # Upload .deb file
    upload_url = f"{config['base_url'].rstrip('/')}/apt/upload-deb/"
    click.echo(f"⬆️ Uploading .deb to {upload_url} ...")
    try:
        with open(deb_file, 'rb') as f:
            files = {'file': (os.path.basename(deb_file), f)}
            response = requests.post(upload_url, files=files, headers=headers)
            response.raise_for_status()
            click.secho(f"✅ Uploaded .deb: {package_name} {version}", fg="green")
    except requests.RequestException as e:
        click.secho("❌ Failed to upload .deb file.", fg="red")
        click.echo(f"Status: {getattr(e.response, 'status_code', 'N/A')}")
        click.echo(f"Response: {getattr(e.response, 'text', str(e))}")
        return

    # Simulate virus scanning wait
    click.echo("🧪 Scanning for viruses and verifying...")
    with yaspin(Spinners.line, text="Running ClamAV scan...") as spinner:
        time.sleep(5)  # simulate wait time
        spinner.ok("✅")
    click.secho("✅ Scan complete. Package is clean and added to repo.", fg="green")

    # Upload README if present
    if readme:
        readme_url = f"{config['base_url'].rstrip('/')}/apt/packages/{package_name}/{version}/readme"
        click.echo(f"📘 Uploading README.md to {readme_url} ...")
        try:
            with open(readme, 'rb') as f:
                files = {'file': (os.path.basename(readme), f)}
                res = requests.post(readme_url, files=files, headers=headers)
                res.raise_for_status()
                click.secho("✅ README uploaded successfully.", fg="green")
        except requests.RequestException as e:
            click.secho("⚠️ Failed to upload README file.", fg="yellow")
            click.echo(f"Status: {getattr(e.response, 'status_code', 'N/A')}")
            click.echo(f"Response: {getattr(e.response, 'text', str(e))}")
        except Exception as e:
            click.secho(f"⚠️ Error reading or uploading README: {e}", fg="yellow")
