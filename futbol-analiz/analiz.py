import pandas as pd

# CSV dosyasından veriyi oku
df = pd.read_csv("premier_lig_maclari.csv")

# Sadece oynanmış maçları al
df = df[df["Durum"] == "FINISHED"]

# Toplam gol sayısını hesapla
df["Toplam Gol"] = df["Ev Sahibi Gol"] + df["Deplasman Gol"]

print("=" * 50)
print("PREMIER LEAGUE 2024 SEZONU ANALİZİ")
print("=" * 50)

# 1. Toplam maç ve gol istatistikleri
print(f"\nToplam oynanan maç: {len(df)}")
print(f"Toplam atılan gol: {df['Toplam Gol'].sum()}")
print(f"Maç başına ortalama gol: {df['Toplam Gol'].mean():.2f}")

# 2. En çok gol atan takımlar
print("\n--- En Çok Gol Atan 5 Takım ---")
ev_golleri = df.groupby("Ev Sahibi")["Ev Sahibi Gol"].sum()
dep_golleri = df.groupby("Deplasman")["Deplasman Gol"].sum()
toplam_goller = ev_golleri.add(dep_golleri, fill_value=0).sort_values(ascending=False)
print(toplam_goller.head())

# 3. En çok gol yiyen takımlar
print("\n--- En Çok Gol Yiyen 5 Takım ---")
ev_yenen = df.groupby("Ev Sahibi")["Deplasman Gol"].sum()
dep_yenen = df.groupby("Deplasman")["Ev Sahibi Gol"].sum()
toplam_yenen = ev_yenen.add(dep_yenen, fill_value=0).sort_values(ascending=False)
print(toplam_yenen.head())

# 4. Ev sahibi avantajı
print("\n--- Ev Sahibi Avantajı ---")
ev_kazandi = len(df[df["Ev Sahibi Gol"] > df["Deplasman Gol"]])
berabere = len(df[df["Ev Sahibi Gol"] == df["Deplasman Gol"]])
dep_kazandi = len(df[df["Ev Sahibi Gol"] < df["Deplasman Gol"]])
print(f"Ev sahibi kazandı: {ev_kazandi} maç (%{ev_kazandi/len(df)*100:.1f})")
print(f"Berabere bitti: {berabere} maç (%{berabere/len(df)*100:.1f})")
print(f"Deplasman kazandı: {dep_kazandi} maç (%{dep_kazandi/len(df)*100:.1f})")

# 5. En gollü maçlar
print("\n--- En Gollü 5 Maç ---")
en_gollu = df.nlargest(5, "Toplam Gol")[["Ev Sahibi", "Deplasman", "Ev Sahibi Gol", "Deplasman Gol", "Toplam Gol"]]
print(en_gollu.to_string(index=False))