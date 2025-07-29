import shutil


def check_dependencies():
    """
    Verify required binaries (like fuse-bindfs, fusermount) exist.
    """
    required = ["fuse-bindfs", "fusermount"]
    for binary in required:
        if shutil.which(binary) is None:
            raise RuntimeError(
                f"Required binary '{binary}' not found in PATH.")


def ensure_directory(path: str):
    """
    Create a directory if it doesn't exist.
    """
    os.makedirs(path, exist_ok=True)
