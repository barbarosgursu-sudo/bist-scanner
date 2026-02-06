import logging
import pytz
from datetime import datetime
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from contextlib import asynccontextmanager

# Türkiye Zaman Dilimi Ayarı
tr_tz = pytz.timezone('Europe/Istanbul')

# Loglama Ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_time_window():
    # Saati direkt Türkiye saatine göre alıyoruz
    now = datetime.now(tr_tz)
    current_hour = now.hour
    
    # 10:00 - 11:00 arası kontrolü
    if 10 <= current_hour < 11:
        logger.info(f"STATUS: active | Türkiye Saati: {now.strftime('%H:%M:%S')}")
    else:
        logger.info(f"STATUS: inactive | Türkiye Saati: {now.strftime('%H:%M:%S')}")

# APScheduler Kurulumu
scheduler = BackgroundScheduler(timezone=tr_tz)
scheduler.add_job(check_time_window, 'interval', minutes=1)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Uygulama TR saatiyle başlatılıyor...")
    if not scheduler.running:
        scheduler.start()
    yield
    logger.info("Uygulama kapatılıyor...")
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now(tr_tz).isoformat()}

@app.get("/")
def root():
    return {"message": "T4-Skeleton TR Timezone active."}
