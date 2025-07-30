import asyncio
import json
import os
import logging
import random
from typing import Callable, List, Optional, Any, Iterator, Dict, Set, TypeVar, Protocol, runtime_checkable

T = TypeVar('T')

@runtime_checkable
class WebSocketClientProtocol(Protocol):
    async def send(self, message: str) -> None: ...
    async def close(self) -> None: ...
    @property
    def open(self) -> bool: ...

# Setup module‐level logger with a default handler if none exists.
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)


class QuotesClient:
    """
    A Python SDK for connecting to the Quotes Server via WebSocket.

    Attributes:
      base_url (str): WebSocket URL of the quotes server.
      token (str): JWT token for authentication.
      log_level (str): Logging level. Options: "error", "info", "debug".
    """

    ACTION_SUBSCRIBE = "subscribe"
    ACTION_UNSUBSCRIBE = "unsubscribe"

    def __init__(
        self,
        base_url: Optional[str] = None,
        token: Optional[str] = None,
        log_level: str = "error",
        max_message_size: int = 10 * 1024 * 1024,
        batch_size: int = 20
    ):
        logger.debug("Initializing QuotesClient with params: base_url=%s, log_level=%s, max_message_size=%d, batch_size=%d", 
                    base_url, log_level, max_message_size, batch_size)

        valid_levels = {"error": logging.ERROR, "info": logging.INFO, "debug": logging.DEBUG}
        if log_level not in valid_levels:
            raise ValueError(f"log_level must be one of {list(valid_levels.keys())}")
        logger.setLevel(valid_levels[log_level])

        self.log_level = log_level
        self.max_message_size = max_message_size
        self.batch_size = batch_size

        self.base_url = base_url or os.environ.get("WZ__QUOTES_BASE_URL")
        self.token = token or os.environ.get("WZ__TOKEN")
        if not self.token:
            raise ValueError("JWT token must be provided as an argument or in .env (WZ__TOKEN)")
        if not self.base_url:
            raise ValueError("Base URL must be provided as an argument or in .env (WZ__QUOTES_BASE_URL)")

        self.url = f"{self.base_url}?token={self.token}"
        self.ws: Optional[WebSocketClientProtocol] = None
        self.subscribed_instruments: Set[str] = set()
        self._running = False
        self._background_task: Optional[asyncio.Task[None]] = None

        self._backoff_base = 1
        self._backoff_factor = 2
        self._backoff_max = 60

        # Callbacks are plain synchronous functions
        self.on_tick: Optional[Callable[[Any, Dict[str, Any]], None]] = None
        self.on_connect: Optional[Callable[[Any], None]] = None
        self.on_close: Optional[Callable[[Any, Optional[int], Optional[str]], None]] = None
        self.on_error: Optional[Callable[[Any, Exception], None]] = None

        logger.debug("QuotesClient initialized successfully")

    def _chunk_list(self, data: List[Any], chunk_size: int) -> Iterator[List[Any]]:
        logger.debug("Chunking list of size %d with chunk_size %d", len(data), chunk_size)
        return (data[i:i + chunk_size] for i in range(0, len(data), chunk_size))

    async def _connect_with_backoff(self) -> None:
        backoff = self._backoff_base
        logger.debug("Starting connection with initial backoff: %d", backoff)

        while self._running:
            try:
                logger.debug("Attempting WebSocket connection to %s", self.url)
                # Using string literal for import to avoid type checking issues
                ws = await __import__('websockets').connect(self.url, max_size=self.max_message_size)
                self.ws = ws
                logger.debug("WebSocket connection established successfully")

                if self.on_connect:
                    logger.debug("Executing on_connect callback")
                    try:
                        self.on_connect(self)
                    except Exception as e:
                        logger.error("Error in on_connect callback: %s", e, exc_info=True)

                if self.subscribed_instruments:
                    logger.debug("Re-subscribing to %d instruments", len(self.subscribed_instruments))
                    for batch in self._chunk_list(list(self.subscribed_instruments), self.batch_size):
                        msg = {"action": self.ACTION_SUBSCRIBE, "instruments": batch}
                        if self.ws:  # Check if ws is not None
                            await self.ws.send(json.dumps(msg))
                            logger.info("Re-subscribed to %d instruments", len(batch))
                            await asyncio.sleep(0.1)

                backoff = self._backoff_base
                await self._handle_messages()

            except Exception as e:
                logger.debug("Connection error occurred: %s", str(e), exc_info=True)
                if self.on_error:
                    try:
                        self.on_error(self, e)
                    except Exception as ex:
                        logger.error("Error in on_error callback: %s", ex, exc_info=True)

            if not self._running:
                logger.debug("Client stopped, breaking reconnection loop")
                break

            sleep_time = min(backoff, self._backoff_max)
            logger.debug("Calculated reconnection backoff: %s seconds", sleep_time)
            await asyncio.sleep(sleep_time)
            backoff = backoff * self._backoff_factor + random.uniform(0, 1)

    async def _handle_messages(self) -> None:
        try:
            logger.debug("Starting message handling loop")
            if self.ws is None:
                logger.error("WebSocket connection is None")
                return
                
            # Using string literal for import to avoid type checking issues
            async for message in self.ws:  # type: ignore
                if isinstance(message, str):
                    msg_size = len(message.encode("utf-8"))
                    logger.debug("Received message of size: %d bytes", msg_size)
                    
                    for chunk in message.strip().split("\n"):
                        if not chunk:
                            continue
                        try:
                            tick = json.loads(chunk)
                            logger.debug("Successfully parsed JSON message for instrument: %s", 
                                       tick.get('instrument', 'unknown'))
                            if self.on_tick:
                                logger.debug("Executing on_tick callback")
                                self.on_tick(self, tick)
                        except json.JSONDecodeError as e:
                            logger.debug("Failed to parse JSON message: %s. Content: %s", str(e), chunk[:100])
                            logger.error("JSON parse error: %s", e)
                else:
                    logger.debug("Received non-string message of type: %s", type(message).__name__)
                    logger.warning("Non-string message: %s", type(message).__name__)
        except Exception as e:
            logger.debug("Error in message handling: %s", str(e), exc_info=True)
            if self.on_error:
                try:
                    self.on_error(self, e)
                except Exception:
                    pass

    async def _subscribe_async(self, instruments: List[str]) -> None:
        logger.debug("Processing async subscription request for %d instruments", len(instruments))
        if self.ws and self.ws.open:
            new = set(instruments) - self.subscribed_instruments
            if new:
                logger.debug("Found %d new instruments to subscribe", len(new))
                self.subscribed_instruments |= new
                for batch in self._chunk_list(list(new), self.batch_size):
                    logger.debug("Sending subscription request for batch of %d instruments", len(batch))
                    await self.ws.send(json.dumps({
                        "action": self.ACTION_SUBSCRIBE,
                        "instruments": batch
                    }))
                    await asyncio.sleep(0.1)
        else:
            logger.debug("WebSocket not ready, queueing %d instruments for later subscription", len(instruments))
            self.subscribed_instruments |= set(instruments)

    async def _unsubscribe_async(self, instruments: List[str]) -> None:
        logger.debug("Processing async unsubscription request for %d instruments", len(instruments))
        if self.ws and self.ws.open:
            to_remove = set(instruments) & self.subscribed_instruments
            if to_remove:
                logger.debug("Found %d instruments to unsubscribe", len(to_remove))
                for batch in self._chunk_list(list(to_remove), self.batch_size):
                    logger.debug("Sending unsubscription request for batch of %d instruments", len(batch))
                    await self.ws.send(json.dumps({
                        "action": self.ACTION_UNSUBSCRIBE,
                        "instruments": batch
                    }))
                    await asyncio.sleep(0.1)
                logger.debug("Removed %d instruments from subscription set", len(to_remove))
                self.subscribed_instruments -= to_remove
        else:
            logger.debug("WebSocket not ready, removing %d instruments from queue", len(instruments))
            self.subscribed_instruments -= set(instruments)

    def subscribe(self, instruments: List[str]) -> None:
        logger.debug("Scheduling subscription for %d instruments", len(instruments))
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        loop.create_task(self._subscribe_async(instruments))

    def unsubscribe(self, instruments: List[str]) -> None:
        logger.debug("Scheduling unsubscription for %d instruments", len(instruments))
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        loop.create_task(self._unsubscribe_async(instruments))

    async def close(self) -> None:
        logger.debug("Initiating WebSocket connection closure")
        self._running = False
        if self.ws:
            logger.debug("Closing active WebSocket connection")
            await self.ws.close()
            logger.info("WebSocket closed.")
        if self._background_task and not self._background_task.done():
            logger.debug("Cancelling background connection task")
            self._background_task.cancel()
            try:
                await self._background_task
            except asyncio.CancelledError:
                pass

    def connect(self) -> None:
        logger.debug("Starting blocking connect operation")
        self._running = True
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        try:
            loop.run_until_complete(self._connect_with_backoff())
        finally:
            if not loop.is_closed():
                tasks = asyncio.all_tasks(loop)
                for t in tasks:
                    t.cancel()
                try:
                    loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
                except Exception:
                    pass

    def connect_async(self) -> None:
        logger.debug("Starting non-blocking async connect operation")
        if self._running:
            logger.warning("Client already running.")
            return
        self._running = True
        loop = asyncio.get_event_loop()
        self._background_task = loop.create_task(self._connect_with_backoff())

    def stop(self) -> None:
        logger.debug("Stop signal received")
        self._running = False
        logger.info("Client stopping; will close soon.")
