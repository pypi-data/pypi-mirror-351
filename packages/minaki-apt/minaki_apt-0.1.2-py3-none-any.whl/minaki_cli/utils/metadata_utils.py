import subprocess

def get_package_metadata(deb_file):
    try:
        pkg = subprocess.run(
            ['dpkg-deb', '-f', deb_file, 'Package'],
            stdout=subprocess.PIPE, text=True, check=True
        ).stdout.strip()
        ver = subprocess.run(
            ['dpkg-deb', '-f', deb_file, 'Version'],
            stdout=subprocess.PIPE, text=True, check=True
        ).stdout.strip()
        return pkg, ver
    except Exception as e:
        raise RuntimeError(f"Failed to extract metadata: {e}")

def get_package_metadata_bad(deb_file):
    try:
        result = subprocess.run(
            ['dpkg-deb', '-f', deb_file, 'Package', 'Version'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        lines = result.stdout.strip().split('\n')
        return lines[0], lines[1]
    except Exception as e:
        raise RuntimeError(f"Failed to extract metadata: {e}")
