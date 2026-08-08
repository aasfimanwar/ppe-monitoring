from app.cameras.onvif_discovery import discover_devices

devices = discover_devices(timeout_seconds=4.0)
print(f"Found {len(devices)} ONVIF device(s)")
for device in devices:
    print(" -", device)