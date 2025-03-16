import unittest
from unittest import mock
from unittest.mock import patch, MagicMock
from pikvm_lib.pikvm_websocket import PiKVMWebsocket
import websocket
import ssl


class TestPiKVMWebsocketRetry(unittest.TestCase):
    def setUp(self):
        self.hostname = "example.com"
        self.username = "user"
        self.password = "password"
        self.secret = None
        self.mock_websocket = mock.Mock()
        map_csv = {',': "Comma", '<ArrowUp>': 'ArrowUp'}
        map_shift_csv = {'_': 'Minus'}
        with patch("websocket.WebSocket") as mock_websocket:
            mock_websocket.return_value = self.mock_websocket
            # Create the test object
            self.pikvm_instance = PiKVMWebsocket(self.hostname, self.username, self.password,
                                                 secret=self.secret, extra_verbose=True)
            self.pikvm_instance.map_csv = map_csv
            self.pikvm_instance.map_shift_csv = map_shift_csv

    
    def test_ensure_connection_success(self):
        """Test successful connection check"""
        # Setup
        self.mock_websocket.ping.return_value = None  # Successful ping
        
        # Execute
        self.pikvm_instance._ensure_connection()
        
        # Verify
        self.mock_websocket.ping.assert_called_once()
        self.mock_websocket.close.assert_not_called()

    def test_ensure_connection_failure_and_reconnect(self):
        """Test connection failure and successful reconnect"""
        # Setup
        self.mock_websocket.ping.side_effect = websocket.WebSocketConnectionClosedException()
        new_websocket = mock.Mock()
        
        with patch("websocket.WebSocket") as mock_ws_class:
            mock_ws_class.return_value = new_websocket
            
            # Execute
            self.pikvm_instance._ensure_connection()
            
            # Verify
            self.mock_websocket.ping.assert_called_once()
            self.mock_websocket.close.assert_called_once()
            mock_ws_class.assert_called_once()
            self.assertEqual(self.pikvm_instance.ws, new_websocket)

    def test_send_with_retry_success(self):
        """Test successful message send"""
        # Setup
        test_message = '{"test": "message"}'
        
        # Execute
        self.pikvm_instance._send_with_retry(test_message)
        
        # Verify
        self.mock_websocket.send.assert_called_once_with(test_message)

    def test_send_with_retry_eventual_success(self):
        """Test message send succeeds after initial failures"""
        # Setup
        test_message = '{"test": "message"}'
        self.mock_websocket.send.side_effect = [
            websocket.WebSocketConnectionClosedException(),
            None
        ]
        new_websocket = mock.Mock()
        
        with patch("websocket.WebSocket") as mock_ws_class:
            mock_ws_class.return_value = new_websocket
            
            # Execute
            self.pikvm_instance._send_with_retry(test_message)
            
            # Verify
            self.assertEqual(self.mock_websocket.send.call_count, 1)
            self.assertEqual(new_websocket.send.call_count, 1)
            self.mock_websocket.close.assert_called_once()

    def test_send_with_retry_max_retries_exceeded(self):
        """Test message send fails after max retries"""
        # Setup
        test_message = '{"test": "message"}'
        self.pikvm_instance.max_retries = 3
        
        # Make all send attempts fail
        self.mock_websocket.send.side_effect = websocket.WebSocketConnectionClosedException()
        
        # Mock both _ensure_connection and _connect to avoid real websocket creation
        with patch.object(self.pikvm_instance, '_connect', return_value=self.mock_websocket):
            # Execute and verify exception is raised
            with self.assertRaises(websocket.WebSocketConnectionClosedException):
                self.pikvm_instance._send_with_retry(test_message)
        
        # Verify retry attempts and connection closure
        self.assertEqual(self.mock_websocket.send.call_count, self.pikvm_instance.max_retries)
        # close() should be called one fewer time than send() since we don't close after the final failure
        self.assertEqual(self.mock_websocket.close.call_count, self.pikvm_instance.max_retries - 1)

    def test_send_with_retry_ssl_error(self):
        """Test handling of SSL EOF errors"""
        # Setup
        test_message = '{"test": "message"}'
        self.mock_websocket.send.side_effect = ssl.SSLEOFError(
            ssl.SSL_ERROR_EOF, 'EOF occurred in violation of protocol')
        
        # Mock the _connect method to return our mock websocket and _ensure_connection to do nothing
        with patch.object(self.pikvm_instance, '_connect', return_value=self.mock_websocket):
            # Execute and verify exception is raised after max retries
            with self.assertRaises(ssl.SSLEOFError):
                self.pikvm_instance._send_with_retry(test_message)
        
        # Verify retry attempts and connection closure
        self.assertEqual(self.mock_websocket.send.call_count, self.pikvm_instance.max_retries)
        # close() should be called one fewer time than send() since we don't close after the final failure
        self.assertEqual(self.mock_websocket.close.call_count, self.pikvm_instance.max_retries - 1)
