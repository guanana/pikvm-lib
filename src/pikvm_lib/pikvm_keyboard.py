from pikvm_lib.pikvm_aux.pikvm_endpoints_base import PiKVMEndpoints
from pikvm_lib.keymaps import KEYMAP_PYAUTOGUI
import time


# API to align with pyautogui API
class PiKVMKeyboard(PiKVMEndpoints):

    def __init__(self):
        self.map_csv_pyautogui = KEYMAP_PYAUTOGUI

    def keyUp(self, key):
        if self._requires_shift(key):
            self.keyUp("shift")
        self.ws_client._send_with_retry(self.ws_client._create_event(self._key_to_keycode(key), "false"))
        
    def keyDown(self, key):
        if self._requires_shift(key):
            self.keyDown("shift")
        self.ws_client._send_with_retry(self.ws_client._create_event(self._key_to_keycode(key), "true"))        
        
    def press(self, key, delay=0.05):
        self.keyDown(key)
        time.sleep(delay)
        self.keyUp(key)

    def hotkey(self, *keys):
        for key in keys:
            self.keyDown(key)
            time.sleep(0.05)
        
        for key in reversed(keys):
            self.keyUp(key)
            time.sleep(0.05)
    

    
    def _requires_shift(self, key):
        return key.isupper() or (key == '"') or (key in self.ws_client.map_shift_csv)
    
    def _key_to_keycode(self, key):
        if "<" not in key and ">" not in key:
            padded_key = f"<{key}>"
        else: 
            padded_key = key
        if key in self.ws_client.map_csv:
            return self.ws_client.map_csv[key]
        elif padded_key in self.ws_client.map_csv:
            return self.ws_client.map_csv[padded_key]
        elif key in self.ws_client.map_shift_csv:
            return self.ws_client.map_shift_csv[key]
        elif padded_key in self.ws_client.map_shift_csv:
            return self.ws_client.map_shift_csv[padded_key]
        elif key in self.map_csv_pyautogui:
            return self.map_csv_pyautogui[key]
        elif key.isdigit():
            return f"Digit{key}"
        elif key.isspace():
            return "Space"
        elif key == '"':
            return "Quote"
        # elif key == "'":
        #     return "Apostrophe"
        # elif key == "`":
        #     return "Backquote"
        else:
            return f"Key{key.upper()}"
