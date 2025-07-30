import unittest
from unittest.mock import Mock

from containerchecker.containers import check_installed_package, get_running_containers


class TestContainers(unittest.TestCase):
    def test_check_installed_package(self):
        ssh_client = Mock()
        ssh_client.exec_command.return_value = (
            None,
            Mock(read=lambda: b"package_name"),
            ssh_client.read().decode(),  # not sure this is a correct way to do this
        )
        self.assertTrue(check_installed_package(ssh_client, "package_name"))

        ssh_client.exec_command.return_value = (None, Mock(read=lambda: b""), None)
        self.assertFalse(check_installed_package(ssh_client, "package_name"))

    def test_get_running_containers(self):
        # sourcery skip: extract-duplicate-method
        ssh_client = Mock()
        ssh_client.exec_command.return_value = (
            None,
            Mock(read=lambda: b"container1 123\ncontainer2 456"),
            ssh_client.read().decode(),
        )
        expected_result = [["container1", "123"], ["container2", "456"]]
        self.assertEqual(get_running_containers(ssh_client, "docker"), expected_result)

        ssh_client.exec_command.return_value = (None, Mock(read=lambda: b""), None)
        self.assertEqual(get_running_containers(ssh_client, "docker"), [])

        ssh_client.exec_command.return_value = (
            None,
            Mock(read=lambda: b"container3 789"),
            ssh_client.read().decode(),
        )
        expected_result = [["container3", "789"]]
        self.assertEqual(get_running_containers(ssh_client, "podman"), expected_result)

        ssh_client.exec_command.return_value = (None, Mock(read=lambda: b""), None)
        self.assertEqual(get_running_containers(ssh_client, "podman"), [])
