import asyncio
import pickle
from dataclasses import dataclass, field
from datetime import timedelta
from logging import getLogger
from types import TracebackType
from typing import Any, Self

import zmq
import zmq.asyncio

from ._commands import Register

_LOG = getLogger(__name__)


class AsyncRougeClientError(Exception): ...


class AsyncRougeTimeoutError(AsyncRougeClientError, TimeoutError): ...


@dataclass(slots=True, frozen=True)
class Cfg:
    host: str
    mem_map_port: int = 9000
    dma_stream_ports: list = field(default_factory=list)
    binary_protocol: bool = True
    timeout: timedelta = timedelta(seconds=10)
    reconnection_delay: timedelta = timedelta(seconds=1)

    def get_port(self) -> int:
        return self.mem_map_port + 1 if self.binary_protocol else 0


def _create_req_socket(
    context: zmq.asyncio.Context, cfg: Cfg
) -> zmq.asyncio.Socket:
    """Create binary RPC REQ socket."""

    sock = context.socket(zmq.REQ)

    sock.setsockopt(zmq.LINGER, 0)
    sock.setsockopt(zmq.REQ_RELAXED, 1)
    sock.setsockopt(zmq.REQ_CORRELATE, 1)

    sock.connect(f"tcp://{cfg.host}:{cfg.get_port()}")

    _LOG.info(f"REQ connected to port '{cfg.host}:{cfg.get_port()}'")

    return sock


def _create_mon_socket(
    context: zmq.asyncio.Context, cfg: Cfg
) -> zmq.asyncio.Socket:
    """Create PUB/SUB monitoring socket."""

    sock = context.socket(zmq.SUB)

    sock.setsockopt(zmq.LINGER, 0)
    sock.setsockopt(zmq.SUBSCRIBE, b"")

    sock.connect(f"tcp://{cfg.host}:{cfg.get_port()}")

    _LOG.info(f"SUB connected to port '{cfg.host}:{cfg.get_port()}'")
    return sock


class AsyncRougeClient:
    _cfg: Cfg
    """Connection details and protocol (plain json or pickel json)"""

    _request_socket: zmq.asyncio.Socket | None = None
    """request socket: read, write or rpc calls"""

    _context: zmq.asyncio.Context = zmq.asyncio.Context.instance()
    """Asyncio context"""

    _monitor_socket: zmq.asyncio.Socket | None = None
    """Subscription socket: monitors updates pushed by the rouge"""

    _lock: asyncio.Lock = asyncio.Lock()
    """asyncio lock to prevent to prevent bursts of reconnections"""

    _closed: bool = False
    """if close had been called."""

    def __init__(self, cfg: Cfg) -> None:
        self._cfg = cfg

    async def __aenter__(self) -> Self:
        await self.connect()
        return self

    async def __aexit__(
        self,
        _exc_type: type[BaseException] | None,
        _exc_val: BaseException | None,
        _exc_tb: TracebackType | None,
    ) -> bool | None:
        await self.close()
        return False

    async def connect(self) -> Self:

        if self._closed:
            raise AsyncRougeClientError("Client has been closed!")

        if self._request_socket is None:
            self._request_socket = _create_req_socket(self._context, self._cfg)

        if self._monitor_socket is None:
            self._monitor_socket = _create_mon_socket(self._context, self._cfg)

        return self

    async def close(self) -> None:

        self._closed = True

        if self._request_socket is not None:
            self._request_socket.close()
            self._request_socket = None

        if self._monitor_socket is not None:
            self._monitor_socket.close()
            self._monitor_socket = None

        _LOG.info("Async Rogue client closed")

    async def get_value[ValueType](self, register: Register[ValueType]) -> Any:
        """Execute a remote PyRogue node attribute."""

        if self._closed or self._request_socket is None:
            raise AsyncRougeClientError("Client is not connected")

        payload = register.generate_get_request()
        print(register)

        async with self._lock:
            try:
                await self._request_socket.send(payload)

                response: bytes = await asyncio.wait_for(
                    self._request_socket.recv(),
                    timeout=self._cfg.timeout.total_seconds(),
                )

            except (TimeoutError, zmq.ZMQError) as exc:
                self._request_socket.close()
                self._request_socket = _create_req_socket(
                    self._context, self._cfg
                )

                raise AsyncRougeTimeoutError(
                    f"Failed to read from {register!s}"
                ) from exc

        result: Any = pickle.loads(response)

        if isinstance(result, Exception):
            raise result

        return result
