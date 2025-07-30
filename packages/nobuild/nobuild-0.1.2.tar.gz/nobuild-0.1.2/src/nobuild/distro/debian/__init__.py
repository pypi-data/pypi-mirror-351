from typing import Annotated, Optional
import platform
import os
import shutil

import typer
from typer import Typer
from rich.console import Console

from .generate import generate

app = Typer()

@app.command("clean", hidden=True)
def clean():
    shutil.rmtree("./work")
    shutil.rmtree("./dist")

@app.command("step", hidden=True)
def step(flavor: Annotated[Optional[str], typer.Option()] = None):
    console = Console()
    if platform.system() != "Linux":
        console.print("[red]ERR[/red]: nobuild-debian supports Debian-based linux only.")
    if os.getuid() != 0:
        console.print("[red]ERR[/red]: Root privileges are required")
        return
    generate(flavor)
    