import unittest
from datetime import datetime

from src.order_book_engine.models.order import Order, OrderType, OrderSide, Position
from src.order_book_engine.models.orderbook import OrderBook


class TestOrderBook(unittest.TestCase):
    def setUp(self):
        self.order_book = OrderBook("GCQ4")
        self.timestamp = datetime.now()

        # Common order parameters
        self.order_params = {
            "symbol": "GCQ4",
            "quantity": 100,
            "timestamp": self.timestamp,
        }

    def test_empty_book(self):
        self.assertIsNone(self.order_book.get_best_bid())
        self.assertIsNone(self.order_book.get_best_ask())
        self.assertIsNone(self.order_book.get_spread())

    def test_add_limit_bid(self):
        bid = Order(
            id="1",
            type=OrderType.LIMIT,
            side=OrderSide.BUY,
            position=Position.LONG,
            price=10.5,
            **self.order_params
        )
        self.order_book.add_bid(bid)
        best_bid = self.order_book.get_best_bid()
        self.assertEqual(best_bid[0], 10.5)


    def test_add_multiple_limit_bids(self):
        bids = [
            Order(id="1", type=OrderType.LIMIT, side=OrderSide.BUY,
                  position=Position.LONG, price=10.5, **self.order_params),
            Order(id="2", type=OrderType.LIMIT, side=OrderSide.BUY,
                  position=Position.LONG, price=11.0, **self.order_params)
        ]
        for bid in bids:
            self.order_book.add_bid(bid)
        best_bid = self.order_book.get_best_bid()
        self.assertEqual(best_bid[0], 11.0)


    def test_add_limit_ask(self):
        ask = Order(
            id="1",
            type=OrderType.LIMIT,
            side=OrderSide.SELL,
            position=Position.SHORT,
            price=10.5,
            **self.order_params
        )
        self.order_book.add_ask(ask)
        best_ask = self.order_book.get_best_ask()
        self.assertEqual(best_ask[0], 10.5)

    def test_limit_order_spread(self):
        bid = Order(
            id="1", type=OrderType.LIMIT, side=OrderSide.BUY,
            position=Position.LONG, price=10.0, **self.order_params
        )
        ask = Order(
            id="2", type=OrderType.LIMIT, side=OrderSide.SELL,
            position=Position.SHORT, price=11.0, **self.order_params
        )

        self.order_book.add_bid(bid)
        self.order_book.add_ask(ask)

        spread = self.order_book.get_spread()
        self.assertEqual(spread, (11.0, 10.0))

    def test_market_order_no_price(self):
        market_order = Order(
            id="1", type=OrderType.MARKET, side=OrderSide.BUY,
            position=Position.LONG, price=None, **self.order_params
        )
        self.assertIsNone(market_order.price)

    def test_limit_order_requires_price(self):
        with self.assertRaises(ValueError):
            Order(id="1", type=OrderType.LIMIT, side=OrderSide.BUY,
                  position=Position.LONG, price=None, **self.order_params)