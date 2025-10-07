import requests

from pikvm_lib.pikvm_atx import PiKVMATX
from pikvm_lib.pikvm_aux.pikvm_aux import BuildPiKVM
from pikvm_lib.pikvm_gpio import PiKVMGPIO
from pikvm_lib.pikvm_msd import PiKVMMSD
from pikvm_lib.pikvm_streamer import PiKVMStreamer
from pikvm_lib.pikvm_websocket import PiKVMWebsocket
from pikvm_lib.pikvm_mouse import PiKVMMouse
from pikvm_lib.pikvm_keyboard import PiKVMKeyboard

class PiKVM(BuildPiKVM, PiKVMATX, PiKVMGPIO, PiKVMMSD, PiKVMStreamer, PiKVMMouse, PiKVMKeyboard):

    def __init__(self, hostname, username, password, secret=None, schema="https", cert_trusted=False, ws_client='initialize'):
        BuildPiKVM.__init__(self, hostname, username, password, secret, schema, cert_trusted)
        PiKVMKeyboard.__init__(self)
        PiKVMMouse.__init__(self)
        
        if self.schema not in ["http", "https"]:
            self.logger.error("Schema must be http or https")
            raise
        if not self.certificate_trusted:
            self.logger.debug("Disabling SSL certificate verification")
            requests.packages.urllib3.disable_warnings()
        self.systeminfo = self.get_system_info()
        if ws_client == 'initialize':
            self.ws_client = PiKVMWebsocket(self.hostname, self.username, self.password, self.secret, self.certificate_trusted)
        else:
            self.ws_client = ws_client
        

    def attach_ws_client(self, ws_client: PiKVMWebsocket):
        """
        Attaches a websocket to the streamer.
        """
        self.ws_client = ws_client
        

    def _auth(self, path="/api/auth/check"):
        """
        Checks if the user is authenticated.

        Parameters:
        - path: The authentication check endpoint path (default is "/api/auth/check").

        Returns:
        - bool: True if authenticated, False otherwise.
        """
        if self._get(path).status_code == 200:
            return True
        return False

    def isauth(self):
        """
        Checks and logs whether the user is authenticated.

        Returns:
        - bool: True if authenticated, False otherwise.
        """
        if self._auth():
            self.logger.info("User is authenticated")
        else:
            self.logger.info("User NOT authenticated")
        return self._auth()

    # Gets

    def get_system_info(self, path="/api/info"):
        """
        Gets system information.

        Parameters:
        - path: The system information endpoint path (default is "/api/info").

        Returns:
        - dict: System information.
        """
        return self._get_infos(path)

    def get_system_log(self, path="/api/log", seek=3600):
        """
        Gets the system log.

        Parameters:
        - path: The system log endpoint path (default is "/api/log").
        - seek: The time to seek in seconds (default is 3600).

        Returns:
        - None
        """
        self.logger.debug(self._get(path, f"seek={seek}").text)

    def get_prometheus_metrics(self, path="/api/export/prometheus/metrics"):
        """
        Gets Prometheus metrics.

        Parameters:
        - path: The Prometheus metrics endpoint path (default is "/api/export/prometheus/metrics").

        Returns:
        - dict: Prometheus metrics information.
        """
        return self._get_infos(path)
