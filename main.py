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
HIT_MINUS_7 = False  
FINAL_CANDIDATE = False 
FINAL_CHECK_DONE = False  # Adım 5: Nihai kontrolün yapılıp yapılmadığını kilitler

# Loglama Ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_time_window():
    global START_PRICE, PRICE_HISTORY, HIT_MINUS_7, FINAL_CANDIDATE, FINAL_CHECK_DONE
    
    # 1. ZAMAN TESPİTİ
    if TEST_MODE:
        # Test Modu: 10:15 simülasyonu (Adım 3-4 akışı korunur)
        now = datetime(2026, 2, 6, 10, 15, tzinfo=tr_tz)
        logger.info("MODE: TEST")
    else:
        # Prod Modu: Gerçek Türkiye saati
        now = datetime.now(tr_tz)
        logger.info("MODE: PROD")

    current_hour = now.hour
    
    # 2. VERİ TOPLAMA PENCERESİ (10:00 - 11:00)
    if 10 <= current_hour < 11:
        try:
            hisse = yf.Ticker(SYMBOL)
            current_price = hisse.fast_info['last_price']
            current_time = now.strftime('%H:%M')

            if START_PRICE is None:
                START_PRICE = current_price
                logger.info(f"START_PRICE_SET | symbol={SYMBOL} | price={START_PRICE:.2f} | time={current_time}")

            PRICE_HISTORY.append({"time": current_time, "price": round(current_price, 2)})
            logger.info(f"PRICE_COLLECTED | symbol={SYMBOL} | price={current_price:.2f} | time={current_time}")

            if START_PRICE and START_PRICE > 0:
                change_pct = ((current_price - START_PRICE) / START_PRICE) * 100
                if change_pct <= -7 and not HIT_MINUS_7:
                    HIT_MINUS_7 = True
                    logger.info(f"HIT_MINUS_7_DETECTED | symbol={SYMBOL} | price={current_price:.2f} | time={current_time} | pct={change_pct:.2f}%")
            
        except Exception as e:
            logger.error(f"Veri toplama hatası: {e}")

    # 3. NİHAİ ADAY KONTROLÜ (Saat 11:00 ve sonrası - SADECE TEK SEFERLİK)
    elif current_hour >= 11 and not FINAL_CHECK_DONE:
        if PRICE_HISTORY and START_PRICE:
            last_entry = PRICE_HISTORY[-1]
            last_price = last_entry["price"]
            last_pct = ((last_price - START_PRICE) / START_PRICE) * 100
            
            # Şartlar sağlanıyorsa aday olarak işaretle
            if HIT_MINUS_7 and last_pct > -7:
                FINAL_CANDIDATE = True
                logger.info(f"FINAL_CANDIDATE_DETECTED | symbol={SYMBOL} | last_price={last_price:.2f} | pct={last_pct:.2f}%")
        
        # Kontrol yapıldı, artık bu blok bir daha çalışmayacak
        FINAL_CHECK_DONE = True
        logger.info(f"STATUS: final_check_completed | TR Saati: {now.strftime('%H:%M:%S')}")
    
    else:
        # 11:00 sonrası sonraki tetiklemelerde sadece durumu bildirir
        logger.info(f"STATUS: monitoring_ended | TR Saati: {now.strftime('%H:%M:%S')}")

# APScheduler Kurulumu (5 Dakika)
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
    return {
        "status": "healthy", 
        "hit_minus_7": HIT_MINUS_7, 
        "final_candidate": FINAL_CANDIDATE,
        "final_check_done": FINAL_CHECK_DONE
    }

@app.get("/")
def root():
    return {"message": "T4-Scanner is running", "test_mode": TEST_MODE}
