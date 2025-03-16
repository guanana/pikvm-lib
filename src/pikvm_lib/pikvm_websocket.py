"""
Module for interacting with PiKVM server using WebSocket
"""

from urllib.parse import urljoin
import csv
import websocket
import ssl
import time
import os.path
import re
import json

from pikvm_lib.pikvm_aux.pikvm_aux import BuildPiKVM


class PiKVMWebsocket(BuildPiKVM):
    """
    Class for sending keyboard events to PiKVM server over WebSocket
    """

    def __init__(self, hostname: str, username: str, password: str, secret: str = None, cert_trusted: bool = False,
                 extra_verbose: bool = False, max_retries: int = 3, retry_delay: float = 1.0, activate_streamer: bool = False):

        """
        Initialize PiKVMWebsocket object

        :param hostname: PiKVM server hostname or IP address
        :param username: PiKVM server username
        :param password: PiKVM server password
        :param secret: PiKVM server secret (optional)
        :param cert_trusted: Whether to trust server's SSL certificate (optional)
        :param extra_verbose: Print extra logging information (optional)
        :param max_retries: Maximum number of connection retry attempts (optional)
        :param retry_delay: Delay between retry attempts in seconds (optional)
        """
        super().__init__(hostname, username, password, secret, schema="wss", cert_trusted=cert_trusted)

        self.base_wss = "/api/ws?stream={}".format(int(activate_streamer))
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.extra_verbose = extra_verbose
        self.ws = self._connect()
        self.streamer_active = activate_streamer
        self.map_csv = self._map_csv()
        self.map_shift_csv = self._map_csv("keymap_shift.csv")
        if self.extra_verbose:
            self.logger.debug(self.ws)

    def __enter__(self):
        """Support for context manager"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ensure websocket is closed when exiting context"""
        self.close()

    def _connect(self):
        """
        Connect to PiKVM server over WebSocket with retry mechanism

        :return: WebSocket object
        :raises: Exception after max_retries attempts
        """
        retries = 0
        last_exception = None
        self.logger.debug(f"Connecting to {self.base_url} with {self.base_wss}")
        while retries < self.max_retries:
            try:
                if not self.certificate_trusted:
                    ws = websocket.WebSocket(sslopt={"cert_reqs": ssl.CERT_NONE})
                else:
                    ws = websocket.WebSocket()
                url = urljoin(self.base_url, self.base_wss)
                ws.connect(url, header=self.headers)
                self.logger.debug(f"Connected to {url} successfully")
                return ws
            except Exception as e:
                last_exception = e
                retries += 1
                if retries < self.max_retries:
                    self.logger.info(f"WebSocket connection attempt {retries} failed: {e}. Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)

        self.logger.error(f"Failed to connect to WebSocket after {self.max_retries} attempts: {last_exception}")
        raise last_exception

    def _ensure_connection(self):
        """
        Ensure WebSocket connection is active, reconnect if necessary

        :return: None
        """
        try:
            self.ws.ping()
        except (websocket.WebSocketConnectionClosedException, 
                websocket.WebSocketException,
                ssl.SSLEOFError) as e:
            self.logger.info(f"WebSocket connection lost: {e}. Attempting to reconnect...")
            try:
                self.ws.close()
            except Exception:
                pass
            self.ws = self._connect()
            return False
        return True

    def _send_with_retry(self, event_str: str):
        """
        Send WebSocket message with automatic reconnection

        :param event_str: Event string to send
        """
        retries = 0
        while retries < self.max_retries:
            try:
                self._ensure_connection()
                self.ws.send(event_str)
                return
            except (websocket.WebSocketConnectionClosedException, 
                   websocket.WebSocketException, 
                   ssl.SSLEOFError) as e:
                retries += 1
                if retries >= self.max_retries:
                    self.logger.error(f"Failed to send WebSocket message after {self.max_retries} attempts: {e}")
                    raise
                self.logger.info(f"Send attempt {retries} failed: {e}. Retrying in {self.retry_delay} seconds...")
                time.sleep(self.retry_delay)
                try:
                    self.ws.close()
                except Exception:
                    pass
                self.ws = self._connect()

    def close(self, **kwargs):
        """
        Close WebSocket connection to PiKVM server

        :param kwargs: keyword arguments to pass to WebSocket.close()
        """
        self.ws.close(**kwargs)
    
    def get_json_message(self):
        """
        Receive and parse a JSON message from the WebSocket connection.
        
        :return: Parsed JSON message as a Python object, or None if parsing fails
        """
        message = self.ws.recv()
        try:
            return json.loads(message)
        except json.JSONDecodeError as e:
            self.logger.debug(f"Failed to parse JSON message: {e} Raw message: {message}")
            return None

    def _map_csv(self, csvname: str = "keymap.csv"):
        """
        Read key mappings from CSV file

        :param csvname: CSV filename (default: keymap.csv)
        :return: dictionary of key mappings
        """
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

    def _create_event(self, key, state: str):
        """
        Create JSON event message to send to PiKVM server

        :param key: key to send
        :param state: key press state (true for pressed, false for released)
        :return: JSON message
        """
        event = f'{{"event_type": "key", "event": {{"key": "{key}", "state": {state}}}}}'
        if self.extra_verbose:
            self.logger.debug(event)
        return event

    def _send_extra_key(self, key: str):
        """
        Send key press event for a special key that is not defined in the key map

        :param key: special key to send
        """
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

    def _find_special_keys(self, text: str):
        """
        Find all the special keys in a string of text.

        :param text: The text to search.

        Returns:
            List[re.Match]: A list of matches for the special keys.
        """
        matches = []
        p = re.compile(r"<(?P<word>\w+)>")
        for m in p.finditer(text):
            if any(key in m.group() for key in self.map_csv.keys()):
                self.logger.debug(f"Found special keys to send: {m.start(), m.end(), m.group()}")
                matches.append(m)
        return matches

    def _send_shift_key(self, key):
        """
        Send a shift key press event. Used mainly for upper case and special characters

        :param key: The key to send.
        """
        self._send_with_retry(self._create_event("ShiftLeft", "true"))
        self.send_key(key)
        self._send_with_retry(self._create_event("ShiftLeft", "false"))

    def _send_standard_keys(self, key):
        """
        Send a key press event for a standard key.

        :param key: The key to send.
        """
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

    def send_ctrl_alt_sup(self):
        """
        Sends the Ctrl+Alt+Delete key combination.
        """
        self._send_with_retry(self._create_event("ControlLeft", "true"))
        time.sleep(0.05)
        self._send_with_retry(self._create_event("AltLeft", "true"))
        time.sleep(0.05)
        self._send_with_retry(self._create_event("Delete", "true"))
        time.sleep(0.05)
        self._send_with_retry(self._create_event("ControlLeft", "false"))
        time.sleep(0.05)
        self._send_with_retry(self._create_event("AltLeft", "false"))
        time.sleep(0.05)
        self._send_with_retry(self._create_event("Delete", "false"))
        time.sleep(0.05)

    def send_key(self, key):
        """
        Send a key press event for a key.

        :param key: The key to send.
        """
        self._send_with_retry(self._create_event(key, "true"))
        time.sleep(0.05)
        self._send_with_retry(self._create_event(key, "false"))
        if self.extra_verbose:
            self.logger.debug(f"Key: {key} sent")
        time.sleep(0.001)

    def send_key_press(self, key, action: str = "true"):
        """
        Send a key press event for a key.

        :param action: It can be true for press or false to release. Default true/pressed
        :param key: The key to send.
        """
        if action not in ["true", "false"]:
            self.logger.error("It can only be true for press or false for release")
            self.logger.error(f"Failed trying to action key {key}")
            raise
        self._send_with_retry(self._create_event(key, action))
        time.sleep(0.05)
        if self.extra_verbose:
            self.logger.debug(f"Key: {key} sent")
        time.sleep(0.001)

    def send_input(self, text: str):
        """
        Send a text input to the PiKVM server.

        :param text: The text to send.
        """
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
                if key.isalpha() or key.isspace() or key.isdigit():
                    self._send_standard_keys(key)
                else:
                    self._send_extra_key(key)
