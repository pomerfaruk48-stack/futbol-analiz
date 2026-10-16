import json
import pandas as pd

# Ham veriyi oku
with open("sakatlik_ham_veri.json", "r", encoding="utf-8") as f:
    data = json.load(f)

injuries = data.get("response", [])

# Veriyi düzenli bir tabloya dönüştür
kayitlar = []
for item in injuries:
    kayitlar.append({
        "Oyuncu": item["player"]["name"],
        "Takım": item["team"]["name"],
        "Tür": item["player"]["type"],        # Missing Fixture / Questionable
        "Neden": item["player"]["reason"],    # Ankle Injury, Red Card vb.
        "Maç Tarihi": item["fixture"]["date"][:10],
        "Lig": item["league"]["name"]
    })

df = pd.DataFrame(kayitlar)

print("=" * 60)
print("SAKATLIK / CEZA VERİLERİ")
print("=" * 60)
print(f"Toplam kayıt: {len(df)}")
print(f"Benzersiz oyuncu: {df['Oyuncu'].nunique()}")
print(f"Benzersiz takım: {df['Takım'].nunique()}")

# Neden türlerine göre dağılım
print("\n--- Neden Türleri (İlk 10) ---")
neden_sayilari = df["Neden"].value_counts().head(10)
for neden, sayi in neden_sayilari.items():
    print(f"{neden}: {sayi}")

# Örnek: Manchester City'nin eksikleri
print("\n--- Manchester City'nin Eksik Oyuncuları ---")
mancity = df[df["Takım"] == "Manchester City"]
if len(mancity) > 0:
    print(mancity[["Oyuncu", "Tür", "Neden", "Maç Tarihi"]].head(10).to_string(index=False))
else:
    print("Kayıt bulunamadı.")

# Örnek: Liverpool'un eksikleri
print("\n--- Liverpool'un Eksik Oyuncuları ---")
liverpool = df[df["Takım"] == "Liverpool"]
if len(liverpool) > 0:
    print(liverpool[["Oyuncu", "Tür", "Neden", "Maç Tarihi"]].head(10).to_string(index=False))
else:
    print("Kayıt bulunamadı.")

# Veriyi CSV'ye kaydet
df.to_csv("sakatlik_verileri.csv", index=False, encoding="utf-8-sig")
print("\n\nVeri 'sakatlik_verileri.csv' dosyasına kaydedildi!")