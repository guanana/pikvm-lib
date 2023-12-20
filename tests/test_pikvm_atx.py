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
        for actions in ['on', 'off', 'off_hard', 'reset_hard']:
            self.pikvm_instance.set_atx_power(action=actions)
            mock_post.assert_called_with(
                f"https://example.com/api/atx/power?action={actions}",
                headers=self.pikvm_instance.headers,
                verify=False
            )
        with self.assertRaises(BaseException):
            self.pikvm_instance.set_atx_power(action='wrong')
            mock_post.assert_called_with(
                "https://example.com/api/atx/power?action=wrong",
                headers=self.pikvm_instance.headers,
                verify=False
            )

    @patch('requests.post')
    def test_click_atx_button(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        for button in ['power', 'power_long', 'reset']:
            self.pikvm_instance.click_atx_button(button_name=button)
            mock_post.assert_called_with(
                f"https://example.com/api/atx/click?button={button}",
                headers=self.pikvm_instance.headers,
                verify=False
            )

        with self.assertRaises(BaseException):
            self.pikvm_instance.click_atx_button(button_name='on')
            mock_post.assert_called_once_with(
                "https://example.com/api/atx/click?button=on",
                headers=self.pikvm_instance.headers,
                verify=False
            )
