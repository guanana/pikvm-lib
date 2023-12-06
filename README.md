# PiKVM: A Python API for Controlling PiKVM Devices

PiKVM is a Python library that provides a simple and intuitive API for controlling PiKVM devices. 
With PiKVM, you can easily perform various actions on your PiKVM devices, such as:

* Getting system information
* Controlling ATX power
* Managing Mass Storage Device (MSD) images
* Interacting with General-Purpose Input/Output (GPIO) channels


With PiKVM, you can automate tasks, integrate PiKVMs into your existing applications, 
and extend the capabilities of your PiKVM devices.

## Installation

To install PiKVM, simply run the following command in your terminal:

```bash
pip install pikvm-lib
```

## Usage

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

## Examples

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
