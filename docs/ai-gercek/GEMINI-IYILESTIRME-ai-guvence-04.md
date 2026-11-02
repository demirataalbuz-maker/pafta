# GEMINI İYİLEŞTİRME RAPORU — ai-guvence-04

**Ders:** `tracks/ai-guvence/lessons/ai-guvence-04-yanlis-pozitiflerin-guvenlik-maliyeti.md`  
**Başlık:** Yanlış Pozitiflerin Güvenlik Maliyeti  
**Yazar:** gemini  
**Tarih:** 2026-11-02  
**Mevcut Puan:** 89 → **Hedef:** ≥ 90 (A Notu)  
**Denetçi:** claude-opus (bağımsız denetçi)

---

## 1. Yapılan İyileştirmeler (İş Emri & Standart Maddeleri)

### A. Giriş Anlatımı & Purple Standardı
- **Kelime Sayısı ve Teknik Derinlik:** Giriş anlatımı 950 kelimeye çıkarıldı.
  - Siber güvenlik operasyon merkezlerinde (SOC) makine öğrenmesi modellerinde simetrik doğruluk (`accuracy`) veya $0.5$ varsayılan eşik yerine maliyet duyarlı eşik optimizasyonunun gerekliliği ayrıntılandırıldı.
  - Yanlış Negatif (FN) kaynaklı güvenlik felaketleri ile Yanlış Pozitif (FP) kaynaklı analist alarm yorgunluğu (alert fatigue) arasındaki asimetrik risk dengesi açıklandı.
  - Aracın altında ne olur: 4 adımlı optimizasyon döngüsü (işletme riskine göre $c_{FP}, c_{FN}$ profil doğrulaması, sürekli olasılık skorlarının $s \ge \tau$ ile hata matrisi hücrelerine ayrıştırılması, Yanlış Pozitif Oranı $FPR = \frac{FP}{FP+TN}$ ve toplam güvenlik maliyeti hesabı $\text{Maliyet}(\tau) = FP \cdot c_{FP} + FN \cdot c_{FN}$, toplam maliyeti minimize eden optimal karar eşiğinin $\tau^*$ belirlenmesi ve eşitlik durumunda güvenlik tarafında kalmak için daha küçük eşiğin seçilmesi).
  - Çıktı nasıl okunur: En iyi eşik, eşiğe göre sıralı satırlar ve FPR analizi.
  - Saldırgan ne dener: Eşik altı seyreltilmiş sızma (low-and-slow evasion) ile olasılığı eşiğin hemen altında tutma, kasıtlı yanlış pozitif üreterek analistleri alarm bombardımanına tutma (alert flooding).
  - Savunma neden kırılır: Varsayılan $0.5$ eşik yanılgısı, temel oran yanılgısı (base rate fallacy), statik eşik tuzağı.
  - Sık yapılan geliştirici tuzakları: `skor >= esik` yerine `skor > esik` yazarak sınır değerlerini kaçırma, `fp + tn == 0` durumunda sıfıra bölme hatası ve `None` dönmeme, eşit maliyette deterministik küçük eşik kuralını atlama, Python'da `bool` tipinin `int` alt sınıfı olması tuzağı, matrisler arası örnek sayısı tutarsızlığı.
- **Purple Standart Tablosu:** 3 sütunlu standart tablo eksiksiz korundu (`| Gerçek araç / model ne gösterir | Bu ders ne kullanır | Ne söyleyemez? |`).
- **Sentetik Sınır Uyarısı (`[!NOT]`):** Standart `> [!NOT]` bloğunda sentetik veriler, temiz kopya yeniden yazımı ve canlı `scikit-learn` olasılık skorları üzerindeki FN-ağır ve FP-ağır deney profillerinin kapsamı açıkça ifade edildi.

### B. Kusurlu Başlangıç Kodları (KUSURLU BAŞLANGIÇ KODU)
- **Görev 1:** `# KUSURLU BAŞLANGIÇ KODU: negatif maliyetleri ve para birimini denetlemeden doğrudan girdi sözlüğünü döndürüyor!`
- **Görev 2:** `# KUSURLU BAŞLANGIÇ KODU: skor >= esik yerine skor > esik kullanıyor ve sınır değerini yanlış sınıflandırıyor!`
- **Görev 3:** `# KUSURLU BAŞLANGIÇ KODU: maliyet hesabı yapmadan her zaman ilk matrisin eşiğini seçiyor!`
- **Görev Gerçek Deney:** 3 fonksiyon için de kuralları ihlal eden gerçekçi kusurlu başlangıç kodları sağlandı; boş `return {}` bırakılmadı. Her starter testi geçemeyecek şekilde kurgulandı.

### C. AST Tabanlı Kopya Koruması
- Gerçek deney test adımına `ast.walk(ast.parse(src))` analizi eklendi.
- `referans`, `maliyet_profili_dogrula_referans`, `esik_matrisi_referans`, `maliyet_raporu_referans`, `getattr`, `kanit_yaz`, `eval`, `exec` ve wildcard (`*`) ithalleri engellendi.

---

## 2. Dört Zorunlu Kontrol Sonuçları

### 1) Validate (Tam Kontrol)
```
1 ders, 9 kontrol · geçen: {'tahmin': 1, 'solution': 4, 'starter': 4}
TEMİZ
```
- 80 test örneğinin canlı `predict_proba` skorları üzerinde FN-ağır ve FP-ağır profillerde optimal eşik seçimi hatasız doğrulandı.

### 2) Tahmin Denetimi (`tahmin.py`)
```
ai-guvence-04:2 [ai-guvence/python] uyuşuyor · 3 satır
1 tahmin, 0 şüpheli
```

### 3) Mutasyon Testi (`mutasyon.py`)
```
ai-guvence-04:3 «1 · Maliyet profilini doğrula» 3 mutant, 3 yakalandı
ai-guvence-04:4 «2 · Verilen eşikte hata matrisi üret» 24 mutant, 24 yakalandı
ai-guvence-04:5 «3 · Eşikleri güvenlik maliyetiyle karşılaştır» 15 mutant, 15 yakalandı
toplam 42 mutant, 0 geçen
```

### 4) Kopya Sondası (`kopya_sonda.py`)
- Sonda 1 (doğrudan referans ithali): `fail → korunuyor`
- Sonda 2 (getattr ile referans alma): `fail → korunuyor`
- Sonda 3 (wildcard import ile referans alma): `fail → korunuyor`

---

## 3. Özet
`ai-guvence-04` dersi iş emrindeki tüm gereksinimleri (Purple tablosu, `[!NOT]`, 950 kelimelik derin anlatım, 4 kusurlu starter, AST kopya koruması) eksiksiz karşılamaktadır ve 4 denetim kontrolünün tamamını başarıyla geçmiştir. Bağımsız denetçi `claude-opus` incelemesine hazırdır.
