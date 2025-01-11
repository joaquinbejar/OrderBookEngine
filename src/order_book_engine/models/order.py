from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


class OrderType(Enum):
    """
    Represents different types of order classifications used in trading or financial
    platforms. These types define how the order is handled when submitted to the
    system.

    This class is an enumeration that can be used to specify whether an order is
    processed as a 'LIMIT' order or a 'MARKET' order, defining its execution
    criteria.

    :ivar LIMIT: Indicates that the order should be executed at a specific
        price or better.
    :type LIMIT: str
    :ivar MARKET: Indicates that the order should be executed immediately at
        the current market price.
    :type MARKET: str
    """
    LIMIT = "LIMIT"
    MARKET = "MARKET"


class OrderSide(Enum):
    """
    Represents the sides of an order in trading.

    This enumeration contains the possible sides of an order, which are typically used
    in trading systems to specify whether an order is for buying or selling an asset.
    """
    BUY = "BUY"
    SELL = "SELL"


class Position(Enum):
    """
    Defines an enumeration for Position with specified constants.

    The `Position` enumeration is used to represent specific states or modes
    for a given context. It contains two constants: `LONG` and `SHORT`, which
    can be utilized in various applications where such classification is
    required.
    """
    LONG = "LONG"
    SHORT = "SHORT"


@dataclass
class Order:
    """
    Represents an order in a financial trading system.

    The Order class is designed to encapsulate all details of a specific
    order, including its type, side (buy/sell), linked position, and more.
    This class supports limit orders by requiring a price for such orders
    upon initialization.

    :ivar id: Unique identifier for the order.
    :type id: str
    :ivar type: Type of the order (e.g., LIMIT, MARKET).
    :type type: OrderType
    :ivar side: Side of the order (e.g., BUY, SELL).
    :type side: OrderSide
    :ivar position: Associated position of the order.
    :type position: Position
    :ivar quantity: Quantity of the order.
    :type quantity: int
    :ivar timestamp: Timestamp indicating when the order was created.
    :type timestamp: datetime
    :ivar price: Price for the order if it is a limit order. This is optional
        and only required for limit orders.
    :type price: Optional[float]
    """
    id: str
    symbol: str
    type: OrderType
    side: OrderSide
    position: Position
    quantity: int
    timestamp: datetime

    price: Optional[float] = None


    def __post_init__(self):
        if self.type == OrderType.LIMIT and self.price is None:
            raise ValueError("Limit orders must have a price")

