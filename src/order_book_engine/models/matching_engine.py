from abc import ABC, abstractmethod
from typing import List, Tuple, Optional, OrderedDict

from .level import PriceLevel
from .order import Order, OrderSide, Position


class MatchingEngine(ABC):
    """
    Abstract base class for implementing a matching engine in a trading system.

    A Matching Engine is responsible for matching buy and sell orders based on their
    prices and other attributes, such as position and side. Concrete implementations
    must provide methods for fetching the best ask and bid prices, as well as the logic
    for fulfilling market and limit orders. The class includes abstract methods that
    must be implemented by subclasses and helper methods for handling various order types.

    :ivar symbol: The trading symbol (e.g., "AAPL", "BTCUSD") the matching
        engine is managing orders for.
    :type symbol: str
    """

    def __init__(self, symbol: str):
        self.symbol = symbol

    @abstractmethod
    def match(self, order: Order) -> List[Tuple[Order, Order]]:
        """
        Matches new orders with existing ones based on predefined rules.

        This abstract method is responsible for defining the logic to match
        incoming orders with orders already present in a system. The matching
        process ensures that the pairing of orders adheres to the system's
        rules to fulfill the requirements of a transactional exchange.

        :param order: The new order object to be matched against existing orders.
        :type order: Order
        :return: A list of tuples where each tuple represents a matched pair of
            orders.
        :rtype: List[Tuple[Order, Order]]
        """
        pass

    @abstractmethod
    def get_best_ask(self) -> Optional[Tuple[float, PriceLevel]]:
        """
        Retrieve the best ask (lowest price) and its associated price level from the market
        data.

        This method is abstract and must be implemented in a subclass. It is used to fetch
        the best available ask price, which helps in analyzing and determining market trends
        or executing trading strategies.

        :raises NotImplementedError: When the method is not implemented in a subclass.
        :return: A tuple containing the ask price as a float and the associated price level.
            If no ask price is available, returns None.
        :rtype: Optional[Tuple[float, PriceLevel]]
        """
        pass

    @abstractmethod
    def get_best_bid(self) -> Optional[Tuple[float, PriceLevel]]:
        """
        Provides an abstract method to retrieve the best bid including its associated price
        level from a given data structure or source. This method is intended to be implemented
        by subclasses, ensuring that they define the specific behavior for extracting the best
        bid details.

        :return: A tuple containing the best bid's price as a float and its associated
            PriceLevel object, or None if no valid bid is available.
        :rtype: Optional[Tuple[float, PriceLevel]]
        """
        pass

    def _match_market_order(self, order: Order) -> Tuple[List[Order], List[Order]]:
        """
        Matches a given market order with existing orders in the order book. Depending on
        the type of the input order, delegates handling and processing to the respective
        handler responsible for either buy or sell orders. The function determines whether
        the order is to open or close long/short positions and processes accordingly.

        :param order: The market order to be matched against the order book.
        :type order: Order

        :return: A tuple containing two lists:
            - The first list consists of fully filled orders.
            - The second list consists of partially filled orders.
        :rtype: Tuple[List[Order], List[Order]]
        """
        filled_orders = []
        partially_filled_orders = []

        # Check the order type and delegate to the respective handler
        is_buy_long = order.side == OrderSide.BUY and order.position == Position.LONG
        is_buy_short = order.side == OrderSide.BUY and order.position == Position.SHORT
        is_sell_short = order.side == OrderSide.SELL and order.position == Position.SHORT
        is_sell_long = order.side == OrderSide.SELL and order.position == Position.LONG

        if is_buy_long or is_buy_short:
            filled_orders, partially_filled_orders = self._handle_buy_order(filled_orders, partially_filled_orders,
                                                                            order)
        elif is_sell_short or is_sell_long:
            filled_orders, partially_filled_orders = self._handle_sell_order(filled_orders, partially_filled_orders,
                                                                             order)

        return filled_orders, partially_filled_orders

    def _handle_buy_order(self, filled_orders: List[Order], partially_filled_orders: List[Order], order: Order) -> \
            Tuple[
                List[Order], List[Order]]:
        """
        Handles a buy order by attempting to match it with the best available ask in the market.

        This function processes a buy order by first checking the best ask price from the order book.
        If a potential match exists, it attempts to fill the order. Any fully filled orders,
        partially filled orders, or remaining quantities are updated accordingly. If there's
        unfulfilled quantity left in the buy order after matching with the best ask, subsequent
        matching with the market is attempted.

        Parameters:
        :param filled_orders: List of orders that have been completely filled during the processing
                              of the buy order.
        :param partially_filled_orders: List of orders that have been partially filled during the
                                         processing of the buy order.
        :param order: The buy order being handled, which may be fully or partially filled, or
                      may have remaining quantity left to process.

        Returns:
        :return: A tuple containing updated lists of filled orders and partially filled orders,
                 respectively.
        """
        best_ask = self.get_best_ask()
        if best_ask:
            filled, partially_filled, remaining_qty = best_ask[1].get_qty(order.quantity, Position.SHORT)
            filled_orders.extend(filled)
            if partially_filled:
                partially_filled_orders.append(partially_filled)
            if remaining_qty > 0:
                order.quantity = remaining_qty
                more_filled, more_partial = self._match_market_order(order)
                filled_orders.extend(more_filled)
                partially_filled_orders.extend(more_partial)
        return filled_orders, partially_filled_orders

    def _handle_sell_order(self, filled_orders: List[Order], partially_filled_orders: List[Order], order: Order) -> \
            Tuple[
                List[Order], List[Order]]:
        """
        Handles a sell order by matching it with the best bid available in the market. It processes filled,
        partially filled, and remaining quantities of the order and updates the provided lists of filled
        and partially filled orders accordingly.

        :param filled_orders:
            A list of orders that have been completely filled. This list will be updated with orders
            that are completely filled during the execution of this function.
        :param partially_filled_orders:
            A list of orders that have been partially filled. This list will be updated with orders that
            are partially filled during the execution of this function.
        :param order:
            The sell order to be matched with the best bid. Its `quantity` attribute may be updated if
            there is remaining quantity after matching with bids.
        :return:
            A tuple containing two lists:
            - The first list contains all the completely filled orders, including the ones updated during
              this function call.
            - The second list contains all partially filled orders, including the ones updated during this
              function call.
        """
        best_bid = self.get_best_bid()
        if best_bid:
            filled, partially_filled, remaining_qty = best_bid[1].get_qty(order.quantity, Position.LONG)
            filled_orders.extend(filled)
            if partially_filled:
                partially_filled_orders.append(partially_filled)
            if remaining_qty > 0:
                order.quantity = remaining_qty
                more_filled, more_partial = self._match_market_order(order)
                filled_orders.extend(more_filled)
                partially_filled_orders.extend(more_partial)
        return filled_orders, partially_filled_orders

    def _match_limit_order(self, order: Order, asks: OrderedDict, bids: OrderedDict) -> Tuple[Order, List[Order], int]:
        matched_orders = []

        if order.side == OrderSide.BUY:
            while asks and min(asks.keys()) <= order.price:
                best_ask = self.get_best_ask()
                if not best_ask:  # Check if the best ask exists
                    break
                filled, partial, remain = best_ask[1].get_qty(
                    order.quantity,
                    Position.SHORT if order.position == Position.LONG else Position.LONG
                )
                matched_orders.extend(filled)
                if partial:
                    matched_orders.append(partial)
                if remain == 0:
                    break
                order.quantity = remain
        else:  # SELL
            while bids and max(bids.keys()) >= order.price:
                best_bid = self.get_best_bid()
                if not best_bid:  # Check if the best bid exists
                    break
                filled, partial, remain = best_bid[1].get_qty(
                    order.quantity,
                    Position.LONG if order.position == Position.SHORT else Position.SHORT
                )
                matched_orders.extend(filled)
                if partial:
                    matched_orders.append(partial)
                if remain == 0:
                    break
                order.quantity = remain

        return order, matched_orders, order.quantity
