# ruff: noqa: D103,D104,E501,S603,S607,ERA001,FIX002,TD002,TD003
import os
import subprocess
import sys
from pathlib import Path

import typer  # type: ignore

from pystruction.commands import (
    initialize_git,
    initialize_project,
    setup_testing,
    setup_documentation,
    setup_code_analysis,
    setup_deployment,
    setup_interactivity,
    setup_precommit,
    setup_logging,
    setup_linter,
    setup_security,
    setup_recipes,
)


def is_project_folder(current_directory: Path) -> bool:
    """Check if the current directory is a project folder.

    The current directory is considered a project folder if it is empty or only contains a .git directory.

    :param current_directory: The current directory to check.
    :return: True if the current directory is a project folder, False otherwise.
    """
    # List all files and directories in the current directory
    contents = list(Path.iterdir(current_directory))

    typer.echo(f"Contents of the current directory: {contents}")

    if not contents:
        return True

    return all(
        [len(contents) == 1, contents[0].name == ".git", Path.is_dir(contents[0])]
    )


def check_guess(input_field: str, default_value: str) -> str:
    """Ask for user input, provide default values as guess.

    :param input_field: The field to ask the user to input.
    :param default_value: The default value to use if the user doesn't input anything.
    :return: The input value, or the default value if the user didn't input anything.
    """
    input_value = input(f"{input_field} [{default_value}]:")

    return input_value if input_value else default_value


def get_config(current_directory: Path) -> dict[str, str]:
    """Get the project configuration settings.

    The values that are asked are:
    - Project Name: Name of the project. The default is the name of the current directory.
    - Author Name: Name of the author. The default is the name configured in git.
    - Version: Initial version of the project. The default is 0.1.0.
    - Python Version: Version of Python to use. The default is current version.

    :param current_directory: The current directory to use for guesses.
    :return: A dictionary with the config values.
    """
    guess_project = current_directory.stem
    guess_author = (
        subprocess.run(["git", "config", "user.name"], capture_output=True, check=False)
        .stdout.strip()
        .decode()
    )
    guess_python_version = (
        f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    )

    config: dict[str, str] = {}

    config["project"] = check_guess("Project Name", guess_project)
    config["author"] = check_guess("Author Name", guess_author)
    config["version"] = check_guess("Version", "0.1.0")
    config["python_version"] = check_guess("Python Version", guess_python_version)

    return config


def main() -> None:
    typer.echo("Hello from pystruction!")

    # project_name = input("What is your project name? ")
    project_name = "testproject"

    os.chdir("..")

    typer.echo(Path.cwd())

    # TODO: Remove when development is done
    subprocess.run(["rm", "-rf", project_name], check=False)

    # Create project directory
    path = Path(project_name)
    path.mkdir(exist_ok=True)
    os.chdir(path)

    typer.echo(Path.cwd())

    initialize_project()
    initialize_git()
    setup_logging()
    setup_interactivity()
    setup_testing(project_name)
    setup_documentation()
    setup_deployment(project_name)
    setup_code_analysis()
    setup_precommit(project_name)
    setup_linter()
    setup_security()
    setup_recipes(project_name)
