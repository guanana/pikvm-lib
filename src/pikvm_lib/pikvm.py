import re
import requests
import json
import pyotp
from urllib.parse import urljoin
import logging
import os

# Create a logger
logger = logging.getLogger(__name__)

# Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
logger.setLevel(logging.DEBUG)

# Create a console handler and set its level
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Create a formatter and add it to the handler
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# Add the console handler to the logger
logger.addHandler(console_handler)


class PiKVM:
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
        try:
            self.schema = re.findall(r"(http|https)://", schema.lower())[0]
        except IndexError:
            logger.error("Schema must be http or https")
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
        logger.debug(f"Parameters: schema: {self.schema}, hostname: {self.hostname}, path={path}, options={options}")
        if not options:
            url = urljoin(self.base_url, path)
        else:
            url = urljoin(urljoin(self.base_url, path), f"?{options}")
        logger.info(f"Calling: {url}")
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
            logger.info("User is authenticated")
        else:
            logger.info("User NOT authenticated")
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
        logger.debug(resp)
        return json.loads(resp)['result']

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
        logger.debug(self._get(path, f"seek={seek}").text)

    def get_atx_state(self, path="/api/atx"):
        """
        Gets the state of the ATX subsystem.

        Parameters:
        - path: The ATX state endpoint path (default is "/api/atx").

        Returns:
        - dict: ATX subsystem state information.
        """
        return self._get_infos(path)

    def get_msd_state(self, path="/api/msd"):
        """
        Gets the state of the Mass Storage Device (MSD) subsystem.

        Parameters:
        - path: The MSD state endpoint path (default is "/api/msd").

        Returns:
        - dict: MSD subsystem state information.
        """
        return self._get_infos(path)

    def get_gpio_state(self, path="/api/gpio"):
        """
        Gets the state of the General-Purpose Input/Output (GPIO) subsystem.

        Parameters:
        - path: The GPIO state endpoint path (default is "/api/gpio").

        Returns:
        - dict: GPIO subsystem state information.
        """
        return self._get_infos(path)

    def get_prometheus_metrics(self, path="/api/export/prometheus/metrics"):
        """
        Gets Prometheus metrics.

        Parameters:
        - path: The Prometheus metrics endpoint path (default is "/api/export/prometheus/metrics").

        Returns:
        - dict: Prometheus metrics information.
        """
        return self._get_infos(path)

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
            logger.error(f"{action} not a valid option. Valid options = {valid_actions}")
            raise
        self._post(path, options=f"{action_name}={action}")

    def set_atx_power(self, path="/api/atx/power", action=None):
        """
        Sets the ATX power.

        Parameters:
        - path: The ATX power endpoint path (default is "/api/atx/power").
        - action: The action value ('on', 'off', 'off_hard', 'reset_hard').

        Returns:
        - None
        """
        valid_actions = {'on', 'off', 'off_hard', 'reset_hard'}
        self._posts(path, "action", action, valid_actions)

    def click_atx_button(self, path="/api/atx/click", action=None):
        """
        Clicks the specified button on the ATX subsystem.

        Parameters:
        - path: The ATX button click endpoint path (default is "/api/atx/click").
        - action: The button action ('power', 'power_long', 'reset').

        Returns:
        - None
        """
        valid_actions = {'power', 'power_long', 'reset'}
        self._posts(path, "button", action, valid_actions)

    def upload_msd_image(self, filepath, image_name=None, path="/api/msd/write"):
        """
        Uploads an MSD (Mass Storage Device) image from a local file.

        Parameters:
        - filepath: The path to the local image file.
        - image_name: The name to assign to the uploaded image (default is the base name of the file).
        - path: The MSD image upload endpoint path (default is "/api/msd/write").

        Returns:
        - None
        """
        if not image_name:
            image_name = os.path.basename(filepath)
        try:
            with open(filepath, 'rb') as f:
                self._post(path, options=f"image={image_name}", data=f)
        except FileNotFoundError:
            logger.error("Please specify a correct path for the iso you want to upload")
            raise
        logger.warning(f"Image {image_name} uploaded")

    def upload_msd_remote(self, remote, image_name=None, path="/api/msd/write_remote"):
        """
        Uploads an MSD (Mass Storage Device) image from a remote location.

        Parameters:
        - remote: The URL of the remote image.
        - image_name: The name to assign to the uploaded image (default is the base name of the remote file).
        - path: The MSD remote image upload endpoint path (default is "/api/msd/write_remote").

        Returns:
        - None
        """
        if not image_name:
            image_name = os.path.basename(remote)
        self._post(path, options=f"url={remote}&image={image_name}")

    def set_msd_parameters(self, image_name, cdrom=False, flash=True, path="/api/msd/set_params"):
        """
        Sets parameters for the Mass Storage Device (MSD) subsystem.

        Parameters:
        - image_name: The name of the MSD image.
        - cdrom: Whether to use CD-ROM mode (default is False).
        - flash: Whether to use flash mode (default is True).
        - path: The MSD parameters setting endpoint path (default is "/api/msd/set_params").

        Returns:
        - None
        """
        if not cdrom and not flash:
            logger.error("Flash OR cdrom needs to be selected")
            raise
        if cdrom and flash:
            logger.error("You cannot choose cdrom and flash. CDROM selected!")
            option = 1
        elif not cdrom:
            option = 0
        else:
            option = 1
        self._post(path, options=f"image={image_name}&cdrom={option}")

    def _control_msd(self, path="/api/msd/set_connected", connected=True):
        """
        Controls the connection state of the Mass Storage Device (MSD) subsystem.

        Parameters:
        - path: The MSD connection control endpoint path (default is "/api/msd/set_connected").
        - connected: Whether to connect (True) or disconnect (False) the MSD (default is True).

        Returns:
        - None
        """
        valid_actions = [0, 1]
        self._posts(path, "connected", connected, valid_actions)
        if connected:
            logger.warning("MSD connected!")
        else:
            logger.warning("MSD disconnected!")

    def connect_msd(self):
        """
        Connects the Mass Storage Device (MSD).

        Returns:
        - None
        """
        self._control_msd()

    def disconnect_msd(self):
        """
        Disconnects the Mass Storage Device (MSD).

        Returns:
        - None
        """
        self._control_msd(connected=False)

    def remove_msd_image(self, image_name, path="/api/msd/remove"):
        """
        Removes an MSD image.

        Parameters:
        - image_name: The name of the MSD image to remove.
        - path: The MSD image removal endpoint path (default is "/api/msd/remove").

        Returns:
        - None
        """
        self._post(path, options=f"image={image_name}")

    def reset_msd(self, path="/api/msd/reset"):
        """
        Resets the Mass Storage Device (MSD).

        Parameters:
        - path: The MSD reset endpoint path (default is "/api/msd/reset").

        Returns:
        - None
        """
        self._post(path)

    def _gpio_channel(self, path, channel, extra_ops=None):
        """
        Controls a General-Purpose Input/Output (GPIO) channel.

        Parameters:
        - path: The GPIO control endpoint path.
        - channel: The GPIO channel.
        - extra_ops: Additional options for the GPIO control (optional).

        Returns:
        - None
        """
        if extra_ops:
            self._post(path, options=f"channel={channel}&{extra_ops}")
        else:
            self._post(path, options=f"channel={channel}")

    def switch_gpio_channel(self, channel, path="/api/gpio/switch", state: int = 1, wait: int = 1):
        """
        Switches a GPIO channel.

        Parameters:
        - channel: The GPIO channel.
        - path: The GPIO switch endpoint path (default is "/api/gpio/switch").
        - state: The state to switch to (default is 1).
        - wait: The wait time in seconds (default is 1).

        Returns:
        - None
        """
        extra_ops = f"state={state}&wait={wait}"
        self._gpio_channel(path, channel, extra_ops)

    def pulse_gpio_channel(self, channel, path="/api/gpio/pulse", delay: float = 0, wait: int = 1):
        """
        Pulses a GPIO channel.

        Parameters:
        - channel: The GPIO channel.
        - path: The GPIO pulse endpoint path (default is "/api/gpio/pulse").
        - delay: The delay in seconds (default is 0).
        - wait: The wait time in seconds (default is 1).

        Returns:
        - None
        """
        extra_ops = f"delay={delay}&wait={wait}"
        self._gpio_channel(path, channel, extra_ops)
