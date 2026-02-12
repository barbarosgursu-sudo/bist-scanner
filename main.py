import yfinance as yf
from datetime import datetime
import pytz
import requests

# ==========================
# CONFIG
# ==========================

TEST_MODE = True          # True → hemen çalışır
RUN_HOUR = 11
RUN_MINUTE = 15

GAS_ENDPOINT = "https://script.google.com/macros/s/AKfycbzyB7tswjwRhLiR7OWI95VtbKrUmMFYnAg9dKwn19jbtyYtZOS3AUy5ob_XCWJQML3r/exec"

ISTANBUL_TZ = pytz.timezone("Europe/Istanbul")

SYMBOLS = [
    "A1CAP.IS",
    "A1YEN.IS",
    "ACSEL.IS",
    "ADEL.IS",
    "ADESE.IS"
]

# ==========================
# MAIN LOGIC
# ==========================

def should_run_now(now):
    if TEST_MODE:
        return True
    return now.hour == RUN_HOUR and now.minute >= RUN_MINUTE


def fetch_snapshot():
    now = datetime.now(ISTANBUL_TZ)
    today_date = now.date()

    results = []

    for symbol in SYMBOLS:
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1d")
            meta = ticker.history_metadata
            market_unix_time = meta.get("regularMarketTime")

            if hist.empty or market_unix_time is None:
                continue

            market_dt = datetime.fromtimestamp(market_unix_time, ISTANBUL_TZ)

            if market_dt.date() != today_date:
                continue

            open_p = float(hist['Open'].iloc[0])
            high_p = float(hist['High'].iloc[0])
            low_p = float(hist['Low'].iloc[0])
            last_p = float(hist['Close'].iloc[-1])

            results.append({
                "symbol": symbol,
                "open": open_p,
                "high": high_p,
                "low": low_p,
                "last": last_p,
                "market_time": market_dt.strftime("%H:%M:%S"),
                "checked_at": now.strftime("%H:%M:%S")
            })

        except Exception:
            pass  # Sessiz geç

    return {
        "date": str(today_date),
        "data": results
    }


def send_to_gas(payload):
    try:
        response = requests.post(GAS_ENDPOINT, json=payload, timeout=30)
        print("GAS RESPONSE:", response.text)
    except Exception as e:
        print("POST HATA:", str(e))


def main():
    now = datetime.now(ISTANBUL_TZ)

    if not should_run_now(now):
        return

    print("Snapshot alınıyor...")

    payload = fetch_snapshot()
    count = len(payload["data"])

    print(f"{count} hisse alındı.")

    if count > 0:
        send_to_gas(payload)


if __name__ == "__main__":
    main()
