import requests
from decimal import Decimal
from django.conf import settings
from datetime import datetime, timedelta, timezone

api_key = settings.BSCSCAN_API_KEY
base_url = 'https://api.bscscan.com/api'


def check_bsc_transaction(address, expected_amount, created_after=None, contract_address=None) -> bool:
    """
    Перевіряє, чи була вхідна транзакція на задану адресу з очікуваною сумою.
    Працює як для BNB, так і для токенів (наприклад USDT, USDC).
    """
    address = address.lower()
    is_token = contract_address is not None

    # Обираємо правильний тип транзакцій
    params = {
        'module': 'account',
        'action': 'tokentx' if is_token else 'txlist',
        'address': address,
        'sort': 'desc',
        'apikey': api_key
    }

    response = requests.get(base_url, params=params)
    if response.status_code != 200:
        print("Помилка запиту:", response.text)
        return False

    transactions = response.json().get('result', [])

    for tx in transactions:
        if tx.get('to', '').lower() != address:
            continue

        if created_after:
            timestamp = int(tx.get('timeStamp', 0))
            tx_time = datetime.fromtimestamp(timestamp, tz=timezone.utc)
            if tx_time <= (created_after - timedelta(hours=3)):
                continue

        # Перевірка токена за контрактом
        if is_token:
            if tx.get('contractAddress', '').lower() != contract_address.lower():
                continue
            token_decimals = int(tx.get('tokenDecimal', 18))
            value = Decimal(tx.get('value')) / Decimal(10 ** token_decimals)
        else:
            # Для BNB
            value = Decimal(tx.get('value')) / Decimal(10 ** 18)

        # Порівняння з похибкою
        if abs(value - expected_amount) < Decimal("0.000001"):
            print("🔍 Знайдено транзакцію:", tx)
            return True

    return False
