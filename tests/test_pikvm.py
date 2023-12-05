import unittest
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
        self.pikvm_instance = PiKVM(self.hostname, self.username, self.password, secret=self.secret, schema="https://")

    def test_init_with_invalid_schema(self):
        with self.assertRaises(Exception):
            PiKVM('hostname', 'username', 'password', schema='ftp://')

    def test_initialization(self):
        # Initialize the PiKVM instance
        pikvm = PiKVM(self.hostname, self.username, self.password, secret=self.secret, schema="https://")

        self.assertEqual(pikvm.hostname, "example.com")
        self.assertEqual(pikvm.username, "user")
        self.assertEqual(pikvm.password, "password")

    @patch('pikvm_lib.pikvm.PiKVM._get')
    def test_get_atx_state(self, mock_get_atx_state):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"result": {"state": "on"}}'
        mock_get_atx_state.return_value = mock_response

        result = self.pikvm_instance.get_atx_state()

        self.assertEqual(result, {"state": "on"})
        mock_get_atx_state.assert_called_once_with('/api/atx')

    @patch('requests.post')
    def test_set_atx_power(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        self.pikvm_instance.set_atx_power(action='on')
        mock_post.assert_called_once_with(
            "https://example.com/api/atx/power?action=on",
            headers=self.pikvm_instance.headers,
            verify=False
        )

        self.pikvm_instance.set_atx_power(action='off')
        mock_post.assert_called_with(
            "https://example.com/api/atx/power?action=off",
            headers=self.pikvm_instance.headers,
            verify=False
        )


if __name__ == '__main__':
    unittest.main()
