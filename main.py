import yfinance as yf
from datetime import datetime, timedelta
import pytz
import time

# --- KONFİGÜRASYON ---
TEST_SYMBOLS = ["A1CAP.IS", "A1YEN.IS", "ACSEL.IS", "ADEL.IS", "ADESE.IS"]
ISTANBUL_TZ = pytz.timezone("Europe/Istanbul")

def run_v1_direct_open():
    while True:
        now = datetime.now(ISTANBUL_TZ)
        today_date = now.date()
        
        print(f"\n--- BIST OPEN CHECK: {now.strftime('%H:%M:%S')} ---")

        for symbol in TEST_SYMBOLS:
            try:
                ticker = yf.Ticker(symbol)
                # '1d' periyodu o günün açılışını içeren ilk satırı getirir
                hist = ticker.history(period="1d")
                
                # Eğer tablo boşsa Yahoo henüz bugünün verisini API'ye açmamıştır
                if hist.empty:
                    print(f"SYMBOL: {symbol} | STATUS: WAITING (Yahoo API henüz veri akışını başlatmadı)")
                    continue

                # Tablodaki İLK satırın 'Open' değeri o günün gerçek açılış fiyatıdır.
                reg_open = hist['Open'].iloc[0]
                
                # Tarih kontrolü: Tablodaki ilk satır bugüne mi ait?
                if hist.index[0].date() != today_date:
                    print(f"SYMBOL: {symbol} | STATUS: STALE (Veri hala düne ait: {hist.index[0].date()})")
                    continue

                # BAŞARILI LOG
                print(f"SYMBOL: {symbol} | AÇILIŞ: {reg_open:.2f} | SAAT: {hist.index[0].strftime('%H:%M:%S')}")

            except Exception as e:
                print(f"SYMBOL: {symbol} | HATA: {str(e)}")

        print("-" * 40)
        print("5 DAKİKA BEKLENİYOR...")
        time.sleep(300)

if __name__ == "__main__":
    run_v1_direct_open()
