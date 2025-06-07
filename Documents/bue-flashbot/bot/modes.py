from datetime import datetime
import time

def run_sim_mode(bot_core, speed=1):
    bot_core.run_cycle(sim=True, speed=speed)

def run_live_mode(bot_core):
    bot_core.run_cycle(sim=False)

def run_historical_mode(bot_core, file, speed=1):
    # Placeholder for historical mode logic
    bot_core.run_historical(file, speed=speed) 