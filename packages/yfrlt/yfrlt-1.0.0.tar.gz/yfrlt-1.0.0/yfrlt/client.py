"""
Yahoo Finance Real-Time WebSocket Client

Handles WebSocket connections to Yahoo Finance v2 API and manages subscriptions.
"""

import asyncio
import json
import logging
import threading
import time
from typing import Callable, List, Optional, Dict, Any, AsyncIterator
import websocket
import websockets

from .parser import MessageParser
from .models import PriceData
from .exceptions import YFRLTError, ConnectionError, SubscriptionError

logger = logging.getLogger(__name__)


class Client:
    """
    Synchronous Yahoo Finance WebSocket client.
    
    Provides real-time financial data streaming from Yahoo Finance WebSocket v2 API.
    """
    
    def __init__(self, 
                 url: str = "wss://streamer.finance.yahoo.com/?version=2",
                 reconnect: bool = True,
                 reconnect_delay: int = 5,
                 timeout: int = 30):
        """
        Initialize the Yahoo Finance WebSocket client.
        
        Args:
            url: WebSocket URL (default: Yahoo Finance v2 endpoint)
            reconnect: Whether to automatically reconnect on disconnect
            reconnect_delay: Seconds to wait before reconnecting
            timeout: Connection timeout in seconds
        """
        self.url = url
        self.reconnect = reconnect
        self.reconnect_delay = reconnect_delay
        self.timeout = timeout
        
        self.ws: Optional[websocket.WebSocketApp] = None
        self.parser = MessageParser()
        self.subscriptions: List[str] = []
        self.callbacks: List[Callable[[PriceData], None]] = []
        self.is_connected = False
        self.should_run = False
        self._thread: Optional[threading.Thread] = None
        
    def subscribe(self, symbols: List[str], callback: Callable[[PriceData], None]) -> None:
        """
        Subscribe to real-time data for given symbols.
        
        Args:
            symbols: List of symbols to subscribe to (e.g., ['BTC-USD', 'AAPL'])
            callback: Function called when new data arrives
        """
        self.subscriptions.extend(symbols)
        self.callbacks.append(callback)
        
        # If already connected, send subscription immediately
        if self.is_connected and self.ws:
            self._send_subscription(symbols)
            
    def start(self) -> None:
        """Start the WebSocket client and begin streaming data."""
        if self.should_run:
            raise YFRLTError("Client is already running")
            
        self.should_run = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        
        # Wait a moment for connection
        time.sleep(1)
        if not self.is_connected:
            logger.warning("Connection may not be established yet")
            
    def stop(self) -> None:
        """Stop the WebSocket client."""
        self.should_run = False
        if self.ws:
            self.ws.close()
        if self._thread:
            self._thread.join(timeout=5)
            
    def _run(self) -> None:
        """Main run loop with reconnection logic."""
        while self.should_run:
            try:
                self._connect()
            except Exception as e:
                logger.error(f"Connection failed: {e}")
                if not self.reconnect or not self.should_run:
                    break
                    
                logger.info(f"Reconnecting in {self.reconnect_delay} seconds...")
                time.sleep(self.reconnect_delay)
                
    def _connect(self) -> None:
        """Establish WebSocket connection."""
        logger.info(f"Connecting to {self.url}")
        
        self.ws = websocket.WebSocketApp(
            self.url,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close
        )
        
        self.ws.run_forever(ping_interval=30, ping_timeout=10)
        
    def _on_open(self, ws) -> None:
        """Handle WebSocket connection opened."""
        logger.info("WebSocket connection established")
        self.is_connected = True
        
        # Send all pending subscriptions
        if self.subscriptions:
            self._send_subscription(self.subscriptions)
            
    def _on_message(self, ws, message: str) -> None:
        """Handle incoming WebSocket messages."""
        try:
            # Parse Yahoo Finance v2 format
            data = json.loads(message)
            if data.get('type') == 'pricing':
                # Parse the protobuf message
                price_data = self.parser.parse_pricing_message(data.get('message', ''))
                
                # Call all registered callbacks
                for callback in self.callbacks:
                    try:
                        callback(price_data)
                    except Exception as e:
                        logger.error(f"Error in callback: {e}")
                        
        except Exception as e:
            logger.error(f"Error parsing message: {e}")
            
    def _on_error(self, ws, error) -> None:
        """Handle WebSocket errors."""
        logger.error(f"WebSocket error: {error}")
        
    def _on_close(self, ws, close_status_code, close_msg) -> None:
        """Handle WebSocket connection closed."""
        logger.info("WebSocket connection closed")
        self.is_connected = False
        
    def _send_subscription(self, symbols: List[str]) -> None:
        """Send subscription message to Yahoo Finance."""
        subscription_msg = {"subscribe": symbols}
        
        try:
            self.ws.send(json.dumps(subscription_msg))
            logger.info(f"Subscribed to: {symbols}")
        except Exception as e:
            logger.error(f"Failed to send subscription: {e}")
            raise SubscriptionError(f"Failed to subscribe to {symbols}")


