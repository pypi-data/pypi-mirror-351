"""Module for Altruist device model."""

from dataclasses import dataclass

from zeroconf.asyncio import AsyncServiceInfo


@dataclass
class AltruistDeviceModel:
    """Data class for storing information about an Altruist device."""

    id: str
    ip_address: str
    name: str = "Altruist Sensor"
    fw_version: str | None = None
