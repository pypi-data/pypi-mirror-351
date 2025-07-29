import os


class FilesystemFreezer:
    """
    Applies additional filesystem restrictions after FUSE mount.
    """

    def __init__(self, path: str):
        self.path = path

    def lockdown(self):
        """
        Attempt to apply additional lockdown measures, such as adjusting permissions.
        """
        for root, dirs, files in os.walk(self.path):
            for d in dirs:
                os.chmod(os.path.join(root, d), 0o555)  # Read/execute only
            for f in files:
                os.chmod(os.path.join(root, f), 0o444)  # Read-only
