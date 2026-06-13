# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd

# 1. Sayfa Ayarları
st.set_page_config(page_title="HKED Canlı Dünya Kupası", page_icon="🏆", layout="wide")

st.title("🏆 HKED Canlı Skor & Tahmin Paneli")
st.write("Skorlar girildiği an tüm katılımcı puanları sistem tarafından otomatik hesaplanır. Saatler TSİ'ye göredir.")

# 2. GİZLİ SKOR DEPOSU (Streamlit Hafızası)
# Siteniz açık kaldığı sürece skorları burada kilitli tutar
if "canli_skorlar" not in st.session_state:
    st.session_state.canli_skorlar = {
        1: "2 - 1",  # Mexico - South Africa
        2: "1 - 1",  # South Korea - Czech Republic
        3: "Oynanmadı",
        4: "Oynanmadı",
        5: "Oynanmadı",
        6: "Oynanmadı",
        7: "Oynanmadı"
    }

# 3. TÜM DETAYLARIYLA DÜNYA KUPASI FİKSTÜRÜ VE TAHMİNLER
MAC_VERILERI = [
    {"id": 1, "tarih": "11 Haziran 2026", "saat": "23:00", "grup": "A", "takim_1": "Mexico", "takim_2": "South Africa", "ulke": "Meksika", "stad": "Estadio Azteca", "tahminler": {"TOLGA": 1, "MUSTAFA": 1, "ISITAN": 1, "YIGIT": 1, "CENK": 0}},
    {"id": 2, "tarih": "12 Haziran 2026", "saat": "19:00", "grup": "A", "takim_1": "South Korea", "takim_2": "Czech Republic", "ulke": "Kanada", "stad": "BC Place", "tahminler": {"TOLGA": 1, "MUSTAFA": 0, "ISITAN": 1, "YIGIT": 1, "CENK": 0}},
    {"id": 3, "tarih": "12 Haziran 2026", "saat": "22:00", "grup": "B", "takim_1": "Canada", "takim_2": "Bosnia and Herzegovina", "ulke": "Kanada", "stad": "BMO Field", "tahminler": {"TOLGA": 1, "MUSTAFA": 2, "ISITAN": 2, "YIGIT": 1, "CENK": 1}},
    {"id": 4, "tarih": "13 Haziran 2026", "saat": "01:00", "grup": "D", "takim_1": "USA", "takim_2": "Paraguay", "ulke": "ABD", "stad": "SoFi Stadium", "tahminler": {"TOLGA": 0, "MUSTAFA": 1, "ISITAN": 0, "YIGIT": 1, "CENK": 1}},
    {"id": 5, "tarih": "13 Haziran 2026", "saat": "18:00", "grup": "B", "takim_1": "Qatar", "takim_2": "Switzerland", "ulke": "ABD", "stad": "MetLife Stadium", "tahminler": {"TOLGA": 2, "MUSTAFA": 2, "ISITAN": 2, "YIGIT": 2, "CENK": 2}},
    {"id": 6, "tarih": "14 Haziran 2026", "saat": "21:00", "grup": "C", "takim_1": "Brazil", "takim_2": "Morocco", "ulke": "Meksika", "stad": "Estadio BBVA", "tahminler": {"TOLGA": 0, "MUSTAFA": 1, "ISITAN": 1, "YIGIT": 1, "CENK": 1}},
    {"id": 7, "tarih": "14 Haziran 2026", "saat": "00:00", "grup": "C", "takim_1": "Haiti", "takim_2": "Scotland", "ulke": "ABD", "stad": "Hard Rock Stadium", "tahminler": {"TOLGA": 2, "MUSTAFA": 2, "ISITAN": 2, "YIGIT": 2, "CENK": 2}}
]

def skoru_yorumla(skor_metni):
    if skor_metni == "Oynanmadı": return None
    try:
        ev, dep = map(int, skor_metni.split("-"))
        if ev > dep: return 1   # Ev Sahibi
        elif dep > ev: return 2 # Deplasman
        return 0                # Beraberlik
    except:
        return None

# --- OTOMATİK PUAN HESAPLAMA MOTORU ---
puanlar = {"TOLGA": 0, "MUSTAFA": 0, "ISITAN": 0, "YIGIT": 0, "CENK": 0}
guncel_fikstur_listesi = []

for mac in MAC_VERILERI:
    mac_id = mac["id"]
    skor_metni = st.session_state.canli_skorlar.get(mac_id, "Oynanmadı")
    mac_sonucu = skoru_yorumla(skor_metni)

    # Eğer maç oynandıysa tahminleri otomatik kontrol et ve puan yaz
    if mac_sonucu is not None:
        for kisi, tahmin in mac["tahminler"].items():
            if tahmin == mac_sonucu:
                puanlar[kisi] += 1

    guncel_fikstur_listesi.append({
        "Tarih 📅": mac["tarih"],
        "TSİ Saat ⏰": mac["saat"],
        "Grup 📁": mac["grup"],
        "Maç ⚔️": f"{mac['takim_1']} - {mac['takim_2']}",
        "Skor ⚽": skor_metni,
        "Ev Sahibi Ülke 🌍": mac["ulke"],
        "Stadyum 🏟️": mac["stad"]
    })

# --- STREAMLIT ARAYÜZÜ ---
sol_kolon, sag_kolon = st.columns([1, 3])

with sol_kolon:
    st.subheader("📊 Canlı Puan Durumu")
    df_puan = pd.DataFrame(list(puanlar.items()), columns=["Yarışmacı", "Puan"]).sort_values(by="Puan", ascending=False).reset_index(drop=True)
    st.dataframe(df_puan, use_container_width=True)
    
    st.markdown("---")
    # GİZLİ ADMIN PANELİ (Sadece skor girmek istediğinde burayı açarsın)
    with st.expander("🛠️ Skor Güncelleme Paneli (Yönetici)"):
        secilen_mac = st.selectbox("Maç Seçin:", [f"{m['id']}: {m['takim_1']}-{m['takim_2']}" for m in MAC_VERILERI])
        mac_id_secilen = int(secilen_mac.split(":")[0])
        
        ev_gol = st.number_input("Ev Sahibi Gol:", min_value=0, max_value=20, value=0, step=1)
        dep_gol = st.number_input("Deplasman Gol:", min_value=0, max_value=20, value=0, step=1)
        mac_durumu = st.radio("Maç Durumu:", ["Oynandı / Canlı", "Henüz Oynanmadı"])
        
        if st.button("Skoru Sisteme İşle 💾"):
            if mac_durumu == "Oynandı / Canlı":
                st.session_state.canli_skorlar[mac_id_secilen] = f"{ev_gol} - {dep_gol}"
            else:
                st.session_state.canli_skorlar[mac_id_secilen] = "Oynanmadı"
            st.success("Skor başarıyla güncellendi ve puanlar yeniden hesaplandı!")
            st.rerun()

with sag_kolon:
    st.subheader("📅 Detaylı Dünya Kupası Fikstürü")
    df_fikstur = pd.DataFrame(guncel_fikstur_listesi)
    st.dataframe(df_fikstur, use_container_width=True)
