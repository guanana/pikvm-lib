from urllib.parse import urljoin
import posixpath
from pikvm_lib.pikvm_aux.pikvm_aux import PiKVMAuxRequests


class PiKVMEndpoints(PiKVMAuxRequests):

    def get_endpoint_state(self, endpoint_base, append_path=""):
        """
        Gets the state of the X subsystem.

        Parameters:
        - path: The X subsystem state endpoint path (default is "").

        Returns:
        - dict: ATX subsystem state information.
        """
        if append_path.startswith('/'):
            append_path = append_path[1:]
        path = urljoin(endpoint_base, append_path)
        return self._get_infos(path)

    def set_endpoint(self, endpoint_base, append_path, valid_actions, action, action_name="action"):
        """
        Sets the X subsytem.

        Parameters:
        - append_path: The "append" endpoint path (ie: power for atx endpoint /api/atx/power).
        - action: The action value (ie: 'on', 'off', 'off_hard', 'reset_hard').

        Returns:
        - None
        """
        if append_path.startswith('/'):
            append_path = append_path[1:]
        path = posixpath.join(endpoint_base, append_path)
        self._posts(path, action_name, action, valid_actions)
