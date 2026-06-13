# -*- coding: utf-8 -*-
import requests

# 1. Sabit Maç ve Tahmin Verileriniz (Excel'den Çevrilen)
MAC_VERILERI = [
    {
        "id": 1,
        "grup": "A",
        "takim_1": "Meksika",
        "takim_2": "Güney Afrika",
        "tahminler": {"TOLGA": 1, "MUSTAFA": 1, "ISITAN": 1, "YIGIT": 1, "CENK": 0}
    },
    {
        "id": 2,
        "grup": "A",
        "takim_1": "Güney Kore",
        "takim_2": "Çekya",
        "tahminler": {"TOLGA": 1, "MUSTAFA": 0, "ISITAN": 1, "YIGIT": 1, "CENK": 0}
    },
    {
        "id": 3,
        "grup": "B",
        "takim_1": "Kanada",
        "takim_2": "Bosna Hersek",
        "tahminler": {"TOLGA": 1, "MUSTAFA": 2, "ISITAN": 2, "YIGIT": 1, "CENK": 1}
    }
    # Diğer 72 maç buraya sıralanacak...
]

def canli_skorlari_getir():
    """İnternetteki ücretsiz API'den canlı veya biten maçları çeker"""
    url = "https://api.scorebat.com/video-api/v3/" # Korumasız, açık canlı skor API'si
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get("response", [])
    except Exception as e:
        print(f"Skorlar çekilirken hata oluştu: {e}")
    return []

def skoru_yorunla(skor_metni):
    """'2 - 1' gibi gelen skor metnini 1, 0, 2 formatına çevirir"""
    try:
        skorlar = skor_metni.split("-")
        ev = int(skorlar[0].strip())
        deplasman = int(skorlar[1].strip())
        if ev > deplasman: return 1
        elif deplasman > ev: return 2
        else: return 0
    except:
        return None

def sistemi_guncelle_ve_hesapla():
    api_maclari = canli_skorlari_getir()
    puanlar = {"TOLGA": 0, "MUSTAFA": 0, "ISITAN": 0, "YIGIT": 0, "CENK": 0}
    
    print("🔄 Canlı skorlar internetten kontrol ediliyor...\n")
    
    for mac in MAC_VERILERI:
        mac_sonucu = None
        
        # İnternetten gelen maçlar arasında bizim takımları ara
        for canli_mac in api_maclari:
            # Takım isimleri eşleşiyor mu kontrol et (Türkçe/İngilizce karakter hassasiyeti için küçük harfe çeviriyoruz)
            if mac["takim_1"].lower() in canli_mac["title"].lower() and mac["takim_2"].lower() in canli_mac["title"].lower():
                # Eğer maçın skoru veya sonucu API'de varsa alıyoruz
                # Örnek: canli_mac["title"] -> "Mexico 2 - 1 South Africa"
                # Buradan skoru ayıklayıp mac_sonucu = 1 yapıyoruz.
                pass 
        
        # Test için (API simülasyonu): Eğer maç sonucu bulunursa puanları hesapla
        # (Şimdilik manuel atama simülasyonu, API bağlandığında otomatik dolacak)
        if mac["id"] == 1: mac_sonucu = 1  # Meksika kazandı varsayalım
        
        if mac_sonucu is not None:
            for kisi, tahmin in mac["tahminler"].items():
                if tahmin == mac_sonucu:
                    puanlar[kisi] += 1

    # Sonuçları ekrana yazdır
    print("--- 🏆 CANLI PUAN DURUMU 🏆 ---")
    for isim, puan in sorted(puanlar.items(), key=lambda x: x[1], reverse=True):
        print(f"{isim}: {puan} Puan")

if __name__ == "__main__":
    sistemi_guncelle_ve_hesapla()