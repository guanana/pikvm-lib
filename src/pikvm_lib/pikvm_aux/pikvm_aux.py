import json
import pyotp
from urllib.parse import urljoin
import logging
import requests


class BuildPiKVM:
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
        self.hostname = hostname
        self.username = username
        self.password = password
        self.secret = secret  # Can be found in /etc/kvmd/totp.secret
        self.certificate_trusted = cert_trusted
        self.logger = logging.getLogger(__name__)
        self.schema = schema
        self.headers = self._set_headers()
        self.base_url = f"{self.schema}://{self.hostname}/placeholder"

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


class PiKVMAuxRequests:
    def _call(self, path, options=None):
        """
        Forms the complete URL for an API call.

        Parameters:
        - path: The API endpoint path.
        - options: Query parameters (optional).

        Returns:
        - str: The complete URL.
        """
        self.logger.debug(
            f"Parameters: schema: {self.schema}, hostname: {self.hostname}, path={path}, options={options}")
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


