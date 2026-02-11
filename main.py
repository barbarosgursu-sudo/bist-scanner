import yfinance as yf
from datetime import datetime
import pytz

# --- YAPILANDIRMA ---
TEST_SYMBOLS = ["A1CAP.IS", "A1YEN.IS", "ACSEL.IS", "ADEL.IS", "ADESE.IS"]
ISTANBUL_TZ = pytz.timezone("Europe/Istanbul")

def run_metadata_test():
    today_date = datetime.now(ISTANBUL_TZ).date()
    
    print(f"\n--- TEST BAŞLATILDI: {datetime.now(ISTANBUL_TZ).strftime('%Y-%m-%d %H:%M:%S')} ---")

    for symbol in TEST_SYMBOLS:
        try:
            ticker = yf.Ticker(symbol)
            # KESİN TALİMAT: Sadece history_metadata kullanılıyor.
            metadata = ticker.history_metadata
            
            reg_open = metadata.get("regularMarketOpen")
            reg_time_epoch = metadata.get("regularMarketTime")
            tz_name = metadata.get("exchangeTimezoneName")

            # --- V1 KATI DOĞRULAMA ---
            if reg_open is None or reg_open <= 0 or tz_name != "Europe/Istanbul":
                print(f"SYMBOL: {symbol}\nMETADATA_INVALID (Fiyat veya TZ Hatalı)")
                print("-" * 32)
                continue

            # Tarih Kontrolü (Bugün değilse yazma)
            reg_dt = datetime.fromtimestamp(reg_time_epoch, ISTANBUL_TZ)
            if reg_dt.date() != today_date:
                print(f"SYMBOL: {symbol}\nSTALE_DATA (Veri henüz bugüne güncellenmemiş)")
                print("-" * 32)
                continue

            # --- TÜM ŞARTLAR OK -> LOG ---
            print(f"SYMBOL: {symbol}")
            print(f"OPEN: {reg_open}")
            print(f"MARKET_TIME_EPOCH: {reg_time_epoch}")
            print(f"MARKET_TIME_IST: {reg_dt.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"TIMEZONE: {tz_name}")
            print("-" * 32)

        except Exception as e:
            print(f"SYMBOL: {symbol}\nERROR: {str(e)}")
            print("-" * 32)

if __name__ == "__main__":
    run_metadata_test()
