"""
Data models for Yahoo Finance real-time data.

Defines the structure of financial data received from Yahoo Finance WebSocket.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional


@dataclass
class PriceData:
    """
    Real-time price data from Yahoo Finance.
    
    Contains all the financial information for a single symbol at a point in time.
    """
    
    # Core price information
    symbol: str                    # Symbol (e.g., "BTC-USD", "AAPL")
    price: float                   # Current price
    timestamp: datetime            # Time of the data
    
    # Market information  
    currency: str                  # Currency (e.g., "USD")
    exchange: str                  # Exchange code (e.g., "NASDAQ", "CCC")
    quote_type: int               # Yahoo's internal quote type
    market_hours: bool            # True if market is open
    
    # Price changes
    change: float                 # Price change from previous close
    change_percent: float         # Percentage change
    
    # Daily statistics
    day_volume: int              # Trading volume for the day
    day_high: float              # Highest price of the day
    day_low: float               # Lowest price of the day
    
    # Additional information
    short_name: str              # Short name of the security
    price_hint: int              # Number of decimal places for display
    
    # Raw data for advanced users
    raw_fields: Dict[str, Any]   # All raw protobuf fields
    
    def __str__(self) -> str:
        """String representation of price data."""
        return f"{self.symbol}: ${self.price:.4f} ({self.change_percent:+.2f}%)"
        
    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return (f"PriceData(symbol='{self.symbol}', price={self.price}, "
                f"change={self.change}, timestamp='{self.timestamp}')")
                
    @property
    def is_market_open(self) -> bool:
        """Check if the market is currently open."""
        return self.market_hours
        
    @property
    def is_crypto(self) -> bool:
        """Check if this is a cryptocurrency."""
        return 'USD' in self.symbol and ('BTC' in self.symbol or 'ETH' in self.symbol or 
                                         'DOGE' in self.symbol or self.symbol.endswith('=X'))
        
    @property
    def is_stock(self) -> bool:
        """Check if this is a stock."""
        return not self.is_crypto and not self.is_index and not self.is_forex
        
    @property 
    def is_index(self) -> bool:
        """Check if this is a market index."""
        return self.symbol.startswith('^')
        
    @property
    def is_forex(self) -> bool:
        """Check if this is a forex pair."""
        return self.symbol.endswith('=X') and not self.is_crypto
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'symbol': self.symbol,
            'price': self.price,
            'timestamp': self.timestamp.isoformat(),
            'currency': self.currency,
            'exchange': self.exchange,
            'quote_type': self.quote_type,
            'market_hours': self.market_hours,
            'change': self.change,
            'change_percent': self.change_percent,
            'day_volume': self.day_volume,
            'day_high': self.day_high,
            'day_low': self.day_low,
            'short_name': self.short_name,
            'price_hint': self.price_hint
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PriceData':
        """Create PriceData from dictionary."""
        # Convert timestamp string back to datetime
        if isinstance(data.get('timestamp'), str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
            
        return cls(
            symbol=data['symbol'],
            price=data['price'],
            timestamp=data['timestamp'],
            currency=data.get('currency', 'USD'),
            exchange=data.get('exchange', 'UNKNOWN'),
            quote_type=data.get('quote_type', 0),
            market_hours=data.get('market_hours', True),
            change=data.get('change', 0.0),
            change_percent=data.get('change_percent', 0.0),
            day_volume=data.get('day_volume', 0),
            day_high=data.get('day_high', 0.0),
            day_low=data.get('day_low', 0.0),
            short_name=data.get('short_name', ''),
            price_hint=data.get('price_hint', 2),
            raw_fields=data.get('raw_fields', {})
        )


@dataclass
class MarketData:
    """
    Container for multiple symbols' market data.
    
    Useful for tracking a portfolio or watchlist.
    """
    
    symbols: Dict[str, PriceData]  # Symbol -> PriceData mapping
    last_updated: datetime
    
    def __init__(self):
        """Initialize empty market data container."""
        self.symbols = {}
        self.last_updated = datetime.now()
        
    def update(self, price_data: PriceData) -> None:
        """Update data for a symbol."""
        self.symbols[price_data.symbol] = price_data
        self.last_updated = datetime.now()
        
    def get(self, symbol: str) -> Optional[PriceData]:
        """Get price data for a specific symbol."""
        return self.symbols.get(symbol)
        
    def get_price(self, symbol: str) -> Optional[float]:
        """Get current price for a symbol."""
        data = self.get(symbol)
        return data.price if data else None
        
    def get_all_symbols(self) -> list[str]:
        """Get list of all tracked symbols."""
        return list(self.symbols.keys())
        
    def get_gainers(self, limit: int = 10) -> list[PriceData]:
        """Get top gaining symbols."""
        return sorted(
            self.symbols.values(), 
            key=lambda x: x.change_percent, 
            reverse=True
        )[:limit]
        
    def get_losers(self, limit: int = 10) -> list[PriceData]:
        """Get top losing symbols."""
        return sorted(
            self.symbols.values(),
            key=lambda x: x.change_percent
        )[:limit]
        
    def get_most_active(self, limit: int = 10) -> list[PriceData]:
        """Get most actively traded symbols by volume."""
        return sorted(
            self.symbols.values(),
            key=lambda x: x.day_volume,
            reverse=True
        )[:limit]
        
    def __len__(self) -> int:
        """Number of symbols being tracked."""
        return len(self.symbols)
        
    def __contains__(self, symbol: str) -> bool:
        """Check if symbol is being tracked."""
        return symbol in self.symbols
        
    def __iter__(self):
        """Iterate over all price data."""
        return iter(self.symbols.values())
        
    def __str__(self) -> str:
        """String representation showing summary."""
        count = len(self.symbols)
        return f"MarketData({count} symbols, updated: {self.last_updated})"