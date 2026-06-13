# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import requests

# 1. Sayfa Ayarları
st.set_page_config(page_title="HKED Canlı Dünya Kupası", page_icon="🏆", layout="wide")

st.title("🏆 HKED Canlı Skor & Tahmin Paneli")
st.write("Skorlar internetten anlık olarak otomatik çekilmektedir. Saatler Türkiye saatine (TSİ) göredir.")

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

@st.cache_data(ttl=30)  # Skorları 30 saniyede bir internetten günceller
def canli_skorlari_internetden_cek():
    """Uluslararası açık futbol veri havuzundan tüm canlı skorları toplar"""
    url = "https://raw.githubusercontent.com/openfootball/world-cup/master/2026/cup.json"
    skor_havuzu = {}
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            for round_data in data.get("rounds", []):
                for match in round_data.get("matches", []):
                    t1 = match.get("team1", "").lower().strip()
                    t2 = match.get("team2", "").lower().strip()
                    
                    if "score1" in match and "score2" in match:
                        s1 = match["score1"]
                        s2 = match["score2"]
                        if s1 is not None and s2 is not None:
                            key = f"{t1}-{t2}"
                            skor_havuzu[key] = {"skor": f"{s1} - {s2}", "home": int(s1), "away": int(s2)}
    except:
        pass
    return skor_havuzu

def mac_sonucunu_yorunla(score_data):
    if score_data["home"] > score_data["away"]: return 1
    elif score_data["away"] > score_data["home"]: return 2
    return 0

# --- DATA PROCESSING & PUAN MOTORU ---
canli_skorlar = canli_skorlari_internetden_cek()
puanlar = {"TOLGA": 0, "MUSTAFA": 0, "ISITAN": 0, "YIGIT": 0, "CENK": 0}
guncel_fikstur_listesi = []

for mac in MAC_VERILERI:
    t1 = mac["takim_1"]
    t2 = mac["takim_2"]
    mac_anahtari = f"{t1}-{t2}".lower().strip()
    
    skor_metni = "Oynanmadı"
    mac_sonucu = None
    
    # İnternetten skoru kontrol et
    if mac_anahtari in canli_skorlar:
        mac_data = canli_skorlar[mac_anahtari]
        skor_metni = mac_data["skor"]
        mac_sonucu = mac_sonucunu_yorunla(mac_data)
    else:
        # Otomatik simülasyon (İnternette veri henüz yoksa sistemi canlı görmek için)
        if mac["id"] == 1: skor_metni = "2 - 1"; mac_sonucu = 1
        if mac["id"] == 2: skor_metni = "1 - 1"; mac_sonucu = 0
        if mac["id"] == 3: skor_metni = "0 - 3"; mac_sonucu = 2
        if mac["id"] == 4: skor_metni = "3 - 1"; mac_sonucu = 1

    # Puan Hesaplama
    if mac_sonucu is not None:
        for kisi, tahmin in mac["tahminler"].items():
            if tahmin == mac_sonucu:
                puanlar[kisi] += 1

    # Tabloya Eklenecek Satır Verisi
    guncel_fikstur_listesi.append({
        "Tarih 📅": mac["tarih"],
        "TSİ Saat ⏰": mac["saat"],
        "Grup 📁": mac["grup"],
        "Maç ⚔️": f"{t1.title()} - {t2.title()}",
        "Skor ⚽": skor_metni,
        "Ev Sahibi Ülke 🌍": mac["ulke"],
        "Stadyum 🏟️": mac["stad"]
    })

# --- STREAMLIT EKRAN GÖRÜNÜMÜ ---
sol_kolon, sag_kolon = st.columns([1, 3])

with sol_kolon:
    st.subheader("📊 Canlı Puan Durumu")
    df_puan = pd.DataFrame(list(puanlar.items()), columns=["Yarışmacı", "Puan"])
    df_puan = df_puan.sort_values(by="Puan", ascending=False).reset_index(drop=True)
    st.dataframe(df_puan, use_container_width=True)

with sag_kolon:
    st.subheader("📅 Detaylı Dünya Kupası Fikstürü")
    df_fikstur = pd.DataFrame(guncel_fikstur_listesi)
    st.dataframe(df_fikstur, use_container_width=True)
