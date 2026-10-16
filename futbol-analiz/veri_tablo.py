import requests
import pandas as pd

# API anahtarını buraya yapıştır
API_KEY = "9ce16ba9fb824e358452c04ca9a2c654"

# Football-Data.org API adresi
url = "https://api.football-data.org/v4/competitions/PL/matches?season=2024"

# API isteği için gerekli başlık bilgisi
headers = {
    "X-Auth-Token": API_KEY
}

# API'ye istek gönder
response = requests.get(url, headers=headers)

# Gelen veriyi işle
if response.status_code == 200:
    data = response.json()
    matches = data.get("matches", [])
    
    # Maç bilgilerini bir listeye dönüştür
    mac_listesi = []
    for match in matches:
        mac_listesi.append({
            "Tarih": match["utcDate"],
            "Ev Sahibi": match["homeTeam"]["name"],
            "Deplasman": match["awayTeam"]["name"],
            "Ev Sahibi Gol": match["score"]["fullTime"]["home"],
            "Deplasman Gol": match["score"]["fullTime"]["away"],
            "Durum": match["status"]
        })
    
    # Listeyi pandas DataFrame'e dönüştür
    df = pd.DataFrame(mac_listesi)
    
    # İlk 5 maçı ekrana yazdır
    print("İlk 5 maç:")
    print(df.head())
    
    # Temel istatistikler
    print(f"\nToplam maç sayısı: {len(df)}")
    print(f"Oynanan maç sayısı: {len(df[df['Durum'] == 'FINISHED'])}")
    
    # Veriyi CSV dosyasına kaydet
    df.to_csv("premier_lig_maclari.csv", index=False, encoding="utf-8-sig")
    print("\nVeri 'premier_lig_maclari.csv' dosyasına kaydedildi!")
else:
    print(f"Hata oluştu! Durum kodu: {response.status_code}")
    print(response.text)