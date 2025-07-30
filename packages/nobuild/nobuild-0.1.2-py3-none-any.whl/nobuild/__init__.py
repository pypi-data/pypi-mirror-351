import subprocess
import os
import platform
from typing import Annotated, Optional

import typer
from typer import Typer
from rich.console import Console

app = Typer()

@app.command(name="cleanup")
def cleanup(distro: str = "debian"):
    console = Console()
    if platform.system() != "Linux":
        console.print("[red]ERR[/red]: nobuild supports Linux only.")
    if os.getuid() == 0:
        subprocess.run(f"nobuild-{distro} clean", shell=True)
    else:
        console.print("[red]ERR[/red]: Root privileges are required")

@app.command(name="generate")
def generate(distro: str = "debian", flavor: Annotated[Optional[str], typer.Option()] = None):
    console = Console()
    if platform.system() != "Linux":
        console.print("[red]ERR[/red]: nobuild supports Linux only.")
    if os.getuid() == 0:
        if os.path.isdir("./flavors"):
            subprocess.run(f"nobuild-{distro} step --flavor {flavor}", shell=True)
        else:
            subprocess.run(f"nobuild-{distro} step", shell=True)
    else:
        console.print("[red]ERR[/red]: Root privileges are required")