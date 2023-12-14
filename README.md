# PiKVM: A Python API for Controlling PiKVM Devices

[![codecov](https://codecov.io/gh/guanana/pikvm-lib/graph/badge.svg?token=ZTJV7JLUTK)](https://codecov.io/gh/guanana/pikvm-lib)

PiKVM is a Python library that provides a simple and intuitive API for controlling PiKVM devices. 
With PiKVM, you can easily perform various actions on your PiKVM devices, such as:

* Getting system information
* Controlling ATX power
* Managing Mass Storage Device (MSD) images
* Interacting with General-Purpose Input/Output (GPIO) channels
* Taking snapshots and receive image
* Reading snapshots with OCR and receive text representation
* Send keys to the server


With PiKVM, you can automate tasks, integrate PiKVMs into your existing applications, 
and extend the capabilities of your PiKVM devices.

## Installation

To install PiKVM, simply run the following command in your terminal:

```bash
pip install pikvm-lib
```

## PiKVM device control

After installing PiKVM, you can import it into your Python script and create an instance of the `PiKVM` class. The `PiKVM` class constructor takes the following parameters:

* `hostname`: The hostname or IP address of the PiKVM device
* `username`: The username for authentication
* `password`: The password for authentication


```python
from pikvm_lib import PiKVM

pikvm_instance = PiKVM(hostname="192.168.1.10", username="admin", password="password")
```

Once you have created an instance of the `PiKVM` class, you can use it to interact with your PiKVM device. 
For example, you can get the system information of the device:

```python
system_info = pikvm_instance.get_system_info()
print(system_info)
```

You can also control the ATX power of the device:

```python
pikvm_instance.set_atx_power(action="on")
```

For more information on how to use PiKVM, 
please refer to the official documentation: [PiKVM official web](https://docs.pikvm.org/) and [PiKVM API Reference](https://docs.pikvm.org/api/)

### Usage examples

Here are some examples of how to use PiKVM to perform common tasks:

* **Getting system information:**

```python
from pikvm_lib import PiKVM

pikvm_instance = PiKVM(hostname="192.168.1.10", username="admin", password="password")
system_info = pikvm_instance.get_system_info()
print(system_info)
```

* **Turning on the ATX power:**

```python
pikvm_instance.set_atx_power(action="on")
```

* **Uploading an MSD image:**

```python
pikvm_instance.upload_msd_image(filepath="/path/to/image.iso")
```

* **Connecting the MSD:**

```python
pikvm_instance.connect_msd()
```

* **Switching a GPIO channel:**

```python
pikvm_instance.switch_gpio_channel(channel=1, state=1)
```

* **Take snapshot and receive OCR text:**

```python
pikvm_instance.get_streamer_snapshot(snapshot_path="/home/user/pikvm-snapshots",
                            filename="test.txt", ocr=True)
```
* **Take snapshot and receive image:**

```python
pikvm_instance.get_streamer_snapshot(snapshot_path="/home/user/pikvm-snapshots",
                            filename="test.jpeg", ocr=False)
```
## PiKVM websocket
The PiKVMWebsocket class is a Python class that allows you to send keyboard events to a PiKVM server over WebSocket. 

It provides methods for sending individual keys, key combinations, and text input. 

The class also handles the connection to the PiKVM server and the parsing of the WebSocket messages.

### Usage examples
```python
from pikvm_lib import PiKVMWebsocket

hostname = "192.168.1.10"  # Replace with your PiKVM server's hostname or IP address
username = "user"
password = "password"

# Create a PiKVMWebsocket object
websocket = PiKVMWebsocket(hostname, username, password)

# Send the Ctrl+Alt+Delete key combination
websocket.send_ctrl_alt_sup()

# Send the text "Hello, world!"
websocket.send_input("Hello, world!")
```

```python
from pikvm_lib import PiKVMWebsocket

hostname = "192.168.1.10"  # Replace with your PiKVM server's hostname or IP address
username = "user"
password = "password"

# Create a PiKVMWebsocket object
websocket = PiKVMWebsocket(hostname, username, password)

# Send the F2 key
websocket.send_key("<F2>")

# Send the Ctrl+B key
websocket.send_key_press("ControlLeft", "true")
websocket.send_input("b") # or websocket.send_key("KeyB")
websocket.send_key_press("ControlLeft", "false")
```