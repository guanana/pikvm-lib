import os

from pikvm_lib.pikvm_aux.pikvm_endpoints_base import PiKVMEndpoints


class PiKVMStreamer(PiKVMEndpoints):
    def get_streamer_state(self, path="/api/streamer"):
        """
        Gets the state of the streamer subsystem.

        Parameters:
        - path: The Streamer state endpoint path (default is "/api/streamer").

        Returns:
        - dict: Streamer subsystem state information.
        """
        return self._get_infos(path)


    def get_streamer_snapshot(self, path="/api/streamer/snapshot", snapshot_path=os.getcwd(), filename="snapshot.jpeg",
                              ocr=False):
        """
        Gets screen snapshot

        Parameters:
        - path: The Streamer state endpoint path (default is "/api/streamer").
        - snapshot_path: Folder to download the snapshot to (default is _current path_)
        - filename: Name of the snapshot or text file name if ocr is enabled (default is "snapshot.jpeg")
        - ocr: Enable OCR recognition and creates a text file instead

        Returns:
        - file: Path to the file.
        """
        options = "allow_offline=1"
        if ocr:
            if filename.endswith(".jpeg"):
                self.logger.warning("Detected OCR but jpeg extension found, changing to txt")
                filename = f"{os.path.splitext(filename)[0]}.txt"
            options = "ocr=1&allow_offline=1"
        else:
            if filename.endswith(".txt"):
                self.logger.warning("OCR off but txt extension found, changing to jpeg")
                filename = f"{os.path.splitext(filename)[0]}.jpeg"

        file = os.path.join(snapshot_path, filename)
        f = open(file, 'wb')
        f.write(self._get(path, options).content)
        f.close()
        self.logger.info(f"Writing snapshot to: {file}")
        return file
