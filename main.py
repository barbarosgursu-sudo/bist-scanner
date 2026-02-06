import logging
import pytz
import yfinance as yf
import requests
from datetime import datetime
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from contextlib import asynccontextmanager

# --- AYARLAR ---
TEST_MODE = True  
TEST_PHASE = "FINAL"  # "COLLECT" -> 10:15 simülasyonu | "FINAL" -> 11:01 simülasyonu
SYMBOL = "THYAO.IS"
tr_tz = pytz.timezone('Europe/Istanbul')
GAS_URL = "https://script.google.com/macros/s/AKfycbwa_Zxh9FWpMPG-Vr8oKq7lTv_ywYKV4nBDweR-oowMNu0gO89UmFee4Y2mandT7nBc/exec"

# --- BELLEK (MEMORY) / STATE ---
START_PRICE = None
PRICE_HISTORY = [] 
HIT_MINUS_7 = False  
FINAL_CANDIDATE = False 
FINAL_CHECK_DONE = False  
EXPORT_DONE = False

# Loglama Ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_time_window():
    global START_PRICE, PRICE_HISTORY, HIT_MINUS_7, FINAL_CANDIDATE, FINAL_CHECK_DONE, EXPORT_DONE
    
    # 1. ZAMAN TESPİTİ (TEST_MODE İÇİN FAZLI SİMÜLASYON)
    if TEST_MODE:
        if TEST_PHASE == "COLLECT":
            now = datetime(2026, 2, 6, 10, 15, tzinfo=tr_tz)
        elif TEST_PHASE == "FINAL":
            now = datetime(2026, 2, 6, 11, 1, tzinfo=tr_tz)
        logger.info(f"MODE: TEST | PHASE={TEST_PHASE}")
    else:
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

    # 3. NİHAİ ADAY KONTROLÜ (Saat 11:00 ve sonrası)
    elif current_hour >= 11:
        if not FINAL_CHECK_DONE:
            if PRICE_HISTORY and START_PRICE:
                last_entry = PRICE_HISTORY[-1]
                last_price = last_entry["price"]
                last_pct = ((last_price - START_PRICE) / START_PRICE) * 100
                
                if HIT_MINUS_7 and last_pct > -7:
                    FINAL_CANDIDATE = True
                    logger.info(f"FINAL_CANDIDATE_DETECTED | symbol={SYMBOL} | last_price={last_price:.2f} | pct={last_pct:.2f}%")
            
            FINAL_CHECK_DONE = True
            logger.info(f"STATUS: final_check_completed | TR Saati: {now.strftime('%H:%M:%S')}")

        # 4. GAS EXPORT (ADIM 10)
        if FINAL_CHECK_DONE and not EXPORT_DONE:
            try:
                payload = {
                    "date": now.strftime("%Y-%m-%d"),
                    "symbol": SYMBOL,
                    "start_price": START_PRICE,
                    "hit_minus_7": HIT_MINUS_7,
                    "final_candidate": FINAL_CANDIDATE,
                    "last_price": PRICE_HISTORY[-1]["price"] if PRICE_HISTORY else None,
                    "price_points": len(PRICE_HISTORY)
                }
                
                response = requests.post(GAS_URL, json=payload, timeout=15)
                
                if response.status_code == 200:
                    EXPORT_DONE = True
                    logger.info("EXPORT_DONE | GAS_WRITE_OK")
                else:
                    logger.warning(f"EXPORT_FAILED | HTTP_{response.status_code}")
                    
            except Exception as e:
                logger.error(f"EXPORT_ERROR | {e}")
    
    else:
        logger.info(f"STATUS: inactive | TR Saati: {now.strftime('%H:%M:%S')}")

# APScheduler Kurulumu (5 Dakika)
scheduler = BackgroundScheduler(timezone=tr_tz)
scheduler.add_job(check_time_window, 'interval', minutes=5)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Uygulama başlatılıyor (TEST_MODE={TEST_MODE}, PHASE={TEST_PHASE})...")
    if not scheduler.running:
        scheduler.start()
    yield
    logger.info("Uygulama kapatılıyor...")
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)

@app.get("/result")
def get_result():
    return {
        "symbol": SYMBOL,
        "start_price": START_PRICE,
        "hit_minus_7": HIT_MINUS_7,
        "final_candidate": FINAL_CANDIDATE,
        "final_check_done": FINAL_CHECK_DONE,
        "export_done": EXPORT_DONE,
        "last_price": PRICE_HISTORY[-1]["price"] if PRICE_HISTORY else None,
        "price_history_size": len(PRICE_HISTORY)
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "test_mode": TEST_MODE, "phase": TEST_PHASE, "export_done": EXPORT_DONE}

@app.get("/")
def root():
    return {"message": "T4-Scanner Core Engine with Phase Simulation Ready."}
