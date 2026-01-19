"""Hub for managing the DigitalSTROM VDC client and TCP listener."""
from __future__ import annotations

import asyncio
import logging
import uuid
import os
from typing import Optional

from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

try:
    import pyvdcapi
    HAS_PYVDCAPI = True
except Exception:
    pyvdcapi = None
    HAS_PYVDCAPI = False


def _get_host_mac(hass: HomeAssistant) -> str:
    """Return the MAC address of the Home Assistant host.

    Tries to read `/sys/class/net/*/address` for a non-loopback
    interface first, falls back to `uuid.getnode()`.
    """
    try:
        # Prefer a real interface MAC from sysfs (Linux)
        for iface in os.listdir("/sys/class/net"):
            if iface == "lo":
                continue
            try:
                with open(f"/sys/class/net/{iface}/address", "r") as f:
                    mac = f.read().strip()
                if mac and mac != "00:00:00:00:00:00":
                    return mac.lower()
            except Exception:
                continue
    except Exception:
        pass

    # Fallback to uuid.getnode()
    mac_int = uuid.getnode()
    mac = ":".join(f"{(mac_int >> ele) & 0xFF:02x}" for ele in range(40, -1, -8))
    return mac


class VdcHost:
    def __init__(self, hass: HomeAssistant, host: str, port: int):
        self.hass = hass
        self.host = host
        self.port = int(port)
        self._server: Optional[asyncio.AbstractServer] = None
        self._vdc_host = None

    async def async_start(self) -> None:
        if HAS_PYVDCAPI:
            try:
                persistence_file = self.hass.config.path("digitalstrom_vdc.yaml")
                mac = _get_host_mac(self.hass)
                name = "Home Assistant vDC Host"
                # Instantiate pyvdcapi VdcHost and start it
                vdc_host = pyvdcapi.VdcHost(
                    name=name,
                    port=self.port,
                    mac_address=mac,
                    vendor_id="homeassistant",
                    persistence_file=persistence_file,
                    announce_service=False,
                )
                await vdc_host.start()
                try:
                    # Create a default vDC using the provided parameters
                    vdc = vdc_host.create_vdc(
                        name="KarlKiels Homeassistant vDC",
                        model="Homeassistant vDC",
                        model_uid="KarlKielHAvDC",
                        model_version="KarlKiels Homeassistant vDC",
                        implementationId="x-KarlKiel-HAvDC",
                    )
                    _LOGGER.info("Created default vDC: %s", getattr(vdc, "dsuid", str(vdc)))
                except Exception:  # pragma: no cover - defensive
                    _LOGGER.exception("Failed to create default vDC on pyvdcapi host")
                self._vdc_host = vdc_host
                _LOGGER.info("Started pyvdcapi VdcHost on port %s", self.port)
                return
            except Exception:  # pragma: no cover - defensive
                _LOGGER.exception("Failed to start pyvdcapi VdcHost")

        # Fallback: simple localhost TCP listener for skeleton integration
        try:
            self._server = await asyncio.start_server(
                self._handle_client, host="127.0.0.1", port=self.port
            )
            _LOGGER.info("DigitalSTROM VDC TCP listener started on port %s", self.port)
        except Exception:  # pragma: no cover - defensive
            _LOGGER.exception("Failed to start TCP listener on port %s", self.port)

    async def async_stop(self) -> None:
        # Stop pyvdcapi host if running
        if self._vdc_host is not None:
            try:
                await self._vdc_host.stop()
            except Exception:
                _LOGGER.exception("Error stopping pyvdcapi VdcHost")
            self._vdc_host = None

        if self._server:
            self._server.close()
            try:
                await self._server.wait_closed()
            except Exception:
                _LOGGER.exception("Error waiting for server to close")
            self._server = None
            _LOGGER.info("DigitalSTROM VDC TCP listener stopped")

    def get_all_vdcs(self):
        """Return list of vDCs managed by the underlying pyvdcapi host, or empty list."""
        if self._vdc_host is not None:
            try:
                return self._vdc_host.get_all_vdcs()
            except Exception:
                _LOGGER.exception("Error getting vDC list from pyvdcapi host")
                return []
        return []

    async def _handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        addr = writer.get_extra_info("peername")
        _LOGGER.debug("Incoming VDC connection from %s", addr)
        try:
            while not reader.at_eof():
                data = await reader.read(1024)
                if not data:
                    break
                # Placeholder: parse/process data and integrate with hass
                _LOGGER.debug("Received %d bytes from %s", len(data), addr)
        except Exception:
            _LOGGER.exception("Error handling VDC client %s", addr)
        finally:
            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass
