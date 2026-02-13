function runFilter(date) {
  const ss = SpreadsheetApp.getActive();
  const rawSheet = ss.getSheetByName("raw_snapshot");
  const resultSheet = ss.getSheetByName("daily_results");

  // --- DEBUG START ---
  writeLog("FILTER_START", "OK", "Filter started for date=" + date, 0, 0);

  let thresholdRaw;
  let threshold;
  try {
    thresholdRaw = getConfigValue("THRESHOLD");
    threshold = toNumber_(thresholdRaw);
  } catch (e) {
    writeLog("FILTER_CONFIG_ERROR", "ERROR", String(e), 0, 0);
    return 0;
  }

  writeLog(
    "FILTER_CONFIG",
    isNaN(threshold) ? "ERROR" : "OK",
    "THRESHOLD raw=" + thresholdRaw + " parsed=" + threshold,
    0,
    0
  );

  const data = rawSheet.getDataRange().getValues();
  if (!data || data.length < 2) {
    writeLog("FILTER_NO_DATA", "OK", "raw_snapshot empty", 0, 0);
    return 0;
  }

  const rows = data.slice(1);
  writeLog("FILTER_RAW_ROWS", "OK", "raw rows=" + rows.length, rows.length, 0);
  // --- DEBUG END ---

  const output = [];

  // Sadece ilk 15 satırı detay logla (log şişmesin)
  let debugLogged = 0;
  const DEBUG_LIMIT = 15;

  rows.forEach((r, idx) => {
    // r: [date, symbol, open, high, low, last, market_time, checked_at]
    const rowDate = Utilities.formatDate(new Date(r[0]), Session.getScriptTimeZone(), "yyyy-MM-dd");
    if (rowDate !== date) return;

    const symbol = r[1];
    const open = toNumber_(r[2]);
    const low = toNumber_(r[4]);
    const last = toNumber_(r[5]);

    if (isNaN(open) || isNaN(low) || isNaN(last) || open === 0) {
      if (debugLogged < DEBUG_LIMIT) {
        writeLog(
          "FILTER_ROW_NAN",
          "ERROR",
          "idx=" + idx +
            " symbol=" + symbol +
            " open=" + r[2] + "->" + open +
            " low=" + r[4] + "->" + low +
            " last=" + r[5] + "->" + last,
          1,
          0
        );
        debugLogged++;
      }
      return;
    }

    const pctLow = ((low - open) / open) * 100;
    const pctLast = ((last - open) / open) * 100;

    const pass = (pctLow <= threshold) && (pctLast > threshold);

    if (debugLogged < DEBUG_LIMIT) {
      writeLog(
        "FILTER_ROW",
        pass ? "PASS" : "FAIL",
        "idx=" + idx +
          " symbol=" + symbol +
          " open=" + open.toFixed(4) +
          " low=" + low.toFixed(4) +
          " last=" + last.toFixed(4) +
          " pctLow=" + pctLow.toFixed(4) +
          " pctLast=" + pctLast.toFixed(4) +
          " thr=" + threshold,
        1,
        pass ? 1 : 0
      );
      debugLogged++;
    }

    if (pass) {
      output.push([
        date,
        symbol,
        open,
        low,
        last,
        pctLow,    // Index 5 (pct_low)
        pctLast,   // Index 6 (pct_last)
        threshold,
        "'" + r[6] // market_time
      ]);
    }
  });

  // --- KRİTİK GÜNCELLEME: pct_low Değerine Göre Sıralama (Index 5) ---
  if (output.length > 0) {
    // Küçükten büyüğe (-8, -6, -4 şeklinde gider)
    output.sort((a, b) => a[5] - b[5]); 
  }

  // Verileri tabloya yazdır
  if (output.length > 0) {
    resultSheet.getRange(resultSheet.getLastRow() + 1, 1, output.length, output[0].length)
      .setValues(output);
  }

  writeLog(
    "FILTER_DONE",
    "OK",
    "done. passed=" + output.length,
    rows.length,
    output.length
  );

  return output.length;
}
