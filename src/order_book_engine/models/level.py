from collections import deque
from copy import deepcopy
from typing import Tuple, List, Optional

from ..models.order import Order, Position, OrderSide


class PriceLevel:
    def __init__(self, price: float):

        self.long_total = 0
        self.short_total = 0
        self.price = price
        # Separate queues for LONG and SHORT positions
        self.long_orders = deque() # FIFO queue
        self.short_orders = deque() # FIFO queue

    def add_order(self, order: Order) -> None:
        """
        Adds an order to the respective list based on the order's position.

        This method processes an incoming order and appends it to either the
        list of long positions or short positions, depending on the position
        type of the provided `order`. Additionally, it updates the total
        quantity held for long or short positions.

        :param order: The order to be added. Should be an instance of Order
            containing the necessary information, such as position type
            (LONG or SHORT) and quantity.
        :type order: Order

        :return: None, the method modifies the long or short orders list
            and updates the respective total quantity.
        :rtype: None
        """
        if order.position == Position.LONG:
            self.long_orders.append(order)
            self.long_total += order.quantity
        else:
            self.short_orders.append(order)
            self.short_total += order.quantity

    def can_match(self, order: Order) -> bool:
        """
        Determines if the given order can be matched based on its position and side by
        validating it against predefined valid match combinations. This method uses the
        order's side and position to lookup potential matching orders in the respective
        queue and checks their validity.

        :param order: The order to evaluate for potential matching.
        :type order: Order

        :return: True if a matching order exists in the respective queue, False otherwise.
        :rtype: bool
        """
        # Valid matching combinations
        valid_matches = {
            (OrderSide.BUY, Position.LONG): (OrderSide.SELL, Position.SHORT),
            (OrderSide.SELL, Position.LONG): (OrderSide.BUY, Position.SHORT),
            (OrderSide.BUY, Position.SHORT): (OrderSide.SELL, Position.LONG),
            (OrderSide.SELL, Position.SHORT): (OrderSide.BUY, Position.LONG)
        }

        target = valid_matches.get((order.side, order.position))
        queue = self.long_orders if target[1] == Position.LONG else self.short_orders

        return len(queue) > 0 and next(iter(queue)).side == target[0]

    def get_qty(self, requested_quantity: int, position: Position) -> Tuple[List[Order], Optional[Order], int]:
        """
        Retrieves filled orders, a partially filled order if applicable, and the remaining quantity
        from the queue based on the requested quantity and the specified position. The function
        processes orders in a queue until the requested quantity is satisfied or the queue is emptied.
        The provided position determines whether to operate on the long or short order queue.

        :param requested_quantity: The quantity to fulfill orders from the order queue.
        :type requested_quantity: int
        :param position: The position type (LONG or SHORT) indicating the order queue to process.
        :type position: Position
        :return: A tuple containing a list of completely filled orders, an optional partially filled
                 order, and the remaining quantity after processing.
        :rtype: Tuple[List[Order], Optional[Order], int]
        """
        queue = self.long_orders if position == Position.LONG else self.short_orders
        filled_orders = []
        remaining_qty = requested_quantity
        partial_order = None
        total = self.long_total if position == Position.LONG else self.short_total

        while remaining_qty > 0 and queue:
            current_order = queue[0]

            if current_order.quantity <= remaining_qty:
                filled_orders.append(queue.popleft())
                remaining_qty -= current_order.quantity
                total -= current_order.quantity
            else:
                partial_order = deepcopy(current_order)
                partial_order.quantity = remaining_qty
                queue[0].quantity -= remaining_qty
                total -= remaining_qty
                remaining_qty = 0

        if position == Position.LONG:
            self.long_total = total
        else:
            self.short_total = total

        return filled_orders, partial_order, remaining_qty