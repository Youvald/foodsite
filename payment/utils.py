# payment/utils.py
import requests

COINGECKO_API_URL = "https://api.coingecko.com/api/v3/simple/price"

CURRENCY_MAP = {
    'BNB': 'binancecoin',
    'LTC': 'litecoin',
    'ETH': 'ethereum',
    'USDT': 'tether',
    'USDC': 'usd-coin',
}

def get_crypto_price(crypto_symbol: str, vs_currency: str = "uah") -> float | None:
    """
    Отримує курс криптовалюти до заданої валюти (за замовчуванням UAH).
    """
    coin_id = CURRENCY_MAP.get(crypto_symbol.upper())
    if not coin_id:
        return None

    try:
        response = requests.get(COINGECKO_API_URL, params={
            "ids": coin_id,
            "vs_currencies": vs_currency
        })
        response.raise_for_status()
        data = response.json()
        return data[coin_id][vs_currency]
    except (requests.RequestException, KeyError):
        return None
