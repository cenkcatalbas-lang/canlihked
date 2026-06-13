# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

# 1. Sayfa Ayarları (Boş ekranı önlemek için en başta olmalı)
st.set_page_config(page_title="HKED Canlı Tahmin", page_icon="🏆", layout="centered")

st.title("🏆 HKED Canlı Skor & Tahmin Paneli")
st.write("Wikipedia üzerinden anlık çekilen skorlar ve arkadaş grubunun puan durumu.")

# 2. Excel Dosyanızdaki 72 Maçlık Fikstür ve Tahminler Verisi
MAC_VERILERI = [
    {"id": 1, "tarih": "2026-06-11", "grup": "A", "takim_1": "Meksika", "takim_2": "Güney Afrika", "tahminler": {"TOLGA": 1, "MUSTAFA": 1, "ISITAN": 1, "YIGIT": 1, "CENK": 0}},
    {"id": 2, "tarih": "2026-06-12", "grup": "A", "takim_1": "Güney Kore", "takim_2": "Çekya", "tahminler": {"TOLGA": 1, "MUSTAFA": 0, "ISITAN": 1, "YIGIT": 1, "CENK": 0}},
    {"id": 3, "tarih": "2026-06-12", "grup": "B", "takim_1": "Kanada", "takim_2": "Bosna Hersek", "tahminler": {"TOLGA": 1, "MUSTAFA": 2, "ISITAN": 2, "YIGIT": 1, "CENK": 1}},
    {"id": 4, "tarih": "2026-06-13", "grup": "D", "takim_1": "ABD", "takim_2": "Paraguay", "tahminler": {"TOLGA": 0, "MUSTAFA": 1, "ISITAN": 0, "YIGIT": 1, "CENK": 1}},
    {"id": 5, "tarih": "2026-06-13", "grup": "B", "takim_1": "Katar", "takim_2": "İsviçre", "tahminler": {"TOLGA": 2, "MUSTAFA": 2, "ISITAN": 2, "YIGIT": 2, "CENK": 2}},
    {"id": 6, "tarih": "2026-06-14", "grup": "C", "takim_1": "Brezilya", "takim_2": "Fas", "tahminler": {"TOLGA": 0, "MUSTAFA": 1, "ISITAN": 1, "YIGIT": 1, "CENK": 1}}
    # Turnuvanın kalan tüm maçlarını bu şekilde buraya ekleyebilirsiniz...
]

@st.cache_data(ttl=300)  # Her 5 dakikada bir veriyi yeniler, siteyi yormaz
def wikipedia_canli_skorlari_al():
    """Wikipedia turnuva sayfasındaki tüm maç bloklarını ve skorları kazır."""
    url = "https://en.wikipedia.org/wiki/2026_FIFA_World_Cup"
    canli_sonuclar = {}
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Wikipedia'daki tüm maç kutularını buluyoruz
            mac_kutulari = soup.find_all('div', class_='fmatch')
            for kutu in mac_kutulari:
                try:
                    home = kutu.find('th', class_='fhome').text.strip()
                    away = kutu.find('th', class_='faway').text.strip()
                    score_button = kutu.find('th', class_='fscore')
                    score = score_button.text.strip() if score_button else ""
                    
                    # Eğer skor girilmişse (Örn: "2–1" veya "0–0")
                    if score and "v" not in score and "—" not in score:
                        # Wikipedia genelde uzun tire (–) kullanır, onu normal tireye çeviriyoruz
                        score = score.replace('–', '-').strip()
                        key = f"{home.lower()}-{away.lower()}"
                        canli_sonuclar[key] = score
                except:
                    continue
    except:
        pass
    return canli_sonuclar

def skor_yorunla(skor_metni):
    """'2-1' şeklindeki metni 1, 0, 2 iddaa formatına çevirir."""
    try:
        parcalar = skor_metni.split("-")
        ev = int(parcalar[0].strip())
        deplasman = int(parcalar[1].strip())
        if ev > deplasman: return 1
        elif deplasman > ev: return 2
        else: return 0
    except:
        return None

# --- ANA HESAPLAMA MOTORU ---
wikipedia_skorlari = wikipedia_canli_skorlari_al()
puanlar = {"TOLGA": 0, "MUSTAFA": 0, "ISITAN": 0, "YIGIT": 0, "CENK": 0}
fikstur_tablosu = []

# İngilizce-Türkçe küçük isim uyumsuzluklarını otomatik gidermek için basit temizlik fonksiyonu
def isim_temizle(isim):
    return isim.lower().replace('ı', 'i').replace('ü', 'u').replace('ö', 'o').replace('ç', 'c').replace('ş', 's').strip()

for mac in MAC_VERILERI:
    mac_sonucu = None
    durum_skor = "Oynanmadı"
    
    t1_bizim = isim_temizle(mac["takim_1"])
    t2_bizim = isim_temizle(mac["takim_2"])
    
    # Wikipedia'dan gelen skorlarla eşleştirme yapıyoruz
    for wiki_key, wiki_score in wikipedia_skorlari.items():
        if t1_bizim in wiki_key or t2_bizim in wiki_key: # Kısmi isim eşleşmesi koruması
            durum_skor = wiki_score
            mac_sonucu = skor_yorunla(wiki_score)
            break
            
    # Puanları Dağıt
    if mac_sonucu is not None:
        for kisi, tahmin in mac["tahminler"].items():
            if tahmin == mac_sonucu:
                puanlar[kisi] += 1

    fikstur_tablosu.append({
        "Tarih": mac["tarih"],
        "Grup": mac["grup"],
        "Maç": f"{mac['takim_1']} - {mac['takim_2']}",
        "Canlı Skor / Durum": durum_skor
    })

# --- STREAMLIT GÖRSEL EKRANI ---
st.subheader("📊 Turnuva Puan Durumu")
df_puan = pd.DataFrame(list(puanlar.items()), columns=["Yarışmacı", "Toplam Puan"])
df_puan = df_puan.sort_values(by="Toplam Puan", ascending=False).reset_index(drop=True)
st.dataframe(df_puan, use_container_width=True)

st.subheader("📅 Canlı Maç Sonuçları ve Fikstür")
df_fikstur = pd.DataFrame(fikstur_tablosu)
st.dataframe(df_fikstur, use_container_width=True)
