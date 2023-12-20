from pikvm_lib.pikvm_aux.pikvm_endpoints_base import PiKVMEndpoints


class PiKVMATX(PiKVMEndpoints):
    def get_atx_state(self, path="/api/atx"):
        """
        Gets the state of the ATX subsystem.

        Parameters:
        - path: The ATX state endpoint path (default is "/api/atx").

        Returns:
        - dict: ATX subsystem state information.
        """
        return self.get_endpoint_state(path)

    def set_atx_power(self, path="/api/atx", action=None):
        """
        Sets the ATX power.

        Parameters:
        - path: The ATX power endpoint path (default is "/api/atx/power").
        - action: The action value ('on', 'off', 'off_hard', 'reset_hard').

        Returns:
        - None
        """
        valid_actions = {'on', 'off', 'off_hard', 'reset_hard'}
        self.set_endpoint(endpoint_base=path, append_path="power", action=action, valid_actions=valid_actions)

    def click_atx_button(self, button_name, path="/api/atx"):
        """
        Clicks the specified button on the ATX subsystem.

        Parameters:
        - path: The ATX button click endpoint path (default is "/api/atx/click").
        - button_name: The button name ('power', 'power_long', 'reset').

        Returns:
        - None
        """
        valid_actions = {'power', 'power_long', 'reset'}
        self.set_endpoint(endpoint_base=path, append_path="click", action_name="button",
                          action=button_name, valid_actions=valid_actions)
