import os


def get_msd_state(self, path="/api/msd"):
    """
    Gets the state of the Mass Storage Device (MSD) subsystem.

    Parameters:
    - path: The MSD state endpoint path (default is "/api/msd").

    Returns:
    - dict: MSD subsystem state information.
    """
    return self._get_infos(path)


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
        self.logger.error("Please specify a correct path for the iso you want to upload")
        raise
    self.logger.warning(f"Image {image_name} uploaded")


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
        self.logger.error("Flash OR cdrom needs to be selected")
        raise
    if cdrom and flash:
        self.logger.error("You cannot choose cdrom and flash. CDROM selected!")
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
        self.logger.warning("MSD connected!")
    else:
        self.logger.warning("MSD disconnected!")


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
