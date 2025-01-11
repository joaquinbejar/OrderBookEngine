from abc import ABC
from collections import OrderedDict
from typing import Tuple, Optional, List

from .level import PriceLevel
from .matching_engine import MatchingEngine
from .order import Order, OrderType, OrderSide


class OrderBook(MatchingEngine, ABC):
    """
    Handles an Order Book for a specific traded symbol, maintaining
    and updating the state of buy and sell orders.

    The class provides functionality for managing and matching orders, retrieving
    the best bid and ask prices, and calculating the bid-ask spread. It supports both
    market and limit orders, updating the order book as orders are matched or added.

    :ivar bids: A dictionary of current bid price levels keyed by price.
    :type bids: OrderedDict
    :ivar asks: A dictionary of current ask price levels keyed by price.
    :type asks: OrderedDict
    :ivar symbol: The trading symbol this order book is associated with.
    :type symbol: str
    """
    def __init__(self, symbol: str):
        super().__init__(symbol)
        self.bids = OrderedDict()
        self.asks = OrderedDict()

    def __str__(self) -> str:
        str_out = (f"symbol={self.symbol}, \n")

        for price, level in self.bids.items():
            str_out += f"\t{level}, \n"

        for price, level in self.asks.items():
            str_out += f"\t{level}, \n"

        return str_out

    def __repr__(self) -> str:
        return self.__str__()

    def match(self, order: Order) -> Tuple[Order, List[Order]]:
        """
        Matches the given order against existing orders depending on its type (MARKET or LIMIT).

        If the order type is MARKET, it attempts to match the order with existing limit orders
        and returns the matching results. If no orders are matched, an exception is raised. For
        LIMIT orders, it matches the order with available orders, processes the remaining
        quantity, and updates the order book accordingly.

        :param order: The order to be matched.
        :type order: Order
        :return: A tuple containing the matched order and a list of matched or partially filled
            orders.
        :rtype: Tuple[Order, List[Order]]
        :raises ValueError: If no orders are matched for a MARKET order.
        """
        if order.type == OrderType.MARKET:
            orders, partially_filled_orders =  self._match_market_order(order)
            orders.extend(partially_filled_orders)
            if len(orders) == 0:
                raise ValueError("No orders matched")
            return order, orders
        else:
            order, matched_orders, remain_qty = self._match_limit_order(order)
            if remain_qty > 0:
                if order.side == OrderSide.BUY:
                    self._add_bid(order)
                else:
                    self._add_ask(order)



    def _add_bid(self, order: Order):
        """
        Adds a bid order to the bid price level map. If the price level does not
        exist in the order book, it creates a new price level and adds the order
        to it. If the price level already exists, it adds the order to the
        existing price level.

        :param order: The order to be added to the bid price level map.
        :type order: Order

        :return: None
        """
        if order.price not in self.bids:
            self.bids[order.price] = PriceLevel(order.price, self.symbol)
        self.bids[order.price].add_order(order)

    def _add_ask(self, order: Order):
        """
        Adds an ask order to the internal order book. If the price level for the order does not exist,
        a new price level is created. Otherwise, the existing price level at the order's price is updated
        with the provided order.

        :param order: The ask order to be added to the order book
        :type order: Order
        """
        if order.price not in self.asks:
            self.asks[order.price] = PriceLevel(order.price, self.symbol)
        self.asks[order.price].add_order(order)

    def get_best_bid(self) -> Optional[Tuple[float, PriceLevel]]:
        """
        Retrieve the best bid from the bids dictionary. The method removes and returns the
        highest bid in the dictionary, if available. If the bids dictionary is empty, it
        returns None.

        :return: A tuple containing the price (float) and the price level (PriceLevel)
            of the best available bid, or None if no bids exist.
        :rtype: Optional[Tuple[float, PriceLevel]]
        """
        return self.bids.popitem(last=True) if self.bids else None

    def get_best_ask(self) -> Optional[Tuple[float, PriceLevel]]:
        """
        Retrieves and removes the lowest price level from the ordered dictionary of asks. If no asks
        are available, returns None.

        :return: A tuple containing the price and corresponding ``PriceLevel`` object if available,
                 otherwise ``None``.
        :rtype: Optional[Tuple[float, PriceLevel]]
        """
        return self.asks.popitem(last=False) if self.asks else None

    def get_spread(self) -> Optional[Tuple[float, float]]:
        """
        Calculate the spread between the best bid and the best ask prices.

        This function retrieves the highest bid price and the lowest ask price
        using the `get_best_bid` and `get_best_ask` methods, respectively. If
        either the bid or ask prices are unavailable, the function will return
        None. Otherwise, it returns the spread as a tuple containing the
        best ask price and best bid price.

        :return: A tuple containing the best ask and best bid prices, or None
            if either value is unavailable.
        :rtype: Optional[Tuple[float, float]]
        """
        best_bid = self.get_best_bid()
        best_ask = self.get_best_ask()
        if not best_bid or not best_ask:
            return None
        return best_ask[0], best_bid[0]
