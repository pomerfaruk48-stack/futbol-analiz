import requests
import pandas as pd
import time

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
}

SEZON = 2026

print("=" * 60)
print("GELECEK SEZON MAÇ VERİLERİ ÇEKİLİYOR")
print("=" * 60)
print(f"Sezon: {SEZON}-{SEZON+1}\n")

basarili = []
basarisiz = []

for lig_kodu, lig_adi in LIGLER.items():
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
                basarisiz.append(lig_adi)
                continue

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
            dosya_adi = f"{lig_kodu.lower()}_maclari_{SEZON}.csv"
            df.to_csv(dosya_adi, index=False, encoding="utf-8-sig")

            oynanmis = len(df[df["Durum"] == "FINISHED"])
            gelecek = len(df[df["Durum"] != "FINISHED"])

            print(f"✅ {lig_adi}: {len(df)} maç çekildi.")
            print(f"   - Oynanmış: {oynanmis}")
            print(f"   - Gelecek: {gelecek}")
            print(f"   - Dosya: {dosya_adi}")

            basarili.append(lig_adi)
        else:
            print(f"❌ {lig_adi}: Hata! Durum kodu: {response.status_code}")
            basarisiz.append(lig_adi)

    except Exception as e:
        print(f"❌ {lig_adi}: Beklenmeyen hata: {e}")
        basarisiz.append(lig_adi)

    time.sleep(7)

print(f"\n\n{'=' * 60}")
print("İŞLEM TAMAMLANDI")
print(f"{'=' * 60}")
print(f"✅ Başarılı: {len(basarili)} lig")
for lig in basarili:
    print(f"   - {lig}")

if basarisiz:
    print(f"\n⚠️ Başarısız: {len(basarisiz)} lig")
    for lig in basarisiz:
        print(f"   - {lig}")