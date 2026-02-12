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
                # Web sitesiyle daha uyumlu olan Fast Info'yu kullanıyoruz
                f_info = ticker.fast_info 
                
                reg_open = f_info.get("open")
                reg_high = f_info.get("day_high")
                reg_low = f_info.get("day_low")
                reg_price = f_info.get("last_price")
                # Zaman damgası ve TZ için yine metadata'ya bakıyoruz
                meta = ticker.history_metadata
                tz_name = meta.get("exchangeTimezoneName")

                # ŞART: Eğer Yahoo hala 'None' gönderiyorsa (Web'de bile yoksa) beklemeye devam.
                if reg_open is None or reg_open <= 0:
                    print(f"SYMBOL: {symbol} | STATUS: WAITING_FOR_YAHOO_PRICE")
                    continue

                # Başarılı Log Formatı (Aynen korundu)
                print(f"SYMBOL: {symbol} | OPEN: {reg_open:.2f} | HIGH: {reg_high:.2f} | LOW: {reg_low:.2f} | LAST: {reg_price:.2f} | TIME: {now.strftime('%H:%M:%S')} | TZ: {tz_name}")

            except Exception as e:
                print(f"SYMBOL: {symbol} | ERROR: {str(e)}")

        print("\n" + "="*40)
        print("5 DAKİKA BEKLENİYOR...")
        print("="*40)
        
        time.sleep(300)

if __name__ == "__main__":
    run_v1_locked()
