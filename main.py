import yfinance as yf
from datetime import datetime, timedelta
import pytz
import time

# --- TEST YAPILANDIRMASI ---
# Sadece ilk 5 hisse üzerinde doğrulama yapıyoruz
TEST_SYMBOLS = ["A1CAP.IS", "A1YEN.IS", "ACSEL.IS", "ADEL.IS", "ADESE.IS"]
ISTANBUL_TZ = pytz.timezone("Europe/Istanbul")

def run_v1_full_data_test():
    while True:
        now = datetime.now(ISTANBUL_TZ)
        today_date = now.date()
        
        print(f"\n--- VERİ DOĞRULAMA (İLK 5 HİSSE): {now.strftime('%H:%M:%S')} ---")

        for symbol in TEST_SYMBOLS:
            try:
                # '1d' periyodu günün açılış, yüksek, düşük ve son fiyatını barındıran tabloyu getirir
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="1d")
                
                if hist.empty:
                    print(f"SYMBOL: {symbol} | STATUS: WAITING (Henüz tablo oluşmadı)")
                    continue

                # Tarih kontrolü (Sadece bugünün verisiyse işle)
                if hist.index[0].date() != today_date:
                    print(f"SYMBOL: {symbol} | STATUS: STALE (Dünün verisi: {hist.index[0].date()})")
                    continue

                # Verileri tablodan söküp alıyoruz
                open_p = hist['Open'].iloc[0]
                high_p = hist['High'].iloc[0]
                low_p = hist['Low'].iloc[0]
                last_p = hist['Close'].iloc[-1]
                data_time = now.strftime('%H:%M:%S') # Verinin çekildiği an

                # TEK SATIRDA TAM LİSTE
                print(f"SYMBOL: {symbol} | AÇILIŞ: {open_p:.2f} | YÜKSEK: {high_p:.2f} | DÜŞÜK: {low_p:.2f} | SON: {last_p:.2f} | SAAT: {data_time}")

            except Exception as e:
                print(f"SYMBOL: {symbol} | HATA: {str(e)}")

        print("-" * 50)
        print("5 DAKİKA SONRA YENİDEN KONTROL EDİLECEK...")
        time.sleep(300)

if __name__ == "__main__":
    run_v1_full_data_test()
