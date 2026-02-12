import yfinance as yf
from datetime import datetime, timedelta
import pytz
import time

# --- KONFİGÜRASYON ---
TEST_SYMBOLS = ["A1CAP.IS", "A1YEN.IS", "ACSEL.IS", "ADEL.IS", "ADESE.IS"]
ISTANBUL_TZ = pytz.timezone("Europe/Istanbul")

def run_v1_minimal():
    while True:
        now = datetime.now(ISTANBUL_TZ)
        today_date = now.date()
        
        print(f"\n--- BIST OPEN CHECK: {now.strftime('%H:%M:%S')} ---")

        for symbol in TEST_SYMBOLS:
            try:
                ticker = yf.Ticker(symbol)
                # Sadece metadata katmanına bakıyoruz
                meta = ticker.history_metadata
                
                reg_open = meta.get("regularMarketOpen")
                reg_time = meta.get("regularMarketTime")
                tz_name = meta.get("exchangeTimezoneName")

                # KONTROL 1: Veri geldi mi?
                if reg_open is None or reg_open <= 0:
                    print(f"SYMBOL: {symbol} | STATUS: WAITING (Açılış fiyatı henüz tescil edilmedi)")
                    continue

                # KONTROL 2: Gelen veri bugüne mi ait?
                dt_ist = datetime.fromtimestamp(reg_time, ISTANBUL_TZ)
                if dt_ist.date() != today_date:
                    print(f"SYMBOL: {symbol} | STATUS: STALE (Yahoo hala dünün verisini tutuyor)")
                    continue

                # BAŞARILI LOG: Sadece açılış fiyatı
                print(f"SYMBOL: {symbol} | AÇILIŞ: {reg_open} | SAAT: {dt_ist.strftime('%H:%M:%S')} | TZ: {tz_name}")

            except Exception as e:
                print(f"SYMBOL: {symbol} | HATA: {str(e)}")

        print("-" * 40)
        print("5 DAKİKA BEKLENİYOR...")
        time.sleep(300)

if __name__ == "__main__":
    run_v1_minimal()
