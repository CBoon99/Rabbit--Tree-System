import requests
import pandas as pd
import time
import os
import logging
import numpy as np
from config import COINS, MOCK_DATA

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Map COINS to CoinGecko IDs
COIN_MAPPING = {
    "BTC": {"coingecko": "bitcoin"},
    "ETH": {"coingecko": "ethereum"},
    "PEPE": {"coingecko": "pepe"},
    "ZBCN": {"coingecko": "zbcn"},
    "DOGE": {"coingecko": "dogecoin"},
    "SHIB": {"coingecko": "shiba-inu"},
    "LINK": {"coingecko": "chainlink"}
}

class DataManager:
    def __init__(self):
        self.cache = {}
        self.cache_timeout = 60  # Cache prices for 60s

    def get_prices(self, mode, coins):
        if "prices" in self.cache and time.time() - self.cache["timestamp"] < self.cache_timeout:
            return self.cache["prices"]
        try:
            coingecko_coins = [COIN_MAPPING[coin]["coingecko"] for coin in coins]
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={','.join(coingecko_coins)}&vs_currencies=gbp"
            headers = {"accept": "application/json"}
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 429:
                logging.warning("CoinGecko rate limit hit, using mock data")
                return MOCK_DATA
            response.raise_for_status()
            prices = response.json()
            mapped_prices = {coin: prices.get(COIN_MAPPING[coin]["coingecko"], {"gbp": 0}) for coin in coins}
            self.cache = {"prices": mapped_prices, "timestamp": time.time()}
            return mapped_prices
        except Exception as e:
            logging.error(f"Price fetch error: {e}")
            return MOCK_DATA

    def get_price_history(self, symbol, mode, days=14):
        max_retries = 3
        retry_delays = [1, 2, 4]
        last_request_time = getattr(self, 'last_request_time', 0)
        current_time = time.time()
        if current_time - last_request_time < 30:
            time.sleep(30 - (current_time - last_request_time))
        self.last_request_time = time.time()

        for retry in range(max_retries):
            try:
                url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=gbp"
                headers = {"accept": "application/json"}
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 429:
                    logging.warning(f"Rate limit hit for {symbol}, using mock data")
                    return [MOCK_DATA.get(symbol, {"gbp": 100})["gbp"] - i * 100 for i in range(15)]
                response.raise_for_status()
                logging.debug(f"Response headers for {symbol}: {response.headers}")
                logging.debug(f"Raw response for {symbol}: {response.text[:500]}")  # First 500 chars only
                data = response.json()
                price = data.get(symbol, {}).get("gbp")

                if price is None:
                    raise ValueError(f"No GBP price found for {symbol}")

                prices = [price]
                self.cache[symbol] = price
                return prices * 15
            except Exception as e:
                logging.error(f"Price history error for {symbol}: {e}")
                if retry < max_retries - 1:
                    time.sleep(retry_delays[retry])
                else:
                    logging.error(f"Failed to fetch price for {symbol} after {max_retries} retries")
                    return [self.cache.get(symbol, 0)] * 15

    def calculate_rsi(self, prices, period=14):
        # Prevent RSI crash on short price history
        if not prices or len(prices) < 2:
            return 0.0
        changes = np.diff(prices)
        gains = np.where(changes > 0, changes, 0)
        losses = np.where(changes < 0, -changes, 0)
        avg_gains = pd.Series(gains).rolling(period).mean()
        avg_losses = pd.Series(losses).rolling(period).mean()
        rs = avg_gains / avg_losses
        rsi = 100 - (100 / (1 + rs)).iloc[-1]
        return rsi if not np.isnan(rsi) else 0.0