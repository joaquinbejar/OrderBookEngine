import unittest
from datetime import datetime
from copy import deepcopy
from src.order_book_engine.models.order import Order, Position, OrderSide, OrderType
from src.order_book_engine.models.level import PriceLevel


class TestPriceLevel(unittest.TestCase):
    def setUp(self):
        self.price_level = PriceLevel(100.0)
        self.long_order = Order(
            id="1",
            type=OrderType.LIMIT,
            side=OrderSide.BUY,
            position=Position.LONG,
            price=100.0,
            quantity=5,
            timestamp=datetime.now()
        )
        self.short_order = Order(
            id="2",
            type=OrderType.LIMIT,
            side=OrderSide.SELL,
            position=Position.SHORT,
            price=100.0,
            quantity=3,
            timestamp=datetime.now()
        )

    def test_add_order(self):
        self.price_level.add_order(self.long_order)
        self.assertEqual(self.price_level.long_total, 5)
        self.assertEqual(len(self.price_level.long_orders), 1)

        self.price_level.add_order(self.short_order)
        self.assertEqual(self.price_level.short_total, 3)
        self.assertEqual(len(self.price_level.short_orders), 1)

    def test_can_match(self):
        self.price_level.add_order(self.short_order)
        self.assertTrue(self.price_level.can_match(self.long_order))

    def test_get_qty_full_fill(self):
        self.price_level.add_order(self.long_order)
        filled, partial, remaining = self.price_level.get_qty(5, Position.LONG)

        self.assertEqual(len(filled), 1)
        self.assertIsNone(partial)
        self.assertEqual(remaining, 0)
        self.assertEqual(self.price_level.long_total, 0)

    def test_get_qty_partial_fill(self):
        self.price_level.add_order(self.long_order)
        filled, partial, remaining = self.price_level.get_qty(3, Position.LONG)

        self.assertEqual(len(filled), 0)
        self.assertEqual(partial.quantity, 3)
        self.assertEqual(remaining, 0)
        self.assertEqual(self.price_level.long_total, 2)

    def test_get_qty_multiple_orders(self):
        order2 = deepcopy(self.long_order)
        order2.id = "2"

        self.price_level.add_order(self.long_order)
        self.price_level.add_order(order2)

        filled, partial, remaining = self.price_level.get_qty(7, Position.LONG)

        self.assertEqual(len(filled), 1)
        self.assertEqual(partial.quantity, 2)
        self.assertEqual(remaining, 0)
        self.assertEqual(self.price_level.long_total, 3)


    def test_get_qty_short_full_fill(self):
        self.price_level.add_order(self.short_order)
        filled, partial, remaining = self.price_level.get_qty(3, Position.SHORT)

        self.assertEqual(len(filled), 1)
        self.assertIsNone(partial)
        self.assertEqual(remaining, 0)
        self.assertEqual(self.price_level.short_total, 0)


    def test_get_qty_short_partial_fill(self):
        self.price_level.add_order(self.short_order)
        filled, partial, remaining = self.price_level.get_qty(2, Position.SHORT)

        self.assertEqual(len(filled), 0)
        self.assertEqual(partial.quantity, 2)
        self.assertEqual(remaining, 0)
        self.assertEqual(self.price_level.short_total, 1)


    def test_get_qty_short_multiple_orders(self):
        order2 = deepcopy(self.short_order)
        order2.id = "3"

        self.price_level.add_order(self.short_order)
        self.price_level.add_order(order2)

        filled, partial, remaining = self.price_level.get_qty(4, Position.SHORT)

        self.assertEqual(len(filled), 1)
        self.assertEqual(partial.quantity, 1)
        self.assertEqual(remaining, 0)
        self.assertEqual(self.price_level.short_total, 2)