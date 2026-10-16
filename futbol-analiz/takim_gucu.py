import pandas as pd

# CSV dosyasından veriyi oku
df = pd.read_csv("premier_lig_maclari.csv")

# Sadece oynanmış maçları al
df = df[df["Durum"] == "FINISHED"].copy()

# Lig ortalamasını hesapla (maç başına gol)
toplam_gol = df["Ev Sahibi Gol"].sum() + df["Deplasman Gol"].sum()
toplam_mac = len(df)
lig_ortalamasi = toplam_gol / (toplam_mac * 2)  # Her maçta 2 takım var

print("=" * 60)
print("TAKIM GÜÇLERİ ANALİZİ")
print("=" * 60)
print(f"Lig maç başına takım gol ortalaması: {lig_ortalamasi:.3f}")

# Her takım için ev ve deplasman istatistiklerini hesapla
takimlar = set(df["Ev Sahibi"].unique()) | set(df["Deplasman"].unique())

takim_gucu = []

for takim in takimlar:
    # Ev sahibi olarak oynadığı maçlar
    ev_maclari = df[df["Ev Sahibi"] == takim]
    ev_attigi = ev_maclari["Ev Sahibi Gol"].sum()
    ev_yedigi = ev_maclari["Deplasman Gol"].sum()
    ev_mac_sayisi = len(ev_maclari)
    
    # Deplasman olarak oynadığı maçlar
    dep_maclari = df[df["Deplasman"] == takim]
    dep_attigi = dep_maclari["Deplasman Gol"].sum()
    dep_yedigi = dep_maclari["Ev Sahibi Gol"].sum()
    dep_mac_sayisi = len(dep_maclari)
    
    # Toplam
    toplam_attigi = ev_attigi + dep_attigi
    toplam_yedigi = ev_yedigi + dep_yedigi
    toplam_mac_sayisi = ev_mac_sayisi + dep_mac_sayisi
    
    # Hücum ve savunma gücü (lig ortalamasına göre)
    hucum_gucu = (toplam_attigi / toplam_mac_sayisi) / lig_ortalamasi
    savunma_gucu = (toplam_yedigi / toplam_mac_sayisi) / lig_ortalamasi
    
    takim_gucu.append({
        "Takım": takim,
        "Maç": toplam_mac_sayisi,
        "Attığı Gol": toplam_attigi,
        "Yediği Gol": toplam_yedigi,
        "Maç Başına Gol": round(toplam_attigi / toplam_mac_sayisi, 2),
        "Maç Başına Yenen": round(toplam_yedigi / toplam_mac_sayisi, 2),
        "Hücum Gücü": round(hucum_gucu, 3),
        "Savunma Gücü": round(savunma_gucu, 3)
    })

# DataFrame'e dönüştür ve hücum gücüne göre sırala
guc_df = pd.DataFrame(takim_gucu)
guc_df = guc_df.sort_values("Hücum Gücü", ascending=False)

print("\n--- En Güçlü Hücumlar (İlk 10) ---")
print(guc_df[["Takım", "Maç Başına Gol", "Hücum Gücü"]].head(10).to_string(index=False))

print("\n--- En İyi Savunmalar (İlk 10) ---")
en_iyi_savunma = guc_df.sort_values("Savunma Gücü").head(10)
print(en_iyi_savunma[["Takım", "Maç Başına Yenen", "Savunma Gücü"]].to_string(index=False))

# Sonuçları CSV'ye kaydet
guc_df.to_csv("takim_gucu.csv", index=False, encoding="utf-8-sig")
print("\nTakım güçleri 'takim_gucu.csv' dosyasına kaydedildi!")