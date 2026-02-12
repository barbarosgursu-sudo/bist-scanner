import yfinance as yf
from datetime import datetime
import pytz
import requests
import time
import math  # Boş değer kontrolü için eklendi
from concurrent.futures import ThreadPoolExecutor

# ==========================
# CONFIG
# ==========================
TEST_MODE = True           
RUN_HOUR = 11
RUN_MINUTE = 15

GAS_ENDPOINT = "https://script.google.com/macros/s/AKfycbzyB7tswjwRhLiR7OWI95VtbKrUmMFYnAg9dKwn19jbtyYtZOS3AUy5ob_XCWJQML3r/exec"
ISTANBUL_TZ = pytz.timezone("Europe/Istanbul")

# Sembol listesi aynı kalıyor...
SYMBOLS = [
    "A1CAP.IS","A1YEN.IS","ACSEL.IS","ADEL.IS","ADESE.IS","ADGYO.IS","AEFES.IS","AFYON.IS","AGESA.IS","AGHOL.IS",
    # ... (Listenin tamamı burada varsayılıyor)
]

# ==========================
# HELPER FUNCTIONS
# ==========================

def get_metadata_worker(symbol):
    try:
        ticker = yf.Ticker(symbol)
        m_time = ticker.history_metadata.get("regularMarketTime")
        if m_time:
            dt = datetime.fromtimestamp(m_time, ISTANBUL_TZ)
            return symbol, dt.strftime("%H:%M:%S")
    except:
        pass
    return symbol, None

def should_run_now(now):
    if TEST_MODE: return True
    return now.hour == RUN_HOUR and now.minute >= RUN_MINUTE

# ==========================
# MAIN LOGIC
# ==========================

def fetch_snapshot_precision():
    now = datetime.now(ISTANBUL_TZ)
    today_date = now.date()
    results = []

    try:
        print(f"[{now.strftime('%H:%M:%S')}] Fiyatlar indiriliyor...")
        all_data = yf.download(SYMBOLS, period="1d", group_by='ticker', threads=True, progress=False)

        print(f"[{now.strftime('%H:%M:%S')}] Zaman damgaları toplanıyor...")
        symbol_times = {}
        with ThreadPoolExecutor(max_workers=20) as executor:
            future_to_symbol = {executor.submit(get_metadata_worker, s): s for s in SYMBOLS}
            for future in future_to_symbol:
                sym, m_time_str = future.result()
                if m_time_str:
                    symbol_times[sym] = m_time_str

        if all_data.empty: return None

        for symbol in SYMBOLS:
            try:
                ticker_df = all_data[symbol] if len(SYMBOLS) > 1 else all_data
                if ticker_df.empty or ticker_df.index[0].date() != today_date:
                    continue

                # Fiyatları al
                open_p = ticker_df['Open'].iloc[0]
                high_p = ticker_df['High'].iloc[0]
                low_p = ticker_df['Low'].iloc[0]
                last_p = ticker_df['Close'].iloc[-1]

                # --- KRİTİK KONTROL: NaN (Boş Veri) Ayıklama ---
                # Eğer herhangi bir fiyat sayı değilse, bu hisseyi atla
                if any(math.isnan(x) for x in [open_p, high_p, low_p, last_p]):
                    continue

                market_time = symbol_times.get(symbol, now.strftime("%H:%M:%S"))

                results.append({
                    "symbol": symbol,
                    "open": float(open_p),
                    "high": float(high_p),
                    "low": float(low_p),
                    "last": float(last_p),
                    "market_time": market_time,
                    "checked_at": now.strftime("%H:%M:%S")
                })
            except:
                continue

    except Exception as e:
        print(f"GENEL HATA: {str(e)}")

    return {"date": str(today_date), "data": results}

def send_to_gas(payload):
    try:
        # JSON gönderimi öncesi son kontrol
        response = requests.post(GAS_ENDPOINT, json=payload, timeout=60)
        print("GAS RESPONSE:", response.text)
    except Exception as e:
        print("POST HATA:", str(e))

def main():
    while True:
        now = datetime.now(ISTANBUL_TZ)
        if should_run_now(now):
            print(f"\nİşlem başlatıldı: {now.strftime('%H:%M:%S')}")
            payload = fetch_snapshot_precision()
            if payload and payload["data"]:
                print(f"{len(payload['data'])} geçerli hisse GAS'a gönderiliyor...")
                send_to_gas(payload)
            
            if TEST_MODE:
                time.sleep(300)
            else:
                time.sleep(82800) 
        else:
            time.sleep(60)

if __name__ == "__main__":
    main()
