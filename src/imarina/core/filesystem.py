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

import os
from pathlib import Path

from imarina.core.exceptions import (
    EnvVarEmptyError,
    EnvVarMissingError,
    FileContentEmptyError,
    FileMissingError,
    FileUnreadableError,
)
from imarina.core.log_utils import get_logger

logger = get_logger(__name__)


def read_env_var(var_name: str) -> str:
    """
    Reads an environment variable.

    Args:
        var_name (str): Name of the environment variable.

    Returns:
        str: The value of the environment variable if valid.

    Raises:
        KeyError: If the environment variable does not exist.
        ValueError: If the environment variable is empty or contains only whitespace.
    """
    # Check if the environment variable exists
    if var_name not in os.environ:
        raise EnvVarMissingError(var_name)

    # Read the value
    value = os.environ[var_name]

    # Check if the value is empty
    if not value:
        raise EnvVarEmptyError(var_name)

    return value


def read_file_content(file_path: str | Path) -> str:
    content = read_file(file_path)

    if not content:
        raise FileContentEmptyError(file_path)

    return content


def read_file(file_path: str | Path) -> str:
    """
    Reads a file and returns its content.
    Handles edge cases such as the file not existing or being unreadable.

    Args:
        file_path (str): Path to the token file.

    Returns:
        str: The content of the file.

    Raises:
        FileNotFoundError: If the file does not exist.
        PermissionError: If the file cannot be read due to permission issues.
    """
    path = Path(file_path)

    # Check if the file exists
    if not path.exists():
        raise FileMissingError(file_path)

    # Check if the file is readable
    if not os.access(path, os.R_OK):
        raise FileUnreadableError(file_path)

    # Read the file
    return path.read_text()


def ensure_gitignore(directory: str | Path) -> None:
    # Ensure existence of .gitignore
    gitignore_path = Path(directory) / ".gitignore"
    gitignore_content = "*\n!.gitignore\n"
    gitignore_path.write_text(gitignore_content)
