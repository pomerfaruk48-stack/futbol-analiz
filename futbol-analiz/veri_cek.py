import requests
import pandas as pd
import time

# ==================== AYARLAR ====================
FOOTBALL_DATA_API_KEY = "9ce16ba9fb824e358452c04ca9a2c654"

LIGLER = {
    "PL": "Premier League",
    "PD": "La Liga",
    "SA": "Serie A",
    "BL1": "Bundesliga",
    "FL1": "Ligue 1",
    "CL": "UEFA Champions League",
    "DED": "Eredivisie",
    "PPL": "Primeira Liga",
    "ELC": "Championship",
    "BSA": "Brezilya Serie A",
    "EC": "European Championship",
    "WC": "FIFA World Cup",
}

SEZON = 2024


# ==================== VERİ ÇEKME ====================
def lig_verisi_cek(lig_kodu, lig_adi):
    print(f"\n{'=' * 60}")
    print(f"📥 {lig_adi} ({lig_kodu}) için veri çekiliyor...")
    print(f"{'=' * 60}")

    url = f"https://api.football-data.org/v4/competitions/{lig_kodu}/matches?season={SEZON}"
    headers = {"X-Auth-Token": FOOTBALL_DATA_API_KEY}

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            matches = data.get("matches", [])

            if len(matches) == 0:
                print(f"⚠️ {lig_adi}: Hiç maç bulunamadı.")
                return None

            mac_listesi = []
            for match in matches:
                mac_listesi.append({
                    "Tarih": match["utcDate"],
                    "Ev Sahibi": match["homeTeam"]["name"] if match["homeTeam"]["name"] else "Bilinmiyor",
                    "Deplasman": match["awayTeam"]["name"] if match["awayTeam"]["name"] else "Bilinmiyor",
                    "Ev Sahibi Gol": match["score"]["fullTime"]["home"],
                    "Deplasman Gol": match["score"]["fullTime"]["away"],
                    "Durum": match["status"],
                    "Lig": lig_adi,
                    "Lig Kodu": lig_kodu
                })

            df = pd.DataFrame(mac_listesi)
            dosya_adi = f"{lig_kodu.lower()}_maclari.csv"
            df.to_csv(dosya_adi, index=False, encoding="utf-8-sig")

            print(f"✅ {lig_adi}: {len(df)} maç çekildi ve '{dosya_adi}' dosyasına kaydedildi.")
            return df

        elif response.status_code == 403:
            print(f"❌ {lig_adi}: Bu lige erişim izniniz yok (ücretsiz plan kapsamı dışında).")
            return None

        elif response.status_code == 429:
            print(f"⚠️ {lig_adi}: İstek limiti aşıldı. 60 saniye bekleniyor...")
            time.sleep(60)
            return lig_verisi_cek(lig_kodu, lig_adi)

        else:
            print(f"❌ {lig_adi}: Hata! Durum kodu: {response.status_code}")
            print(response.text)
            return None

    except Exception as e:
        print(f"❌ {lig_adi}: Beklenmeyen hata: {e}")
        return None


# ==================== ANA PROGRAM ====================
print("=" * 60)
print("FOOTBALL-DATA.ORG ÇOKLU LİG VERİ ÇEKME")
print("=" * 60)
print(f"Toplam {len(LIGLER)} lig çekilecek.")
print(f"Sezon: {SEZON}")
print(f"⚠️ Her lig arasında 7 saniye beklenecek.\n")

basarili_ligler = []
basarisiz_ligler = []

for lig_kodu, lig_adi in LIGLER.items():
    df = lig_verisi_cek(lig_kodu, lig_adi)

    if df is not None:
        basarili_ligler.append(lig_adi)
    else:
        basarisiz_ligler.append(lig_adi)

    time.sleep(7)

print(f"\n\n{'=' * 60}")
print("İŞLEM TAMAMLANDI")
print(f"{'=' * 60}")
print(f"✅ Başarılı: {len(basarili_ligler)} lig")
for lig in basarili_ligler:
    print(f"   - {lig}")

if basarisiz_ligler:
    print(f"\n❌ Başarısız: {len(basarisiz_ligler)} lig")
    for lig in basarisiz_ligler:
        print(f"   - {lig}")

print(f"\n📁 Tüm CSV dosyaları 'futbol-analiz' klasöründe.")