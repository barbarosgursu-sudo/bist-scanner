import logging
from datetime import datetime
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from contextlib import async_contextmanager

# Loglama Ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_time_window():
    """Zaman penceresini kontrol eden ana mantık."""
    now = datetime.now()
    current_hour = now.hour
    
    # 10:00 - 11:00 arası kontrolü
    if 10 <= current_hour < 11:
        logger.info(f"STATUS: active | Current Time: {now.strftime('%H:%M:%S')}")
        # İleride veri toplama işlemleri buraya gelecek.
    else:
        logger.info(f"STATUS: inactive | Current Time: {now.strftime('%H:%M:%S')}")

# APScheduler Kurulumu
scheduler = BackgroundScheduler()
scheduler.add_job(check_time_window, 'interval', minutes=1) # Her dakika kontrol eder

@async_contextmanager
async def lifespan(app: FastAPI):
    # Uygulama başlarken çalışır
    logger.info("Uygulama başlatılıyor...")
    scheduler.start()
    yield
    # Uygulama kapanırken çalışır
    logger.info("Uygulama kapatılıyor...")
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)

@app.get("/health")
def health_check():
    """Railway ve monitoring servisleri için sağlık kontrolü."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/")
def root():
    return {"message": "Railway Python Skeleton is running."}
