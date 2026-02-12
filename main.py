import yfinance as yf
from datetime import datetime, timedelta
import pytz
import time

# --- KONFİGÜRASYON ---
TEST_SYMBOLS = ["A1CAP.IS", "A1YEN.IS", "ACSEL.IS", "ADEL.IS", "ADESE.IS"]
ISTANBUL_TZ = pytz.timezone("Europe/Istanbul")

def run_v1_locked():
    while True:
        now = datetime.now(ISTANBUL_TZ)
        today_date = now.date()
        next_trigger = now + timedelta(minutes=5)
        
        print(f"\n--- BIS VALIDATION RUN: {now.strftime('%Y-%m-%d %H:%M:%S')} ---")
        print(f"BİR SONRAKİ ÇALIŞMA: {next_trigger.strftime('%H:%M:%S')}")
        print("-" * 32)

        for symbol in TEST_SYMBOLS:
            try:
                ticker = yf.Ticker(symbol)
                # TETİKLEYİCİ DEĞİŞTİ: 1d bazen boş döner, 2d Yahoo'yu veri göndermeye zorlar.
                # Bu bir yedek plan değil, veriyi getirme yöntemidir.
                _ = ticker.history(period="2d") 
                
                meta = ticker.history_metadata
                
                reg_open = meta.get("regularMarketOpen")
                reg_high = meta.get("regularMarketDayHigh")
                reg_low = meta.get("regularMarketDayLow")
                reg_price = meta.get("regularMarketPrice")
                reg_time = meta.get("regularMarketTime")
                tz_name = meta.get("exchangeTimezoneName")

                # ŞARTLARIMIZ AYNI: Eğer Yahoo hala 'None' gönderiyorsa beklemeye devam.
                if reg_open is None or reg_open <= 0:
                    print(f"SYMBOL: {symbol} | STATUS: WAITING_FOR_YAHOO_METADATA")
                    continue

                dt_ist = datetime.fromtimestamp(reg_time, ISTANBUL_TZ)
                
                # SADECE BUGÜNÜN VERİSİNE İZİN VER:
                if dt_ist.date() != today_date:
                    print(f"SYMBOL: {symbol} | STATUS: STALE_DATA (Yahoo hala dünü gösteriyor: {dt_ist.date()})")
                    continue

                print(f"SYMBOL: {symbol} | OPEN: {reg_open} | HIGH: {reg_high} | LOW: {reg_low} | LAST: {reg_price} | TIME: {dt_ist.strftime('%H:%M:%S')} | TZ: {tz_name}")

            except Exception as e:
                print(f"SYMBOL: {symbol} | ERROR: {str(e)}")

        print("\n" + "="*40)
        print("5 DAKİKA BEKLENİYOR...")
        print("="*40)
        
        time.sleep(300)

if __name__ == "__main__":
    run_v1_locked()
