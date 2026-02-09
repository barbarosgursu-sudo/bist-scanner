import os
import logging
import pytz
import yfinance as yf
import requests
from datetime import datetime
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from contextlib import asynccontextmanager

GAS_BASE_URL = "https://script.google.com/macros/s/AKfycbwGYHsm-3umHvyP9aZv1GQV-N1-vv3I91AHVbrucgGCPv79-YTcru_7PV-4b2b80hnz/exec"
TR_TZ = pytz.timezone("Europe/Istanbul")
BATCH_SIZE = 50

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def get_force_now_str():
    return os.getenv("FORCE_NOW")


def get_now():
    force_now = get_force_now_str()
    if force_now:
        naive = datetime.strptime(force_now, "%Y-%m-%d %H:%M")
        return TR_TZ.localize(naive)
    return datetime.now(TR_TZ)


def get_time_bucket(dt):
    minute = (dt.minute // 5) * 5
    return dt.replace(minute=minute, second=0, microsecond=0).strftime("%H:%M")


def collect_job():
    now = get_now()

    # 10:01–10:59
    if not (now.hour == 10 and 1 <= now.minute <= 59):
        return

    date_str = now.strftime("%Y-%m-%d")
    time_bucket = get_time_bucket(now)

    try:
        symbols = requests.get(
            f"{GAS_BASE_URL}?action=getSymbols",
            timeout=15
        ).json().get("symbols", [])

        start_prices = requests.get(
            f"{GAS_BASE_URL}?action=getStartPrices&date={date_str}",
            timeout=15
        ).json()
    except Exception as e:
        logger.error(f"INIT_DATA_ERR: {e}")
        return

    if not symbols:
        return

    for i in range(0, len(symbols), BATCH_SIZE):
        batch = symbols[i:i + BATCH_SIZE]

        try:
            data = yf.download(
                batch,
                period="1d",
                interval="1m",
                progress=False,
                threads=True
            )

            if data.empty:
                continue

            rows = []

            for symbol in batch:
                try:
                    price_val = (
                        data["Close"][symbol].iloc[-1]
                        if len(batch) > 1
                        else data["Close"].iloc[-1]
                    )

                    if price_val is None or str(price_val) == "nan":
                        continue

                    price = round(float(price_val), 2)
                    open_price = start_prices.get(symbol)

                    pct = None
                    if open_price is not None:
                        pct = round(
                            ((price - float(open_price)) / float(open_price)) * 100,
                            2
                        )

                    rows.append([symbol, price, pct])
                except Exception:
                    continue

            if rows:
                payload = {
                    "date": date_str,
                    "time_bucket": time_bucket,
                    "rows": rows
                }
                requests.post(
                    f"{GAS_BASE_URL}?action=postCollectBatch",
                    json=payload,
                    timeout=20
                )
                logger.info(f"COLLECT_BATCH_SENT: {len(rows)} | {time_bucket}")

        except Exception as e:
            logger.error(f"BATCH_ERR: {i} | {e}")


def finalize_job():
    now = get_now()
    if now.hour < 11:
        return

    date_str = now.strftime("%Y-%m-%d")

    try:
        requests.post(
            f"{GAS_BASE_URL}?action=postFinalize",
            json={"date": date_str},
            timeout=30
        )
        logger.info(f"FINALIZE_SENT: {date_str}")
    except Exception as e:
        logger.error(f"FINALIZE_ERR: {e}")


scheduler = BackgroundScheduler(timezone=TR_TZ)
scheduler.add_job(collect_job, "interval", minutes=5)
scheduler.add_job(finalize_job, "interval", minutes=5)


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
        "force_now": get_force_now_str()
    }
