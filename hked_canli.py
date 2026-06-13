# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import requests
import json

# 1. Sayfa Ayarları
st.set_page_config(page_title="HKED Canlı Dünya Kupası", page_icon="🏆", layout="wide")

st.title("🏆 HKED Canlı Skor & Tahmin Paneli")
st.write("Skorlar küresel turnuva veri merkezlerinden anlık olarak otomatik çekilmektedir. Saatler TSİ'ye göredir.")

# 2. TÜM DETAYLARIYLA DÜNYA KUPASI FİKSTÜRÜ VE TAHMİNLER
MAC_VERILERI = [
    {
        "id": 1, 
        "tarih": "11 Haziran 2026", 
        "saat": "23:00", 
        "grup": "A", 
        "takim_1": "mexico", 
        "takim_2": "south africa", 
        "ulke": "Meksika", 
        "stad": "Estadio Azteca (Mexico City)",
        "tahminler": {"TOLGA": 1, "MUSTAFA": 1, "ISITAN": 1, "YIGIT": 1, "CENK": 0}
    },
    {
        "id": 2, 
        "tarih": "12 Haziran 2026", 
        "saat": "19:00", 
        "grup": "A", 
        "takim_1": "south korea", 
        "takim_2": "czech republic", 
        "ulke": "Kanada", 
        "stad": "BC Place (Vancouver)",
        "tahminler": {"TOLGA": 1, "MUSTAFA": 0, "ISITAN": 1, "YIGIT": 1, "CENK": 0}
    },
    {
        "id": 3, 
        "tarih": "12 Haziran 2026", 
        "saat": "22:00", 
        "grup": "B", 
        "takim_1": "canada", 
        "takim_2": "bosnia and herzegovina", 
        "ulke": "Kanada", 
        "stad": "BMO Field (Toronto)",
        "tahminler": {"TOLGA": 1, "MUSTAFA": 2, "ISITAN": 2, "YIGIT": 1, "CENK": 1}
    },
    {
        "id": 4, 
        "tarih": "13 Haziran 2026", 
        "saat": "01:00", 
        "grup": "D", 
        "takim_1": "usa", 
        "takim_2": "paraguay", 
        "ulke": "ABD", 
        "stad": "SoFi Stadium (Los Angeles)",
        "tahminler": {"TOLGA": 0, "MUSTAFA": 1, "ISITAN": 0, "YIGIT": 1, "CENK": 1}
    },
    {
        "id": 5, 
        "tarih": "13 Haziran 2026", 
        "saat": "18:00", 
        "grup": "B", 
        "takim_1": "qatar", 
        "takim_2": "switzerland", 
        "ulke": "ABD", 
        "stad": "MetLife Stadium (New York)",
        "tahminler": {"TOLGA": 2, "MUSTAFA": 2, "ISITAN": 2, "YIGIT": 2, "CENK": 2}
    },
    {
        "id": 6, 
        "tarih": "14 Haziran 2026", 
        "saat": "21:00", 
        "grup": "C", 
        "takim_1": "brazil", 
        "takim_2": "morocco", 
        "ulke": "Meksika", 
        "stad": "Estadio BBVA (Monterrey)",
        "tahminler": {"TOLGA": 0, "MUSTAFA": 1, "ISITAN": 1, "YIGIT": 1, "CENK": 1}
    },
    {
        "id": 7, 
        "tarih": "14 Haziran 2026", 
        "saat": "00:00", 
        "grup": "C", 
        "takim_1": "haiti", 
        "takim_2": "scotland", 
        "ulke": "ABD", 
        "stad": "Hard Rock Stadium (Miami)",
        "tahminler": {"TOLGA": 2, "MUSTAFA": 2, "ISITAN": 2, "YIGIT": 2, "CENK": 2}
    }
]

@st.cache_data(ttl=15)  # Skorları 15 saniyede bir internetten çeker ve yeniler
def canli_skorlari_kazila():
    """Turnuvanın canlı olarak işlendiği ham text/json deposundan skorları filtreler"""
    url = "https://raw.githubusercontent.com/openfootball/world-cup/master/2026/cup.json"
    skor_havuzu = {}
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            data = res.json()
            for round_idx, round_data in enumerate(data.get("rounds", [])):
                for match in round_data.get("matches", []):
                    t1 = str(match.get("team1", "")).lower().strip()
                    t2 = str(match.get("team2", "")).lower().strip()
                    
                    # Eğer maçta score1 ve score2 alanı varsa ve boş değilse
                    if "score1" in match and "score2" in match:
                        s1 = match["score1"]
                        s2 = match["score2"]
                        if s1 is not None and s2 is not None:
                            key = f"{t1}-{t2}"
                            skor_havuzu[key] = {"skor": f"{s1} - {s2}", "home": int(s1), "away": int(s2)}
    except:
        pass
    return skor_havuzu

def mac_sonucunu_yorunla(score_info):
    if score_info["home"] > score_info["away"]: return 1   # Ev sahibi
    elif score_info["away"] > score_info["home"]: return 2 # Deplasman
    return 0                                               # Beraberlik

# --- HESAPLAMA VE SENKRONİZASYON MOTORU ---
canli_skorlar = canli_skorlari_kazila()
puanlar = {"TOLGA": 0, "MUSTAFA": 0, "ISITAN": 0, "YIGIT": 0, "CENK": 0}
guncel_fikstur_listesi = []

for mac in MAC_VERILERI:
    t1 = mac["takim_1"]
    t2 = mac["takim_2"]
    mac_anahtari = f"{t1}-{t2}".lower().strip()
    
    skor_metni = "Oynanmadı"
    mac_sonucu = None
    
    # İnternetteki havuzda maç sonucu tescillenmiş mi kontrol et
    if mac_anahtari in canli_skorlar:
        mac_data = canli_skorlar
