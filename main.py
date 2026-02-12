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
"A1CAP.IS","A1YEN.IS","ACSEL.IS","ADEL.IS","ADESE.IS","ADGYO.IS","AEFES.IS","AFYON.IS","AGESA.IS","AGHOL.IS","AGROT.IS","AGYO.IS","AHGAZ.IS","AHSGY.IS","AKBNK.IS","AKCNS.IS","AKENR.IS","AKFGY.IS","AKFIS.IS","AKFYE.IS","AKGRT.IS","AKHAN.IS","AKMGY.IS","AKSA.IS","AKSEN.IS","AKSGY.IS","AKSUE.IS","AKYHO.IS","ALARK.IS","ALBRK.IS","ALCAR.IS","ALCTL.IS","ALFAS.IS","ALGYO.IS","ALKA.IS","ALKIM.IS","ALKLC.IS","ALTNY.IS","ALVES.IS","ANELE.IS","ANGEN.IS","ANHYT.IS","ANSGR.IS","ARASE.IS","ARCLK.IS","ARDYZ.IS","ARENA.IS","ARFYE.IS","ARMGD.IS","ARSAN.IS","ARTMS.IS","ARZUM.IS","ASELS.IS","ASGYO.IS","ASTOR.IS","ASUZU.IS","ATAGY.IS","ATAKP.IS","ATATP.IS","ATEKS.IS","ATLAS.IS","ATSYH.IS","AVGYO.IS","AVHOL.IS","AVOD.IS","AVPGY.IS","AVTUR.IS","AYCES.IS","AYDEM.IS","AYEN.IS","AYES.IS","AYGAZ.IS","AZTEK.IS","BAGFS.IS","BAHKM.IS","BAKAB.IS","BALAT.IS","BALSU.IS","BANVT.IS","BARMA.IS","BASCM.IS","BASGZ.IS","BAYRK.IS","BEGYO.IS","BERA.IS","BESLR.IS","BEYAZ.IS","BFREN.IS","BIENY.IS","BIGCH.IS","BIGEN.IS","BIGTK.IS","BIMAS.IS","BINBN.IS","BINHO.IS","BIOEN.IS","BIZIM.IS","BJKAS.IS","BLCYT.IS","BLUME.IS","BMSCH.IS","BMSTL.IS","BNTAS.IS","BOBET.IS","BORLS.IS","BORSK.IS","BOSSA.IS","BRISA.IS","BRKO.IS","BRKSN.IS","BRKVY.IS","BRLSM.IS","BRMEN.IS","BRSAN.IS","BRYAT.IS","BSOKE.IS","BTCIM.IS","BUCIM.IS","BULGS.IS","BURCE.IS","BURVA.IS","BVSAN.IS","BYDNR.IS","CANTE.IS","CASA.IS","CATES.IS","CCOLA.IS","CELHA.IS","CEMAS.IS","CEMTS.IS","CEMZY.IS","CEOEM.IS","CGCAM.IS","CIMSA.IS","CLEBI.IS","CMBTN.IS","CMENT.IS","CONSE.IS","COSMO.IS","CRDFA.IS","CRFSA.IS","CUSAN.IS","CVKMD.IS","CWENE.IS","DAGI.IS","DAPGM.IS","DARDL.IS","DCTTR.IS","DENGE.IS","DERHL.IS","DERIM.IS","DESA.IS","DESPC.IS","DEVA.IS","DGATE.IS","DGGYO.IS","DGNMO.IS","DIRIT.IS","DITAS.IS","DMRGD.IS","DMSAS.IS","DNISI.IS","DOAS.IS","DOCO.IS","DOFER.IS","DOFRB.IS","DOGUB.IS","DOHOL.IS","DOKTA.IS","DSTKF.IS","DUNYH.IS","DURDO.IS","DURKN.IS","DYOBY.IS","DZGYO.IS","EBEBK.IS","ECILC.IS","ECOGR.IS","ECZYT.IS","EDATA.IS","EDIP.IS","EFOR.IS","EGEEN.IS","EGEGY.IS","EGEPO.IS","EGGUB.IS","EGPRO.IS","EGSER.IS","EKGYO.IS","EKIZ.IS","EKOS.IS","EKSUN.IS","ELITE.IS","EMKEL.IS","EMNIS.IS","ENDAE.IS","ENERY.IS","ENJSA.IS","ENKAI.IS","ENSRI.IS","ENTRA.IS","EPLAS.IS","ERBOS.IS","ERCB.IS","EREGL.IS","ERSU.IS","ESCAR.IS","ESCOM.IS","ESEN.IS","ETILR.IS","ETYAT.IS","EUHOL.IS","EUKYO.IS","EUPWR.IS","EUREN.IS","EUYO.IS","EYGYO.IS","FADE.IS","FENER.IS","FLAP.IS","FMIZP.IS","FONET.IS","FORMT.IS","FORTE.IS","FRIGO.IS","FRMPL.IS","FROTO.IS","FZLGY.IS","GARAN.IS","GARFA.IS","GEDIK.IS","GEDZA.IS","GENIL.IS","GENTS.IS","GEREL.IS","GESAN.IS","GIPTA.IS","GLBMD.IS","GLCVY.IS","GLRMK.IS","GLRYH.IS","GLYHO.IS","GMTAS.IS","GOKNR.IS","GOLTS.IS","GOODY.IS","GOZDE.IS","GRNYO.IS","GRSEL.IS","GRTHO.IS","GSDDE.IS","GSDHO.IS","GSRAY.IS","GUBRF.IS","GUNDG.IS","GWIND.IS","GZNMI.IS","HALKB.IS","HATEK.IS","HATSN.IS","HDFGS.IS","HEDEF.IS","HEKTS.IS","HKTM.IS","HLGYO.IS","HOROZ.IS","HRKET.IS","HTTBT.IS","HUBVC.IS","HUNER.IS","HURGZ.IS","ICBCT.IS","ICUGS.IS","IDGYO.IS","IEYHO.IS","IHAAS.IS","IHEVA.IS","IHGZT.IS","IHLAS.IS","IHLGM.IS","IHYAY.IS","IMASM.IS","INDES.IS","INFO.IS","INGRM.IS","INTEK.IS","INTEM.IS","INVEO.IS","INVES.IS","ISATR.IS","ISBIR.IS","ISBTR.IS","ISCTR.IS","ISDMR.IS","ISFIN.IS","ISGSY.IS","ISGYO.IS","ISKPL.IS","ISKUR.IS","ISMEN.IS","ISSEN.IS","ISYAT.IS","IZENR.IS","IZFAS.IS","IZINV.IS","IZMDC.IS","JANTS.IS","KAPLM.IS","KAREL.IS","KARSN.IS","KARTN.IS","KATMR.IS","KAYSE.IS","KBORU.IS","KCAER.IS","KCHOL.IS","KENT.IS","KERVN.IS","KFEIN.IS","KGYO.IS","KIMMR.IS","KLGYO.IS","KLKIM.IS","KLMSN.IS","KLNMA.IS","KLRHO.IS","KLSER.IS","KLSYN.IS","KLYPV.IS","KMPUR.IS","KNFRT.IS","KOCMT.IS","KONKA.IS","KONTR.IS","KONYA.IS","KOPOL.IS","KORDS.IS","KOTON.IS","KRDMA.IS","KRDMB.IS","KRDMD.IS","KRGYO.IS","KRONT.IS","KRPLS.IS","KRSTL.IS","KRTEK.IS","KRVGD.IS","KSTUR.IS","KTLEV.IS","KTSKR.IS","KUTPO.IS","KUVVA.IS","KUYAS.IS","KZBGY.IS","KZGYO.IS","LIDER.IS","LIDFA.IS","LILAK.IS","LINK.IS","LKMNH.IS","LMKDC.IS","LOGO.IS","LRSHO.IS","LUKSK.IS","LYDHO.IS","LYDYE.IS","MAALT.IS","MACKO.IS","MAGEN.IS","MAKIM.IS","MAKTK.IS","MANAS.IS","MARBL.IS","MARKA.IS","MARMR.IS","MARTI.IS","MAVI.IS","MEDTR.IS","MEGAP.IS","MEGMT.IS","MEKAG.IS","MEPET.IS","MERCN.IS","MERIT.IS","MERKO.IS","METRO.IS","MEYSU.IS","MGROS.IS","MHRGY.IS","MIATK.IS","MMCAS.IS","MNDRS.IS","MNDTR.IS","MOBTL.IS","MOGAN.IS","MOPAS.IS","MPARK.IS","MRGYO.IS","MRSHL.IS","MSGYO.IS","MTRKS.IS","MTRYO.IS","MZHLD.IS","NATEN.IS","NETAS.IS","NETCD.IS","NIBAS.IS","NTGAZ.IS","NTHOL.IS","NUGYO.IS","NUHCM.IS","OBAMS.IS","OBASE.IS","ODAS.IS","ODINE.IS","OFSYM.IS","ONCSM.IS","ONRYT.IS","ORCAY.IS","ORGE.IS","ORMA.IS","OSMEN.IS","OSTIM.IS","OTKAR.IS","OTTO.IS","OYAKC.IS","OYAYO.IS","OYLUM.IS","OYYAT.IS","OZATD.IS","OZGYO.IS","OZKGY.IS","OZRDN.IS","OZSUB.IS","OZYSR.IS","PAGYO.IS","PAHOL.IS","PAMEL.IS","PAPIL.IS","PARSN.IS","PASEU.IS","PATEK.IS","PCILT.IS","PEKGY.IS","PENGD.IS","PENTA.IS","PETKM.IS","PETUN.IS","PGSUS.IS","PINSU.IS","PKART.IS","PKENT.IS","PLTUR.IS","PNLSN.IS","PNSUT.IS","POLHO.IS","POLTK.IS","PRDGS.IS","PRKAB.IS","PRKME.IS","PRZMA.IS","PSDTC.IS","PSGYO.IS","QNBFK.IS","QNBTR.IS","QUAGR.IS","RALYH.IS","RAYSG.IS","REEDR.IS","RGYAS.IS","RNPOL.IS","RODRG.IS","RTALB.IS","RUBNS.IS","RUZYE.IS","RYGYO.IS","RYSAS.IS","SAFKR.IS","SAHOL.IS","SAMAT.IS","SANEL.IS","SANFM.IS","SANKO.IS","SARKY.IS","SASA.IS","SAYAS.IS","SDTTR.IS","SEGMN.IS","SEGYO.IS","SEKFK.IS","SEKUR.IS","SELEC.IS","SELVA.IS","SERNT.IS","SEYKM.IS","SILVR.IS","SISE.IS","SKBNK.IS","SKTAS.IS","SKYLP.IS","SKYMD.IS","SMART.IS","SMRTG.IS","SMRVA.IS","SNGYO.IS","SNICA.IS","SNPAM.IS","SODSN.IS","SOKE.IS","SOKM.IS","SONME.IS","SRVGY.IS","SUMAS.IS","SUNTK.IS","SURGY.IS","SUWEN.IS","TABGD.IS","TARKM.IS","TATEN.IS","TATGD.IS","TAVHL.IS","TBORG.IS","TCELL.IS","TCKRC.IS","TDGYO.IS","TEHOL.IS","TEKTU.IS","TERA.IS","TEZOL.IS","TGSAS.IS","THYAO.IS","TKFEN.IS","TKNSA.IS","TLMAN.IS","TMPOL.IS","TMSN.IS","TNZTP.IS","TOASO.IS","TRALT.IS","TRCAS.IS","TRENJ.IS","TRGYO.IS","TRHOL.IS","TRILC.IS","TRMET.IS","TSGYO.IS","TSKB.IS","TSPOR.IS","TTKOM.IS","TTRAK.IS","TUCLK.IS","TUKAS.IS","TUPRS.IS","TUREX.IS","TURGG.IS","TURSG.IS","UCAYM.IS","UFUK.IS","ULAS.IS","ULKER.IS","ULUFA.IS","ULUSE.IS","ULUUN.IS","UNLU.IS","USAK.IS","VAKBN.IS","VAKFA.IS","VAKFN.IS","VAKKO.IS","VANGD.IS","VBTYZ.IS","VERTU.IS","VERUS.IS","VESBE.IS","VESTL.IS","VKFYO.IS","VKGYO.IS","VKING.IS","VRGYO.IS","VSNMD.IS","YAPRK.IS","YATAS.IS","YAYLA.IS","YBTAS.IS","YEOTK.IS","YESIL.IS","YGGYO.IS","YGYO.IS","YIGIT.IS","YKBNK.IS","YKSLN.IS","YONGA.IS","YUNSA.IS","YYAPI.IS","YYLGD.IS","ZEDUR.IS","ZERGY.IS","ZGYO.IS","ZOREN.IS","ZRGYO.IS"
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
            pass

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
