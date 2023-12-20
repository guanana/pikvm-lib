import os
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
    def test_get_streamer_state(self, mock_get_streamer_state):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"result": {"state": "on"}}'
        mock_get_streamer_state.return_value = mock_response

        result = self.pikvm_instance.get_streamer_state()

        self.assertEqual(result, {"state": "on"})
        mock_get_streamer_state.assert_called_once_with('/api/streamer')

    @patch('pikvm_lib.pikvm.PiKVM._get')
    def test_get_streamer_snapshot(self, mock_get_streamer_snapshot):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"result": {"state": "on"}}'
        mock_response.content = b"This is the file"
        mock_get_streamer_snapshot.return_value = mock_response
        result = self.pikvm_instance.get_streamer_snapshot()

        self.assertEqual(result, f"{os.getcwd()}/snapshot.jpeg")
        mock_get_streamer_snapshot.assert_called_once_with('/api/streamer/snapshot', 'allow_offline=1')

        result = self.pikvm_instance.get_streamer_snapshot(filename="/tmp/test.txt")

        self.assertEqual(result, "/tmp/test.jpeg")
        mock_get_streamer_snapshot.assert_called_with('/api/streamer/snapshot', 'allow_offline=1')

    @patch('pikvm_lib.pikvm.PiKVM._get')
    def test_get_streamer_snapshot_ocr(self, mock_get_streamer_snapshot):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"result": {"state": "on"}}'
        mock_response.content = b"This is the file"
        mock_get_streamer_snapshot.return_value = mock_response
        result = self.pikvm_instance.get_streamer_snapshot(ocr=1)
        self.assertEqual(result, f"{os.getcwd()}/snapshot.txt")
        mock_get_streamer_snapshot.assert_called_once_with('/api/streamer/snapshot', 'ocr=1&allow_offline=1')
