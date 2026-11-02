# GEMINI İYİLEŞTİRME RAPORU — ai-guvence-13

**Ders:** `tracks/ai-guvence/lessons/ai-guvence-13-zehirleme-orani-ve-etki-egrisi.md`  
**Başlık:** Zehirleme Oranı ve Etki Eğrisi  
**Yazar:** gemini  
**Tarih:** 2026-11-01  
**Mevcut Puan:** 89 → **Hedef:** ≥ 90 (A Notu)  
**Denetçi:** claude-opus (bağımsız denetçi)

---

## 1. Yapılan İyileştirmeler (İş Emri & Standart Maddeleri)

### A. Giriş Anlatımı & Purple Standardı
- **Kelime Sayısı ve Teknik Derinlik:** Giriş anlatımı 804 kelimeye çıkarıldı.
  - Veri zehirleme oranı ile performans kaybı arasındaki ilişki, modelin zehre duyarlılık dinamizmi ve doğrusal olmayan etki eğrisi grafiği ayrıntılandırıldı.
  - Aracın altında ne olur: 3 aşamalı döngü (zehirleme oranı hesaplama, sıfırdan yeniden eğitimle etki eğrisi ve taban kaybı çıkarma, eşik ve doyum noktalarının saptanması).
  - Çıktı nasıl okunur: Ani çöküş (`cliff effect`) dinamikleri ve zehirlemenin henüz başlamadığı erken düzlüklerdeki yalancı doyum noktası tuzağı (`erken düzlük tuzağı`).
  - Saldırgan ne dener: Eşik altı gizli zehirleme (`sub-threshold poisoning`), doyum noktası manipülasyonu.
  - Savunma neden kırılır: Taban noktasının kirlenmesi, orantısız hedef sınıf dağılımı.
  - Sık yapılan geliştirici tuzakları: Python'da `bool` tipinin `int` alt sınıfı olması (`isinstance(True, int) == True`), temiz kayıt sayısına bölerek sıfıra bölme hatası (`ZeroDivisionError`) oluşturma, kayıtları sıralamadan eşik ve doyum arama, maksimum kayıp seçiminde eşitlik durumunda en küçük oranı seçme kuralı.
- **Purple Standart Tablosu:** 3 sütunlu standart tablo eksiksiz korundu (`| Gerçek araç / model ne gösterir | Bu ders ne kullanır | Ne söyleyemez? |`).
- **Sentetik Sınır Uyarısı (`[!NOT]`):** Standart `> [!NOT]` bloğunda sentetik veri sınırları, kurulum geçiciliği ve canlı `scikit-learn` yeniden eğitim deneyinin kapsamı net olarak ifade edildi.

### B. Kusurlu Başlangıç Kodları (KUSURLU BAŞLANGIÇ KODU)
- **Görev 1:** `# KUSURLU BAŞLANGIÇ KODU: zehirli > toplam ve negatif değerleri reddetmiyor, oranı temiz kayıtlara bölüyor!`
- **Görev 2:** `# KUSURLU BAŞLANGIÇ KODU: tabanı oran=0 satırı yerine listedeki ilk kayıttan alıyor (sıralamadan önce)!`
- **Görev 3:** `# KUSURLU BAŞLANGIÇ KODU: satırları orana göre sıralamadan dosya sırasıyla eşik ve doyum arıyor!`
- **Görev Gerçek Deney:** 3 fonksiyon için de kuralları ihlal eden gerçekçi kusurlu başlangıç kodları sağlandı; boş `return {}` bırakılmadı. Her starter testi geçemeyecek şekilde kurgulandı.

### C. AST Tabanlı Kopya Koruması
- Gerçek deney test adımına `ast.walk(ast.parse(src))` analizi eklendi.
- `referans`, `zehir_orani_hesapla_referans`, `etki_egrisi_referans`, `esik_doyum_raporu_referans`, `getattr`, `kanit_yaz` ve wildcard (`*`) ithalleri engellendi.

---

## 2. Dört Zorunlu Kontrol Sonuçları

### 1) Validate (Tam Kontrol)
```
1 ders, 9 kontrol · geçen: {'tahmin': 1, 'solution': 4, 'starter': 4}
TEMİZ
```
- Canlı `scikit-learn` (`LogisticRegression`) 7 farklı zehir oranında sıfırdan eğitilerek hedef sınıf doğruluk kaybı canlı olarak doğrulandı.

### 2) Tahmin Denetimi (`tahmin.py`)
```
ai-guvence-13:3 [ai-guvence/python] uyuşuyor · 3 satır
1 tahmin, 0 şüpheli
```

### 3) Mutasyon Testi (`mutasyon.py`)
```
ai-guvence-13:4 «1 · Zehirli örnek oranını hesapla» 4 mutant, 4 yakalandı
ai-guvence-13:5 «2 · Performans kaybı eğrisini üret» 8 mutant, 8 yakalandı
ai-guvence-13:6 «3 · Eşik ve doyum noktalarını bul» 14 mutant, 14 yakalandı
toplam 26 mutant, 0 geçen
```

### 4) Kopya Sondası (`kopya_sonda.py`)
- Sonda 1 (doğrudan referans ithali): `fail → korunuyor`
- Sonda 2 (getattr ile referans alma): `fail → korunuyor`
- Sonda 3 (wildcard import ile referans alma): `fail → korunuyor`

---

## 3. Özet
`ai-guvence-13` dersi iş emrindeki tüm gereksinimleri (Purple tablosu, `[!NOT]`, 804 kelimelik derin anlatım, 4 kusurlu starter, AST kopya koruması) eksiksiz karşılamaktadır ve 4 denetim kontrolünün tamamını başarıyla geçmiştir. Bağımsız denetçi `claude-opus` incelemesine hazırdır.
