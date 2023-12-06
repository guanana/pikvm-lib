import re
import requests
import json
import pyotp
from urllib.parse import urljoin
import logging


class PiKVM:
    from ._atx import get_atx_state, set_atx_power, click_atx_button
    from ._msd import (get_msd_state, set_msd_parameters, connect_msd, disconnect_msd, reset_msd,
                       upload_msd_remote, upload_msd_image, remove_msd_image)
    from ._gpio import pulse_gpio_channel, switch_gpio_channel, get_gpio_state

    def __init__(self, hostname, username, password, secret=None, schema="https://", cert_trusted=False):
        """
        Initializes the PiKVM object.

        Parameters:
        - hostname: The hostname or IP address of the PiKVM device.
        - username: The username for authentication.
        - password: The password for authentication.
        - secret: The secret for two-factor authentication (optional).
        - schema: The protocol schema, either "http" or "https" (default is "https").
        - cert_trusted: Whether the SSL certificate is issue by a trusted authority or not (default is False).
        """
        self.logger = logging.getLogger(__name__)
        try:
            self.schema = re.findall(r"(http|https)://", schema.lower())[0]
        except IndexError:
            self.logger.error("Schema must be http or https")
            raise
        self.certificate_trusted = cert_trusted
        if not self.certificate_trusted:
            requests.packages.urllib3.disable_warnings()

        self.hostname = hostname
        self.base_url = f"{self.schema}://{self.hostname}/placeholder"
        self.username = username
        self.password = password
        self.secret = secret  # Can be found in /etc/kvmd/totp.secret
        self.headers = self._set_headers()
        self.systeminfo = self.get_system_info()

    def _set_headers(self):
        """
        Sets the HTTP headers for authentication.

        Returns:
        - dict: The headers.
        """
        if self.secret:
            kvmd_passwd = self.password + pyotp.TOTP(self.secret).now()
        else:
            kvmd_passwd = self.password

        headers = {
            "X-KVMD-User": self.username,
            "X-KVMD-Passwd": kvmd_passwd
        }
        return headers

    def _call(self, path, options=None):
        """
        Forms the complete URL for an API call.

        Parameters:
        - path: The API endpoint path.
        - options: Query parameters (optional).

        Returns:
        - str: The complete URL.
        """
        self.logger.debug(f"Parameters: schema: {self.schema}, hostname: {self.hostname}, path={path}, options={options}")
        if not options:
            url = urljoin(self.base_url, path)
        else:
            url = urljoin(urljoin(self.base_url, path), f"?{options}")
        self.logger.info(f"Calling: {url}")
        return url

    def _get(self, path, options=None):
        """
        Performs a GET request.

        Parameters:
        - path: The API endpoint path.
        - options: Query parameters (optional).

        Returns:
        - requests.Response: The HTTP response object.
        """
        url = self._call(path, options)
        resp = requests.get(url, headers=self.headers, verify=self.certificate_trusted)
        return resp

    def _post(self, path, options=None, **req_kwargs):
        """
        Performs a POST request.

        Parameters:
        - path: The API endpoint path.
        - options: Query parameters (optional).
        - req_kwargs: Additional request parameters.

        Returns:
        - requests.Response: The HTTP response object.
        """
        url = self._call(path, options)
        resp = requests.post(url, headers=self.headers, verify=self.certificate_trusted, **req_kwargs)
        return resp

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
    def _get_infos(self, path):
        """
        Performs a GET request and returns parsed result information.

        Parameters:
        - path: The API endpoint path.

        Returns:
        - dict: Parsed result information.
        """
        resp = self._get(path).text
        self.logger.debug(resp)
        return json.loads(resp)['result']

    # Posts
    def _posts(self, path, action_name=None, action=None, valid_actions=None):
        """
        Performs a POST request with specified action parameters.

        Parameters:
        - path: The API endpoint path.
        - action_name: The name of the action parameter.
        - action: The action value.
        - valid_actions: Valid action values.

        Returns:
        - None
        """
        if action not in valid_actions:
            self.logger.error(f"{action} not a valid option. Valid options = {valid_actions}")
            raise
        self._post(path, options=f"{action_name}={action}")

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

