import subprocess
from .base import SystemCheck

class LinuxSystemCheck(SystemCheck):
    def check_disk_encryption(self):
        output = subprocess.getoutput("lsblk -o NAME,TYPE,FSTYPE,MOUNTPOINT")
        return "crypto_LUKS" in output

    def check_os_updates(self):
        output = subprocess.getoutput("apt list --upgradable 2>/dev/null")
        lines = output.strip().splitlines()
        # If only "Listing... Done" is present, then no updates
        return len(lines) > 1

    def check_antivirus_status(self):
        output = subprocess.getoutput("ps aux | grep [c]lam")
        return {
            "AntivirusEnabled" : bool(output.strip())
        }

    def check_sleep_settings(self):
        def get_timeout(setting):
            output = subprocess.getoutput(f"gsettings get org.gnome.settings-daemon.plugins.power {setting}")
            return int(output.split()[-1])

        ac_time = get_timeout("sleep-inactive-ac-timeout")
        dc_time = get_timeout("sleep-inactive-battery-timeout")

        return {
            "ac_time": ac_time,
            "dc_time": dc_time
        }