class AsyncClient:
    """
    Asynchronous Yahoo Finance WebSocket client.
    
    Provides async/await interface for real-time financial data streaming.
    """
    
    def __init__(self, 
                 url: str = "wss://streamer.finance.yahoo.com/?version=2",
                 reconnect: bool = True,
                 reconnect_delay: int = 5):
        """
        Initialize the async Yahoo Finance WebSocket client.
        
        Args:
            url: WebSocket URL
            reconnect: Whether to automatically reconnect
            reconnect_delay: Seconds to wait before reconnecting
        """
        self.url = url
        self.reconnect = reconnect
        self.reconnect_delay = reconnect_delay
        
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None
        self.parser = MessageParser()
        self.subscriptions: List[str] = []
        self.is_connected = False
        
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()
        
    async def connect(self) -> None:
        """Establish WebSocket connection."""
        try:
            logger.info(f"Connecting to {self.url}")
            self.websocket = await websockets.connect(self.url)
            self.is_connected = True
            logger.info("WebSocket connection established")
            
            # Send pending subscriptions
            if self.subscriptions:
                await self._send_subscription(self.subscriptions)
                
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            raise ConnectionError(f"Failed to connect to {self.url}")
            
    async def disconnect(self) -> None:
        """Close WebSocket connection."""
        if self.websocket:
            await self.websocket.close()
            self.is_connected = False
            logger.info("WebSocket connection closed")
            
    async def subscribe(self, symbols: List[str]) -> None:
        """
        Subscribe to real-time data for given symbols.
        
        Args:
            symbols: List of symbols to subscribe to
        """
        self.subscriptions.extend(symbols)
        
        if self.is_connected:
            await self._send_subscription(symbols)
            
    async def stream(self) -> AsyncIterator[PriceData]:
        """
        Stream real-time price data.
        
        Yields:
            PriceData objects with real-time market information
        """
        if not self.is_connected:
            raise ConnectionError("Not connected. Call connect() first.")
            
        try:
            async for message in self.websocket:
                try:
                    # Parse Yahoo Finance v2 format
                    data = json.loads(message)
                    if data.get('type') == 'pricing':
                        price_data = self.parser.parse_pricing_message(data.get('message', ''))
                        yield price_data
                        
                except Exception as e:
                    logger.error(f"Error parsing message: {e}")
                    continue
                    
        except websockets.exceptions.ConnectionClosed:
            logger.warning("WebSocket connection closed")
            if self.reconnect:
                logger.info(f"Reconnecting in {self.reconnect_delay} seconds...")
                await asyncio.sleep(self.reconnect_delay)
                await self.connect()
                # Continue streaming after reconnection
                async for data in self.stream():
                    yield data
                    
    async def _send_subscription(self, symbols: List[str]) -> None:
        """Send subscription message."""
        subscription_msg = {"subscribe": symbols}
        
        try:
            await self.websocket.send(json.dumps(subscription_msg))
            logger.info(f"Subscribed to: {symbols}")
        except Exception as e:
            logger.error(f"Failed to send subscription: {e}")
            raise SubscriptionError(f"Failed to subscribe to {symbols}")


# Convenience functions
def create_client(**kwargs) -> Client:
    """Create a synchronous client with default settings."""
    return Client(**kwargs)


def create_async_client(**kwargs) -> AsyncClient:
    """Create an asynchronous client with default settings."""
    return AsyncClient(**kwargs)