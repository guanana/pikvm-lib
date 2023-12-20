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

    @patch('pikvm_lib.pikvm.PiKVM._get')
    def test_get_gpio_state(self, mock_get_gpio_state):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"result": {"state": "on"}}'
        mock_get_gpio_state.return_value = mock_response

        result = self.pikvm_instance.get_gpio_state()

        self.assertEqual(result, {"state": "on"})
        mock_get_gpio_state.assert_called_once_with('/api/gpio')

    @patch('requests.post')
    def test_switch_gpio_channel(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        channel = 1
        self.pikvm_instance.switch_gpio_channel(channel=channel)
        mock_post.assert_called_with(
            f"https://example.com/api/gpio/switch?channel={channel}&state=1&wait=1",
            headers=self.pikvm_instance.headers,
            verify=False
        )
        self.pikvm_instance.switch_gpio_channel(channel=channel, state=1, wait=None)
        mock_post.assert_called_with(
            f"https://example.com/api/gpio/switch?channel={channel}&state=1",
            headers=self.pikvm_instance.headers,
            verify=False
        )

    @patch('requests.post')
    def test_pulse_gpio_channel(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        channel = 1
        self.pikvm_instance.pulse_gpio_channel(channel=channel, delay=None, wait=None)
        mock_post.assert_called_with(
            f"https://example.com/api/gpio/pulse?channel={channel}",
            headers=self.pikvm_instance.headers,
            verify=False
        )
        self.pikvm_instance.pulse_gpio_channel(channel=channel)
        mock_post.assert_called_with(
            f"https://example.com/api/gpio/pulse?channel={channel}&delay=0&wait=1",
            headers=self.pikvm_instance.headers,
            verify=False
        )
