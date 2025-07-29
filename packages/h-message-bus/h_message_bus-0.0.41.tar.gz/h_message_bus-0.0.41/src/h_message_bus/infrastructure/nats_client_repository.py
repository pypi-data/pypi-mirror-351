import logging
import asyncio
from typing import Optional, Callable, Any

import nats
from nats.aio.client import Client as NatsClient

from ..infrastructure.nats_config import NatsConfig

class NatsClientRepository:
    """
    Repository for managing connection and interaction with a NATS server.
    """

    def __init__(self, config: NatsConfig):
        self.config = config
        self.client: Optional[NatsClient] = None
        self.subscriptions = []
        self.logger = logging.getLogger(__name__)

    async def connect(self) -> None:
        """Connect to NATS server with event handlers and logging."""
        if self.client and self.client.is_connected:
            return

        async def error_cb(e):
            self.logger.error(f"NATS client error: {e}")

        async def disconnect_cb():
            self.logger.warning("NATS client disconnected.")

        async def reconnect_cb():
            self.logger.info("NATS client reconnected.")

        async def closed_cb():
            self.logger.warning("NATS client connection closed.")

        self.logger.info(f"Connecting to NATS server at {self.config.server}")

        self.client = await nats.connect(
            servers=self.config.server,
            max_reconnect_attempts=self.config.max_reconnect_attempts,
            reconnect_time_wait=self.config.reconnect_time_wait,
            connect_timeout=self.config.connection_timeout,
            ping_interval=self.config.ping_interval,
            max_outstanding_pings=self.config.max_outstanding_pings,
            error_cb=error_cb,
            disconnected_cb=disconnect_cb,
            reconnected_cb=reconnect_cb,
            closed_cb=closed_cb,
        )  # type: ignore

    async def _ensure_connected(self, retries: int = 5):
        """Wait and retry until the client is connected."""
        for attempt in range(retries):
            if self.client and self.client.is_connected:
                return
            self.logger.info(f"Waiting for NATS connection (attempt {attempt+1})...")
            await asyncio.sleep(2 ** attempt)
        raise ConnectionError("Could not establish connection to NATS server.")

    async def publish(self, subject: str, payload: bytes, retries: int = 3) -> None:
        """Publish a raw message to NATS with retries and backoff."""
        for attempt in range(retries):
            try:
                await self._ensure_connected()
                await self.client.publish(subject, payload)
                return
            except Exception as e:
                self.logger.error(f"Failed to publish message (attempt {attempt+1}): {e}")
                await asyncio.sleep(2 ** attempt)
        self.logger.error("Giving up publishing after retries.")

    async def subscribe(self, subject: str, callback: Callable) -> Any:
        """Subscribe to a subject with a callback."""
        await self._ensure_connected()
        try:
            subscription = await self.client.subscribe(subject, cb=callback)
            self.subscriptions.append(subscription)
            return subscription
        except Exception as e:
            self.logger.error(f"Failed to subscribe to {subject}: {e}")
            return None

    async def request(self, subject: str, payload: bytes, timeout: float = 2.0, retries: int = 3) -> Optional[bytes]:
        """Send a request and get a raw response with retries and backoff."""
        for attempt in range(retries):
            try:
                await self._ensure_connected()
                response = await self.client.request(subject, payload, timeout=timeout)
                return response.data
            except Exception as e:
                self.logger.error(f"NATS request failed (attempt {attempt+1}): {e}")
                await asyncio.sleep(2 ** attempt)
        self.logger.error("Giving up request after retries.")
        return None

    async def close(self) -> None:
        """Close all subscriptions and NATS connection."""
        if self.client and self.client.is_connected:
            try:
                for sub in self.subscriptions:
                    await sub.unsubscribe()
                await self.client.drain()
            except Exception as e:
                self.logger.error(f"Error during NATS cleanup: {e}")
            finally:
                self.client = None
                self.subscriptions = []