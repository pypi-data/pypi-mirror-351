import platform
from .windows import WindowsSystemCheck
from .macos import MacSystemCheck
from .linux import LinuxSystemCheck

def get_os_type():
    os_name = platform.system()
    if os_name == "Windows":
        return "windows"
    elif os_name == "Darwin":
        return "macos"
    elif os_name == "Linux":
        return "linux"
    else:
        return "unknown"

def get_checker():
    os_type = get_os_type()
    if os_type == "windows":
        return WindowsSystemCheck()
    elif os_type == "macos":
        return MacSystemCheck()
    elif os_type == "linux":
        return LinuxSystemCheck()
    else:
        raise NotImplementedError("Unsupported OS")
