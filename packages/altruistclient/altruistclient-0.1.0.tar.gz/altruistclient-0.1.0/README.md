# AltruistClient

Python async library for discovering and communicating with Altruist ESP32-based sensors over the local network using mDNS (zeroconf) and HTTP.

## Features

- Discover sensors on your LAN using Zeroconf (`_altruist._tcp.local.`)
- Fetch sensor metadata and measurement data from `/data.json`
- Filter supported sensor names
- Async/AIOHTTP-based for fast, non-blocking usage

---

## Installation

```bash
pip install atruistclient
```

---

## Quick Start

```python
import asyncio
from aiohttp import ClientSession
from zeroconf.asyncio import AsyncZeroconf
from altruistclient import AltruistDiscoverer, AltruistClient

async def main():
    async with AsyncZeroconf() as zc, ClientSession() as session:
        discoverer = AltruistDiscoverer(zc, session)
        devices = await discoverer.get_devices()

        for device in devices:
            client = AltruistClient(session, device)
            data = await client.fetch_data()
            print(f"Device {client.device_id} (fw: {client.fw_version})")
            print("Sensor names:", client.sensor_names)
            print("Data:", data)

asyncio.run(main())
```

---

## Class Overview

### `AltruistDiscoverer`

- Scans for `_altruist._tcp.local.` devices using zeroconf.
- Filters and validates devices via their `/data.json` response.
- Returns a list of `AltruistDeviceModel` instances.

```python
discoverer = AltruistDiscoverer(zc, session)
devices = await discoverer.get_devices()
```

---

### `AltruistClient`

- Handles data fetching and parsing from a specific device.
- Extracts firmware version, sensor types, and measurements.

```python
client = AltruistClient(session, device)
data = await client.fetch_data()
print(client.fw_version, client.sensor_names)
```

You can also construct it directly from an IP:

```python
client = await AltruistClient.from_ip_address(session, "192.168.1.45")
```

---

### `AltruistDeviceModel`

Simple dataclass containing:

- `id`: sensor ID (from `/data.json`)
- `ip_address`: resolved IP
- `fw_version`: firmware version (optional)

```python
@dataclass
class AltruistDeviceModel:
    id: str
    ip_address: str
    name: str = "Altruist Sensor"
    fw_version: str | None = None
```

---

## Notes

- `get_devices()` waits 5 seconds for mDNS discovery.
- Only devices that respond to `/data.json` and provide a valid `sensor_id` are returned.
- Internally uses `aiohttp`.
