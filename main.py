import yfinance as yf
from datetime import datetime
import pytz
import time

# --- TEST YAPILANDIRMASI ---
TEST_SYMBOLS = ["A1CAP.IS", "A1YEN.IS", "ACSEL.IS", "ADEL.IS", "ADESE.IS"]
ISTANBUL_TZ = pytz.timezone("Europe/Istanbul")

def run_v1_timestamp_check():
    while True:
        now = datetime.now(ISTANBUL_TZ)
        today_date = now.date()
        
        print(f"\n--- ZAMAN DAMGALI VERİ KONTROLÜ: {now.strftime('%H:%M:%S')} ---")

        for symbol in TEST_SYMBOLS:
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="1d")
                
                # Yahoo'nun veriyi paketlediği gerçek zaman damgasını alıyoruz
                meta = ticker.history_metadata
                market_unix_time = meta.get("regularMarketTime")
                
                if hist.empty or market_unix_time is None:
                    print(f"SYMBOL: {symbol} | STATUS: WAITING (Veri henüz hazır değil)")
                    continue

                # Unix zamanını İstanbul saatine çeviriyoruz
                market_dt = datetime.fromtimestamp(market_unix_time, ISTANBUL_TZ)
                
                # Tarih Kilidi: Sadece bugünün verisiyse işle
                if market_dt.date() != today_date:
                    print(f"SYMBOL: {symbol} | STATUS: STALE (Yahoo hala dünü gösteriyor)")
                    continue

                # Verileri çekiyoruz
                open_p = hist['Open'].iloc[0]
                high_p = hist['High'].iloc[0]
                low_p = hist['Low'].iloc[0]
                last_p = hist['Close'].iloc[-1]

                # LOG FORMATI: Market Time (Gecikmeli) ve Run Time (Şu an)
                print(f"SYMBOL: {symbol} | OPEN: {open_p:.2f} | HIGH: {high_p:.2f} | LOW: {low_p:.2f} | LAST: {last_p:.2f} | "
                      f"MARKET TIME: {market_dt.strftime('%H:%M:%S')} | "
                      f"CHECKED AT: {now.strftime('%H:%M:%S')}")

            except Exception as e:
                print(f"SYMBOL: {symbol} | HATA: {str(e)}")

        print("-" * 60)
        print("5 DAKİKA BEKLENİYOR...")
        time.sleep(300)

if __name__ == "__main__":
    run_v1_timestamp_check()
