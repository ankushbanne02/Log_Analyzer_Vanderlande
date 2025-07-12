
import re
from collections import defaultdict
from datetime import datetime

# mapping of message IDs
ID_MAP = {
    "1": "ItemRegister",
    "2": "ItemPropertiesUpdate",
    "3": "ItemInstruction",
    "5": "UnverifiedSortReport",
    "6": "VerifiedSortReport",
    "7": "ItemDeRegister",
    "98": "WatchdogReply",
    "99": "WatchdogRequest",
}

LOG_TS   = re.compile(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),(\d{3})')
RAW_BODY = re.compile(r'\): (.*?)(?: \[\]$)')

def parse_log(text: str):
    """Return list[dict] — one lifecycle per PIC."""
    parcels = defaultdict(lambda: {
        "pic": None,
        "hostId": None,
        "lifeCycle": {"registeredAt": None, "closedAt": None, "status": "open"},
        "barcodeErr": False,
        "events": []
    })

    for line in text.splitlines():
        ts_m, body_m = LOG_TS.search(line), RAW_BODY.search(line)
        if not (ts_m and body_m):
            continue

        ts_iso = datetime.strptime(
            f"{ts_m.group(1)}.{ts_m.group(2)}", "%Y-%m-%d %H:%M:%S.%f"
        ).isoformat()
        parts = body_m.group(1).strip().split("|")
        if len(parts) < 5 or ID_MAP.get(parts[3], "").startswith("Watchdog"):
            continue

        try:
            pic = int(parts[4])
        except ValueError:
            continue

        parcel = parcels[pic]
        parcel["pic"] = pic
        msg = ID_MAP.get(parts[3], f"Type{parts[3]}")

        # ---- update lifecycle summary ----
        if msg == "ItemRegister":
            parcel["lifeCycle"]["registeredAt"] = (
                parcel["lifeCycle"]["registeredAt"] or ts_iso
            )
        elif msg == "ItemInstruction":
            parcel["hostId"] = parcel["hostId"] or parts[5]
        elif msg == "ItemPropertiesUpdate":
            if parts[8].split(";")[0] != "6":
                parcel["barcodeErr"] = True
        elif msg == "VerifiedSortReport":
            parcel["lifeCycle"]["status"] = "sorted"
        elif msg == "ItemDeRegister":
            if parcel["lifeCycle"]["status"] != "sorted":
                parcel["lifeCycle"]["status"] = "deregistered"
            parcel["lifeCycle"]["closedAt"] = ts_iso

        # ---- store raw event ----
        parcel["events"].append({
            "ts": ts_iso,
            "type": msg,
            "raw": "|".join(parts)
        })

    return list(parcels.values())
