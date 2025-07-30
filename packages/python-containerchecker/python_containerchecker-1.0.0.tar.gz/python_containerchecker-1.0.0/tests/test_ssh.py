import unittest
import warnings
from unittest.mock import Mock

from cryptography.utils import CryptographyDeprecationWarning

from containerchecker.ssh import create_ssh_client

with warnings.catch_warnings(action="ignore", category=CryptographyDeprecationWarning):
    import paramiko


class TestSSH(unittest.TestCase):
    def test_create_ssh_client_with_password_authentication(self):
        ssh_client = Mock()
        ssh_client.connect.return_value = None
        with unittest.mock.patch(
            "containerchecker.ssh.paramiko.SSHClient", return_value=ssh_client
        ):
            result = create_ssh_client("hostname", 22, "username", "password")
            self.assertIsNotNone(result)
            ssh_client.connect.assert_called_once_with(
                "hostname", 22, username="username", password="password", timeout=10
            )

    def test_create_ssh_client_with_key_authentication(self):
        ssh_client = Mock()
        ssh_client.connect.return_value = None
        key = Mock()
        with (
            unittest.mock.patch(
                "containerchecker.ssh.paramiko.SSHClient", return_value=ssh_client
            ),
            unittest.mock.patch(
                "containerchecker.ssh.paramiko.Ed25519Key.from_private_key_file",
                return_value=key,
            ),
        ):
            result = create_ssh_client(
                "hostname",
                22,
                "username",
                key_filename="keyfile",
                key_password="keypassword",
            )
            self.assertIsNotNone(result)
            ssh_client.connect.assert_called_once_with(
                "hostname", 22, username="username", pkey=key, timeout=10
            )

    def test_create_ssh_client_with_invalid_credentials(self):
        result = create_ssh_client("hostname", 22, "username", "password")
        self.assertIsNone(result)

    def test_create_ssh_client_with_authentication_error(self):
        ssh_client = Mock()
        ssh_client.connect.side_effect = paramiko.AuthenticationException(
            "Authentication failed."
        )
        result = create_ssh_client("hostname", 22, "username", "password")
        self.assertIsNone(result)

    def test_create_ssh_client_with_ssh_connection_error(self):
        ssh_client = Mock()
        ssh_client.connect.side_effect = paramiko.SSHException("SSH connection failed.")
        result = create_ssh_client("hostname", 22, "username", "password")
        self.assertIsNone(result)

    def test_create_ssh_client_with_other_error(self):
        ssh_client = Mock()
        ssh_client.connect.side_effect = Exception("An error occurred.")
        result = create_ssh_client("hostname", 22, "username", "password")
        self.assertIsNone(result)
