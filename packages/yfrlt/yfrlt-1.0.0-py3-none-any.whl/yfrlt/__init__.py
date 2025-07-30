"""
yfrlt - Yahoo Finance Real-Time WebSocket Library

A modern Python library for streaming real-time financial data from Yahoo Finance WebSocket API v2.

Author: Community Project
License: MIT
Version: 1.0.0
"""

from .client import Client, AsyncClient
from .exceptions import YFRLTError, ConnectionError, AuthenticationError, SubscriptionError
from .models import PriceData, MarketData

__version__ = "1.0.0"
__author__ = "YFRLT Community"
__email__ = "support@yfrlt.dev"
__description__ = "Yahoo Finance Real-Time WebSocket Library"

__all__ = [
    "Client",
    "AsyncClient", 
    "PriceData",
    "MarketData",
    "YFRLTError",
    "ConnectionError",
    "AuthenticationError", 
    "SubscriptionError"
]

# Quick start example for documentation
EXAMPLE_USAGE = '''
# Simple Usage
import yfrlt

def on_price_update(data):
    print(f"{data.symbol}: ${data.price}")

client = yfrlt.Client()
client.subscribe(['BTC-USD', 'AAPL'], on_price_update)
client.start()

# Async Usage
import asyncio
import yfrlt

async def main():
    async with yfrlt.AsyncClient() as client:
        await client.subscribe(['BTC-USD'])
        async for data in client.stream():
            print(f"{data.symbol}: ${data.price}")

asyncio.run(main())
'''