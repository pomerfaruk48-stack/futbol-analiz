import requests
import pandas as pd
import time

API_KEY = "efd3af952aaf8ce27a09f1bd3a14feb6"

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

print("=" * 60)
print("API-FOOTBALL TAKIM ID'LERİ ÇEKİLİYOR")
print("=" * 60)

tum_takimlar = []

for lig_id, lig_adi in LIGLER.items():
    print(f"\n📥 {lig_adi} (ID: {lig_id}) için takımlar çekiliyor...")

    url = "https://v3.football.api-sports.io/teams"
    params = {"league": lig_id}   # season parametresi kaldırıldı
    headers = {"x-apisports-key": API_KEY}

    try:
        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            takimlar = data.get("response", [])
            kalan = response.headers.get('x-ratelimit-requests-remaining', 'Bilinmiyor')

            print(f"   ✅ {len(takimlar)} takım bulundu. Kalan hak: {kalan}")

            for t in takimlar:
                tum_takimlar.append({
                    "Takım ID": t["team"]["id"],
                    "Takım Adı": t["team"]["name"],
                    "Ülke": t["team"]["country"],
                    "Lig": lig_adi,
                    "Lig ID": lig_id
                })
        else:
            print(f"   ❌ Hata! Durum kodu: {response.status_code}")
            print(f"   {response.text[:200]}")

    except Exception as e:
        print(f"   ❌ Hata: {e}")

    time.sleep(7)

if tum_takimlar:
    df = pd.DataFrame(tum_takimlar)
    df = df.drop_duplicates(subset=["Takım ID"])
    df.to_csv("takim_idleri.csv", index=False, encoding="utf-8-sig")
    print(f"\n\n{'=' * 60}")
    print("İŞLEM TAMAMLANDI")
    print(f"{'=' * 60}")
    print(f"Toplam takım: {len(df)}")
    print(f"✅ Veri 'takim_idleri.csv' dosyasına kaydedildi!")

    # İlk 10 takımı göster
    print("\n--- İlk 10 Takım ---")
    print(df[["Takım ID", "Takım Adı", "Lig"]].head(10).to_string(index=False))
else:
    print("\n❌ Hiç takım verisi çekilemedi.")