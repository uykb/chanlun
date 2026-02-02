from chanlun.base import Market
from chanlun.exchange.exchange import Exchange

g_exchange_obj = {}


def get_exchange(market: Market) -> Exchange:
    global g_exchange_obj
    if market.value in g_exchange_obj.keys():
        return g_exchange_obj[market.value]

    if market == Market.CURRENCY:
        from chanlun.exchange.exchange_binance import ExchangeBinance

        g_exchange_obj[market.value] = ExchangeBinance(market_type="futures")
    elif market == Market.CURRENCY_SPOT:
        from chanlun.exchange.exchange_binance import ExchangeBinance

        g_exchange_obj[market.value] = ExchangeBinance(market_type="spot")
    else:
        raise Exception(f"不支持的市场 {market}")

    return g_exchange_obj[market.value]
