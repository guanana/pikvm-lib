from typing import TypedDict, Literal, Union
import time
import json

from pikvm_lib.pikvm_aux.pikvm_endpoints_base import PiKVMEndpoints

class KeyEvent(TypedDict):
    """Type definition for keyboard events"""
    event_type: Literal["key"]
    event: dict[Literal["key", "state"], str]

class MouseButtonEventData(TypedDict):
    """Type definition for mouse button event data"""
    button: Literal["left", "right", "middle", "up", "down"]
    state: Literal["true", "false"]

class MouseButtonEvent(TypedDict):
    """Type definition for mouse button events"""
    event_type: Literal["mouse_button"]
    event: MouseButtonEventData

class MouseMoveEvent(TypedDict):
    """Type definition for mouse movement events"""
    event_type: Literal["mouse_move"]
    event: dict[Literal["to"], dict[Literal["x", "y"], int]]

class MouseWheelEvent(TypedDict):
    """Type definition for mouse wheel events"""
    event_type: Literal["mouse_wheel"]
    event: dict[Literal["delta"], int]

Event = Union[KeyEvent, MouseButtonEvent, MouseMoveEvent, MouseWheelEvent]



class PiKVMMouse(PiKVMEndpoints):

    def __init__(self):
        self.width = None
        self.height = None
        self.extra_verbose = False

    def send_mouse_event(self, button: str, state: str = "true"):
        """
        Send a mouse button event to the PiKVM server.

        :param button: Mouse button name ("left", "right", "middle", "up", "down")
        :param state: Button state ("true" for press, "false" for release)
        """
        if state not in ["true", "false"]:
            self.logger.error("State can only be 'true' for press or 'false' for release")
            raise ValueError("Invalid mouse button state")

        if button not in ["left", "right", "middle", "up", "down"]:
            self.logger.error("Button must be one of: left, right, middle, up, down")
            raise ValueError("Invalid mouse button")
        
        event: MouseButtonEvent = {
            "event_type": "mouse_button",
            "event": {
                "button": button,
                "state": state
            }
        }
        self.ws_client._send_with_retry(json.dumps(event))
        if self.extra_verbose:
            self.logger.debug(f"Mouse button {button} {state} sent")

    def _scale_mouse_xy_to_i16(self, screenx: int, screeny: int, width: int, height: int) -> tuple[int, int]:
        """
        Convert screen coordinates to 16-bit signed integers expected by PiKVM.
        
        :param screenx: X coordinate in screen pixels
        :param screeny: Y coordinate in screen pixels
        :param width: Screen width in pixels (default: 1920)
        :param height: Screen height in pixels (default: 1080)
        :return: Tuple of (x, y) coordinates as 16-bit signed integers
        """
        # Map from (0, width) to signed 16-bit integer (-32768 to 32767)
        hid_x_i16 = int((screenx / width) * 0xFFFF - 0x8000)
        
        # Map from (0, height) to signed 16-bit integer (-32768 to 32767)
        hid_y_i16 = int((screeny / height) * 0xFFFF - 0x8000)
        
        return (hid_x_i16, hid_y_i16)

    def send_mouse_move_event(self, x: int, y: int):
        """
        Send a mouse movement event to the PiKVM server.

        :param x: X coordinate in screen pixels
        :param y: Y coordinate in screen pixels
        """
        if self.width is None or self.height is None:
            streamer_image = self.get_streamer_image()
            self.width, self.height = streamer_image.size
            if self.extra_verbose:
                self.logger.debug(f"Screen size detected: {self.width}x{self.height}")

        kvmx, kvmy = self._scale_mouse_xy_to_i16(x, y, self.width, self.height)
        event: MouseMoveEvent = {
            "event_type": "mouse_move",
            "event": {
                "to": {
                    "x": kvmx,
                    "y": kvmy
                }
            }
        }
        self.ws_client._send_with_retry(json.dumps(event))
        if self.extra_verbose:
            self.logger.debug(f"Mouse moved to x:{x}, y:{y} (KVM coords: {kvmx}, {kvmy})")

    def send_mouse_wheel_event(self, delta: int):
        """
        Send a mouse wheel event to the PiKVM server.

        :param delta: Wheel movement delta (-1 for down, 1 for up)
        """
        event: MouseWheelEvent = {
            "event_type": "mouse_wheel",
            "event": {
                "delta": delta
            }
        }
        self.ws_client._send_with_retry(json.dumps(event))
        if self.extra_verbose:
            self.logger.debug(f"Mouse wheel delta: {delta}")

    def send_click(self, button: Literal["left", "right", "middle", "up", "down"], delay: float = 0.05):
        """
        Send a complete mouse click (press and release) for the specified button.

        :param button: Mouse button name ("left", "right", "middle", "up", "down")
        :param delay: Delay between press and release (default: 0.05 seconds)
        """
        self.send_mouse_event(button, "true")
        time.sleep(delay)
        self.send_mouse_event(button, "false")
        if self.extra_verbose:
            self.logger.debug(f"Mouse {button} click completed")
