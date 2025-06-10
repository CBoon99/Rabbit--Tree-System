import requests
import pandas as pd
import numpy as np
import time
import os
import logging
import sys
import fcntl
from datetime import datetime
import csv
import json
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = "/Users/carlboon/Documents/bue-flashbot"
sys.path.append(BASE_DIR)
from data_manager import DataManager
from config import COINS, MOCK_DATA

# Load .env (for future API keys)
load_dotenv()

CONTROL_FILE = os.path.join(BASE_DIR, "bot_control.json")
STATUS_FILE = os.path.join(BASE_DIR, "bot_status.json")
BUE_LOG = os.path.join(BASE_DIR, "bue_log.csv")
WHY_NOT_LOG = os.path.join(BASE_DIR, "log-why-not-trading.txt")

logging.basicConfig(filename=os.path.join(BASE_DIR, "bot.log"), level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class BotEngine:
    def __init__(self):
        self.data_manager = DataManager()
        self.mode = "SIM"
        self.balance = 1000
        self.min_cash = 100
        self.leverage = 200
        self.delta = 0.01
        self.trailing_bue = 0.97
        self.rsi_buy = 75
        self.rsi_sell = 35
        self.positions = {}
        self.coins = COINS
        self.running = False
        self.ensure_files()

    def ensure_files(self):
        for log in [BUE_LOG, WHY_NOT_LOG, CONTROL_FILE, STATUS_FILE]:
            Path(log).touch()
            os.chmod(log, 0o644)
        with open(BUE_LOG, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Time", "Coin", "Action", "Price", "Amount", "P&L", "Balance"])

    def safe_json_write(self, filepath, data):
        with open(filepath, 'w') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            json.dump(data, f)
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    def calculate_rsi(self, prices, period=14):
        if len(prices) < period + 1:
            return 50
        changes = np.diff(prices)
        gains = np.where(changes > 0, changes, 0)
        losses = np.where(changes < 0, -changes, 0)
        avg_gains = pd.Series(gains).rolling(period).mean()
        avg_losses = pd.Series(losses).rolling(period).mean()
        rs = avg_gains / avg_losses
        rsi = 100 - (100 / (1 + rs)).iloc[-1]
        return rsi if not np.isnan(rsi) else 50

    def calculate_position_size(self, price, volatility):
        risk_per_trade = 0.01 * self.balance
        stop_loss = price * 0.05
        size = risk_per_trade / stop_loss
        return min(size, self.balance * self.leverage / price)

    def run(self):
        self.running = True
        self.safe_json_write(STATUS_FILE, {"status": "running", "message": "Bot started"})
        logging.info("Bot engine started")

        while self.running:
            try:
                with open(CONTROL_FILE, "r") as f:
                    fcntl.flock(f.fileno(), fcntl.LOCK_SH)
                    control = json.load(f)
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                if control["command"] == "stop":
                    self.running = False
                    break
                self.mode = control["mode"]
                self.balance = control["deposit"]

                prices = self.data_manager.get_prices(self.mode, self.coins)
                for coin in self.coins:
                    price = prices.get(coin, {}).get("gbp", 0)
                    if not price:
                        continue
                    history = self.data_manager.get_price_history(coin, self.mode)
                    rsi = self.calculate_rsi(history)
                    delta_price = (price - history[-2]) / history[-2] if len(history) > 1 else 0
                    mean_price = np.mean(history[-14:]) if len(history) >= 14 else 1
                    volatility = np.std(history[-14:]) / mean_price if mean_price > 0 else 0.1

                    if rsi < self.rsi_buy and delta_price > self.delta and self.balance > self.min_cash:
                        amount = self.calculate_position_size(price, volatility)
                        stop_loss = price * 0.95
                        self.positions[coin] = {"amount": amount, "entry": price, "trailing_stop": price * self.trailing_bue, "stop_loss": stop_loss}
                        self.balance -= amount * price / self.leverage
                        self.log_trade(coin, "BUY", price, amount)
                        logging.info(f"BUY {coin} at {price}, RSI: {rsi}, Delta: {delta_price}")

                    elif coin in self.positions:
                        pos = self.positions[coin]
                        if rsi > self.rsi_sell or price < pos["stop_loss"] or price < pos["trailing_stop"]:
                            self.balance += pos["amount"] * price / self.leverage
                            pl = (price - pos["entry"]) * pos["amount"]
                            self.log_trade(coin, "SELL", price, pos["amount"], pl)
                            logging.info(f"SELL {coin} at {price}, RSI: {rsi}, P&L: {pl}")
                            del self.positions[coin]
                        else:
                            pos["trailing_stop"] = max(pos["trailing_stop"], price * self.trailing_bue)

                    else:
                        with open(WHY_NOT_LOG, "a") as f:
                            f.write(f"{datetime.now()}: No trade for {coin} - RSI: {rsi}, Delta: {delta_price}\n")

                time.sleep(5)
            except Exception as e:
                logging.error(f"Bot error: {e}")
                self.safe_json_write(STATUS_FILE, {"status": "error", "message": str(e)})
                time.sleep(10)

        self.safe_json_write(STATUS_FILE, {"status": "stopped", "message": "Bot stopped"})
        logging.info("Bot engine stopped")

    def log_trade(self, coin, action, price, amount, pl=0):
        with open(BUE_LOG, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([datetime.now(), coin, action, price, amount, pl, self.balance])

if __name__ == "__main__":
    bot = BotEngine()
    bot.run()