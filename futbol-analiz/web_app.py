import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson

# ==================== SAYFA AYARLARI ====================
st.set_page_config(
    page_title="Futbol Analiz Platformu",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== ÖZEL CSS ====================
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #A90432 0%, #FDB912 100%);
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin-bottom: 30px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .main-header h1 { color: white; font-size: 2.2em; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
    .main-header p { color: white; font-size: 1.0em; margin-top: 10px; opacity: 0.95; }
    .metrik-kutu {
        background: white;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        border-top: 3px solid #FDB912;
    }
    .metrik-deger { font-size: 1.7em; font-weight: bold; color: #A90432; }
    .metrik-etiket { font-size: 0.9em; color: #666; margin-top: 5px; }
    .skor-kutu {
        background: linear-gradient(135deg, #A90432 0%, #FDB912 100%);
        color: white;
        padding: 10px 18px;
        border-radius: 8px;
        text-align: center;
        font-weight: bold;
        margin: 5px;
        display: inline-block;
    }
    .aciklama-kutu {
        background: #fff8e1;
        border-left: 4px solid #FDB912;
        padding: 15px;
        border-radius: 8px;
        margin-top: 10px;
        margin-bottom: 10px;
        font-size: 0.95em;
        color: #333;
        line-height: 1.6;
    }
    .eksik-oyuncu {
        background: #ffebee;
        border-left: 4px solid #c62828;
        padding: 10px 15px;
        border-radius: 6px;
        margin-bottom: 8px;
        font-size: 0.9em;
    }
    .stApp { background-color: #f8f9fa; }
</style>
""", unsafe_allow_html=True)


# ==================== LİG DOSYALARI ====================
LIGLER = {
    "Premier League": "pl",
    "La Liga": "pd",
    "Serie A": "sa",
    "Bundesliga": "bl1",
    "Ligue 1": "fl1",
    "UEFA Champions League": "cl",
    "Eredivisie": "ded",
    "Primeira Liga": "ppl",
    "Championship": "elc",
    "Brezilya Serie A": "bsa",
}


# ==================== YARDIMCI FONKSİYONLAR ====================
def mac_aciklamasi(row):
    ev = row["Ev Sahibi"]
    dep = row["Deplasman"]
    ev_hucum = row.get("Ev Hücum Gücü", 1.0)
    dep_savunma = row.get("Dep Savunma Gücü", 1.0)
    ev_avantaj = row.get("Ev Avantajı", 1.15)
    ev_gol_bek = row["Ev Gol Beklentisi"]
    dep_gol_bek = row["Dep Gol Beklentisi"]
    ev_kaz = row["Ev Kazanma %"]
    ber = row["Beraberlik %"]
    dep_kaz = row["Dep Kazanma %"]
    alt25 = row["Alt 2.5 %"]
    ust25 = row["Üst 2.5 %"]
    kg = row["KG %"]

    if ev_hucum > 1.2:
        ev_hucum_yorum = f"güçlü (lig ortalamasının %{int((ev_hucum-1)*100)} üstünde)"
    elif ev_hucum > 1.0:
        ev_hucum_yorum = f"ortalamanın biraz üstünde (%{int((ev_hucum-1)*100)})"
    else:
        ev_hucum_yorum = f"ortalama altı (%{int((1-ev_hucum)*100)} düşük)"

    if dep_savunma > 1.2:
        dep_savunma_yorum = f"zayıf (lig ortalamasının %{int((dep_savunma-1)*100)} üstünde gol yiyor)"
    elif dep_savunma > 1.0:
        dep_savunma_yorum = f"ortalamanın biraz altında (%{int((dep_savunma-1)*100)})"
    else:
        dep_savunma_yorum = f"sağlam (%{int((1-dep_savunma)*100)} daha az gol yiyor)"

    aciklama_1x2 = f"""
    <b>📊 1X2 Analizi:</b><br>
    <b>{ev}</b> takımının hücum gücü <b>{ev_hucum:.2f}</b> ({ev_hucum_yorum}). 
    <b>{dep}</b> takımının savunma gücü <b>{dep_savunma:.2f}</b> ({dep_savunma_yorum}).<br><br>
    Bu maçta <b>{ev}</b> takımının beklenen gol sayısı <b>{ev_gol_bek}</b>, 
    <b>{dep}</b> takımının beklenen gol sayısı <b>{dep_gol_bek}</b>.<br><br>
    Ev sahibi avantajı katsayısı <b>{ev_avantaj:.2f}</b> ile bu maçta ev sahibi lehine ekstra bir üstünlük var.<br><br>
    <b>Sonuç:</b> Ev sahibi kazanma <b>%{ev_kaz}</b>, beraberlik <b>%{ber}</b>, 
    deplasman kazanma <b>%{dep_kaz}</b>.
    """

    toplam_bek = ev_gol_bek + dep_gol_bek
    if toplam_bek > 2.8:
        toplam_yorum = "yüksek (gollü maç beklentisi)"
    elif toplam_bek > 2.3:
        toplam_yorum = "orta seviyede"
    else:
        toplam_yorum = "düşük (az gollü maç beklentisi)"

    aciklama_alt_ust = f"""
    <b>⚽ Alt/Üst 2.5 Gol Analizi:</b><br>
    İki takımın toplam beklenen gol sayısı <b>{toplam_bek:.2f}</b> ({toplam_yorum}).<br><br>
    <b>{ev}</b> takımı maç başına <b>{ev_gol_bek}</b> gol atması bekleniyor. 
    <b>{dep}</b> takımı için bu değer <b>{dep_gol_bek}</b>.<br><br>
    Bu verilere göre <b>2.5 gol altı</b> olasılığı <b>%{alt25}</b>, 
    <b>2.5 gol üstü</b> olasılığı <b>%{ust25}</b>.
    """

    aciklama_kg = f"""
    <b>🎯 Karşılıklı Gol Analizi:</b><br>
    <b>{ev}</b> takımının gol atma beklentisi <b>{ev_gol_bek}</b>, 
    <b>{dep}</b> takımının gol atma beklentisi <b>{dep_gol_bek}</b>.<br><br>
    Her iki takımın da gol atma olasılığı <b>%{kg}</b>. 
    Bu, iki takımın da savunma zaafları ve hücum güçleri dikkate alındığında hesaplanmıştır.
    """

    return aciklama_1x2, aciklama_alt_ust, aciklama_kg


def eksik_oyunculari_getir(takim_adi):
    try:
        df = pd.read_csv("tum_sakatliklar.csv")
        takim_df = df[df["Takım"].str.contains(takim_adi.split()[0], case=False, na=False)]
        if len(takim_df) == 0:
            return None
        takim_df["Maç Tarihi"] = pd.to_datetime(takim_df["Maç Tarihi"])
        son_tarih = takim_df["Maç Tarihi"].max()
        son_30 = takim_df[takim_df["Maç Tarihi"] >= (son_tarih - pd.Timedelta(days=30))]
        if len(son_30) == 0:
            return None
        return son_30.drop_duplicates(subset=["Oyuncu"], keep="last")
    except Exception:
        return None


# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 15px 0; margin-bottom: 20px;">
        <div style="font-size: 3em;">🦁</div>
        <div style="color: #A90432; font-weight: bold; font-size: 1.3em;">Futbol Analiz</div>
        <div style="color: #666; font-size: 0.85em;">Yapay Zeka Destekli</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🏆 Lig Seçin")
    secilen_lig = st.selectbox("Lig:", list(LIGLER.keys()), label_visibility="collapsed")

    st.markdown("---")
    st.caption("⚠️ Bu tahminler istatistiksel modellere dayanır ve kesin sonuç garantisi vermez.")


# ==================== ANA İÇERİK ====================
st.markdown(f'''
<div class="main-header">
    <h1>⚽ {secilen_lig} - Gelecek Maçlar</h1>
    <p>2026-2027 Sezonu Tahminleri</p>
</div>
''', unsafe_allow_html=True)

lig_kodu = LIGLER[secilen_lig]

try:
    tahmin_df = pd.read_csv(f"{lig_kodu}_tahminleri_2026.csv")
except FileNotFoundError:
    st.error(f"❌ {lig_kodu}_tahminleri_2026.csv dosyası bulunamadı! Önce tahmin_2026.py dosyasını çalıştırın.")
    st.stop()

if len(tahmin_df) == 0:
    st.warning(f"⚠️ {secilen_lig} için henüz tahmin üretilmemiş maç yok.")
    st.stop()

st.markdown(f"### 📅 {len(tahmin_df)} Gelecek Maç Bulundu")
st.markdown("Aşağıdaki maçlardan birine tıklayarak detaylı analizi görebilirsiniz.")
st.markdown("---")

for idx, row in tahmin_df.iterrows():
    mac_basligi = f"⚽ {row['Ev Sahibi']} vs {row['Deplasman']}"
    tarih = row["Tarih"][:10] if "Tarih" in row else ""

    with st.expander(f"{mac_basligi}  —  📅 {tarih}"):
        st.markdown("#### 🎯 Maç Sonucu Olasılıkları")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f'<div class="metrik-kutu"><div class="metrik-deger">%{row["Ev Kazanma %"]}</div><div class="metrik-etiket">Ev Kazanma (1)</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metrik-kutu"><div class="metrik-deger">%{row["Beraberlik %"]}</div><div class="metrik-etiket">Beraberlik (X)</div></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="metrik-kutu"><div class="metrik-deger">%{row["Dep Kazanma %"]}</div><div class="metrik-etiket">Deplasman Kazanma (2)</div></div>', unsafe_allow_html=True)

        st.markdown("#### ⚽ Gol Beklentileri")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f'<div class="metrik-kutu"><div class="metrik-deger">{row["Ev Gol Beklentisi"]}</div><div class="metrik-etiket">Ev Gol</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metrik-kutu"><div class="metrik-deger">{row["Dep Gol Beklentisi"]}</div><div class="metrik-etiket">Dep Gol</div></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="metrik-kutu"><div class="metrik-deger">%{row["Alt 2.5 %"]}</div><div class="metrik-etiket">Alt 2.5</div></div>', unsafe_allow_html=True)
        with col4:
            st.markdown(f'<div class="metrik-kutu"><div class="metrik-deger">%{row["Üst 2.5 %"]}</div><div class="metrik-etiket">Üst 2.5</div></div>', unsafe_allow_html=True)

        st.markdown(f'<div class="metrik-kutu" style="margin-top:10px;"><div class="metrik-deger">%{row["KG %"]}</div><div class="metrik-etiket">Karşılıklı Gol</div></div>', unsafe_allow_html=True)

        st.markdown("#### 📖 Detaylı Açıklama")
        acik_1x2, acik_alt_ust, acik_kg = mac_aciklamasi(row)
        st.markdown(f'<div class="aciklama-kutu">{acik_1x2}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="aciklama-kutu">{acik_alt_ust}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="aciklama-kutu">{acik_kg}</div>', unsafe_allow_html=True)

        st.markdown("#### 🎲 En Olası Skorlar")
        skor_html = ""
        if "En Olası Skorlar" in row and pd.notna(row["En Olası Skorlar"]):
            for skor in str(row["En Olası Skorlar"]).split(", "):
                skor_html += f'<div class="skor-kutu">{skor}</div>'
        st.markdown(skor_html, unsafe_allow_html=True)

        st.markdown("#### 🏥 Eksik Oyuncular")
        ev_eksik = eksik_oyunculari_getir(row["Ev Sahibi"])
        dep_eksik = eksik_oyunculari_getir(row["Deplasman"])

        col_ev, col_dep = st.columns(2)
        with col_ev:
            st.markdown(f"**{row['Ev Sahibi']}**")
            if ev_eksik is not None and len(ev_eksik) > 0:
                for _, oyuncu in ev_eksik.head(8).iterrows():
                    st.markdown(f'<div class="eksik-oyuncu">🚫 <b>{oyuncu["Oyuncu"]}</b><br><span style="font-size:0.85em; color:#666;">{oyuncu["Tür"]} — {oyuncu["Neden"]}</span></div>', unsafe_allow_html=True)
            else:
                st.info("Eksik oyuncu bilgisi bulunamadı.")
        with col_dep:
            st.markdown(f"**{row['Deplasman']}**")
            if dep_eksik is not None and len(dep_eksik) > 0:
                for _, oyuncu in dep_eksik.head(8).iterrows():
                    st.markdown(f'<div class="eksik-oyuncu">🚫 <b>{oyuncu["Oyuncu"]}</b><br><span style="font-size:0.85em; color:#666;">{oyuncu["Tür"]} — {oyuncu["Neden"]}</span></div>', unsafe_allow_html=True)
            else:
                st.info("Eksik oyuncu bilgisi bulunamadı.")

        st.markdown("---")