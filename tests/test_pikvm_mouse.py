import unittest
from unittest.mock import patch, MagicMock
import json
import time
from PIL import Image
from pikvm_lib.pikvm_mouse import PiKVMMouse
from pikvm_lib.pikvm import PiKVM
import mock_pikvm_response

class TestPiKVMMouse(unittest.TestCase):
    def setUp(self):
        # Mock the parent class
        self.hostname = "example.com"
        self.username = "user"
        self.password = "password"
        self.secret = None
        self.mock_pikvm = patch('pikvm_lib.pikvm.PiKVM.get_system_info',
                                return_value=mock_pikvm_response.pikvm_mock_info).start()
        
        mock_ws_client = MagicMock()
        
        self.mouse = PiKVM(self.hostname, self.username, self.password, 
                                   secret=self.secret, schema="https", 
                                   ws_client=mock_ws_client)
        
        # Set screen dimensions for testing
        self.mouse.width = 1920
        self.mouse.height = 1080

    def test_initialization(self):
        # Test that the object initializes properly
        with patch('pikvm_lib.pikvm_aux.pikvm_endpoints_base.PiKVMEndpoints'):
            mouse = PiKVMMouse()
            self.assertIsNone(mouse.width)
            self.assertIsNone(mouse.height)
            self.assertFalse(mouse.extra_verbose)

    def test_send_mouse_event_valid(self):
        # Test sending a valid mouse button event
        self.mouse.send_mouse_event("left", "true")
        
        expected_event = {
            "event_type": "mouse_button",
            "event": {
                "button": "left",
                "state": "true"
            }
        }
        self.mouse.ws_client._send_with_retry.assert_called_once_with(json.dumps(expected_event))

    def test_send_mouse_event_invalid_state(self):
        # Test sending an invalid mouse button state
        with self.assertRaises(ValueError) as context:
            self.mouse.send_mouse_event("left", "invalid")
            
        self.assertIn("Invalid mouse button state", str(context.exception))
        self.mouse.ws_client._send_with_retry.assert_not_called()

    def test_send_mouse_event_invalid_button(self):
        # Test sending an invalid mouse button
        with self.assertRaises(ValueError) as context:
            self.mouse.send_mouse_event("invalid", "true")
            
        self.assertIn("Invalid mouse button", str(context.exception))
        self.mouse.ws_client._send_with_retry.assert_not_called()

    def test_scale_mouse_xy_to_i16(self):
        # Test coordinate scaling function with multiple values
        test_cases = [
            # (x, y, expected_kvmx, expected_kvmy)
            (0, 0, -32768, -32768),
            (1920, 1080, 32767, 32767),
            (960, 540, 0, 0),
            (480, 270, -16384, -16384),
            (1440, 810, 16383, 16383)
        ]
        
        for x, y, expected_kvmx, expected_kvmy in test_cases:
            kvmx, kvmy = self.mouse._scale_mouse_xy_to_i16(x, y, 1920, 1080)
            self.assertEqual(kvmx, expected_kvmx)
            self.assertEqual(kvmy, expected_kvmy)

    def test_send_mouse_move_event_with_dimensions(self):
        # Test sending a mouse move event when dimensions are already set
        self.mouse.send_mouse_move_event(960, 540)
        
        expected_event = {
            "event_type": "mouse_move",
            "event": {
                "to": {
                    "x": 0,
                    "y": 0
                }
            }
        }
        self.mouse.ws_client._send_with_retry.assert_called_once_with(json.dumps(expected_event))

    def test_send_mouse_move_event_get_dimensions(self):
        # Test sending a mouse move event when dimensions need to be fetched
        self.mouse.width = None
        self.mouse.height = None
        
        # Mock the get_streamer_image method
        mock_image = MagicMock()
        mock_image.size = (1920, 1080)
        self.mouse.get_streamer_image = MagicMock(return_value=mock_image)
        
        self.mouse.send_mouse_move_event(960, 540)
        
        # Verify get_streamer_image was called
        self.mouse.get_streamer_image.assert_called_once()
        
        # Verify dimensions were set
        self.assertEqual(self.mouse.width, 1920)
        self.assertEqual(self.mouse.height, 1080)
        
        # Verify the correct event was sent
        expected_event = {
            "event_type": "mouse_move",
            "event": {
                "to": {
                    "x": 0,
                    "y": 0
                }
            }
        }
        self.mouse.ws_client._send_with_retry.assert_called_once_with(json.dumps(expected_event))

    def test_send_mouse_wheel_event(self):
        # Test sending mouse wheel events
        test_cases = [
            (1, {"event_type": "mouse_wheel", "event": {"delta": 1}}),  # Scroll up
            (-1, {"event_type": "mouse_wheel", "event": {"delta": -1}}),  # Scroll down
            (5, {"event_type": "mouse_wheel", "event": {"delta": 5}}),  # Multiple lines up
            (-3, {"event_type": "mouse_wheel", "event": {"delta": -3}})  # Multiple lines down
        ]
        
        for delta, expected_event in test_cases:
            self.mouse.ws_client.reset_mock()
            self.mouse.send_mouse_wheel_event(delta)
            self.mouse.ws_client._send_with_retry.assert_called_once_with(json.dumps(expected_event))

    def test_send_click(self):
        # Test sending a complete mouse click (press and release)
        with patch('time.sleep') as mock_sleep:
            self.mouse.send_click("left")
            
            # Verify press and release events were sent
            calls = self.mouse.ws_client._send_with_retry.call_args_list
            self.assertEqual(len(calls), 2)
            
            # Verify press event
            press_event = json.loads(calls[0][0][0])
            self.assertEqual(press_event["event_type"], "mouse_button")
            self.assertEqual(press_event["event"]["button"], "left")
            self.assertEqual(press_event["event"]["state"], "true")
            
            # Verify release event
            release_event = json.loads(calls[1][0][0])
            self.assertEqual(release_event["event_type"], "mouse_button")
            self.assertEqual(release_event["event"]["button"], "left")
            self.assertEqual(release_event["event"]["state"], "false")
            
            # Verify sleep was called with the correct delay
            mock_sleep.assert_called_once_with(0.05)

    def test_send_click_custom_delay(self):
        # Test click with custom delay
        with patch('time.sleep') as mock_sleep:
            self.mouse.send_click("right", delay=0.2)
            
            # Verify sleep was called with the custom delay
            mock_sleep.assert_called_once_with(0.2)
            
            # Verify correct events were sent
            calls = self.mouse.ws_client._send_with_retry.call_args_list
            
            press_event = json.loads(calls[0][0][0])
            self.assertEqual(press_event["event"]["button"], "right")
            self.assertEqual(press_event["event"]["state"], "true")
            
            release_event = json.loads(calls[1][0][0])
            self.assertEqual(release_event["event"]["button"], "right")
            self.assertEqual(release_event["event"]["state"], "false")

    def test_extra_verbose_logging(self):
        # Test that extra verbose logging works
        with patch.object(self.mouse, 'logger') as mock_logger:
            self.mouse.extra_verbose = True
            
            # Test different operations with logging enabled
            self.mouse.send_mouse_event("left", "true")
            mock_logger.debug.assert_called_with("Mouse button left true sent")
            
            mock_logger.reset_mock()
            self.mouse.send_mouse_move_event(100, 200)
            self.assertTrue(mock_logger.debug.called)
            
            mock_logger.reset_mock()
            self.mouse.send_mouse_wheel_event(1)
            mock_logger.debug.assert_called_with("Mouse wheel delta: 1")


if __name__ == '__main__':
    unittest.main() 