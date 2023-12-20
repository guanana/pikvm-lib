from __future__ import annotations

from pikvm_lib.pikvm_aux.pikvm_endpoints_base import PiKVMEndpoints


class PiKVMGPIO(PiKVMEndpoints):
    def get_gpio_state(self):
        """
        Gets the state of the General-Purpose Input/Output (GPIO) subsystem.

        Parameters:
        - path: The GPIO state endpoint path (default is "/api/gpio").

        Returns:
        - dict: GPIO subsystem state information.
        """
        return self.get_endpoint_state("/api/gpio")

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

    def switch_gpio_channel(self, channel, path="/api/gpio/switch", state: int = 1, wait: int | None = 1):
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
        state = f"state={state}"
        if wait:
            extra_ops = f"{state}&wait={wait}"
        else:
            extra_ops = state
        self._gpio_channel(path, channel, extra_ops)

    def pulse_gpio_channel(self, channel, path="/api/gpio/pulse", delay: float | None = 0, wait: int | None = 1):
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
        if delay or wait:
            extra_ops = f"delay={delay}&wait={wait}"
        else:
            extra_ops = None
        self._gpio_channel(path, channel, extra_ops)
