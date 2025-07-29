"""Common enums used across multiple models in the Nomy data processing system."""

import enum
from enum import Enum


class MarketType(str, enum.Enum):
    """Enum for different market types."""

    SPOT = "spot"
    PERPETUAL = "perp"


class PositionDirection(str, Enum):
    """Enum for position direction."""

    BUY = "buy"
    SELL = "sell"


class TradeDirection(str, Enum):
    """Enum for trade direction."""

    OPEN_LONG = "open_long"
    OPEN_SHORT = "open_short"
    CLOSE_LONG = "close_long"
    CLOSE_SHORT = "close_short"
    LONG_TO_SHORT = "long_to_short"
    SHORT_TO_LONG = "short_to_long"


class PositionStatus(str, Enum):
    """Enum for position status."""

    OPEN = "open"
    CLOSED = "closed"
    LIQUIDATED = "liquidated"


class PositionTradeType(str, Enum):
    """Enum for position trade type relative to a position."""

    OPENING = "opening"
    CLOSING = "closing"


class DataState(str, enum.Enum):
    """Enum for data quality states."""

    EMPTY = "empty"
    PARTIAL = "partial"
    COMPLETE = "complete"
    ERROR = "error"


class SyncState(str, enum.Enum):
    """Enum for synchronization states."""

    SYNCED = "synced"
    SYNCED_MISSING_OPEN = "synced_missing_open"
    SYNCED_MISSING_CLOSE = "synced_missing_close"
    SYNCED_MISSING_OPEN_CLOSE = "synced_missing_open_close"
    SYNCING = "syncing"
    PENDING = "pending"
    FAILED = "failed"


class ProcessingState(str, enum.Enum):
    """Enum for service processing states."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
