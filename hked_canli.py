import streamlit as st
import pandas as pd
import requests

# 1. Excel'den Tahminleri Yükle
@st.cache_data(ttl=3600)
def load_tahminler():
    # Excel'iniz: 0:Maç, 3:Oran1, 4:Oran0, 5:Oran2, 6:TOLGA, 7:MUSTAFA, 8:IŞITAN, 9:YİĞİT, 10:CENK
    return pd.read_excel("NEW HKED.xlsx", header=None)

# 2. API'den Canlı Skorları Çek
@st.cache_data(ttl=300)
def get_live_scores():
    url = "https://www.thesportsdb.com/api/v1/json/3/eventspastleague.php?id=4429"
    try:
        response = requests.get(url)
        data = response.json()
        results = {}
        if 'events' in data and data['events']:
            for e in data['events']:
                key = f"{e['strHomeTeam']} - {e['strAwayTeam']}"
                home = int(e['intHomeScore'] or 0)
                away = int(e['intAwayScore'] or 0)
                # Sonucu 1-0-2 formatına çevir
                if home > away: res = "1"
                elif home < away: res = "2"
                else: res = "0"
                results[key] = {'sonuc': res, 'skor': f"{home}-{away}"}
        return results
    except: return {}

# 3. Puan Hesaplama Motoru
def hesapla():
    df = load_tahminler()
    live_results = get_live_scores()
    katilimcilar = {6: 'TOLGA', 7: 'MUSTAFA', 8: 'IŞITAN', 9: 'YİĞİT', 10: 'CENK'}
    puanlar = {isim: 0.0 for isim in katilimcilar.values()}
    detaylar = []

    for _, row in df.iterrows():
        mac = row[0]
        if mac in live_results:
            gercek = live_results[mac]['sonuc']
            skor = live_results[mac]['skor']
            
            # Excel'deki katsayıları al (1:3, 0:4, 2:5)
            oran_map = {"1": 3, "0": 4, "2": 5}
            katsayi = float(row[oran_map[gercek]])
            
            tahmin_dict = {isim: str(row[col]) for col, isim in katilimcilar.items()}
            
            # Puan ekle
            for isim, tahmin in tahmin_dict.items():
                if tahmin == gercek:
                    puanlar[isim] += katsayi
            
            detaylar.append({'Maç': mac, 'Skor': skor, **tahmin_dict})
            
    return puanlar, detaylar

# 4. Arayüz
st.set_page_config(layout="wide", page_title="HKED 2026")
st.title("🏆 HKED 2026 Dünya Kupası Canlı Paneli")

puanlar, detaylar = hesapla()

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📊 Güncel Puan Durumu")
    puan_df = pd.DataFrame(list(puanlar.items()), columns=['İsim', 'Toplam Puan'])
    st.table(puan_df.sort_values(by='Toplam Puan', ascending=False).reset_index(drop=True))

with col2:
    st.subheader("⚽ Maç Sonuçları ve Tahminler")
    st.dataframe(pd.DataFrame(detaylar), use_container_width=True)
