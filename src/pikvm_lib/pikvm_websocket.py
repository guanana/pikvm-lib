from urllib.parse import urljoin
import csv
import websocket
import ssl
import time
import os.path
import re

from .pikvm import _BuildPiKVM


class PiKVMWebsocket(_BuildPiKVM):

    def __init__(self, hostname, username, password, secret=None, schema="wss://", cert_trusted=False, extra_verbose=False):
        super().__init__(hostname, username, password, secret, schema, cert_trusted)
        self.base_wss = "/api/ws?stream=0"
        self.ws = self._connect()
        self.extra_verbose = extra_verbose
        self.map_csv = self._map_csv()
        self.map_shift_csv = self._map_csv("keymap_shift.csv")
        if self.extra_verbose:
            self.logger.debug(self.ws)

    def _connect(self):
        if not self.certificate_trusted:
            ws = websocket.WebSocket(sslopt={"cert_reqs": ssl.CERT_NONE})
        else:
            ws = websocket.WebSocket()
        url = urljoin(self.base_url, self.base_wss)
        ws.connect(url, header=self.headers)
        return ws

    def close(self, **kwargs):
        self.ws.close(**kwargs)

    def _map_csv(self, csvname="keymap.csv"):
        current_dir = os.path.dirname(__file__)
        csvpath = os.path.join(current_dir, csvname)
        map_keys = {}
        with open(csvpath, 'r') as csvfile:
            # Create a CSV reader object
            reader = csv.reader(csvfile, delimiter=',')
            for row in reader:
                try:
                    # Extract key and value from the row
                    key = row[0]
                    value = row[1]
                    # Add key-value pair to the map
                    map_keys[key] = value
                except IndexError as e:
                    self.logger.error(f"Couldn't parse {key} or {value}")
        if self.extra_verbose:
            self.logger.debug(f"Map loaded:\n {map_keys}")
        return map_keys

    def _create_event(self, key, state):
        event = f'{{"event_type": "key", "event": {{"key": "{key}", "state": {state}}}}}'
        if self.extra_verbose:
            self.logger.debug(event)
        return event

    def _send_extra_key(self, key: str):
        try:
            if self.extra_verbose:
                self.logger.debug(f"Found special keys to send: {key}")
            self.send_key(self.map_csv[key])
        except KeyError:
            try:
                if self.extra_verbose:
                    self.logger.debug(f"Looking for 'shift' key to send: {key}")
                # Special case for "
                if key == '"':
                    self._send_shift_key("Quote")

                self._send_shift_key(self.map_shift_csv[key])
            except KeyError:
                self.logger.debug(f"Special key found that cannot be recognised {key}")

    def _find_special_keys(self, text):
        matches = []
        p = re.compile("<(?P<word>\w+)>")
        for m in p.finditer(text):
            if any(key in m.group() for key in self.map_csv.keys()):
                self.logger.debug(f"Found special keys to send: {m.start(), m.end(), m.group()}")
                matches.append(m)
        return matches

    def _send_shift_key(self, key):
        self.ws.send(self._create_event("ShiftLeft", "true"))
        self.send_key(key)
        self.ws.send(self._create_event("ShiftLeft", "false"))

    def _send_standard_keys(self, key):
        if key.isupper():
            self._send_shift_key(f"Key{key.upper()}")
            if self.extra_verbose:
                self.logger.debug(f"Upper case {key} sent")
        elif key.isdigit():
            self.send_key(f"Digit{key}")
        elif key.isspace():
            self.send_key("Space")
            if self.extra_verbose:
                self.logger.debug(f"Space sent")
        else:
            self.send_key(f"Key{key.upper()}")

    def send_key(self, key):
        self.ws.send(self._create_event(key, "true"))
        time.sleep(0.05)
        self.ws.send(self._create_event(key, "false"))
        if self.extra_verbose:
            self.logger.debug(f"Key: {key} sent")
        time.sleep(0.001)

    def send_input(self, text: str):
        self.logger.debug(f"Sending input {text}")
        matches = self._find_special_keys(text)
        iteration = enumerate(text)
        for idx, key in iteration:
            if matches and matches[0].start() == idx:
                self.send_key(matches[0].group("word"))
                self.logger.debug(f"Sent special key {matches[0].group('word')}")
                characters_to_remove = matches[0].end() - matches[0].start() - 1
                [next(iteration) for _ in range(characters_to_remove)]
                matches.pop(0)
            else:
                if key.isalpha() or key.isspace():
                    self._send_standard_keys(key)
                else:
                    self._send_extra_key(key)
