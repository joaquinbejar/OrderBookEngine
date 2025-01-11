import unittest
from datetime import datetime

from src.order_book_engine.models.order import OrderType, Order, OrderSide, Position
from src.order_book_engine.utils.match import is_valid_match


class TestMatching(unittest.TestCase):
   def setUp(self):
       self.timestamp = datetime.now()
       self.order_params = {
           "id": "1",
           "symbol": "GCQ4",
           "quantity": 10,
           "timestamp": self.timestamp,
           "type": OrderType.LIMIT,
           "price": 100
       }

   def test_buy_long_vs_sell_short(self):
       order1 = Order(**self.order_params, side=OrderSide.BUY, position=Position.LONG)
       order2 = Order(**self.order_params, side=OrderSide.SELL, position=Position.SHORT)
       self.assertTrue(is_valid_match(order1, order2))

   def test_sell_long_vs_buy_short(self):
       order1 = Order(**self.order_params, side=OrderSide.SELL, position=Position.LONG)
       order2 = Order(**self.order_params, side=OrderSide.BUY, position=Position.SHORT)
       self.assertTrue(is_valid_match(order1, order2))

   def test_invalid_match(self):
       order1 = Order(**self.order_params, side=OrderSide.BUY, position=Position.LONG)
       order2 = Order(**self.order_params, side=OrderSide.BUY, position=Position.SHORT)
       self.assertFalse(is_valid_match(order1, order2))