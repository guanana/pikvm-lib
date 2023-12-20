import unittest
from tempfile import NamedTemporaryFile
from unittest.mock import patch, MagicMock
from pikvm_lib.pikvm import PiKVM
import mock_pikvm_response
import os


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
    def test_get_msd_state(self, mock_get_msd_state):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"result": {"state": "on"}}'
        mock_get_msd_state.return_value = mock_response

        result = self.pikvm_instance.get_msd_state()

        self.assertEqual(result, {"state": "on"})
        mock_get_msd_state.assert_called_once_with('/api/msd')

    @patch('requests.post')
    def test_upload_msd_image(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        file_content = b"column1,column2,column3\nvalue1,value2,value3"
        temp_file = NamedTemporaryFile(delete=False)
        temp_file.write(file_content)
        temp_file.close()
        self.pikvm_instance.upload_msd_image(image_name="test.iso", filepath=temp_file.name)
        mock_post.assert_called_once()
        assert "https://example.com/api/msd/write?image=test.iso" == mock_post.call_args.args[0]
        assert self.pikvm_instance.headers == mock_post.call_args.kwargs["headers"]
        assert not mock_post.call_args.kwargs["verify"]

        self.pikvm_instance.upload_msd_image(filepath=temp_file.name)
        mock_post.assert_called()
        assert f"https://example.com/api/msd/write?image={os.path.basename(temp_file.name)}" == mock_post.call_args.args[0]
        assert self.pikvm_instance.headers == mock_post.call_args.kwargs["headers"]
        assert not mock_post.call_args.kwargs["verify"]

        with self.assertRaises(FileNotFoundError):
            self.pikvm_instance.upload_msd_image(image_name="test", filepath="makeup_path")

    @patch('requests.post')
    def test_set_msd_parameters(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        self.pikvm_instance.set_msd_parameters(image_name="test", cdrom=False)
        mock_post.assert_called_once_with(
            "https://example.com/api/msd/set_params?image=test&cdrom=0",
            headers=self.pikvm_instance.headers,
            verify=False
        )

        with self.assertRaises(BaseException):
            self.pikvm_instance.set_msd_parameters(image_name="test", flash=False)

        self.pikvm_instance.set_msd_parameters(image_name="test", flash=True, cdrom=True)
        mock_post.assert_called_with(
            "https://example.com/api/msd/set_params?image=test&cdrom=1",
            headers=self.pikvm_instance.headers,
            verify=False
        )

        self.pikvm_instance.set_msd_parameters(image_name="test", flash=True)
        mock_post.assert_called_with(
            "https://example.com/api/msd/set_params?image=test&cdrom=0",
            headers=self.pikvm_instance.headers,
            verify=False
        )

        self.pikvm_instance.set_msd_parameters(image_name="test", flash=False, cdrom=True)
        mock_post.assert_called_with(
            "https://example.com/api/msd/set_params?image=test&cdrom=1",
            headers=self.pikvm_instance.headers,
            verify=False
        )

    @patch('requests.post')
    def test_upload_msd_remote(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        self.pikvm_instance.upload_msd_remote(remote="https://mytest.com/test.iso")
        mock_post.assert_called_with(
            "https://example.com/api/msd/write_remote?url=https://mytest.com/test.iso",
            headers=self.pikvm_instance.headers,
            verify=False
        )

        self.pikvm_instance.upload_msd_remote(remote="https://mytest.com/test.iso", image_name="test2")
        mock_post.assert_called_with(
            "https://example.com/api/msd/write_remote?url=https://mytest.com/test.iso&image=test2",
            headers=self.pikvm_instance.headers,
            verify=False
        )

    @patch('requests.post')
    def test_connect_msd(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        self.pikvm_instance.connect_msd()
        mock_post.assert_called_with(
            "https://example.com/api/msd/set_connected?connected=1",
            headers=self.pikvm_instance.headers,
            verify=False
        )

    @patch('requests.post')
    def test_disconnect_msd(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        self.pikvm_instance.disconnect_msd()
        mock_post.assert_called_with(
            "https://example.com/api/msd/set_connected?connected=0",
            headers=self.pikvm_instance.headers,
            verify=False
        )

    @patch('requests.post')
    def test_remove_msd(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        self.pikvm_instance.remove_msd_image(image_name="test.iso")
        mock_post.assert_called_with(
            "https://example.com/api/msd/remove?image=test.iso",
            headers=self.pikvm_instance.headers,
            verify=False
        )

    @patch('requests.post')
    def test_reset_msd(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        self.pikvm_instance.reset_msd()
        mock_post.assert_called_with(
            "https://example.com/api/msd/reset",
            headers=self.pikvm_instance.headers,
            verify=False
        )
