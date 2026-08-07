# imarina-load - Automated imarina data loads
# Copyright (C) 2026  Aleix Mariné Tena (AleixMT) and Sonia Sayalero
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
import imarina.commands.download.cli
import imarina.commands.notify.cli
import imarina.commands.publish.cli
import imarina.commands.upload.cli
import imarina.core.cli_global

console = Console()
app = typer.Typer(add_completion=False, help="imarina CLI", no_args_is_help=True)

# Use the imported modules directly
app.callback()(imarina.core.cli_global.cli_global_callback)


app.command("build")(imarina.commands.build.cli.build_controller)
app.command("download")(imarina.commands.download.cli.download_controller)
app.command("upload")(imarina.commands.upload.cli.upload_controller)
app.command("publish")(imarina.commands.publish.cli.publish_controller)
app.command("notify")(imarina.commands.notify.cli.notify_controller)

if __name__ == "__main__":
    app()
