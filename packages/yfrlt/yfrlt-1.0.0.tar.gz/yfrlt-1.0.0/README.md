# YFRLT - Yahoo Finance Real-Time ✨

**Get real-time stock, crypto, and market data from Yahoo Finance WebSocket v2**

Simple Python library for streaming live financial data. Works with the latest Yahoo Finance WebSocket API.


## 🚀 Quick Start

### Install

```bash
pip install yfrlt
```

### Basic Usage

```python
import yfrlt

def on_price_update(data):
    print(f"{data.symbol}: ${data.price:.4f} ({data.change_percent:+.2f}%)")

client = yfrlt.Client()
client.subscribe(['AAPL', 'BTC-USD'], on_price_update)
client.start()  # Runs forever, press Ctrl+C to stop
```

## 📊 What Data You Get

Every price update includes:

```python
data.symbol           # "AAPL", "BTC-USD", etc.
data.price            # Current price: 150.2567 (full precision)
data.change           # Price change: -1.5023
data.change_percent   # Percentage change: -0.99
data.day_volume       # Trading volume: 1234567
data.day_high         # Day's high price: 152.0045
data.day_low          # Day's low price: 149.5012
data.market_hours     # True if market is open
data.currency         # "USD", "EUR", etc.
data.exchange         # "NASDAQ", "NYSE", etc.
data.timestamp        # When the data was received
```

## 🔗 Supported Symbols

**We support almost all symbols available on Yahoo Finance** - stocks (AAPL, GOOGL, TSLA), crypto (BTC-USD, ETH-USD), indices (^GSPC, ^DJI), forex (EURUSD=X, GBPUSD=X), and commodities (GC=F, CL=F). **Find any symbol**: Search on [Yahoo Finance](https://finance.yahoo.com) and use the symbol from the URL.

## 💻 Google Colab Usage

Perfect for testing without installing anything locally:

```python
# Install in Colab
!pip install yfrlt

import yfrlt
from datetime import datetime

# Simple price monitor
def show_price(data):
    time = datetime.now().strftime("%H:%M:%S")
    print(f"[{time}] {data.symbol}: ${data.price:.4f} ({data.change_percent:+.2f}%)")

# Create client and subscribe
client = yfrlt.Client()
client.subscribe(['BTC-USD', 'AAPL', 'TSLA'], show_price)

# Run for 30 seconds (good for Colab)
import threading
import time

thread = threading.Thread(target=client.start, daemon=True)
thread.start()
time.sleep(30)  # Run for 30 seconds
client.stop()
print("✅ Done!")
```

## 🔄 Async Usage (Multiple Symbols)

For modern async/await code:

```python
import asyncio
import yfrlt

async def get_multiple_prices():
    async with yfrlt.AsyncClient() as client:
        # Subscribe to multiple symbols
        symbols = ['AAPL', 'GOOGL', 'MSFT', 'BTC-USD', 'ETH-USD']
        await client.subscribe(symbols)

        # Get live updates
        async for data in client.stream():
            print(f"{data.symbol}: ${data.price:.4f} | "
                  f"Change: {data.change_percent:+.2f}% | "
                  f"Volume: {data.day_volume:,}")

# Run the async function
asyncio.run(get_multiple_prices())
```

## 📈 Real Examples

### Portfolio Tracker

```python
import yfrlt

portfolio = {
    'AAPL': 10,    # 10 shares of Apple
    'BTC-USD': 0.1, # 0.1 Bitcoin
    'GOOGL': 5     # 5 shares of Google
}

def track_portfolio(data):
    if data.symbol in portfolio:
        shares = portfolio[data.symbol]
        value = shares * data.price
        print(f"{data.symbol}: {shares} shares = ${value:,.4f} "
              f"({data.change_percent:+.2f}%)")

client = yfrlt.Client()
client.subscribe(list(portfolio.keys()), track_portfolio)
client.start()
```

### Crypto Monitor

```python
import yfrlt

crypto_symbols = ['BTC-USD', 'ETH-USD', 'DOGE-USD', 'ADA-USD']

def crypto_tracker(data):
    # Only show crypto updates
    if 'USD' in data.symbol:
        print(f"💰 {data.symbol}: ${data.price:,.4f} ({data.change_percent:+.2f}%)")

client = yfrlt.Client()
client.subscribe(crypto_symbols, crypto_tracker)
client.start()
```

### Market Overview

```python
import yfrlt

# Major indices and big tech
symbols = ['^GSPC', '^DJI', '^IXIC', 'AAPL', 'GOOGL', 'MSFT', 'TSLA']

def market_overview(data):
    if data.symbol.startswith('^'):
        print(f"📊 INDEX {data.symbol}: {data.price:.4f} ({data.change_percent:+.2f}%)")
    else:
        print(f"🏢 STOCK {data.symbol}: ${data.price:.4f} ({data.change_percent:+.2f}%)")

client = yfrlt.Client()
client.subscribe(symbols, market_overview)
client.start()
```

## 🛠️ Local Development

```bash
# Clone repository
git clone https://github.com/yourusername/yfrlt.git
cd yfrlt

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .

# Test it works
python -c "import yfrlt; print('✅ YFRLT installed!')"
```

## ⚡ Quick Test

```python
import yfrlt
import time
import threading

def quick_test():
    def show_data(data):
        print(f"✅ {data.symbol}: ${data.price:.4f}")

    client = yfrlt.Client()
    client.subscribe(['BTC-USD'], show_data)  # Bitcoin trades 24/7

    # Run for 10 seconds
    thread = threading.Thread(target=client.start, daemon=True)
    thread.start()
    time.sleep(10)
    client.stop()
    print("Test complete!")

quick_test()
```

## ❓ FAQ

**Q: Is this free?**  
A: Yes! Uses Yahoo Finance's public WebSocket API.

**Q: What's the update frequency?**  
A: Usually 1-5 updates per second per symbol during market hours.

**Q: Does it work outside market hours?**  
A: Crypto symbols work 24/7. Stocks only update during market hours.

**Q: Can I get historical data?**  
A: No, this is only for real-time data.

## 📜 License

MIT License - use it however you want!

## 🤝 Contributing

Found a bug? Want a feature? Open an issue on GitHub!

---

**⭐ Star this repo if it helps you!**
