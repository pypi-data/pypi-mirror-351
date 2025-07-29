import os
import time
import json
import hashlib
import socket
import requests
from datetime import datetime
from system_checks import get_checker, get_os_type
from dotenv import load_dotenv

load_dotenv()

API_ENDPOINT = os.getenv("API_URL") or "https://healthwatch-1ibo.onrender.com/reports"

MACHINE_ID = socket.gethostname()

def get_system_snapshot():
    checker = get_checker()

    snapshot = {
        "machine_id": MACHINE_ID,
        "timestamp": datetime.utcnow().isoformat(),
        "os_type": get_os_type(),
        "disk_encryption": checker.check_disk_encryption(),
        "os_updates": checker.check_os_updates(),
        "antivirus_status": checker.check_antivirus_status(),
        "sleep_settings": checker.check_sleep_settings(),
    }
    return snapshot


def hash_snapshot(snapshot):
    """Returns a hash of the snapshot to detect change."""
    snapshot_copy = snapshot.copy()
    snapshot_copy.pop("timestamp", None)
    snapshot_str = json.dumps(snapshot_copy, sort_keys=True)
    return hashlib.sha256(snapshot_str.encode()).hexdigest()


def send_report(snapshot):
    try:
        response = requests.post(API_ENDPOINT, json=snapshot)
        print("Report sent:", response.status_code)
    except requests.exceptions.RequestException as e:
        print("Failed to send report:", e)


def main():
    print("Starting system check agent...")
    previous_hash = None

    while True:
        snapshot = get_system_snapshot()
        current_hash = hash_snapshot(snapshot)

        if current_hash != previous_hash:
            print("Change detected, sending update...")
            send_report(snapshot)
            previous_hash = current_hash
        else:
            print("No change detected, skipping report.")

        sleep_time = 30 * 60
        print(f"Sleeping for {sleep_time // 60} minutes...\n")
        time.sleep(sleep_time)


if __name__ == "__main__":
    main()
