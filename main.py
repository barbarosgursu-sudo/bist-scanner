import yfinance as yf
from datetime import datetime, timedelta
import pytz

# --- KONFİGÜRASYON ---
TEST_SYMBOLS = ["A1CAP.IS", "A1YEN.IS", "ACSEL.IS", "ADEL.IS", "ADESE.IS"]
ISTANBUL_TZ = pytz.timezone("Europe/Istanbul")

def run_v1_locked():
    now = datetime.now(ISTANBUL_TZ)
    today_date = now.date()
    
    # Bir sonraki 5 dakikalık tetiklemeyi hesapla
    next_minute = 5 - (now.minute % 5)
    next_trigger = (now + timedelta(minutes=next_minute)).replace(second=0, microsecond=0)
    
    print(f"\n--- BIS VALIDATION RUN: {now.strftime('%Y-%m-%d %H:%M:%S')} ---")
    print(f"BİR SONRAKİ TETİKLEME ZAMANI: {next_trigger.strftime('%H:%M:%S')}")
    print("-" * 32)

    for symbol in TEST_SYMBOLS:
        try:
            ticker = yf.Ticker(symbol)
            # Metadata'nın güncellenmesi için yfinance'i tetikle (V1 kurallarını bozmaz)
            _ = ticker.history(period="1d") 
            
            # KESİN TALİMAT: Sadece metadata
            meta = ticker.history_metadata
            
            reg_open = meta.get("regularMarketOpen")
            reg_high = meta.get("regularMarketDayHigh")  # Günün En Yükseği
            reg_low = meta.get("regularMarketDayLow")    # Günün En Düşüğü
            reg_price = meta.get("regularMarketPrice")   # Son Fiyat
            reg_time = meta.get("regularMarketTime")
            tz_name = meta.get("exchangeTimezoneName")

            # V1 KATI ŞARTLAR (Açılış fiyatı yoksa veya tarih yanlışsa geç)
            if reg_open is None or reg_open <= 0 or tz_name != "Europe/Istanbul":
                print(f"SYMBOL: {symbol}\nSTATUS: WAITING_FOR_DATA_OR_CLOSED\n" + "-"*32)
                continue

            # Tarih Doğrulaması
            dt_ist = datetime.fromtimestamp(reg_time, ISTANBUL_TZ)
            if dt_ist.date() != today_date:
                print(f"SYMBOL: {symbol}\nSTATUS: STALE_DATA (Eski Tarih: {dt_ist.date()})\n" + "-"*32)
                continue

            # BAŞARILI LOG (Tüm veriler tek seferde)
            print(f"SYMBOL: {symbol}")
            print(f"OPEN (Açılış): {reg_open}")
            print(f"HIGH (En Yüksek): {reg_high}")
            print(f"LOW (En Düşük): {reg_low}")
            print(f"LAST (Son Fiyat): {reg_price}")
            print(f"MARKET_TIME_IST: {dt_ist.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"TIMEZONE: {tz_name}")
            print("-" * 32)

        except Exception:
            print(f"SYMBOL: {symbol}\nSTATUS: ERROR\n" + "-"*32)

if __name__ == "__main__":
    run_v1_locked()
