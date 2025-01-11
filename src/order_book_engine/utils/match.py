from ..models.order import OrderSide, Position, Order


def is_valid_match(order1: Order, order2: Order) -> bool:
    """
    Determines if two orders are a valid match based on their side and position.
    A valid match occurs when the combination of side and position from `order1`
    is a corresponding inverse of the combination from `order2` as defined by
    the `valid_matches` mapping.

    :param order1: The first order to compare.
    :type order1: Order
    :param order2: The second order to compare.
    :type order2: Order
    :return: True if the orders form a valid match, False otherwise.
    :rtype: bool
    """
    valid_matches = {
        (OrderSide.BUY, Position.LONG): (OrderSide.SELL, Position.SHORT),
        (OrderSide.SELL, Position.LONG): (OrderSide.BUY, Position.SHORT),
        (OrderSide.BUY, Position.SHORT): (OrderSide.SELL, Position.LONG),
        (OrderSide.SELL, Position.SHORT): (OrderSide.BUY, Position.LONG)
    }
    return valid_matches.get((order1.side, order1.position)) == (order2.side, order2.position)