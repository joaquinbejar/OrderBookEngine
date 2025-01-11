
# OrderBookEngine

OrderBookEngine is a Python-based implementation of an advanced trading order book. It supports both limit and market orders, and provides functionality for order matching, position tracking, and integration with various trading instruments, including futures contracts. This engine is designed for extensibility and robustness in trading applications.

## Features

- **Order Management**: Supports buy and sell orders with `LIMIT` and `MARKET` types.
- **Position Tracking**: Tracks `LONG` and `SHORT` positions for all orders.
- **Order Matching**: Implements matching logic for both market and limit orders.
- **Price Levels**: Maintains detailed price levels for efficient order management.
- **Futures Contract Support**: Handles orders with expiration dates and filters matches by contract symbols.
- **Unit Tested**: Includes comprehensive test cases for all critical modules.

## Requirements

- Python 3.8+
- Libraries:
  - `unittest` (for running test cases)
  - Standard Python libraries (datetime, enum, collections, etc.)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/joaquinbejar/OrderBookEngine.git
   cd OrderBookEngine
   ```

2. Install any required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

The project is structured into modules, each handling specific aspects of the order book. Here's how to get started:

1. **Initialize an Order Book**:
   ```python
   from src.order_book_engine.models.orderbook import OrderBook

   order_book = OrderBook("GCQ4")  # Create an order book for Gold Futures
   ```

2. **Add Orders**:
   ```python
   from src.order_book_engine.models.order import Order, OrderType, OrderSide, Position
   from datetime import datetime

   order = Order(
       id="1",
       symbol="GCQ4",
       type=OrderType.LIMIT,
       side=OrderSide.BUY,
       position=Position.LONG,
       quantity=10,
       price=1500.0,
       timestamp=datetime.now(),
   )
   order_book.add_bid(order)
   ```

3. **Match Orders**:
   ```python
   match = order_book.match(order)
   print("Matched Orders:", match)
   ```

4. **View Order Book State**:
   ```python
   print(order_book)
   ```

## Running Tests

The repository includes unit tests to validate the functionality of the order book and its components.

1. Run all tests:
   ```bash
   python -m unittest discover tests
   ```

2. Check specific test files:
   ```bash
   python tests/order_test.py
   python tests/matching_engine_test.py
   ```

## Project Structure

```
OrderBookEngine/
│
├── src/
│   ├── order_book_engine/
│   │   ├── models/
│   │   │   ├── order.py        # Defines Order and related enums
│   │   │   ├── level.py        # Implements PriceLevel
│   │   │   ├── matching_engine.py # Abstract Matching Engine
│   │   │   ├── orderbook.py    # OrderBook implementation
│   │   ├── utils/
│   │   │   ├── logging.py      # Logging configuration
│
├── tests/
│   ├── order_test.py           # Unit tests for Order class
│   ├── level_test.py           # Unit tests for PriceLevel class
│   ├── matching_engine_test.py # Unit tests for MatchingEngine
│   ├── order_book_test.py      # Unit tests for OrderBook class
│
└── README.md
```

## Extensibility

OrderBookEngine is designed with extensibility in mind. Key areas for further development include:

- Adding support for multiple trading instruments.
- Implementing cancel/modify orders functionality.
- Enhancing performance with optimized data structures.

## License

This project is open-source and available under the [MIT License](LICENSE).

## Contributing

Feel free to fork this repository, open issues, and submit pull requests. Contributions are welcome!

## Contact

For any questions or inquiries, please contact [Joaquín Bejar](https://github.com/joaquinbejar).
