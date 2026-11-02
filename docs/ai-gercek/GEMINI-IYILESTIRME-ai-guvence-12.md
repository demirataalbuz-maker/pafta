# GEMINI İYİLEŞTİRME RAPORU — ai-guvence-12

**Ders:** `tracks/ai-guvence/lessons/ai-guvence-12-etiket-gurultusu-ile-zehirlemenin-ayrimi.md`  
**Başlık:** Etiket Gürültüsü ile Zehirlemenin Ayrımı  
**Yazar:** gemini  
**Tarih:** 2026-11-02  
**Mevcut Puan:** 89 → **Hedef:** ≥ 90 (A Notu)  
**Denetçi:** claude-opus (bağımsız denetçi)

---

## 1. Yapılan İyileştirmeler (İş Emri & Standart Maddeleri)

### A. Giriş Anlatımı & Purple Standardı
- **Kelime Sayısı ve Teknik Derinlik:** Giriş anlatımı 827 kelimeye çıkarıldı.
  - Rastgele etiket gürültüsü (`random label noise`) ile hedefli etiket zehirlemesi (`targeted label flipping`) arasındaki asimetrik farklar detaylandırıldı.
  - Aracın altında ne olur: 3 aşamalı döngü (yönlü `"eski>yeni"` geçiş profili, üç koşullu canlı model eğitim karşılaştırması, asimetrik hedef odaklı inceleme sinyali).
  - Çıktı nasıl okunur: İnceleme sinyalinin (`hedef_odakli: True`) analiste sağladığı filtreleme gücü ve doğal sınıf örtüşmesi (`class overlap`) sınırları.
  - Saldırgan ne dener: Temiz sınıf doğruluğunu bozmadan hedef sınıfı çökertme (`stealth poisoning`), gürültü kamuflajı.
  - Savunma neden kırılır: Yalnızca genel makro doğruluğa (`macro validation accuracy`) bakıp sınıf bazlı asimetriyi görememe, yönsüz geçiş analizleri.
  - Sık yapılan geliştirici tuzakları: Python'da `bool` tipinin `int` alt sınıfı olması (`isinstance(True, int) == True`), değişmeyen etiketleri (`0>0`) geçiş sözlüğüne katma, mutlak fark yerine oransal yüzdelik kayıp hesaplama, üç koşulun varlığını denetlemeden bölme yapma.
- **Purple Standart Tablosu:** 3 sütunlu standart tablo eksiksiz korundu (`| Gerçek araç / model ne gösterir | Bu ders ne kullanır | Ne söyleyemez? |`).
- **Sentetik Sınır Uyarısı (`[!NOT]`):** Standart `> [!NOT]` bloğunda sentetik veri sınırları, kurulum geçiciliği ve canlı `scikit-learn` yeniden eğitim deneyinin kapsamı net olarak ifade edildi.

### B. Kusurlu Başlangıç Kodları (KUSURLU BAŞLANGIÇ KODU)
- **Görev 1:** `# KUSURLU BAŞLANGIÇ KODU: yönlü geçiş sözlüğünü (eski>yeni) boş bırakıp yalnız değişen sayısını döndürüyor!`
- **Görev 2:** `# KUSURLU BAŞLANGIÇ KODU: taban ortalamasından fark almak yerine kayıpları sıfır bırakıyor!`
- **Görev 3:** `# KUSURLU BAŞLANGIÇ KODU: temiz_kayip <= temiz_esik koşulunu kontrol etmeden yalnız hedef_kayip'a bakıyor!`
- **Görev Gerçek Deney:** 3 fonksiyon için de kuralları ihlal eden gerçekçi kusurlu başlangıç kodları sağlandı; boş `return {}` bırakılmadı. Her starter testi geçemeyecek şekilde kurgulandı.

### C. AST Tabanlı Kopya Koruması
- Gerçek deney test adımına `ast.walk(ast.parse(src))` analizi eklendi.
- `referans`, `etiket_gecis_profili_referans`, `etki_karsilastirmasi_referans`, `deney_bayraklari_referans`, `getattr`, `kanit_yaz` ve wildcard (`*`) ithalleri engellendi.

---

## 2. Dört Zorunlu Kontrol Sonuçları

### 1) Validate (Tam Kontrol)
```
1 ders, 9 kontrol · geçen: {'tahmin': 1, 'solution': 4, 'starter': 4}
TEMİZ
```
- Canlı `scikit-learn` (`LogisticRegression`) taban, rastgele ve hedefli koşullarında sıfırdan eğitilerek temiz ve hedef kayıp farkları canlı olarak doğrulandı.

### 2) Tahmin Denetimi (`tahmin.py`)
```
ai-guvence-12:3 [ai-guvence/python] uyuşuyor · 3 satır
1 tahmin, 0 şüpheli
```

### 3) Mutasyon Testi (`mutasyon.py`)
```
ai-guvence-12:4 «1 · Etiket geçiş profili çıkar» 6 mutant, 6 yakalandı
ai-guvence-12:5 «2 · Rastgele ve hedefli deney etkilerini karşılaştır» 10 mutant, 10 yakalandı
ai-guvence-12:6 «3 · Hedef odaklı inceleme sinyali üret» 16 mutant, 16 yakalandı
toplam 32 mutant, 0 geçen
```

### 4) Kopya Sondası (`kopya_sonda.py`)
- Sonda 1 (doğrudan referans ithali): `fail → korunuyor`
- Sonda 2 (getattr ile referans alma): `fail → korunuyor`
- Sonda 3 (wildcard import ile referans alma): `fail → korunuyor`

---

## 3. Özet
`ai-guvence-12` dersi iş emrindeki tüm gereksinimleri (Purple tablosu, `[!NOT]`, 827 kelimelik derin anlatım, 4 kusurlu starter, AST kopya koruması) eksiksiz karşılamaktadır ve 4 denetim kontrolünün tamamını başarıyla geçmiştir. Bağımsız denetçi `claude-opus` incelemesine hazırdır.
