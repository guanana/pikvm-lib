def get_atx_state(self, path="/api/atx"):
    """
    Gets the state of the ATX subsystem.

    Parameters:
    - path: The ATX state endpoint path (default is "/api/atx").

    Returns:
    - dict: ATX subsystem state information.
    """
    return self._get_infos(path)


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
