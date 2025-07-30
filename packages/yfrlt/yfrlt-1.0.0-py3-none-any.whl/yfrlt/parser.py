"""
Message parser for Yahoo Finance WebSocket data.

Handles parsing of protobuf messages from Yahoo Finance v2 API.
"""

import base64
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from .models import PriceData
from .exceptions import YFRLTError

logger = logging.getLogger(__name__)


class MessageParser:
    """Parser for Yahoo Finance protobuf messages."""
    
    def __init__(self):
        """Initialize the message parser."""
        pass
        
    def parse_pricing_message(self, base64_message: str) -> PriceData:
        """
        Parse a base64-encoded protobuf pricing message.
        
        Args:
            base64_message: Base64 encoded protobuf data
            
        Returns:
            PriceData object with parsed information
        """
        try:
            # Decode base64 to binary
            binary_data = base64.b64decode(base64_message)
            
            # Parse protobuf manually (since we don't have the exact .proto file)
            parsed_data = self._parse_protobuf_binary(binary_data)
            
            # Convert to PriceData object
            return self._create_price_data(parsed_data)
            
        except Exception as e:
            logger.error(f"Failed to parse pricing message: {e}")
            raise YFRLTError(f"Message parsing failed: {e}")
            
    def _parse_protobuf_binary(self, binary_data: bytes) -> Dict[str, Any]:
        """
        Parse protobuf binary data manually.
        
        Based on known Yahoo Finance protobuf schema.
        """
        fields = {}
        offset = 0
        
        while offset < len(binary_data):
            try:
                # Read field tag (field number + wire type)
                tag, offset = self._read_varint(binary_data, offset)
                field_number = tag >> 3
                wire_type = tag & 0x7
                
                # Parse field based on wire type
                if wire_type == 0:  # Varint
                    value, offset = self._read_varint(binary_data, offset)
                    fields[field_number] = value
                    
                elif wire_type == 1:  # 64-bit
                    if offset + 8 <= len(binary_data):
                        value = self._read_fixed64(binary_data, offset)
                        offset += 8
                        fields[field_number] = value
                    else:
                        break
                        
                elif wire_type == 2:  # Length-delimited (string/bytes)
                    length, offset = self._read_varint(binary_data, offset)
                    if offset + length <= len(binary_data):
                        value = binary_data[offset:offset + length]
                        # Try to decode as string
                        try:
                            fields[field_number] = value.decode('utf-8')
                        except UnicodeDecodeError:
                            fields[field_number] = value
                        offset += length
                    else:
                        break
                        
                elif wire_type == 5:  # 32-bit
                    if offset + 4 <= len(binary_data):
                        value = self._read_fixed32(binary_data, offset)
                        offset += 4
                        fields[field_number] = value
                    else:
                        break
                        
                else:
                    # Unknown wire type, skip
                    logger.warning(f"Unknown wire type: {wire_type}")
                    break
                    
            except Exception as e:
                logger.error(f"Error parsing field at offset {offset}: {e}")
                break
                
        return fields
        
    def _read_varint(self, data: bytes, offset: int) -> tuple[int, int]:
        """Read a protobuf varint from binary data."""
        result = 0
        shift = 0
        
        while offset < len(data):
            byte = data[offset]
            offset += 1
            
            result |= (byte & 0x7F) << shift
            if (byte & 0x80) == 0:
                break
            shift += 7
            
        return result, offset
        
    def _read_fixed32(self, data: bytes, offset: int) -> float:
        """Read a 32-bit float from binary data."""
        import struct
        return struct.unpack('<f', data[offset:offset + 4])[0]
        
    def _read_fixed64(self, data: bytes, offset: int) -> float:
        """Read a 64-bit double from binary data."""
        import struct
        return struct.unpack('<d', data[offset:offset + 8])[0]
        
    def _create_price_data(self, fields: Dict[str, Any]) -> PriceData:
        """
        Create PriceData object from parsed protobuf fields.
        
        Field mapping based on reverse-engineered Yahoo Finance schema:
        1: id (symbol)
        2: price  
        3: time
        4: currency
        5: exchange
        6: quote_type
        7: market_hours
        8: change_percent
        9: day_volume
        10: day_high
        11: day_low
        12: change
        13: short_name
        27: price_hint
        """
        
        # Extract known fields with defaults
        symbol = fields.get(1, 'UNKNOWN')
        price = fields.get(2, 0.0)
        timestamp = fields.get(3, 0)
        currency = fields.get(4, 'USD')
        exchange = fields.get(5, 'UNKNOWN')
        quote_type = fields.get(6, 0)
        market_hours = fields.get(7, 1)
        change_percent = fields.get(8, 0.0)
        day_volume = fields.get(9, 0)
        day_high = fields.get(10, 0.0)
        day_low = fields.get(11, 0.0)
        change = fields.get(12, 0.0)
        short_name = fields.get(13, '')
        price_hint = fields.get(27, 2)
        
        # Convert timestamp (Yahoo uses milliseconds)
        if timestamp > 0:
            dt = datetime.fromtimestamp(timestamp / 1000.0)
        else:
            dt = datetime.now()
            
        return PriceData(
            symbol=symbol,
            price=float(price),
            timestamp=dt,
            currency=currency,
            exchange=exchange,
            quote_type=int(quote_type),
            market_hours=bool(market_hours),
            change_percent=float(change_percent),
            day_volume=int(day_volume),
            day_high=float(day_high),
            day_low=float(day_low),
            change=float(change),
            short_name=short_name,
            price_hint=int(price_hint),
            raw_fields=fields  # Keep raw data for debugging
        )