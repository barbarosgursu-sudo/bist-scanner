import logging
import pytz
import yfinance as yf
import requests
from datetime import datetime
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from contextlib import asynccontextmanager

GAS_BASE_URL = "https://script.google.com/macros/s/AKfycbwa_Zxh9FWpMPG-Vr8oKq7lTv_ywYKV4nBDweR-oowMNu0gO89UmFee4Y2mandT7nBc/exec"
TR_TZ = pytz.timezone('Europe/Istanbul')
FORCE_NOW = None

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_now():
    if FORCE_NOW:
        return FORCE_NOW
    return datetime.now(TR_TZ)

def get_time_bucket(dt):
    minute = (dt.minute // 5) * 5
    return dt.replace(minute=minute, second=0, microsecond=0).strftime("%H:%M")

def collect_job():
    now = get_now()
    if not (10 <= now.hour < 11):
        return

    date_str = now.strftime("%Y-%m-%d")
    time_bucket = get_time_bucket(now)

    try:
        symbols_res = requests.get(f"{GAS_BASE_URL}?action=getSymbols", timeout=10)
        symbols = symbols_res.json().get("symbols", [])
    except Exception as e:
        logger.error(f"ERR_GET_SYMBOLS | {e}")
        return

    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            current_price = ticker.fast_info['last_price']
            
            start_price = None
            pct = 0.0

            try:
                start_res = requests.get(
                    f"{GAS_BASE_URL}?action=getStartPrice&date={date_str}&symbol={symbol}", 
                    timeout=10
                )
                start_data = start_res.json()
                start_price = start_data.get("start_price")
            except Exception as e:
                logger.warning(f"GAS_START_PRICE_FETCH_ERR | {symbol} | {e}")

            if start_price and float(start_price) > 0:
                pct = ((current_price - float(start_price)) / float(start_price)) * 100

            payload = {
                "date": date_str,
                "symbol": symbol,
                "time_bucket": time_bucket,
                "price": round(current_price, 2),
                "pct": round(pct, 2)
            }
            
            post_res = requests.post(f"{GAS_BASE_URL}?action=postCollect", json=payload, timeout=10)
            
            if post_res.status_code == 200:
                msg = post_res.json().get("status")
                if msg == "ok":
                    logger.info(f"COLLECT_OK | {symbol} | {time_bucket} | P:{payload['price']} | %:{payload['pct']}")
            
        except Exception as e:
            logger.error(f"ERR_SYMBOL | {symbol} | {e}")
            continue

scheduler = BackgroundScheduler(timezone=TR_TZ)
scheduler.add_job(collect_job, 'interval', minutes=5)

@asynccontextmanager
async def lifespan(app: FastAPI):
    if not scheduler.running:
        scheduler.start()
    yield
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)

@app.get("/health")
def health():
    now = get_now()
    return {
        "status": "healthy",
        "tr_time": now.strftime("%H:%M:%S"),
        "force_now": FORCE_NOW is not None
    }
