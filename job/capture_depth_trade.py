import time
import logging
from datetime import datetime, timedelta
from common.config_logging import get_file_logger, enable_console_logging
from common.interface_book import Trade, VenueOrderBook, Side
from gateway.binance2.binance2 import BinanceGateway, ProductType

# parameters
contract = 'BTCUSDT'
product_type = ProductType.FUTURE_USD
duration_minutes = 10
now = datetime.now()
end_time = now + timedelta(minutes=duration_minutes)

# create logging files
datetimeStr = now.strftime("%Y%m%d_%H%M%S")
filename_book = "/data/{}_book_{}.csv".format(contract, datetimeStr)
filename_trade = "/data/{}_trade_{}.csv".format(contract, datetimeStr)

logger_book = get_file_logger("book", filename_book)
logger_trade = get_file_logger("trade", filename_trade)

# enable logging to console
enable_console_logging()

# csv headers
logger_book.info("timestamp,"
                 "ask1price,ask1qty,bid1price,bid1qty,"
                 "ask2price,ask2qty,bid2price,bid2qty,"
                 "ask3price,ask3qty,bid3price,bid3qty,"
                 "ask4price,ask4qty,bid4price,bid4qty,"
                 "ask5price,ask5qty,bid5price,bid5qty,")

logger_trade.info("timestamp,side,price,size")

def to_timestamp_str(timestamp: int):
    # timestamp includes milliseconds
    return datetime.utcfromtimestamp(timestamp/1000.0).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]


# callback on order book update
def on_order_book(venue: str, venue_book: VenueOrderBook):
    book = venue_book.book
    _line = "{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}".format(
        to_timestamp_str(book.timestamp),
        book.asks[0].price, book.asks[0].size, book.bids[0].price, book.bids[0].size,
        book.asks[1].price, book.asks[1].size, book.bids[1].price, book.bids[1].size,
        book.asks[2].price, book.asks[2].size, book.bids[2].price, book.bids[2].size,
        book.asks[3].price, book.asks[3].size, book.bids[3].price, book.bids[3].size,
        book.asks[4].price, book.asks[4].size, book.bids[4].price, book.bids[4].size,
    )
    logger_book.info(_line)


# callback on trades update
def on_trades(trades: [Trade]):
    for trade in trades:
        _line = "{},{},{},{}".format(
            to_timestamp_str(trade.received_time),
            "b" if trade.side is Side.Buy else "s",
            trade.price,
            trade.size
        )
        logger_trade.info(_line)


if __name__ == '__main__':
    # gateway
    binance = BinanceGateway(symbol=contract, product_type=product_type)

    # register callbacks
    binance.register_depth_callback(on_order_book)
    binance.register_market_trades_callback(on_trades)

    # start
    binance.connect()

    while True:
        # heartbeat
        time.sleep(10)
        logging.info("Running ok")
        if datetime.now() > end_time:
            logging.info("Completed recording")
            break

