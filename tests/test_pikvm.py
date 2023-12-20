import unittest
from tempfile import NamedTemporaryFile
from unittest.mock import patch, MagicMock
from pikvm_lib.pikvm import PiKVM
import mock_pikvm_response


class TestPiKVM(unittest.TestCase):
    def setUp(self):
        self.hostname = "example.com"
        self.username = "user"
        self.password = "password"
        self.secret = None
        self.mock_pikvm = patch('pikvm_lib.pikvm.PiKVM.get_system_info',
                                return_value=mock_pikvm_response.pikvm_mock_info).start()
        self.pikvm_instance = PiKVM(self.hostname, self.username, self.password, secret=self.secret, schema="https")

    def test_init_with_invalid_schema(self):
        with self.assertRaises(Exception):
            PiKVM('hostname', 'username', 'password', schema='ftp')

    def test_initialization(self):
        # Initialize the PiKVM instance
        pikvm = PiKVM(self.hostname, self.username, self.password, secret=self.secret, schema="https")

        self.assertEqual(pikvm.hostname, "example.com")
        self.assertEqual(pikvm.username, "user")
        self.assertEqual(pikvm.password, "password")

    @patch('pikvm_lib.pikvm.PiKVM._get')
    def test_auth(self, mock_get_auth):
        # Initialize the PiKVM instance
        pikvm = PiKVM(self.hostname, self.username, self.password, secret=self.secret, schema="https")
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get_auth.return_value = mock_response

        auth = pikvm.isauth()
        self.assertEqual(auth, True)
        mock_get_auth.assert_called_with("/api/auth/check")
    @patch('pikvm_lib.pikvm.PiKVM._get')
    def test_no_auth(self, mock_get_auth):
        # Initialize the PiKVM instance
        pikvm = PiKVM(self.hostname, self.username, self.password, secret=self.secret, schema="https")
        mock_response = MagicMock()
        mock_response.status_code = 402
        mock_get_auth.return_value = mock_response

        auth = pikvm.isauth()
        self.assertEqual(auth, False)
        mock_get_auth.assert_called_with("/api/auth/check")
