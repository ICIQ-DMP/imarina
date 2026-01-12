"""
The responsibility of this file is to implement the functions that will be called when calling each subcommand in the
CLI. Each function is responsible for attending a single subcommand with their arguments specified through the function
typehint arguments using Typer. Each function will build a Settings object with the CLI overrides, arguments and default
settings, which will be passed to the function and run a command.
Each function will also be responsible for aborting execution with CLI arguments that are impossible. This only applies
to data coming from the CLI, the syntax of the overrides is not responsibility of the function of these files.
"""

from __future__ import annotations

import typer
from rich.console import Console

import imarina.commands.build.cli
import imarina.core.cli_global

console = Console()
app = typer.Typer(
    add_completion=False, help="imarina CLI", no_args_is_help=True
)  # TODO Completion does not work

# Use the imported modules directly
app.callback()(imarina.core.cli_global.cli_global_callback)

app.command("build")(imarina.commands.build.cli.build_controller)

if __name__ == "__main__":
    app()