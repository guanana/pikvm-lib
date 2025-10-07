import os
import unittest
from tempfile import NamedTemporaryFile
from unittest.mock import patch, MagicMock
from pikvm_lib.pikvm import PiKVM
import mock_pikvm_response
from PIL import Image


class TestPiKVM(unittest.TestCase):
    def setUp(self):
        self.hostname = "example.com"
        self.username = "user"
        self.password = "password"
        self.secret = None
        self.mock_pikvm = patch('pikvm_lib.pikvm.PiKVM.get_system_info',
                                return_value=mock_pikvm_response.pikvm_mock_info).start()
        
        mock_ws_client = MagicMock()
        
        self.pikvm_instance = PiKVM(self.hostname, self.username, self.password, 
                                   secret=self.secret, schema="https", 
                                   ws_client=mock_ws_client)

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

    @patch('pikvm_lib.pikvm.PiKVM._get')
    @patch('PIL.Image.open')
    def test_get_streamer_image(self, mock_image_open, mock_get_streamer_image):
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"Mock image data"
        mock_get_streamer_image.return_value = mock_response
        
        # Mock the Image.open to return a mock image
        mock_img = MagicMock()
        mock_image_open.return_value = mock_img
        
        # Test image retrieval
        result = self.pikvm_instance.get_streamer_image()
        
        # Assert the result is the mocked image
        self.assertEqual(result, mock_img)
        mock_get_streamer_image.assert_called_with('/api/streamer/snapshot', 'allow_offline=1')
        
        # Verify Image.open was called with BytesIO containing our mock data
        mock_image_open.assert_called_once()
        # Get the first positional argument that was passed to Image.open
        bytes_io_arg = mock_image_open.call_args[0][0]
        self.assertEqual(bytes_io_arg.getvalue(), b"Mock image data")
