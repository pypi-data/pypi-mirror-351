from .mount import MountManager
from .freezer import FilesystemFreezer


class Snowfuse:
    """
    Main interface for freezing and managing a FUSE-based filesystem.
    """

    def __init__(self, source_path: str, mount_point: str):
        self.source_path = source_path
        self.mount_point = mount_point
        self.mounter = MountManager(source_path, mount_point)
        self.freezer = FilesystemFreezer(mount_point)

    def freeze(self):
        """
        Freeze the filesystem by mounting it as read-only.
        """
        self.mounter.mount(read_only=True)
        self.freezer.lockdown()

    def unfreeze(self):
        """
        Unmount and cleanup the frozen filesystem.
        """
        self.mounter.unmount()

    def status(self):
        """
        Check if the filesystem is currently frozen.
        """
        return self.mounter.is_mounted()
