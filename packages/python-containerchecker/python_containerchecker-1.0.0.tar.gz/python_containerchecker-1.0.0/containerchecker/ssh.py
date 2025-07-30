import logging
import warnings

from cryptography.utils import CryptographyDeprecationWarning

with warnings.catch_warnings(action="ignore", category=CryptographyDeprecationWarning):
    import paramiko

from rich import print  # pylint: disable=redefined-builtin

from containerchecker.constants import USER_HOME
from containerchecker.containers import check_installed_package, display_containers

logger = logging.getLogger("rich")


def create_ssh_client(
    hostname,
    port,
    username,
    password=None,
    key_filename=None,
    key_password=None,
    verbose=False,
):
    """Create an SSH client object."""
    logger.debug(f"Creating SSH client for {hostname}")
    try:  # pylint: disable=too-many-try-statements
        ssh_key_file_path = f"{USER_HOME}/.ssh/{key_filename}"
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        if key_filename:
            # if using rsa keys then need to use RSAKey instead of Ed25519Key
            key = paramiko.Ed25519Key.from_private_key_file(
                ssh_key_file_path, password=key_password
            )
            ssh.connect(hostname, port, username=username, pkey=key, timeout=10)
            logger.debug(f"Connected to {hostname}")
        else:
            ssh.connect(
                hostname, port, username=username, password=password, timeout=10
            )
        return ssh
    except paramiko.AuthenticationException as e:
        if verbose:
            logger.exception(f"Authentication failed: {e}")
            print(f"Authentication failed: {e}")
        else:
            logger.debug(f"Authentication failed: {e}")
            print("Failed to authenticate.")
    except paramiko.SSHException as e:
        if verbose:
            logger.exception(f"SSH connection failed: {e}")
            print(f"SSH connection failed: {e}")
        else:
            logger.debug(f"SSH connection failed: {e}")
            print("SSH connection failed.")
    except FileNotFoundError:
        if verbose:
            logger.exception(f"Private key file not found: {key_filename}")
            print(f"Private key file not found: {key_filename}")
        else:
            logger.debug(f"Private key file not found: {key_filename}")
            print("Private key file not found.")
    except Exception as e:
        if verbose:
            logger.exception(f"An error occurred: {e}")
            print(f"An error occurred: {e}")
        else:
            logger.debug(f"An error occurred: {e}")
            print("An unknown error occurred during SSH connection.")
    return None


def process_server(
    host, port, user, password, ssh_key, ssh_key_password, verbose=False
):
    """Process a server."""
    logger.debug(f"Processing server: {host}")
    try:
        ssh_client = create_ssh_client(
            host, port, user, password, ssh_key, ssh_key_password, verbose=verbose
        )

        if ssh_client is None:
            print(f"Failed to connect to [bold red]{host}[/bold red]\n")
            return

        # # Check the environment and PATH for debugging purposes
        # stdin, stdout, stderr = ssh_client.exec_command("echo $PATH")
        # path_output = stdout.read().decode().strip()
        # logger.debug(f"PATH on {host}: {path_output}")

        if check_installed_package(ssh_client, "podman"):
            logger.debug(f"Podman is installed on {host}")
            display_containers(ssh_client, "podman", host)
        elif check_installed_package(ssh_client, "docker"):
            logger.debug(f"Docker is installed on {host}")
            display_containers(ssh_client, "docker", host)
        # TODO
        # poor workaround for being unable to find docker on a synologynas
        # the enviornment and path seem to be different and setting the path does not seem to work
        # need to investigate further
        elif check_installed_package(ssh_client, "/usr/local/bin/docker"):
            logger.debug(f"Docker is installed on {host}")
            display_containers(ssh_client, "/usr/local/bin/docker", host)
        else:
            logger.debug(f"Neither Podman nor Docker is installed on {host}")
            print(
                f"Neither Podman nor Docker is installed on [bold yellow]{host}[/bold yellow]."
            )

    except Exception as e:
        if verbose:
            logger.exception(f"Failed to connect to {host}: {e}")
            print(f"Failed to connect to {host}: {e}")
        else:
            logger.debug(f"Failed to connect to {host}: {e}")
            print(f"Failed to connect to [bold red]{host}[/bold red]\n")
    finally:
        if "ssh_client" in locals() and ssh_client:
            ssh_client.close()
