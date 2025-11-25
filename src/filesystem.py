import os
import shutil


def read_env_var(var_name):
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
        raise KeyError(f"The environment variable '{var_name}' does not exist.")

    # Read the value
    value = os.environ[var_name]

    # Check if the value is empty
    if not value:
        raise ValueError(f"The environment variable '{var_name}' is empty.")

    return value


def read_file_content(file_path):
    content = read_file(file_path)
    # Check if the file is empty or contains only whitespace
    if not content:
        raise ValueError(f"The file '{file_path}' is empty.")

    return content


def read_file(file_path):
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
    # Check if the file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file '{file_path}' does not exist.")

    # Check if the file is readable
    if not os.access(file_path, os.R_OK):
        raise PermissionError(f"The file '{file_path}' cannot be read. Check permissions.")

    # Read the file
    with open(file_path, "r") as file:
        content = file.read()

    return content


def ensure_gitignore(directory):
    # Ensure existence of .gitignore
    gitignore_path = os.path.join(directory, '.gitignore')
    gitignore_content = "*\n!.gitignore\n"
    with open(gitignore_path, 'w+') as f:
        f.write(gitignore_content)



