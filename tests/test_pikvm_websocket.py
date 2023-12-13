import unittest
from unittest import mock
from unittest.mock import patch, MagicMock
from pikvm_lib.pikvm_websocket import PiKVMWebsocket


# Own version of create event for tests
def create_key_event(key):
    event_on = f'{{"event_type": "key", "event": {{"key": "Key{key.upper()}", "state": true}}}}'
    event_off = f'{{"event_type": "key", "event": {{"key": "Key{key.upper()}", "state": false}}}}'
    return event_on, event_off


# Own version of create event for tests
def create_digit_event(digit):
    event_on = f'{{"event_type": "key", "event": {{"key": "Digit{digit}", "state": true}}}}'
    event_off = f'{{"event_type": "key", "event": {{"key": "Digit{digit}", "state": false}}}}'
    return event_on, event_off


# Own version of create event for tests
def create_special_event(name):
    event_on = f'{{"event_type": "key", "event": {{"key": "{name}", "state": true}}}}'
    event_off = f'{{"event_type": "key", "event": {{"key": "{name}", "state": false}}}}'
    return event_on, event_off


class TestPiKVMWebsocket(unittest.TestCase):
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

    def test_initialization(self):
        # Initialize the PiKVM instance
        with patch("websocket.WebSocket") as mock_websocket:
            mock_websocket.return_value = self.mock_websocket
            pikvm_ws = PiKVMWebsocket(self.hostname, self.username, self.password,
                                      secret=self.secret)

        self.assertEqual(pikvm_ws.hostname, "example.com")
        self.assertEqual(pikvm_ws.username, "user")
        self.assertEqual(pikvm_ws.password, "password")

    def test_send_letter(self):
        key_on, key_off = create_key_event("b")
        # Make the call
        self.pikvm_instance._send_standard_keys("b")
        # Check sequence
        self.mock_websocket.send.assert_has_calls([
            mock.call(key_on),
            mock.call(key_off),
        ])
        # Check last call was as expected
        self.mock_websocket.send.assert_called_with(key_off)
        # Check it was called twice
        self.assertEqual(self.pikvm_instance.ws.send.call_count, 2)

    def test_send_space(self):
        space_on, space_off = create_special_event("Space")
        # Make the call
        self.pikvm_instance._send_standard_keys(" ")
        # Check sequence
        self.mock_websocket.send.assert_has_calls([
            mock.call(space_on),
            mock.call(space_off),
        ])
        # Check last call was as expected
        self.mock_websocket.send.assert_called_with(space_off)
        # Check it was called twice
        self.assertEqual(self.pikvm_instance.ws.send.call_count, 2)

    def test_send_digit(self):
        digit_on, digit_off = create_digit_event(1)
        # Make the call
        self.pikvm_instance._send_standard_keys("1")
        # Check sequence
        self.mock_websocket.send.assert_has_calls([
            mock.call(digit_on),
            mock.call(digit_off),
        ])
        # Check last call was as expected
        self.mock_websocket.send.assert_called_with(digit_off)
        # Check it was called twice
        self.assertEqual(self.pikvm_instance.ws.send.call_count, 2)

    def test_send_upper(self):
        shift_on, shift_off = create_special_event("ShiftLeft")
        key_on, key_off = create_key_event("a")
        # Make the call
        self.pikvm_instance._send_standard_keys("A")
        # Check sequence
        self.mock_websocket.send.assert_has_calls([
            mock.call(shift_on),
            mock.call(key_on),
            mock.call(key_off),
            mock.call(shift_off),
        ])
        # Check last call was as expected
        self.mock_websocket.send.assert_called_with(shift_off)
        # Check it was called 4 times, 2 for the shift and 2 for the letter
        self.assertEqual(self.pikvm_instance.ws.send.call_count, 4)

    def test_send_input(self):
        shift_on, shift_off = create_special_event("ShiftLeft")
        key_on, key_off = create_key_event("h")
        digit_on, digit_off = create_digit_event(2)
        # Make the call
        self.pikvm_instance.send_input("H2")
        # Check sequence
        self.mock_websocket.send.assert_has_calls([
            mock.call(shift_on),
            mock.call(key_on),
            mock.call(key_off),
            mock.call(shift_off),
            mock.call(digit_on),
            mock.call(digit_off),
        ])
        # Check last call was as expected
        self.mock_websocket.send.assert_called_with(digit_off)
        # Check it was called 6 times, 2 for the shift and 2 for the letter and 2 for digit
        self.assertEqual(self.pikvm_instance.ws.send.call_count, 6)

    def test_send_input_specials(self):
        shift_on, shift_off = create_special_event("ShiftLeft")
        comma_on, comma_off = create_special_event("Comma")
        minus_on, minus_off = create_special_event("Minus")
        arrowup_on, arrowup_off = create_special_event("ArrowUp")
        key_on, key_off = create_key_event("h")
        digit_on, digit_off = create_digit_event(2)
        # Make the call
        self.pikvm_instance.send_input("H2,_<ArrowUp>")
        # Check sequence
        self.mock_websocket.send.assert_has_calls([
            mock.call(shift_on),
            mock.call(key_on),
            mock.call(key_off),
            mock.call(shift_off),
            mock.call(digit_on),
            mock.call(digit_off),
            mock.call(comma_on),
            mock.call(comma_off),
            mock.call(shift_on),
            mock.call(minus_on),
            mock.call(minus_off),
            mock.call(shift_off),
            mock.call(arrowup_on),
            mock.call(arrowup_off),
        ])
        # Check last call was as expected
        self.mock_websocket.send.assert_called_with(arrowup_off)
        # Check it was called 14 times:
        # 4 for the shift, 2 for the letter, 2 for digit,
        # 2 for comma, 2 for minus and 2 for arrow up
        self.assertEqual(self.pikvm_instance.ws.send.call_count, 14)

    def test_send_input_specials_quote(self):
        shift_on, shift_off = create_special_event("ShiftLeft")
        comma_on, comma_off = create_special_event("Comma")
        quote_on, quote_off = create_special_event("Quote")
        key_on, key_off = create_key_event("h")
        digit_on, digit_off = create_digit_event(2)
        # Make the call
        self.pikvm_instance.send_input('H2,"')
        # Check sequence
        self.mock_websocket.send.assert_has_calls([
            mock.call(shift_on),
            mock.call(key_on),
            mock.call(key_off),
            mock.call(shift_off),
            mock.call(digit_on),
            mock.call(digit_off),
            mock.call(comma_on),
            mock.call(comma_off),
            mock.call(shift_on),
            mock.call(quote_on),
            mock.call(quote_off),
            mock.call(shift_off),
        ])
        # Check last call was as expected
        self.mock_websocket.send.assert_called_with(shift_off)
        # Check it was called 12 times:
        # 4 for the shift, 2 for the letter, 2 for digit,
        # 2 for comma, 2 for quote
        self.assertEqual(self.pikvm_instance.ws.send.call_count, 12)

    def test_send_ctrl_alt_sup(self):
        control_on, control_off = create_special_event("ControlLeft")
        alt_on, alt_off = create_special_event("AltLeft")
        delete_on, delete_off = create_special_event("Delete")
        # Make the call
        self.pikvm_instance.send_ctrl_alt_sup()
        # Check sequence
        self.mock_websocket.send.assert_has_calls([
            mock.call(control_on),
            mock.call(alt_on),
            mock.call(delete_on),
            mock.call(control_off),
            mock.call(alt_off),
            mock.call(delete_off),
        ])
        # Check last call was as expected
        self.mock_websocket.send.assert_called_with(delete_off)
        # Check it was called 6 times:
        # 2 control, 2 for alt, 2 for delete
        self.assertEqual(self.pikvm_instance.ws.send.call_count, 6)

    def test_send_key_press(self):
        control_on, control_off = create_special_event("ControlLeft")
        key_on, key_off = create_key_event("b")
        # Make the call
        self.pikvm_instance.send_key_press("ControlLeft")
        self.pikvm_instance.send_input("b")
        self.pikvm_instance.send_key_press("ControlLeft", "false")
        # Check sequence
        self.mock_websocket.send.assert_has_calls([
            mock.call(control_on),
            mock.call(key_on),
            mock.call(key_off),
            mock.call(control_off),
        ])
        # Check last call was as expected
        self.mock_websocket.send.assert_called_with(control_off)
        # Check it was called 4 times:
        # 2 control, 2 for b
        self.assertEqual(self.pikvm_instance.ws.send.call_count, 4)


if __name__ == '__main__':
    unittest.main()
