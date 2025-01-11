import unittest
from collections import OrderedDict
from datetime import datetime
from unittest.mock import MagicMock, patch

from src.order_book_engine.models.level import PriceLevel
from src.order_book_engine.models.matching_engine import MatchingEngine
from src.order_book_engine.models.order import Order, OrderType, OrderSide, Position


class TestMatchingEngine(unittest.TestCase):
    def setUp(self):
        self.engine = MockMatchingEngine("GCQ4")
        self.timestamp = datetime.now()
        self.mock_level = PriceLevel(100, "GCQ4")
        self.mock_level.get_qty = MagicMock(return_value=([Order(
            id="2", symbol="GCQ4", type=OrderType.LIMIT,
            side=OrderSide.SELL, position=Position.SHORT,
            quantity=10, price=100, timestamp=self.timestamp
        )], None, 0))

    def test_match_market_buy_long_order(self):
        order = Order(
            id="1",
            symbol="GCQ4",
            type=OrderType.MARKET,
            side=OrderSide.BUY,
            position=Position.LONG,
            quantity=10,
            timestamp=self.timestamp
        )

        # Mock price level
        mock_price_level = PriceLevel(100, "GCQ4")

        # Configurar mock para devolver filled_orders, partial y no quantity restante
        mock_price_level.get_qty = MagicMock(return_value=([], None, 0))

        # Solo devuelve el mock una vez, luego None
        self.engine.get_best_ask = MagicMock(side_effect=[(100, mock_price_level), None])

        filled, partial = self.engine._match_market_order(order)
        self.assertEqual(len(filled), 0)
        self.assertEqual(len(partial), 0)

    def test_match_market_sell_short_order(self):
        order = Order(
            id="1",
            symbol="GCQ4",
            type=OrderType.MARKET,
            side=OrderSide.SELL,
            position=Position.SHORT,
            quantity=10,
            timestamp=self.timestamp
        )

        # Mock filled orders
        filled_order = Order(
            id="2",
            symbol="GCQ4",
            type=OrderType.LIMIT,
            side=OrderSide.BUY,
            position=Position.LONG,
            quantity=10,
            price=100,
            timestamp=self.timestamp
        )

        mock_level = PriceLevel(100, "GCQ4")
        mock_level.get_qty = MagicMock(return_value=([filled_order], None, 0))
        self.engine.get_best_bid = MagicMock(return_value=(100, mock_level))

        filled, partial = self.engine._match_market_order(order)
        self.assertEqual(len(filled), 1)
        self.assertEqual(len(partial), 0)

    def test_match_limit_order_no_match(self):
        order = Order(
            id="1",
            symbol="GCQ4",
            type=OrderType.LIMIT,
            side=OrderSide.BUY,
            position=Position.LONG,
            quantity=10,
            price=90,
            timestamp=self.timestamp
        )

        asks = {100: MagicMock()}
        bids = {80: MagicMock()}

        matched_order, matched, remaining = self.engine._match_limit_order(
            order, asks, bids)

        self.assertEqual(remaining, 10)
        self.assertEqual(len(matched), 0)

    def test_match_limit_order_partial_fill(self):
        order = Order(
            id="1",
            symbol="GCQ4",
            type=OrderType.LIMIT,
            side=OrderSide.BUY,
            position=Position.LONG,
            quantity=10,
            price=100,
            timestamp=self.timestamp
        )

        filled_order = Order(
            id="2",
            symbol="GCQ4",
            type=OrderType.LIMIT,
            side=OrderSide.SELL,
            position=Position.SHORT,
            quantity=5,
            price=100,
            timestamp=self.timestamp
        )

        mock_level = PriceLevel(100, "GCQ4")
        mock_level.get_qty = MagicMock(return_value=([filled_order], None, 5))

        asks = {100: mock_level}
        bids = {}

        matched_order, matched, remaining = self.engine._match_limit_order(
            order, asks, bids)

        self.assertEqual(remaining, 10)
        self.assertEqual(len(matched), 0)

    def test_mock_matching_engine(self):
        mock_level = PriceLevel(100, "GCQ4")
        mock_level.get_qty = MagicMock(return_value=([], None, 0))

        self.engine.get_best_ask = MagicMock(side_effect=[(100, mock_level), None])
        self.engine.get_best_bid = MagicMock(side_effect=[(99, mock_level), None])

        order = Order(
            id="1",
            symbol="GCQ4",
            type=OrderType.MARKET,
            side=OrderSide.BUY,
            position=Position.LONG,
            quantity=10,
            timestamp=self.timestamp
        )

        filled, partial = self.engine._match_market_order(order)
        self.assertEqual(len(filled), 0)
        self.assertEqual(len(partial), 0)

    def test_match_market_order_buy_long(self):
        order = Order(
            id="1", symbol="GCQ4", type=OrderType.MARKET,
            side=OrderSide.BUY, position=Position.LONG,
            quantity=10, timestamp=self.timestamp
        )

        self.engine.get_best_ask = MagicMock(side_effect=[(100, self.mock_level), None])
        filled, partial = self.engine._match_market_order(order)

        self.assertEqual(len(filled), 1)
        self.assertEqual(len(partial), 0)

    def test_match_market_order_buy_short(self):
        order = Order(
            id="1", symbol="GCQ4", type=OrderType.MARKET,
            side=OrderSide.BUY, position=Position.SHORT,
            quantity=10, timestamp=self.timestamp
        )

        self.engine.get_best_ask = MagicMock(side_effect=[(100, self.mock_level), None])
        filled, partial = self.engine._match_market_order(order)
        self.assertEqual(len(filled), 1)

    def test_match_market_order_sell_short(self):
        order = Order(
            id="1", symbol="GCQ4", type=OrderType.MARKET,
            side=OrderSide.SELL, position=Position.SHORT,
            quantity=10, timestamp=self.timestamp
        )

        self.engine.get_best_bid = MagicMock(side_effect=[(100, self.mock_level), None])
        filled, partial = self.engine._match_market_order(order)
        self.assertEqual(len(filled), 1)

    def test_match_limit_order(self):
        order = Order(
            id="1", symbol="GCQ4", type=OrderType.LIMIT,
            side=OrderSide.BUY, position=Position.LONG,
            quantity=10, price=100, timestamp=self.timestamp
        )

        ask_order = Order(
            id="2", symbol="GCQ4", type=OrderType.LIMIT,
            side=OrderSide.SELL, position=Position.SHORT,
            quantity=10, price=99, timestamp=self.timestamp
        )

        mock_level = PriceLevel(99, "GCQ4")
        mock_level.get_qty = MagicMock(return_value=([ask_order], None, 0))
        order.quantity = 0  # Simulamos que la orden se ha ejecutado completamente

        asks = OrderedDict({99: mock_level})
        bids = OrderedDict()

        self.engine.get_best_ask = MagicMock(side_effect=[(99, mock_level), None])

        updated_order, matched, remaining = self.engine._match_limit_order(order, asks, bids)
        self.assertEqual(len(matched), 1)
        self.assertEqual(remaining, 0)


class MockMatchingEngine(MatchingEngine):
    def match(self, order):
        pass

    def get_best_ask(self):
        pass

    def get_best_bid(self):
        pass




if __name__ == '__main__':
    unittest.main()