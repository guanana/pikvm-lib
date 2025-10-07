import os
from io import BytesIO
from PIL import Image
import random
import string
import time

from pikvm_lib.pikvm_aux.pikvm_endpoints_base import PiKVMEndpoints
from pikvm_lib.pikvm_websocket import PiKVMWebsocket

class PiKVMStreamer(PiKVMEndpoints):

    def _await_streamer_initialization(self, timeout=30):
        """
        Awaits the streamer to be initialized.
        
        Parameters:
        - timeout: Maximum time in seconds to wait for initialization (default is 30)
        
        Returns:
        - bool: True if initialization succeeded, False if timed out
        """
        self.logger.info(f"Awaiting streamer initialization (timeout: {timeout}s)")
        streamer_initialized = False
        start_time = time.time()
        
        while not streamer_initialized:
            # Check if timeout has been reached
            if time.time() - start_time > timeout:
                self.logger.warning(f"Streamer initialization timed out after {timeout} seconds")
                return False
                
            try:
                message = self.ws_client.get_json_message()
                self.logger.debug(f"Received message: {message}")
                if (isinstance(message, dict) and 
                    message.get('event_type') == 'streamer' and 
                    message.get('event', {}).get('streamer', {}).get('source', {}).get('online', False)):
                    streamer_initialized = True
            except Exception as e:
                self.logger.debug(f"Error processing streamer message: {e}")
                continue
        
        return True

    def _ensure_streamer_started(self):
        """
        Ensures the streamer is started.
        """
        if (self.ws_client is not None and not self.ws_client.streamer_active):
            self.ws_client.close()
            self.ws_client = None
        
        if self.ws_client is None:
            self.logger.info("Starting new streamer enabled websocket")
            self.ws_client = PiKVMWebsocket(
                self.hostname, 
                self.username, 
                self.password, 
                self.secret, 
                self.certificate_trusted, 
                activate_streamer=True
            )
            result = self._await_streamer_initialization()
            if not result:
                self.logger.error("Failed to initialize streamer")
                raise Exception("Failed to initialize streamer")
        else:
            streamer_initialized = self.ws_client._ensure_connection()
            if not streamer_initialized:
                result = self._await_streamer_initialization()
                if not result:
                    self.logger.error("Failed to initialize streamer")
                    raise Exception("Failed to initialize streamer")

    
    def get_streamer_state(self, path="/api/streamer"):
        """
        Gets the state of the streamer subsystem.

        Parameters:
        - path: The Streamer state endpoint path (default is "/api/streamer").

        Returns:
        - dict: Streamer subsystem state information.
        """
        return self._get_infos(path)
    
    # @staticmethod
    # def _make_random_id():
    #     chars = string.ascii_letters + string.digits
    #     return ''.join(random.choice(chars) for _ in range(16))
    
    # def initialize_streamer(self, path="/kvm/streamer/stream"):
    #     """
    #     Initializes the streamer subsystem.

    #     Parameters:
    #     - path: The Streamer state endpoint path (default is "/api/streamer").
    #     """
    #     options = "key={}".format(PiKVMStreamer._make_random_id())
    #     return self._get(path, options).content

    def _validate_streamer_response(self, response):
        """
        Validates the streamer response for potential JSON errors.
        
        Parameters:
        - response: The response object to validate
        
        Returns:
        - bool: True if response is valid, False if it contains errors
        """
        try:
            json_response = response.json()
            if 'result' in json_response and 'error' in json_response['result']:
                return False
        except ValueError:
            # Response is not JSON, proceed with normal handling
            pass
        return True

    def get_streamer_snapshot(self, path="/api/streamer/snapshot", snapshot_path=os.getcwd(), filename="snapshot.jpeg",
                              ocr=False):
        """
        Gets screen snapshot

        Parameters:
        - path: The Streamer state endpoint path (default is "/api/streamer").
        - snapshot_path: Folder to download the snapshot to (default is _current path_)
        - filename: Name of the snapshot or text file name if ocr is enabled (default is "snapshot.jpeg")
        - ocr: Enable OCR recognition and creates a text file instead

        Returns:
        - file: Path to the file.
        """
        self._ensure_streamer_started()

        options = "allow_offline=1"
        if ocr:
            if filename.endswith(".jpeg"):
                self.logger.warning("Detected OCR but jpeg extension found, changing to txt")
                filename = f"{os.path.splitext(filename)[0]}.txt"
            options = "ocr=1&allow_offline=1"
        else:
            if filename.endswith(".txt"):
                self.logger.warning("OCR off but txt extension found, changing to jpeg")
                filename = f"{os.path.splitext(filename)[0]}.jpeg"

        response = self._get(path, options)
        if not self._validate_streamer_response(response):
            self.ws_client.close()
            return self.get_streamer_snapshot(path, snapshot_path, filename, ocr)
        response_content = response.content
        file = os.path.join(snapshot_path, filename)
        f = open(file, 'wb')
        f.write(response_content)
        f.close()
        self.logger.info(f"Writing snapshot to: {file}")
        return file

    def get_streamer_image(self, path="/api/streamer/snapshot", max_retries=3) -> Image.Image:
        """
        Gets screen snapshot as bytes

        Parameters:
        - path: The Streamer state endpoint path (default is "/api/streamer/snapshot").
        - max_retries: Maximum number of retry attempts (default is 3)

        Returns:
        - Image.Image: PIL Image object containing the snapshot
        
        Raises:
        - Exception: If maximum retries are exceeded
        """
        self._ensure_streamer_started()
        options = "allow_offline=1"
        response = self._get(path, options)
        if not self._validate_streamer_response(response):
            if max_retries <= 0:
                self.logger.error("Failed to get valid streamer image after multiple attempts")
                raise Exception("Maximum retries exceeded when getting streamer image")
            
            self.logger.info(f"Invalid streamer response, retrying ({max_retries} attempts left)")
            self.ws_client.close()
            return self.get_streamer_image(path, max_retries - 1)
            
        response_content = response.content
        bytes_im = BytesIO(response_content)
        source_im = Image.open(bytes_im, formats=['JPEG'])
        return source_im
