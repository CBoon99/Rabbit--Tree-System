import streamlit as st
import pandas as pd
import plotly.express as px
import time
import os
import csv
from datetime import datetime, timedelta
import numpy as np
import asyncio
import logging
import subprocess
import signal
import psutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
from queue import Queue
import json
import atexit

# Configure logging
logging.basicConfig(
    filename='logs/dashboard.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Helper to get today's bot log path
def get_today_bot_log():
    return f"logs/bot_{datetime.now().strftime('%Y%m%d')}.log"

# ... existing code ... 