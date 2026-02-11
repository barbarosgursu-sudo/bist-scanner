import yfinance as yf
from datetime import datetime
import pytz
import json

TEST_SYMBOLS = ["A1CAP.IS", "ACSEL.IS", "A1YEN.IS", "ADEL.IS", "ADESE.IS"]
ISTANBUL_TZ = pytz.timezone("Europe/Istanbul")

def debug_metadata():
    print(f"\n--- DEBUG BAŞLATILDI: {datetime.now(ISTANBUL_TZ)} ---")

    for symbol in TEST_SYMBOLS:
        try:
            ticker = yf.Ticker(symbol)
            meta = ticker.history_metadata
            
            # Ham veriyi görelim
            print(f"SYMBOL: {symbol}")
            print(f"RAW_OPEN: {meta.get('regularMarketOpen')}")
            print(f"RAW_TZ: {meta.get('exchangeTimezoneName')}")
            print(f"RAW_TIME: {meta.get('regularMarketTime')}")
            
            # Eğer tarih varsa onu da yazalım
            if meta.get('regularMarketTime'):
                dt = datetime.fromtimestamp(meta.get('regularMarketTime'), ISTANBUL_TZ)
                print(f"RAW_DATE_IN_IST: {dt.date()}")

            print("-" * 20)
            
        except Exception as e:
            print(f"SYMBOL: {symbol} | ERROR: {str(e)}")

if __name__ == "__main__":
    debug_metadata()
