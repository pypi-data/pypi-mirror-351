import os
import subprocess
import shutil
import hashlib

from rich.console import Console

from ...config import load_config
from ...types import Config
from ...pkg import get_package_list

from .repo import copy_files, copy_repo

debian_versions = {
    "1.1": "buzz",
    "1.2": "rex",
    "1.3": "bo",
    "2": "hamm",
    "2.1": "slink",
    "2.2": "potato",
    "3": "woody",
    "3.1": "sarge",
    "4": "etch",
    "5": "lenny",
    "6": "squeeze",
    "7": "wheezy",
    "8": "jessie",
    "9": "stretch",
    "10": "buster",
    "11": "bullseye",
    "12": "bookworm",
    "13": "trixie",
    "14": "forky",
    "sid": "sid",
    "testing": "testing",
    "stable": "stable"
}

def calculate_sha256(file_path):
    sha256_hash = hashlib.sha256()
    
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    
    return sha256_hash.hexdigest()

def set_mirror(url: str):
    subprocess.run(f'lb config --mirror-bootstrap "{url}"', cwd="./work", shell=True)
    subprocess.run(f'lb config --mirror-chroot "{url}"', cwd="./work", shell=True)
    subprocess.run(f'lb config --mirror-binary "{url}"', cwd="./work", shell=True)

def set_arch(arch: str):
    subprocess.run(f'lb config -a {arch}', cwd="./work", shell=True)

def set_base_version(version: str):
    subprocess.run(f'lb config --distribution {version}', cwd="./work", shell=True)

def dump_filename(text: str, **kwargs):
    return text.replace("${name}", kwargs["name"]).replace("${version}", kwargs["version"]).replace("${arch}", kwargs["arch"])

def generate(flavor: str | None = None):
    console = Console()

    config: Config = load_config()
    version = config['base']['version']
    architecture = config['base']['architecture']
    mirror = config["extra"].get("mirror")

    console.print("nobuild-debian")
    console.print(f"base: {version}-{architecture}")
    os.makedirs("./dist", exist_ok=True)

    if os.path.isdir("./work"):
        console.print("Old configuration found. reusing...")
        subprocess.run("lb clean --binary", shell=True, cwd="./work")
    else:
        console.print("Generating live-build configuration...")
        cmd = 'lb config --archive-areas "main contrib non-free non-free-firmware" --bootloaders "grub-efi grub-pc" --bootappend-live "boot=live components"'
        os.makedirs("./work", exist_ok=True)
        subprocess.run(cmd, cwd="./work", shell=True)
    set_arch(architecture)
    set_base_version(debian_versions.get(version, version))
    if mirror:
        set_mirror(mirror)

    copy_repo()
    with open("./work/config/package-lists/standard.list.chroot", "w") as f:
        f.write("! Packages Priority standard")
    with open("./work/config/package-lists/base.list.chroot", "w") as f:
        f.write("\n".join(get_package_list()))
    copy_files()
    if flavor:
        copy_repo(f"./src/flavor/{flavor}/repo")
        copy_files(f"./src/flavor/{flavor}/files")
        with open(f"./work/config/package-lists/{flavor}.list.chroot", "w") as f:
            f.write("\n".join(get_package_list(f"./src/flavor/{flavor}/packages.nv")))

    console.print("Building Distro....")
    subprocess.run("lb build", cwd="./work", shell=True)

    filename = config["build"]["filename"]
    filename = dump_filename(filename, name=config["main"]["name"], version=config["main"]["version"], arch=config["base"]["architecture"])
    
    shutil.move(f"./work/live-image-{architecture}.hybrid.iso", f"./dist/{filename}")
    console.print("Generating hash....")
    with open(f"./dist/{filename}.sha256", "w") as f:
        f.write(calculate_sha256(f"./dist/{filename}"))
    console.print("Done!")