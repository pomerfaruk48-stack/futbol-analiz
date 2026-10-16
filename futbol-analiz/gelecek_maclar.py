import requests
import pandas as pd
import numpy as np
from scipy.stats import poisson

# API anahtarını buraya yapıştır
API_KEY = "9ce16ba9fb824e358452c04ca9a2c654"

# Takım güçlerini ve lig ortalamasını oku
guc_df = pd.read_csv("takim_gucu.csv")
maclar = pd.read_csv("premier_lig_maclari.csv")
maclar = maclar[maclar["Durum"] == "FINISHED"]

toplam_gol = maclar["Ev Sahibi Gol"].sum() + maclar["Deplasman Gol"].sum()
lig_ortalamasi = toplam_gol / (len(maclar) * 2)

ev_gol = maclar["Ev Sahibi Gol"].sum()
dep_gol = maclar["Deplasman Gol"].sum()
ev_avantaji = ev_gol / dep_gol

print("=" * 60)
print("GELECEK MAÇLAR İÇİN TAHMİNLER")
print("=" * 60)

def takim_bul(takim_adi):
    """Takım adını içeren satırı bulur (kısmi eşleşme)."""
    # API'den gelen isimler ile CSV'deki isimler farklı olabilir, esnek arama yap
    sonuc = guc_df[guc_df["Takım"].str.contains(takim_adi.split()[0], case=False, na=False)]
    if len(sonuc) == 0:
        return None
    return sonuc.iloc[0]

def mac_tahmini(ev_sahibi_adi, deplasman_adi, max_gol=8):
    """İki takım arasındaki maç için Poisson tahmini yapar."""
    
    ev = takim_bul(ev_sahibi_adi)
    dep = takim_bul(deplasman_adi)
    
    if ev is None or dep is None:
        print(f"\nATLANDI: {ev_sahibi_adi} vs {deplasman_adi} (takım bulunamadı)")
        return None
    
    ev_lambda = ev["Hücum Gücü"] * dep["Savunma Gücü"] * lig_ortalamasi * ev_avantaji
    dep_lambda = dep["Hücum Gücü"] * ev["Savunma Gücü"] * lig_ortalamasi
    
    ev_gol_olasilik = [poisson.pmf(i, ev_lambda) for i in range(max_gol)]
    dep_gol_olasilik = [poisson.pmf(i, dep_lambda) for i in range(max_gol)]
    skor_matrisi = np.outer(ev_gol_olasilik, dep_gol_olasilik)
    
    ev_kazanma = np.sum(np.tril(skor_matrisi, -1))
    beraberlik = np.sum(np.diag(skor_matrisi))
    dep_kazanma = np.sum(np.triu(skor_matrisi, 1))
    
    alt_25 = sum(skor_matrisi[i][j] for i in range(max_gol) for j in range(max_gol) if i + j <= 2)
    ust_25 = 1 - alt_25
    
    karsilikli_gol = sum(skor_matrisi[i][j] for i in range(1, max_gol) for j in range(1, max_gol))
    
    return {
        "Ev Sahibi": ev["Takım"],
        "Deplasman": dep["Takım"],
        "Ev Gol Beklentisi": round(ev_lambda, 2),
        "Dep Gol Beklentisi": round(dep_lambda, 2),
        "Ev Kazanma %": round(ev_kazanma * 100, 1),
        "Beraberlik %": round(beraberlik * 100, 1),
        "Dep Kazanma %": round(dep_kazanma * 100, 1),
        "Alt 2.5 %": round(alt_25 * 100, 1),
        "Üst 2.5 %": round(ust_25 * 100, 1),
        "KG %": round(karsilikli_gol * 100, 1)
    }

# API'den gelecek maçları çek
url = "https://api.football-data.org/v4/competitions/PL/matches?status=SCHEDULED"
headers = {"X-Auth-Token": API_KEY}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()
    matches = data.get("matches", [])
    
    print(f"\nToplam planlanmış maç: {len(matches)}")
    print(f"İlk 5 maç için tahmin üretiliyor...\n")
    
    tahminler = []
    for match in matches[:5]:
        ev = match["homeTeam"]["name"]
        dep = match["awayTeam"]["name"]
        tarih = match["utcDate"]
        
        print(f"\n{'=' * 60}")
        print(f"{tarih[:10]} - {ev} vs {dep}")
        print(f"{'=' * 60}")
        
        tahmin = mac_tahmini(ev, dep)
        
        if tahmin:
            tahminler.append(tahmin)
            print(f"Beklenen gol: {tahmin['Ev Gol Beklentisi']} - {tahmin['Dep Gol Beklentisi']}")
            print(f"1X2: %{tahmin['Ev Kazanma %']} / %{tahmin['Beraberlik %']} / %{tahmin['Dep Kazanma %']}")
            print(f"Alt/Üst 2.5: %{tahmin['Alt 2.5 %']} / %{tahmin['Üst 2.5 %']}")
            print(f"Karşılıklı Gol: %{tahmin['KG %']}")
    
    # Tahminleri CSV'ye kaydet
    if tahminler:
        tahmin_df = pd.DataFrame(tahminler)
        tahmin_df.to_csv("gelecek_mac_tahminleri.csv", index=False, encoding="utf-8-sig")
        print(f"\n\nTahminler 'gelecek_mac_tahminleri.csv' dosyasına kaydedildi!")
    
else:
    print(f"Hata oluştu! Durum kodu: {response.status_code}")
    print(response.text)