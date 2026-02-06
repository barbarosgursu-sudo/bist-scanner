import logging
import pytz
import yfinance as yf
from datetime import datetime
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from contextlib import asynccontextmanager

# --- AYARLAR ---
TEST_MODE = False  # Test yapmak için True, canlı çalışma için False yapın
SYMBOL = "THYAO.IS"
tr_tz = pytz.timezone('Europe/Istanbul')

# --- BELLEK (MEMORY) ---
START_PRICE = None

# Loglama Ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_time_window():
    global START_PRICE
    
    # 1. ZAMAN TESPİTİ
    if TEST_MODE:
        # Test Modu: Sabit bir zaman simüle edilir (10:15)
        now = datetime(2026, 2, 6, 10, 15, tzinfo=tr_tz)
        logger.info("MODE: TEST")
    else:
        # Prod Modu: Gerçek Türkiye saati
        now = datetime.now(tr_tz)
        logger.info("MODE: PROD")

    current_hour = now.hour
    
    # 2. ANA MANTIK (ASLA DEĞİŞMEZ)
    if 10 <= current_hour < 11:
        if START_PRICE is None:
            try:
                hisse = yf.Ticker(SYMBOL)
                fiyat = hisse.fast_info['last_price']
                START_PRICE = fiyat
                logger.info(f"START_PRICE_SET | symbol={SYMBOL} | price={START_PRICE:.2f} | time={now.strftime('%H:%M')}")
            except Exception as e:
                logger.error(f"Başlangıç fiyatı hatası: {e}")
        else:
            logger.info(f"START_PRICE_ALREADY_SET | symbol={SYMBOL} | current_start_price={START_PRICE:.2f}")
    else:
        logger.info(f"STATUS: inactive | TR Saati: {now.strftime('%H:%M:%S')}")

# APScheduler Kurulumu
scheduler = BackgroundScheduler(timezone=tr_tz)
scheduler.add_job(check_time_window, 'interval', minutes=1)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Uygulama başlatılıyor (TEST_MODE={TEST_MODE})...")
    if not scheduler.running:
        scheduler.start()
    yield
    logger.info("Uygulama kapatılıyor...")
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)

@app.get("/health")
def health_check():
    return {"status": "healthy", "test_mode": TEST_MODE}

@app.get("/")
def root():
    return {"message": "T4-Scanner is running", "test_mode": TEST_MODE}
