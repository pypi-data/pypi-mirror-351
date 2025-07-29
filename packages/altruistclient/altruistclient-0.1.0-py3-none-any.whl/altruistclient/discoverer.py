"""Module for discovering Altruist sensors using zeroconf."""

import asyncio
import logging

from zeroconf import ServiceStateChange, Zeroconf
from aiohttp import ClientError, ClientSession
from zeroconf.asyncio import AsyncServiceBrowser, AsyncServiceInfo, AsyncZeroconf

from .client import AltruistClient
from .model import AltruistDeviceModel
from .errors import AltruistError

_LOGGER: logging.Logger = logging.getLogger(__name__)

_PENDING_TASKS: set[asyncio.Task] = set()


class AltruistDiscoverer:
    """Discover ESP32 sensors using zeroconf."""

    def __init__(self, zeroconf_instance: AsyncZeroconf, session: ClientSession) -> None:
        """Initialize the discoverer.

        :param zeroconf_instance: An instance of AsyncZeroconf.
        """
        self.zeroconf: Zeroconf = zeroconf_instance.zeroconf
        self.session = session
        self._devices: list[AltruistDeviceModel] = []

    async def get_devices(self) -> list[AltruistDeviceModel]:
        """Discover devices advertising the given service type.

        This method waits for a fixed interval to collect available devices.
        If no device is discovered, it raises DevicesNotFoundException.

        :return: A list of ServiceInfo objects for the discovered devices.
        :raises DevicesNotFoundException: If no devices are found.
        """
        # Clear previous results.
        self._devices.clear()
        services = ["_altruist._tcp.local."]
        aiobrowser = AsyncServiceBrowser(
            self.zeroconf, services, handlers=[self._async_on_service_state_change]
        )
        await asyncio.sleep(5)

        return self._devices

    def _async_on_service_state_change(
        self, zeroconf, service_type: str, name: str, state_change: ServiceStateChange
    ) -> None:
        _LOGGER.debug(f"Service {name} of type {service_type} state changed: {state_change}")
        if state_change is not ServiceStateChange.Added:
            return
        task = asyncio.ensure_future(self._async_add_device(zeroconf, service_type, name))
        _PENDING_TASKS.add(task)
        task.add_done_callback(_PENDING_TASKS.discard)


    async def _async_add_device(self, zeroconf, service_type: str, name: str) -> None:
        info = AsyncServiceInfo(service_type, name)
        await info.async_request(zeroconf, 3000)
        ip = info.parsed_addresses()[0]
        try:
            client = await AltruistClient.from_ip_address(self.session, ip)
            device = client.device
            self._devices.append(device)
            _LOGGER.debug(f"Added device: {device}")
        except AltruistError:
            _LOGGER.warning("Skipping unreachable or malformed device at %s", ip)

