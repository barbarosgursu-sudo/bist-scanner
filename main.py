import yfinance as yf
from datetime import datetime
import pytz

# --- KONFİGÜRASYON ---
TEST_SYMBOLS = ["A1CAP.IS", "A1YEN.IS", "ACSEL.IS", "ADEL.IS", "ADESE.IS"]
ISTANBUL_TZ = pytz.timezone("Europe/Istanbul")

def run_v1_locked():
    today_date = datetime.now(ISTANBUL_TZ).date()
    print(f"\n--- BIS VALIDATION RUN: {datetime.now(ISTANBUL_TZ).strftime('%Y-%m-%d %H:%M:%S')} ---")

    for symbol in TEST_SYMBOLS:
        try:
            ticker = yf.Ticker(symbol)
            # Metadata'nın güncellenmesi için yfinance'i tetikle (V1 kurallarını bozmaz)
            _ = ticker.history(period="1d") 
            
            # KESİN TALİMAT: Sadece metadata
            meta = ticker.history_metadata
            
            reg_open = meta.get("regularMarketOpen")
            reg_time = meta.get("regularMarketTime")
            tz_name = meta.get("exchangeTimezoneName")

            # V1 KATI ŞARTLAR
            if reg_open is None or reg_open <= 0 or tz_name != "Europe/Istanbul":
                print(f"SYMBOL: {symbol}\nSTATUS: WAITING_FOR_DATA_OR_CLOSED\n" + "-"*32)
                continue

            # Tarih Doğrulaması
            dt_ist = datetime.fromtimestamp(reg_time, ISTANBUL_TZ)
            if dt_ist.date() != today_date:
                print(f"SYMBOL: {symbol}\nSTATUS: STALE_DATA (Eski Tarih: {dt_ist.date()})\n" + "-"*32)
                continue

            # BAŞARILI LOG
            print(f"SYMBOL: {symbol}")
            print(f"OPEN: {reg_open}")
            print(f"MARKET_TIME_IST: {dt_ist.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"TIMEZONE: {tz_name}")
            print("-" * 32)

        except Exception:
            print(f"SYMBOL: {symbol}\nSTATUS: ERROR\n" + "-"*32)

if __name__ == "__main__":
    run_v1_locked()
