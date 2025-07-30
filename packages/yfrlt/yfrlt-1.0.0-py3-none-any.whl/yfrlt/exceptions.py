"""
Custom exceptions for YFRLT library.

Defines specific error types that can occur when using the Yahoo Finance WebSocket API.
"""


class YFRLTError(Exception):
    """Base exception for all YFRLT errors."""
    
    def __init__(self, message: str, details: str = None):
        """
        Initialize YFRLT error.
        
        Args:
            message: Human-readable error message
            details: Additional technical details (optional)
        """
        super().__init__(message)
        self.message = message
        self.details = details
        
    def __str__(self) -> str:
        """String representation of the error."""
        if self.details:
            return f"{self.message} (Details: {self.details})"
        return self.message


class ConnectionError(YFRLTError):
    """Raised when WebSocket connection fails."""
    
    def __init__(self, message: str = "Failed to connect to Yahoo Finance WebSocket", details: str = None):
        super().__init__(message, details)


class AuthenticationError(YFRLTError):
    """Raised when authentication fails (if Yahoo adds auth in future)."""
    
    def __init__(self, message: str = "Authentication failed", details: str = None):
        super().__init__(message, details)


class SubscriptionError(YFRLTError):
    """Raised when symbol subscription fails."""
    
    def __init__(self, message: str = "Failed to subscribe to symbols", details: str = None):
        super().__init__(message, details)


class ParsingError(YFRLTError):
    """Raised when message parsing fails."""
    
    def __init__(self, message: str = "Failed to parse WebSocket message", details: str = None):
        super().__init__(message, details)


class TimeoutError(YFRLTError):
    """Raised when operations timeout."""
    
    def __init__(self, message: str = "Operation timed out", details: str = None):
        super().__init__(message, details)


class RateLimitError(YFRLTError):
    """Raised when Yahoo Finance rate limits are hit."""
    
    def __init__(self, message: str = "Rate limit exceeded", details: str = None):
        super().__init__(message, details)


class InvalidSymbolError(YFRLTError):
    """Raised when an invalid symbol is used."""
    
    def __init__(self, symbol: str, message: str = None):
        if not message:
            message = f"Invalid symbol: {symbol}"
        super().__init__(message)
        self.symbol = symbol