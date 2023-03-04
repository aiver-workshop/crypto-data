from common.interface_book import OrderBook


class GatewayInterface:

    def get_name(self):
        pass

    """ get order book """
    def get_order_book(self, symbol: str) -> OrderBook:
        pass

    """ register a depth callback function takes three argument: 
        (exchange_name:str, contract_name:str, book: OrderBook) """
    def register_depth_callback(self, callback):
        pass

    """ register a callback to listen to market trades that takes one argument: [Trades] """
    def register_market_trades_callback(self, callback):
        pass

