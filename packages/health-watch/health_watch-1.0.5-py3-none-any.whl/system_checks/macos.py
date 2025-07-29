import subprocess
from .base import SystemCheck
import re

class MacSystemCheck(SystemCheck):
    def check_disk_encryption(self):
        output = subprocess.getoutput("fdesetup status")
        is_encrypted = True if "FileVault is On" in output else False
        return is_encrypted

    def check_os_updates(self):
        output = subprocess.getoutput("softwareupdate -l").strip()

        # Check if output contains "No new software available."
        updates_available = False if "No new software available." in output else True
        return updates_available

    def check_antivirus_status(self):
        # Common AV process keywords to look for
        av_keywords = ['avast', 'avg', 'kaspersky', 'clam', 'sophos', 'mcafee', 'bitdefender', 'norton', 'av']

        # Run ps aux
        process_list = subprocess.getoutput("ps aux").lower()

        # Check if any antivirus keyword appears in the process list
        found_av_processes = [kw for kw in av_keywords if kw in process_list]

        if found_av_processes:
            result = {
                "AntivirusEnabled": True
            }
        else:
            result = {
                "AntivirusEnabled": False
            }
        return result

    def check_sleep_settings(self):
        output = subprocess.getoutput("pmset -g custom").lower()

        # Extract sleep time under "battery power"
        battery_match = re.search(r"battery power:\s+.*?sleep\s+(\d+)", output, re.DOTALL)
        ac_match = re.search(r"ac power:\s+.*?sleep\s+(\d+)", output, re.DOTALL)

        return {
            "ac_time": int(ac_match.group(1)) if ac_match else None,
            "dc_time": int(battery_match.group(1)) if battery_match else None
        }
