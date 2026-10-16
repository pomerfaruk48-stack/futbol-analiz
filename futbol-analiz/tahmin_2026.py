import pandas as pd
import numpy as np
from scipy.stats import poisson

LIGLER = {
    "pl": "Premier League",
    "pd": "La Liga",
    "sa": "Serie A",
    "bl1": "Bundesliga",
    "fl1": "Ligue 1",
    "cl": "UEFA Champions League",
    "ded": "Eredivisie",
    "ppl": "Primeira Liga",
    "elc": "Championship",
    "bsa": "Brezilya Serie A",
}

def lig_tahmini_uret(lig_kodu, lig_adi):
    print(f"\n{'=' * 60}")
    print(f"🔮 {lig_adi} için 2026-2027 tahmini üretiliyor...")
    print(f"{'=' * 60}")

    # Hem 2024 hem 2026 sezonunu birleştir (takım güçleri için)
    sezonlar = []
    for sezon in ["", "_2026"]:
        try:
            df = pd.read_csv(f"{lig_kodu}_maclari{sezon}.csv")
            df["Sezon"] = "2024" if sezon == "" else "2026"
            sezonlar.append(df)
        except FileNotFoundError:
            pass

    if len(sezonlar) == 0:
        print(f"⚠️ {lig_adi}: Hiç maç verisi yok, atlanıyor.")
        return None

    tum_maclar = pd.concat(sezonlar, ignore_index=True)
    oynanmis = tum_maclar[tum_maclar["Durum"] == "FINISHED"].copy()

    if len(oynanmis) == 0:
        print(f"⚠️ {lig_adi}: Oynanmış maç yok, atlanıyor.")
        return None

    toplam_gol = oynanmis["Ev Sahibi Gol"].sum() + oynanmis["Deplasman Gol"].sum()
    lig_ortalamasi = toplam_gol / (len(oynanmis) * 2)

    ev_gol = oynanmis["Ev Sahibi Gol"].sum()
    dep_gol = oynanmis["Deplasman Gol"].sum()
    ev_avantaji = ev_gol / dep_gol if dep_gol > 0 else 1.0

    print(f"Toplam oynanmış maç: {len(oynanmis)}")
    print(f"Lig ortalaması: {lig_ortalamasi:.3f}")
    print(f"Ev sahibi avantajı: {ev_avantaji:.3f}")

    takimlar = set(oynanmis["Ev Sahibi"].unique()) | set(oynanmis["Deplasman"].unique())
    takim_gucu = {}

    for takim in takimlar:
        ev_mac = oynanmis[oynanmis["Ev Sahibi"] == takim]
        dep_mac = oynanmis[oynanmis["Deplasman"] == takim]

        ev_attigi = ev_mac["Ev Sahibi Gol"].sum()
        ev_yedigi = ev_mac["Deplasman Gol"].sum()
        dep_attigi = dep_mac["Deplasman Gol"].sum()
        dep_yedigi = dep_mac["Ev Sahibi Gol"].sum()

        toplam_mac = len(ev_mac) + len(dep_mac)
        if toplam_mac == 0:
            continue

        hucum = ((ev_attigi + dep_attigi) / toplam_mac) / lig_ortalamasi
        savunma = ((ev_yedigi + dep_yedigi) / toplam_mac) / lig_ortalamasi

        takim_gucu[takim] = {"hucum": hucum, "savunma": savunma}

    # 2026 sezonunun oynanmamış maçlarını filtrele
    maclar_2026 = tum_maclar[tum_maclar["Sezon"] == "2026"].copy()
    gelecek = maclar_2026[maclar_2026["Durum"] != "FINISHED"].copy()

    if len(gelecek) == 0:
        print(f"⚠️ {lig_adi}: Gelecek maç yok, atlanıyor.")
        return None

    tahminler = []
    for _, mac in gelecek.iterrows():
        ev = mac["Ev Sahibi"]
        dep = mac["Deplasman"]

        if ev not in takim_gucu or dep not in takim_gucu:
            continue

        ev_lambda = takim_gucu[ev]["hucum"] * takim_gucu[dep]["savunma"] * lig_ortalamasi * ev_avantaji
        dep_lambda = takim_gucu[dep]["hucum"] * takim_gucu[ev]["savunma"] * lig_ortalamasi

        max_gol = 8
        ev_olasilik = [poisson.pmf(i, ev_lambda) for i in range(max_gol)]
        dep_olasilik = [poisson.pmf(i, dep_lambda) for i in range(max_gol)]
        matris = np.outer(ev_olasilik, dep_olasilik)

        ev_kazanma = np.sum(np.tril(matris, -1))
        beraberlik = np.sum(np.diag(matris))
        dep_kazanma = np.sum(np.triu(matris, 1))

        alt_25 = sum(matris[i][j] for i in range(max_gol) for j in range(max_gol) if i + j <= 2)
        ust_25 = 1 - alt_25
        kg = sum(matris[i][j] for i in range(1, max_gol) for j in range(1, max_gol))

        skorlar = []
        for i in range(max_gol):
            for j in range(max_gol):
                skorlar.append((i, j, matris[i][j]))
        skorlar.sort(key=lambda x: x[2], reverse=True)
        en_olasi = ", ".join([f"{i}-{j}" for i, j, _ in skorlar[:5]])

        tahminler.append({
            "Tarih": mac["Tarih"],
            "Ev Sahibi": ev,
            "Deplasman": dep,
            "Lig": lig_adi,
            "Ev Gol Beklentisi": round(ev_lambda, 2),
            "Dep Gol Beklentisi": round(dep_lambda, 2),
            "Ev Kazanma %": round(ev_kazanma * 100, 1),
            "Beraberlik %": round(beraberlik * 100, 1),
            "Dep Kazanma %": round(dep_kazanma * 100, 1),
            "Alt 2.5 %": round(alt_25 * 100, 1),
            "Üst 2.5 %": round(ust_25 * 100, 1),
            "KG %": round(kg * 100, 1),
            "En Olası Skorlar": en_olasi,
            "Ev Hücum Gücü": round(takim_gucu[ev]["hucum"], 2),
            "Ev Savunma Gücü": round(takim_gucu[ev]["savunma"], 2),
            "Dep Hücum Gücü": round(takim_gucu[dep]["hucum"], 2),
            "Dep Savunma Gücü": round(takim_gucu[dep]["savunma"], 2),
            "Lig Ortalaması": round(lig_ortalamasi, 2),
            "Ev Avantajı": round(ev_avantaji, 2)
        })

    if len(tahminler) == 0:
        print(f"⚠️ {lig_adi}: Tahmin üretilecek maç yok.")
        return None

    tahmin_df = pd.DataFrame(tahminler)
    dosya_adi = f"{lig_kodu}_tahminleri_2026.csv"
    tahmin_df.to_csv(dosya_adi, index=False, encoding="utf-8-sig")

    print(f"✅ {lig_adi}: {len(tahmin_df)} maç için tahmin üretildi.")
    print(f"📁 Dosya: {dosya_adi}")
    return tahmin_df


print("=" * 60)
print("2026-2027 SEZONU İÇİN TAHMİN ÜRETME")
print("=" * 60)

basarili = []
basarisiz = []

for lig_kodu, lig_adi in LIGLER.items():
    sonuc = lig_tahmini_uret(lig_kodu, lig_adi)
    if sonuc is not None:
        basarili.append(lig_adi)
    else:
        basarisiz.append(lig_adi)

print(f"\n\n{'=' * 60}")
print("İŞLEM TAMAMLANDI")
print(f"{'=' * 60}")
print(f"✅ Başarılı: {len(basarili)} lig")
for lig in basarili:
    print(f"   - {lig}")

if basarisiz:
    print(f"\n⚠️ Atlanan: {len(basarisiz)} lig")
    for lig in basarisiz:
        print(f"   - {lig}")