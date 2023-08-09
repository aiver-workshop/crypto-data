from binance.client import Client
from common.config_logging import get_file_logger


# binance client
client = Client()

# futures coin
logger_coin = get_file_logger("static", "/temp/product_binance_futures_coin.csv")
logger_coin.info("{},{},{},{},{},{}".format("symbol", "pricePrecision", "quantityPrecision", "minQty", "maxQty", "minNotional"))
futures_coin_info = client.futures_coin_exchange_info()
for symbol_info in futures_coin_info['symbols']:
    symbol = symbol_info['symbol']
    pricePrecision = symbol_info['pricePrecision']
    quantityPrecision = symbol_info['quantityPrecision']

    filters = symbol_info['filters']
    for filter in filters:
        filter_type = filter['filterType']

        if filter_type == 'LOT_SIZE':
            minQty = filter['minQty']
            maxQty = filter['maxQty']

        minNotional = 1
        if filter_type == 'MIN_NOTIONAL':
            minNotional = filter['notional']



    logger_coin.info("{},{},{},{},{},{}".format(symbol, pricePrecision, quantityPrecision, minQty, maxQty, minNotional))