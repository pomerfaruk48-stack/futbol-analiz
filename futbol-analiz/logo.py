import streamlit as st
import base64

# Aslan logosu - tamamen bize ait SVG tasarım
LOGO_SVG = """
<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <linearGradient id="gsGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#A90432;stop-opacity:1" />
            <stop offset="50%" style="stop-color:#FDB912;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#A90432;stop-opacity:1" />
        </linearGradient>
        <linearGradient id="maneGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" style="stop-color:#FDB912;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#D4A017;stop-opacity:1" />
        </linearGradient>
    </defs>
    <circle cx="100" cy="100" r="95" fill="url(#gsGradient)" stroke="#1a1a2e" stroke-width="3"/>
    <g fill="url(#maneGradient)">
        <path d="M 100 20 Q 110 30 100 40 Q 90 30 100 20 Z" />
        <path d="M 140 30 Q 145 45 130 50 Q 130 35 140 30 Z" />
        <path d="M 170 60 Q 165 75 150 70 Q 155 55 170 60 Z" />
        <path d="M 180 100 Q 170 110 160 100 Q 170 90 180 100 Z" />
        <path d="M 170 140 Q 165 125 150 130 Q 155 145 170 140 Z" />
        <path d="M 140 170 Q 145 155 130 150 Q 130 165 140 170 Z" />
        <path d="M 100 180 Q 110 170 100 160 Q 90 170 100 180 Z" />
        <path d="M 60 170 Q 55 155 70 150 Q 70 165 60 170 Z" />
        <path d="M 30 140 Q 35 125 50 130 Q 45 145 30 140 Z" />
        <path d="M 20 100 Q 30 90 40 100 Q 30 110 20 100 Z" />
        <path d="M 30 60 Q 35 75 50 70 Q 45 55 30 60 Z" />
        <path d="M 60 30 Q 55 45 70 50 Q 70 35 60 30 Z" />
    </g>
    <ellipse cx="100" cy="105" rx="55" ry="60" fill="#FDB912" stroke="#A90432" stroke-width="2"/>
    <ellipse cx="70" cy="55" rx="12" ry="15" fill="#FDB912" stroke="#A90432" stroke-width="2"/>
    <ellipse cx="130" cy="55" rx="12" ry="15" fill="#FDB912" stroke="#A90432" stroke-width="2"/>
    <ellipse cx="80" cy="95" rx="8" ry="10" fill="#1a1a2e"/>
    <ellipse cx="120" cy="95" rx="8" ry="10" fill="#1a1a2e"/>
    <circle cx="82" cy="92" r="3" fill="white"/>
    <circle cx="122" cy="92" r="3" fill="white"/>
    <path d="M 95 115 Q 100 125 105 115 Q 100 118 95 115 Z" fill="#1a1a2e"/>
    <path d="M 100 125 Q 90 135 85 130" stroke="#1a1a2e" stroke-width="2" fill="none"/>
    <path d="M 100 125 Q 110 135 115 130" stroke="#1a1a2e" stroke-width="2" fill="none"/>
    <line x1="60" y1="115" x2="90" y2="118" stroke="#1a1a2e" stroke-width="1.5"/>
    <line x1="60" y1="122" x2="90" y2="122" stroke="#1a1a2e" stroke-width="1.5"/>
    <line x1="110" y1="118" x2="140" y2="115" stroke="#1a1a2e" stroke-width="1.5"/>
    <line x1="110" y1="122" x2="140" y2="122" stroke="#1a1a2e" stroke-width="1.5"/>
</svg>
"""

# SVG'yi base64'e çevir
b64 = base64.b64encode(LOGO_SVG.encode('utf-8')).decode('utf-8')

# Sayfa ayarları
st.set_page_config(page_title="Logo Test", page_icon="🦁", layout="centered")

st.markdown(f"""
<div style="text-align: center; padding: 30px;">
    <img src="data:image/svg+xml;base64,{b64}" width="250" height="250" />
    <h1 style="color: #A90432; margin-top: 20px;">🦁 Futbol Analiz Platformu</h1>
    <p style="color: #666; font-size: 1.1em;">Yapay Zeka Destekli Maç Analizi</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")
st.success("✅ Logo başarıyla oluşturuldu!")
st.info("📌 Bu logoyu web_app.py dosyasına entegre edeceğiz.")