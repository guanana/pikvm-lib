from pikvm_lib.pikvm_aux.pikvm_endpoints_base import PiKVMEndpoints
import time
import os
import csv
from importlib.resources import files


# API to align with pyautogui API
class PiKVMKeyboard(PiKVMEndpoints):

    def __init__(self):
        self.map_csv_pyautogui = {}
        self._load_keymap_pyautogui()

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
    

    def _load_keymap_pyautogui(self):
        # Point to the CSV file inside the same package
        resource = files(__package__) / "keymap_pyautogui.csv"

        map_keys = {}
        with resource.open("r", encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile, delimiter=",")
            for row in reader:
                try:
                    key = row[0]
                    value = row[1]
                    if value == "":
                        continue
                    map_keys[key] = value
                except IndexError:
                    self.logger.error(f"Couldn't parse row: {row}")

        self.map_csv_pyautogui = map_keys
