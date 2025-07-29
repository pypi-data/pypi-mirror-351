import subprocess
import os
from .exceptions import MountError


class MountManager:
    """
    Handles mounting and unmounting of a FUSE filesystem.
    """

    def __init__(self, source: str, target: str):
        self.source = os.path.abspath(source)
        self.target = os.path.abspath(target)

    def mount(self, read_only=True):
        """
        Mount the source directory to the target using FUSE with optional read-only mode.
        """
        os.makedirs(self.target, exist_ok=True)
        options = "ro" if read_only else "rw"
        try:
            subprocess.run(
                ["fuse-bindfs", f"-o{options}", self.source, self.target], check=True)
        except subprocess.CalledProcessError as e:
            raise MountError(
                f"Failed to mount {self.source} at {self.target}") from e

    def unmount(self):
        """
        Unmount the FUSE filesystem.
        """
        try:
            subprocess.run(["fusermount", "-u", self.target], check=True)
        except subprocess.CalledProcessError as e:
            raise MountError(f"Failed to unmount {self.target}") from e

    def is_mounted(self):
        """
        Check if the mount point is active.
        """
        try:
            output = subprocess.check_output(["mount"]).decode()
            return self.target in output
        except Exception:
            return False
