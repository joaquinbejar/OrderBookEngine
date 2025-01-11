import unittest
from datetime import datetime

from src.order_book_engine.models.order import Order, OrderType, OrderSide, Position


class TestOrder(unittest.TestCase):
   def setUp(self):
       self.timestamp = datetime.now()

   def test_market_order_creation(self):
       order = Order(
           id="1",
           type=OrderType.MARKET,
           side=OrderSide.BUY,
           position=Position.LONG,
           quantity=100,
           timestamp=self.timestamp
       )
       self.assertIsNone(order.price)

   def test_limit_order_creation(self):
       order = Order(
           id="2",
           type=OrderType.LIMIT,
           side=OrderSide.SELL,
           position=Position.SHORT,
           quantity=100,
           timestamp=self.timestamp,
           price=10.5
       )
       self.assertEqual(order.price, 10.5)

   def test_limit_order_without_price(self):
       with self.assertRaises(ValueError) as context:
           Order(
               id="3",
               type=OrderType.LIMIT,
               side=OrderSide.BUY,
               position=Position.LONG,
               quantity=100,
               timestamp=self.timestamp
           )
       self.assertTrue("Limit orders must have a price" in str(context.exception))

   def test_order_enums(self):
       order = Order(
           id="4",
           type=OrderType.MARKET,
           side=OrderSide.BUY,
           position=Position.LONG,
           quantity=100,
           timestamp=self.timestamp
       )
       self.assertIn(order.type, OrderType)
       self.assertIn(order.side, OrderSide)
       self.assertIn(order.position, Position)

if __name__ == '__main__':
   unittest.main()