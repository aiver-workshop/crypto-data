from binance.client import Client
from common.config_logging import get_file_logger

# output file
logger_usd = get_file_logger("static", "/temp/product_binance_futures_usd.csv")
logger_usd.info("{},{},{},{},{},{}".format("symbol", "pricePrecision", "quantityPrecision", "minQty", "maxQty", "minNotional"))

# binance client
client = Client()

# futures usd
futures_usd_info = client.futures_exchange_info()

for symbol_info in futures_usd_info['symbols']:
    symbol = symbol_info['symbol']
    pricePrecision = symbol_info['pricePrecision']
    quantityPrecision = symbol_info['quantityPrecision']

    filters = symbol_info['filters']
    for filter in filters:
        filter_type = filter['filterType']

        if filter_type == 'LOT_SIZE':
            minQty = filter['minQty']
            maxQty = filter['maxQty']

        if filter_type == 'MIN_NOTIONAL':
            minNotional = filter['notional']

    logger_usd.info("{},{},{},{},{},{}".format(symbol, pricePrecision, quantityPrecision, minQty, maxQty, minNotional))



