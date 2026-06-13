# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import requests

# Sayfa Ayarları (Boş ekranı önlemek ve başlık eklemek için en başta olmalı)
st.set_page_config(page_title="HKED Tahmin Yarışması", page_icon="🏆", layout="centered")

st.title("🏆 HKED Canlı Skor ve Tahmin Paneli")
st.write("Turnuva maçları ve arkadaş grubunun anlık puan durumu.")

# 72 Maçlık Tüm Fikstür ve Katılımcı Tahminleri Veri Seti
MAC_VERILERI = [
    {
        "id": 1, "tarih": "2026-06-11", "saat": "22:00:00", "grup": "A",
        "takim_1": "Meksika", "takim_2": "Güney Afrika",
        "tahminler": {"TOLGA": 1, "MUSTAFA": 1, "ISITAN": 1, "YIGIT": 1, "CENK": 0}
    },
    {
        "id": 2, "tarih": "2026-06-12", "saat": "05:00:00", "grup": "A",
        "takim_1": "Güney Kore", "takim_2": "Çekya",
        "tahminler": {"TOLGA": 1, "MUSTAFA": 0, "ISITAN": 1, "YIGIT": 1, "CENK": 0}
    },
    {
        "id": 3, "tarih": "2026-06-12", "saat": "22:00:00", "grup": "B",
        "takim_1": "Kanada", "takim_2": "Bosna Hersek",
        "tahminler": {"TOLGA": 1, "MUSTAFA": 2, "ISITAN": 2, "YIGIT": 1, "CENK": 1}
    },
    {
        "id": 4, "tarih": "2026-06-13", "saat": "04:00:00", "grup": "D",
        "takim_1": "ABD", "takim_2": "Paraguay",
        "tahminler": {"TOLGA": 0, "MUSTAFA": 1, "ISITAN": 0, "YIGIT": 1, "CENK": 1}
    },
    {
        "id": 5, "tarih": "2026-06-13", "saat": "22:00:00", "grup": "B",
        "takim_1": "Katar", "takim_2": "İsviçre",
        "tahminler": {"TOLGA": 2, "MUSTAFA": 2, "ISITAN": 2, "YIGIT": 2, "CENK": 2}
    }
    # Diğer 72 maç buraya bu formatta eklenebilir...
]

def canli_skorlari_getir():
    """İnternetteki ücretsiz API'den canlı veya biten maçları çeker"""
    url = "https://api.scorebat.com/video-api/v3/"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get("response", [])
    except:
        pass
    return []

# Skorları Çek ve Hesapla
api_maclari = canli_skorlari_getir()
puanlar = {"TOLGA": 0, "MUSTAFA": 0, "ISITAN": 0, "YIGIT": 0, "CENK": 0}
gosterilecek_maclar = []

for mac in MAC_VERILERI:
    mac_sonucu = None
    skor_metni = "Oynanmadı"
    
    # API Simülasyonu / Eşleştirme (Test amaçlı ilk maçları sonuçlandıralım)
    if mac["id"] == 1: mac_sonucu = 1; skor_metni = "2 - 1"
    if mac["id"] == 3: mac_sonucu = 2; skor_metni = "0 - 3"
    
    # Puan Hesaplama
    if mac_sonucu is not None:
        for kisi, tahmin in mac["tahminler"].items():
            if tahmin == mac_sonucu:
                puanlar[kisi] += 1

    # Tablo için veriyi hazırla
    gosterilecek_maclar.append({
        "Tarih": mac["tarih"],
        "Grup": mac["grup"],
        "Maç": f"{mac['takim_1']} vs {mac['takim_2']}",
        "Durum/Skor": skor_metni
    })

# --- STREAMLIT ARAYÜZÜ (Ekrana Çizdirme) ---

st.subheader("📊 Güncel Liderlik Tablosu")
# Puanları sıralı diziye çevirip tablo yapalım
df_puan = pd.DataFrame(list(puanlar.items()), columns=["Katılımcı", "Toplam Puan"])
df_puan = df_puan.sort_values(by="Toplam Puan", ascending=False).reset_index(drop=True)
st.dataframe(df_puan, use_container_width=True)

st.subfigure = st.subheader("📅 Maç Fikstürü ve Sonuçlar")
df_maclar = pd.DataFrame(gosterilecek_maclar)
st.dataframe(df_maclar, use_container_width=True)
