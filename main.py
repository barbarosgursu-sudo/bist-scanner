import yfinance as yf
from datetime import datetime, timedelta
import pytz
import time  # Süre beklemek için eklendi

# --- KONFİGÜRASYON ---
TEST_SYMBOLS = ["A1CAP.IS", "A1YEN.IS", "ACSEL.IS", "ADEL.IS", "ADESE.IS"]
ISTANBUL_TZ = pytz.timezone("Europe/Istanbul")

def run_v1_locked():
    while True:  # SONSUZ DÖNGÜ: Script hiç kapanmaz
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
                tz_name = meta.get("exchangeTimezoneName")

                if reg_open is None or reg_open <= 0 or tz_name != "Europe/Istanbul":
                    print(f"SYMBOL: {symbol} | STATUS: WAITING_FOR_DATA_OR_CLOSED")
                    continue

                dt_ist = datetime.fromtimestamp(reg_time, ISTANBUL_TZ)
                if dt_ist.date() != today_date:
                    print(f"SYMBOL: {symbol} | STATUS: STALE_DATA (Eski Tarih: {dt_ist.date()})")
                    continue

                print(f"SYMBOL: {symbol} | OPEN: {reg_open} | HIGH: {reg_high} | LOW: {reg_low} | LAST: {reg_price}")

            except Exception:
                print(f"SYMBOL: {symbol} | STATUS: ERROR")

        print("\n" + "="*40)
        print("5 DAKİKA BEKLENİYOR...")
        print("="*40)
        
        time.sleep(300)  # 300 saniye (5 dakika) uyu ve başa dön

if __name__ == "__main__":
    run_v1_locked()
