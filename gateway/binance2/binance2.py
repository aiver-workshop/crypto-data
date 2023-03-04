"""
Binance gateway implementation using library https://github.com/sammchardy/python-binance

Support public endpoints only.

"""
import asyncio
import logging
import sys
from enum import Enum
from threading import Thread
from binance import AsyncClient, BinanceSocketManager, DepthCacheManager
from binance.depthcache import FuturesDepthCacheManager
from binance.enums import FuturesType
from gateway.gateway_interface import GatewayInterface
from common.callback_utils import assert_param_counts
from common.interface_book import VenueOrderBook, PriceLevel, OrderBook, Trade, Side


class ProductType(Enum):
    SPOT = 0
    FUTURE_USD = 1      # settle in USDT or BUSD
    FUTURE_COIN = 2     # settle in underlying coin


class BinanceGateway(GatewayInterface):
    def __init__(self, symbol: str, product_type=ProductType.FUTURE_USD, name='Binance'):
        self._exchange_name = name
        self._symbol = symbol
        self._product_type = product_type

        # binance async client
        self._client = None
        self._bm = None         # binance socket manager
        self._dcm = None        # depth cache, which implements the logic to manage a local order book
        self._dws = None        # depth async WebSocket session
        self._ts  = None        # trade socket
        self._tws = None        # trade async WebSocket session

        # depth cache
        self._depth_cache = None

        # this is a loop and dedicated thread to run all async concurrent tasks
        self._loop = asyncio.new_event_loop()
        self._loop_thread = Thread(target=self._run_async_tasks, daemon=True, name=name)

        # readiness and circuit breaker flag
        self._signal_reconnect = False

        # callbacks
        self._depth_callbacks = []
        self._market_trades_callbacks = []

        # streaming status flags
        self._streaming_book = False
        self._streaming_trade = False

    def connect(self):
        logging.info('Initializing connection')

        self._loop.run_until_complete(self._reconnect_ws())

        logging.info("starting event loop thread")
        self._loop_thread.start()

    def _run_async_tasks(self):
        """ Run the following tasks concurrently in the current thread """
        self._loop.create_task(self._listen_depth_forever())
        self._loop.create_task(self._listen_trade_forever())
        self._loop.run_forever()

    def _has_keys(self) -> bool:
        return self._api_key and self._api_secret

    async def _reconnect_ws(self):
        logging.info("reconnecting")

        # ws connect
        await self._connect_ws()

    async def _connect_ws(self):
        logging.info("connecting to ws")
        self._client = await AsyncClient.create()
        self._bm = BinanceSocketManager(self._client)

    async def _listen_depth_forever(self):
        logging.info("start subscribing and listen to depth events")
        while True:
            if not self._dws:
                logging.info("depth socket not connected, reconnecting")
                if self._product_type == ProductType.SPOT:
                    self._dcm = DepthCacheManager(self._client, symbol=self._symbol, bm=self._bm, ws_interval=100)
                else:
                    self._dcm = FuturesDepthCacheManager(self._client, symbol=self._symbol, bm=self._bm)

                self._dws = await self._dcm.__aenter__()
                self._streaming_book = True
                logging.info("depth stream successfully started")

            # wait for depth update
            try:
                self._depth_cache = await self._dws.recv()

                if self._depth_callbacks:
                    for _cb in self._depth_callbacks:
                        _cb(self._exchange_name, VenueOrderBook(self._exchange_name, self._get_order_book()))

            except Exception as e:
                await self._handle_exception(e, 'encountered issue in depth processing')

    async def _listen_trade_forever(self):
        logging.info("start subscribing and listen to trade events")
        while True:
            if not self._tws:
                logging.info("trade socket not connected, reconnecting")
                if self._product_type == ProductType.SPOT:
                    self._ts = self._bm.aggtrade_socket(self._symbol)
                elif self._product_type == ProductType.FUTURE_USD:
                    self._ts = self._bm.aggtrade_futures_socket(symbol=self._symbol, futures_type=FuturesType.USD_M)
                elif self._product_type == ProductType.FUTURE_COIN:
                    self._ts = self._bm.aggtrade_futures_socket(symbol=self._symbol, futures_type=FuturesType.COIN_M)
                else:
                    sys.exit('Unrecognized product type: '.format(self._product_type))

                self._tws = await self._ts.__aenter__()
                logging.info("trade stream successfully started")

            # wait for trade message
            try:
                """
                {
                    "e": "trade",     // Event type
                    "E": 123456789,   // Event time
                    "s": "BNBBTC",    // Symbol
                    "t": 12345,       // Trade ID
                    "p": "0.001",     // Price
                    "q": "100",       // Quantity
                    "b": 88,          // Buyer order ID
                    "a": 50,          // Seller order ID
                    "T": 123456785,   // Trade time
                    "m": true,        // Is the buyer the market maker?
                    "M": true         // Ignore
                }                
                """
                message = await self._tws.recv()

                if self._market_trades_callbacks:
                    data = message['data']
                    # Is the buyer the market maker? side is from taker view
                    # true means maker buy, taker sell; false means taker buy
                    side = Side.Sell if data['m'] is True else Side.Buy
                    trade = Trade(received_time=data['T'],
                                  contract_name=data['s'],
                                  price=float(data['p']),
                                  size=float(data['q']),
                                  side=side,
                                  liquidation=False)
                    for _cb in self._market_trades_callbacks:
                        _cb([trade])

            except Exception as e:
                await self._handle_exception(e, 'encountered issue in trade processing')

    async def _handle_exception(self, e: Exception, msg: str):
        self._streaming_book = False
        self._streaming_trade = False
        logging.exception(msg)
        # reset all sockets
        self._dws = None
        self._tws = None
        # reconnect client
        await self._reconnect_ws()

    def _get_order_book(self) -> OrderBook:
        bids = [PriceLevel(price=p, size=s) for (p, s) in self._depth_cache.get_bids()[:10]]
        asks = [PriceLevel(price=p, size=s) for (p, s) in self._depth_cache.get_asks()[:10]]
        return OrderBook(timestamp=self._depth_cache.update_time, contract_name=self._symbol, bids=bids, asks=asks)

    #############################################
    ##               Interface                 ##
    #############################################

    def get_name(self):
        return self._exchange_name

    def not_ready(self) -> bool:
        return self._streaming

    def get_order_book(self, contract_name: str) -> OrderBook:
        return self._get_order_book()

    def register_depth_callback(self, callback):
        """ a depth callback function takes two argument: (exchange_name:str, book: VenueOrderBook) """
        assert_param_counts(callback, 2)
        self._depth_callbacks.append(callback)

    """ register a callback to listen to market trades that takes one argument: [Trades] """
    def register_market_trades_callback(self, callback):
        assert_param_counts(callback, 1)
        self._market_trades_callbacks.append(callback)
