import unittest
from datetime import datetime
from unittest.mock import MagicMock

from src.order_book_engine.models.order import Order, OrderType, OrderSide, Position
from src.order_book_engine.models.orderbook import OrderBook


class TestOrderBook(unittest.TestCase):
    def setUp(self):
        self.order_book = OrderBook("GCQ4")
        self.timestamp = datetime.now()

    def test_add_bid_new_price_level(self):
        order = Order(
            id="1", symbol="GCQ4",
            type=OrderType.LIMIT,
            side=OrderSide.BUY,
            position=Position.LONG,
            quantity=10,
            price=100,
            timestamp=self.timestamp
        )
        self.order_book._add_bid(order)
        self.assertIn(100, self.order_book.bids)

    def test_add_ask_new_price_level(self):
        order = Order(
            id="1", symbol="GCQ4",
            type=OrderType.LIMIT,
            side=OrderSide.SELL,
            position=Position.SHORT,
            quantity=10,
            price=100,
            timestamp=self.timestamp
        )
        self.order_book._add_ask(order)
        self.assertIn(100, self.order_book.asks)

    def test_get_best_bid_empty(self):
        self.assertIsNone(self.order_book.get_best_bid())

    def test_get_best_ask_empty(self):
        self.assertIsNone(self.order_book.get_best_ask())

    def test_get_spread_empty(self):
        self.assertIsNone(self.order_book.get_spread())

    def test_get_spread(self):
        bid = Order(
            id="1", symbol="GCQ4",
            type=OrderType.LIMIT,
            side=OrderSide.BUY,
            position=Position.LONG,
            quantity=10,
            price=99,
            timestamp=self.timestamp
        )
        ask = Order(
            id="2", symbol="GCQ4",
            type=OrderType.LIMIT,
            side=OrderSide.SELL,
            position=Position.SHORT,
            quantity=10,
            price=100,
            timestamp=self.timestamp
        )

        self.order_book._add_bid(bid)
        self.order_book._add_ask(ask)

        spread = self.order_book.get_spread()
        self.assertEqual(spread, (100, 99))

    def test_match_market_order_no_matches(self):
        order = Order(
            id="1", symbol="GCQ4",
            type=OrderType.MARKET,
            side=OrderSide.BUY,
            position=Position.LONG,
            quantity=10,
            timestamp=self.timestamp
        )

        with self.assertRaises(ValueError):
            self.order_book.match(order)

    def test_match_limit_order(self):
        limit_order = Order(
            id="1", symbol="GCQ4",
            type=OrderType.LIMIT,
            side=OrderSide.BUY,
            position=Position.LONG,
            quantity=10,
            price=100,
            timestamp=self.timestamp
        )

        self.order_book._match_limit_order = MagicMock(
            return_value=(limit_order, [], 10)
        )

        self.order_book.match(limit_order)
        self.assertIn(100, self.order_book.bids)