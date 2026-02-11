import yfinance as yf
from datetime import datetime, timedelta
import pytz
import time

# --- KONFİGÜRASYON ---
TEST_SYMBOLS = ["A1CAP.IS", "A1YEN.IS", "ACSEL.IS", "ADEL.IS", "ADESE.IS"]
ISTANBUL_TZ = pytz.timezone("Europe/Istanbul")

def run_v1_locked():
    while True:  # Sonsuz döngü: Script hep uyanık kalır
        now = datetime.now(ISTANBUL_TZ)
        today_date = now.date()
        
        # Bir sonraki tetiklemeyi hesapla (Görsel takip için)
        next_trigger = now + timedelta(minutes=5)
        
        print(f"\n--- BIS VALIDATION RUN: {now.strftime('%Y-%m-%d %H:%M:%S')} ---")
        print(f"BİR SONRAKİ ÇALIŞMA: {next_trigger.strftime('%H:%M:%S')}")
        print("-" * 32)

        for symbol in TEST_SYMBOLS:
            try:
                ticker = yf.Ticker(symbol)
                _ = ticker.history(period="1d") 
                meta = ticker.history_metadata
                
                reg_open = meta.get("regularMarketOpen")
                reg_high = meta.get("regularMarketDayHigh")
                reg_low = meta.get("regularMarketDayLow")
                reg_price = meta.get("regularMarketPrice")
                reg_time = meta.get("regularMarketTime")
                tz_name = meta.get("exchangeTimezoneName")  # Zaman dilimi bilgisi

                if reg_open is None or reg_open <= 0 or tz_name != "Europe/Istanbul":
                    print(f"SYMBOL: {symbol} | STATUS: WAITING_FOR_DATA_OR_CLOSED")
                    continue

                dt_ist = datetime.fromtimestamp(reg_time, ISTANBUL_TZ)
                if dt_ist.date() != today_date:
                    print(f"SYMBOL: {symbol} | STATUS: STALE_DATA (Eski Tarih: {dt_ist.date()})")
                    continue

                # İstediğin tüm bilgiler tek satırda:
                print(f"SYMBOL: {symbol} | OPEN: {reg_open} | HIGH: {reg_high} | LOW: {reg_low} | LAST: {reg_price} | TZ: {tz_name}")

            except Exception:
                print(f"SYMBOL: {symbol} | STATUS: ERROR")

        print("\n" + "="*40)
        print("5 DAKİKA BEKLENİYOR...")
        print("="*40)
        
        time.sleep(300)  # 5 dakika uyu ve döngüyü başa sar

if __name__ == "__main__":
    run_v1_locked()
