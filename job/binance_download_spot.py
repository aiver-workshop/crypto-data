from binance.client import Client
from common.config_logging import get_file_logger

# binance client
client = Client()

logger_spot = get_file_logger("static", "/temp/product_binance_spots.csv")
logger_spot.info("{},{},{},{},{},{},{}".format("symbol", "pricePrecision", "quantityPrecision", "minQty", "maxQty", "minNotional", "maxNotional"))

spots_info = client.get_exchange_info()

for symbol_info in spots_info['symbols']:
    symbol = symbol_info['symbol']

    filters = symbol_info['filters']

    for filter in filters:
        filter_type = filter['filterType']

        if filter_type == 'PRICE_FILTER':
            pricePrecision = filter['tickSize']

        if filter_type == 'LOT_SIZE':
            quantityPrecision = filter['stepSize']
            minQty = filter['minQty']
            maxQty = filter['maxQty']

        if filter_type == 'NOTIONAL':
            minNotional = filter['minNotional']
            maxNotional = filter['maxNotional']

    logger_spot.info("{},{},{},{},{},{},{}".format(symbol, pricePrecision, quantityPrecision, minQty, maxQty, minNotional, maxNotional))
