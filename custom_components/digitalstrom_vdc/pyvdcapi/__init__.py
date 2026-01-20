"""Minimal shim of pyvdcapi for Home Assistant integration.

This provides a small subset of the real library's API (VdcHost, Vdc,
VdSD) so the integration can run without installing the external
package. It's intentionally lightweight and not a full implementation.
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from typing import List, Optional

logger = logging.getLogger(__name__)


class Vdc:
    def __init__(self, dsuid: Optional[str] = None, name: Optional[str] = None, model: Optional[str] = None):
        self.dsuid = dsuid or uuid.uuid4().hex.upper()
        self.name = name
        self.model = model

    def __str__(self) -> str:
        return f"<Vdc {self.dsuid}>"


class VdSD:
    def __init__(self, dsuid: Optional[str] = None, name: Optional[str] = None):
        self.dsuid = dsuid or uuid.uuid4().hex.upper()
        self.name = name


class VdcHost:
    """Lightweight VdcHost shim implementing the methods used by the integration.

    Methods implemented:
    - async start()
    - async stop()
    - create_vdc(...)
    - get_all_vdcs()
    """

    def __init__(
        self,
        name: str,
        port: int = 8444,
        mac_address: str = "",
        vendor_id: str = "pyvdc-shim",
        persistence_file: Optional[str] = None,
        announce_service: bool = False,
        **properties,
    ) -> None:
        self.name = name
        self.port = int(port)
        self.mac_address = mac_address
        self.vendor_id = vendor_id
        self.persistence_file = persistence_file
        self.announce_service = announce_service
        self._vdcs: List[Vdc] = []
        self._running = False

    async def start(self) -> None:
        """Simulate starting the host/server."""
        # minimal async start to match real API
        await asyncio.sleep(0)
        self._running = True
        logger.info("pyvdcapi shim: started on port %s", self.port)

    async def stop(self) -> None:
        await asyncio.sleep(0)
        self._running = False
        logger.info("pyvdcapi shim: stopped")

    def create_vdc(self, name: str, model: str, model_uid: Optional[str] = None, model_version: str = "1.0", vendor_id: Optional[str] = None, mac_address: Optional[str] = None, **properties) -> Vdc:
        v = Vdc(dsuid=uuid.uuid4().hex.upper(), name=name, model=model)
        self._vdcs.append(v)
        return v

    def get_all_vdcs(self) -> List[Vdc]:
        return list(self._vdcs)


__all__ = ["VdcHost", "Vdc", "VdSD"]
