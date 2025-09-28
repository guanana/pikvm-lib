import unittest
from unittest import mock
from unittest.mock import patch, MagicMock
import os
import time
import csv
from pikvm_lib.pikvm_keyboard import PiKVMKeyboard
from pikvm_lib.pikvm import PiKVM
import mock_pikvm_response


class TestPiKVMKeyboard(unittest.TestCase):
    def setUp(self):
        self.hostname = "example.com"
        self.username = "user"
        self.password = "password"
        self.secret = None
        self.mock_pikvm = patch('pikvm_lib.pikvm.PiKVM.get_system_info',
                                return_value=mock_pikvm_response.pikvm_mock_info).start()
        
        mock_ws_client = MagicMock()
        
        self.keyboard = PiKVM(self.hostname, self.username, self.password, 
                                   secret=self.secret, schema="https", 
                                   ws_client=mock_ws_client)
            
        # Mock the websocket client
        self.keyboard.ws_client = MagicMock()
        self.keyboard.ws_client.map_csv = {
            '<enter>': 'Enter',
            '<tab>': 'Tab',
            ',': 'Comma'
        }
        self.keyboard.ws_client.map_shift_csv = {
            '_': 'Minus',
            '"': 'Quote',
            '?': 'Slash'
        }
        
        # Mock the pyautogui keymap
        self.keyboard.map_csv_pyautogui = {
            'enter': 'Enter',
            'tab': 'Tab',
            'shift': 'ShiftLeft',
            'ctrl': 'ControlLeft',
            'alt': 'AltLeft',
            'delete': 'Delete'
        }


    def test_key_down(self):
        # Test keyDown for a standard key
        self.keyboard.keyDown('a')
        self.keyboard.ws_client._send_with_retry.assert_called_once()
        self.keyboard.ws_client._create_event.assert_called_with('KeyA', 'true')

    def test_key_up(self):
        # Test keyUp for a standard key
        self.keyboard.keyUp('a')
        self.keyboard.ws_client._send_with_retry.assert_called_once()
        self.keyboard.ws_client._create_event.assert_called_with('KeyA', 'false')

    def test_uppercase_key_down(self):
        # Test keyDown for an uppercase letter
        self.keyboard.keyDown('A')
        
        # Should call keyDown for 'shift' first, then 'A'
        self.keyboard.ws_client._create_event.assert_any_call('ShiftLeft', 'true')
        self.keyboard.ws_client._create_event.assert_any_call('KeyA', 'true')
        self.assertEqual(self.keyboard.ws_client._send_with_retry.call_count, 2)

    def test_uppercase_key_up(self):
        # Test keyUp for an uppercase letter
        self.keyboard.keyUp('A')
        
        # Should call keyUp for 'A' and then for 'shift'
        self.keyboard.ws_client._create_event.assert_any_call('KeyA', 'false')
        self.keyboard.ws_client._create_event.assert_any_call('ShiftLeft', 'false')
        self.assertEqual(self.keyboard.ws_client._send_with_retry.call_count, 2)

    def test_press(self):
        # Test press for a single key
        with patch('time.sleep') as mock_sleep:
            self.keyboard.press('a')
            
            # Should call keyDown and keyUp with appropriate events
            self.keyboard.ws_client._create_event.assert_any_call('KeyA', 'true')
            self.keyboard.ws_client._create_event.assert_any_call('KeyA', 'false')
            self.assertEqual(self.keyboard.ws_client._send_with_retry.call_count, 2)
            mock_sleep.assert_called_once_with(0.05)

    def test_hotkey(self):
        # Test hotkey with multiple keys
        with patch('time.sleep') as mock_sleep:
            self.keyboard.hotkey('ctrl', 'alt', 'delete')
            
            # Should press all keys in order, then release in reverse order
            calls = self.keyboard.ws_client._create_event.call_args_list
            self.assertEqual(len(calls), 6)  # 3 keys down, 3 keys up
            
            # Keys should be pressed in order
            self.assertEqual(calls[0][0], ('ControlLeft', 'true'))  # ctrl
            self.assertEqual(calls[1][0], ('AltLeft', 'true'))  # alt
            self.assertEqual(calls[2][0], ('Delete', 'true'))  # delete
            
            # Keys should be released in reverse order
            self.assertEqual(calls[3][0], ('Delete', 'false'))  # delete
            self.assertEqual(calls[4][0], ('AltLeft', 'false'))  # alt
            self.assertEqual(calls[5][0], ('ControlLeft', 'false'))  # ctrl
            
            # Sleep should be called between each key operation
            self.assertEqual(mock_sleep.call_count, 6)

    def test_requires_shift(self):
        # Test _requires_shift method
        self.assertTrue(self.keyboard._requires_shift('A'))  # uppercase letter
        self.assertTrue(self.keyboard._requires_shift('"'))  # quotation mark
        self.assertTrue(self.keyboard._requires_shift('_'))  # in map_shift_csv
        self.assertFalse(self.keyboard._requires_shift('a'))  # lowercase letter
        self.assertFalse(self.keyboard._requires_shift('1'))  # digit

    def test_key_to_keycode_standard(self):
        # Test standard key conversion
        self.assertEqual(self.keyboard._key_to_keycode('a'), 'KeyA')
        self.assertEqual(self.keyboard._key_to_keycode('z'), 'KeyZ')
        self.assertEqual(self.keyboard._key_to_keycode('5'), 'Digit5')
        self.assertEqual(self.keyboard._key_to_keycode(' '), 'Space')

    def test_key_to_keycode_special(self):
        # Test special key conversion
        self.assertEqual(self.keyboard._key_to_keycode('<enter>'), 'Enter')
        self.assertEqual(self.keyboard._key_to_keycode('enter'), 'Enter')  # From pyautogui map
        self.assertEqual(self.keyboard._key_to_keycode(','), 'Comma')  # From map_csv
        self.assertEqual(self.keyboard._key_to_keycode('_'), 'Minus')  # From map_shift_csv
        self.assertEqual(self.keyboard._key_to_keycode('"'), 'Quote')  # Special case


if __name__ == '__main__':
    unittest.main() 