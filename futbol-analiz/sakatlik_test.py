import requests
import json

API_KEY = "efd3af952aaf8ce27a09f1bd3a14feb6"  # Kendi anahtarını yaz

url = "https://v3.football.api-sports.io/injuries"
params = {"league": 39, "season": 2024}
headers = {"x-apisports-key": API_KEY}

print("API'ye istek gönderiliyor...")
response = requests.get(url, headers=headers, params=params)

if response.status_code == 200:
    data = response.json()
    print(f"Toplam sonuç: {data.get('results', 0)}")
    print(f"Kalan günlük istek hakkı: {response.headers.get('x-ratelimit-requests-remaining', 'Bilinmiyor')}")
    
    injuries = data.get("response", [])
    
    if len(injuries) == 0:
        print("\n⚠️ Hiç sakat/cezalı oyuncu verisi bulunamadı.")
    else:
        print(f"\n--- İlk 15 Eksik Oyuncu ---")
        for i, item in enumerate(injuries[:15], 1):
            oyuncu = item["player"]["name"]
            takim = item["team"]["name"]
            tur = item["player"]["type"]        # "Missing Fixture" veya "Questionable"
            neden = item["player"]["reason"]    # "Ankle Injury", "Red Card" vb.
            mac_tarihi = item["fixture"]["date"][:10]
            
            print(f"\n{i}. {oyuncu} ({takim})")
            print(f"   Tür: {tur}")
            print(f"   Neden: {neden}")
            print(f"   Maç Tarihi: {mac_tarihi}")
    
    # Ham veriyi JSON dosyasına kaydet
    with open("sakatlik_ham_veri.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("\n\nHam veri 'sakatlik_ham_veri.json' dosyasına kaydedildi.")
    
else:
    print(f"❌ Hata oluştu! Durum kodu: {response.status_code}")
    print(response.text)