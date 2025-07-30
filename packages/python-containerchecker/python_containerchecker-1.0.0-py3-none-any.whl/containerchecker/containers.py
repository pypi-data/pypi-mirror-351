import logging

from rich import print  # pylint: disable=redefined-builtin
from rich.table import Table

from containerchecker.constants import console

logger = logging.getLogger("rich")


def check_installed_package(ssh_client, package_name):
    """Check if a package is installed on the remote server."""
    try:
        stdin, stdout, stderr = ssh_client.exec_command(f"command -v {package_name}")
        output = stdout.read().decode()
        error = stderr.read().decode()
        logger.debug(f"Command output: {output}")
        logger.debug(f"Command error: {error}")
        return bool(output.strip())
    except Exception as e:
        logger.exception(f"Failed to check installed package {package_name}: {e}")
        return False


def get_running_containers(ssh_client, package_name):
    """Get the list of running containers on the remote server."""
    try:
        if package_name == "docker":
            command = 'docker ps --format "{{.Names}} {{.ID}}"'
        elif package_name == "podman":
            command = 'podman ps --format "{{.Names}} {{.ID}}"'
        elif package_name == "/usr/local/bin/docker":
            command = '/usr/local/bin/docker ps --format "{{.Names}} {{.ID}}"'
        else:
            return []

        stdin, stdout, stderr = ssh_client.exec_command(command)
        output = stdout.read().decode()
        error = stderr.read().decode()
        logger.debug(f"Command output: {output}")
        logger.debug(f"Command error: {error}")
        containers = output.splitlines()
        return [container.split() for container in containers]
    except Exception as e:
        logger.exception(f"Failed to get running containers for {package_name}: {e}")
        return []


def sort_containers(containers):
    """Sort containers by name."""
    return sorted(containers, key=lambda x: x[0])


def display_containers(ssh_client, package_name, host):
    """Display running containers on the server."""
    logger.debug(f"Displaying running {package_name} containers on {host}")
    if containers := get_running_containers(ssh_client, package_name):
        sorted_containers = sort_containers(containers)
        num_containers = len(sorted_containers)
        #  sourcery skip: extract-method
        print(
            f"{num_containers} running {package_name.capitalize()} containers on [bold green]{host}[/bold green]:"
        )
        table = Table()
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("ID", style="magenta")
        for container in sorted_containers:
            table.add_row(container[0], container[1])
        console.print(table)
    else:
        console.print(
            f"No running {package_name.capitalize()} containers on [bold yellow]{host}[/bold yellow]."
        )
    console.print("")
