import logging
import pytz
import yfinance as yf
from datetime import datetime
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from contextlib import asynccontextmanager

# --- AYARLAR ---
TEST_MODE = True  
SYMBOL = "THYAO.IS"
tr_tz = pytz.timezone('Europe/Istanbul')

# --- BELLEK (MEMORY) ---
START_PRICE = None
PRICE_HISTORY = [] 

# Loglama Ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_time_window():
    global START_PRICE, PRICE_HISTORY
    
    # 1. ZAMAN TESPİTİ
    if TEST_MODE:
        now = datetime(2026, 2, 6, 10, 15, tzinfo=tr_tz)
        logger.info("MODE: TEST")
    else:
        now = datetime.now(tr_tz)
        logger.info("MODE: PROD")

    current_hour = now.hour
    
    # 2. ANA MANTIK (10:00 - 11:00)
    if 10 <= current_hour < 11:
        try:
            hisse = yf.Ticker(SYMBOL)
            current_price = hisse.fast_info['last_price']
            current_time = now.strftime('%H:%M')

            # A) Başlangıç Fiyatı Kontrolü
            if START_PRICE is None:
                START_PRICE = current_price
                logger.info(f"START_PRICE_SET | symbol={SYMBOL} | price={START_PRICE:.2f} | time={current_time}")

            # B) Fiyat Biriktirme
            data_point = {
                "time": current_time,
                "price": round(current_price, 2)
            }
            PRICE_HISTORY.append(data_point)
            
            logger.info(f"PRICE_COLLECTED | symbol={SYMBOL} | price={current_price:.2f} | time={current_time}")
            logger.info(f"HISTORY_SIZE: {len(PRICE_HISTORY)}")
            
        except Exception as e:
            logger.error(f"Veri toplama hatası: {e}")
    else:
        logger.info(f"STATUS: inactive | TR Saati: {now.strftime('%H:%M:%S')}")

# APScheduler Kurulumu - 5 DAKİKA OLARAK GÜNCELLENDİ
scheduler = BackgroundScheduler(timezone=tr_tz)
scheduler.add_job(check_time_window, 'interval', minutes=5)

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
