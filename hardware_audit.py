import json
import subprocess
from datetime import datetime

with open("baseline.json", "r") as f:
    baseline = json.load(f)

mem_output = subprocess.check_output("free -m | awk '/Mem:/ {print $2}'", shell=True).decode().strip()
live_ram = int(mem_output)

disk_output = subprocess.check_output("lsblk -d -n -o NAME", shell=True).decode().splitlines()
live_disks = [d for d in disk_output if not d.startswith("loop") and not d.startswith("sr")]

alerts = []
if live_ram < baseline["expected_ram_mb"]:
    alerts.append(
        f"MEMORY MISMATCH: Expected {baseline['expected_ram_mb']}MB, detected {live_ram}MB. Possible failed DIMM."
    )

for disk in baseline["expected_disks"]:
    if disk not in live_disks:
        alerts.append(f"STORAGE FAILURE: Expected drive /dev/{disk} is missing.")

if alerts:
    ticket = (
        f"=== AUTOMATED RMA HARDWARE TICKET ===\n"
        f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"Asset Tag: {baseline['asset_tag']}\n"
        f"Physical Location: {baseline['rack_location']}\n"
        f"IP Address: {baseline['ip_address']}\n"
        f"Diagnostics:\n - " + "\n - ".join(alerts) + "\n"
        f"Action Required: Dispatch technician to {baseline['rack_location']} for component reseat/replacement.\n"
    )
    print(ticket)
    with open("rma_ticket.txt", "w") as out:
        out.write(ticket)
else:
    print(f"[OK] {baseline['asset_tag']} ({baseline['rack_location']}) passed all hardware checks.")