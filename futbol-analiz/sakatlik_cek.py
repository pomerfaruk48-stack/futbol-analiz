import requests
import pandas as pd
import time

# API-Football anahtarın
API_KEY = "efd3af952aaf8ce27a09f1bd3a14feb6"

# Liglerin API-Football ID'leri
LIGLER = {
    39: "Premier League",
    140: "La Liga",
    135: "Serie A",
    78: "Bundesliga",
    61: "Ligue 1",
    2: "UEFA Champions League",
    88: "Eredivisie",
    94: "Primeira Liga",
    40: "Championship",
    71: "Brezilya Serie A",
}

SEZON = 2024

tum_sakatliklar = []

print("=" * 60)
print("API-FOOTBALL ÇOKLU LİG SAKATLIK VERİSİ ÇEKME")
print("=" * 60)
print(f"Toplam {len(LIGLER)} lig çekilecek.\n")

for lig_id, lig_adi in LIGLER.items():
    print(f"\n{'=' * 60}")
    print(f"📥 {lig_adi} (ID: {lig_id}) için sakatlık verisi çekiliyor...")
    print(f"{'=' * 60}")

    url = "https://v3.football.api-sports.io/injuries"
    params = {"league": lig_id, "season": SEZON}
    headers = {"x-apisports-key": API_KEY}

    try:
        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            injuries = data.get("response", [])
            kalan_hak = response.headers.get('x-ratelimit-requests-remaining', 'Bilinmiyor')

            print(f"✅ {len(injuries)} kayıt bulundu. Kalan günlük hak: {kalan_hak}")

            for item in injuries:
                tum_sakatliklar.append({
                    "Oyuncu": item["player"]["name"],
                    "Takım": item["team"]["name"],
                    "Tür": item["player"]["type"],
                    "Neden": item["player"]["reason"],
                    "Maç Tarihi": item["fixture"]["date"][:10],
                    "Lig": lig_adi
                })
        else:
            print(f"❌ Hata! Durum kodu: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"❌ Beklenmeyen hata: {e}")

    time.sleep(7)

print(f"\n\n{'=' * 60}")
print("İŞLEM TAMAMLANDI")
print(f"{'=' * 60}")
print(f"Toplam sakatlık kaydı: {len(tum_sakatliklar)}")

if tum_sakatliklar:
    df = pd.DataFrame(tum_sakatliklar)
    df.to_csv("tum_sakatliklar.csv", index=False, encoding="utf-8-sig")
    print(f"✅ Veri 'tum_sakatliklar.csv' dosyasına kaydedildi.")
    print(f"\nBenzersiz takım sayısı: {df['Takım'].nunique()}")
    print(f"Benzersiz oyuncu sayısı: {df['Oyuncu'].nunique()}")