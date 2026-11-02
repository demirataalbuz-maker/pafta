# GEMINI İYİLEŞTİRME RAPORU — ai-guvence-02

**Ders:** `tracks/ai-guvence/lessons/ai-guvence-02-taban-model-ve-olcum-referansi.md`  
**Başlık:** Taban Model ve Ölçüm Referansı  
**Yazar:** gemini  
**Tarih:** 2026-11-02  
**Mevcut Puan:** 89 → **Hedef:** ≥ 90 (A Notu)  
**Denetçi:** claude-opus (bağımsız denetçi)

---

## 1. Yapılan İyileştirmeler (İş Emri & Standart Maddeleri)

### A. Giriş Anlatımı & Purple Standardı
- **Kelime Sayısı ve Teknik Derinlik:** Giriş anlatımı 895 kelimeye çıkarıldı.
  - Güvenlik ve AI güvence (assurance) çalışmalarında taban model (baseline model) referansının önemi, savunma ve saldırı etkilerinin ancak sağlam bir taban üzerinde anlam kazandığı açıklandı.
  - Veri sızıntısının (data leakage) engellenmesi, eğitim ve test ayrımının matematiksel bütünlüğü vurgulandı.
  - Dengesiz veri kümelerinde tekil doğruluk (`accuracy`) yanılgısı, duyarlılık (`recall`) ve kesinlik (`precision`) ayrımı detaylandırıldı.
  - Tahmin belirsizliği marjı ($\min(p, 1-p)$) ve olasılık kalibrasyonunun karar sınırındaki güvenlik rolü anlatıldı.
  - Aracın altında ne olur: 3 adımlı değerlendirme döngüsü (veri ayrımı ve bütünlük doğrulaması, karışıklık matrisi ve sınıf ölçümleri, olasılıksal tahmin belirsizliği marjı).
  - Çıktı nasıl okunur: Doğruluk vs duyarlılık/kesinlik, paydası sıfır olan metriklerde `None` kullanımı, ortalama ve yüksek belirsizlik analizi.
  - Saldırgan ne dener: Veri sızıntısını istismar etme, karar sınırına yakın belirsizlik bölgesine ($\min(p, 1-p) \approx 0.5$) sızma, aşırı özgüvenli hataları kışkırtma.
  - Savunma neden kırılır: Doğruluk paradoksu (accuracy paradox), dolaylı özellik sızıntısı (feature leakage), kalibrasyon yoksunluğu.
  - Sık yapılan geliştirici tuzakları: Sıfıra bölme hatasında `None` dönmeme veya `0.0` dönme hatası, belirsizlik formülünde $\min(p, 1-p)$ yerine basit olasılık ortalaması alma, `belirsizlik >= esik` sınır eşitliği ihmali, Python'da `bool` tipinin `int` alt sınıfı olması tuzağı, deterministik sıralama (`sorted()`) yapmama.
- **Purple Standart Tablosu:** 3 sütunlu standart tablo eksiksiz korundu (`| Gerçek araç / model ne gösterir | Bu ders ne kullanır | Ne söyleyemez? |`).
- **Sentetik Sınır Uyarısı (`[!NOT]`):** Standart `> [!NOT]` bloğunda sentetik veriler, temiz kopya yeniden yazımı ve 160 örneklik canlı `LogisticRegression` deneyinin kapsamı açıkça ifade edildi.

### B. Kusurlu Başlangıç Kodları (KUSURLU BAŞLANGIÇ KODU)
- **Görev 1:** `# KUSURLU BAŞLANGIÇ KODU: kimlikleri doğrulamadan ve sıralamadan yalnız eğitim listesine topluyor!`
- **Görev 2:** `# KUSURLU BAŞLANGIÇ KODU: yalnız toplam doğruluğu hesaplayıp duyarlılık ve kesinliği sabit 0.0 bırakıyor!`
- **Görev 3:** `# KUSURLU BAŞLANGIÇ KODU: min(p, 1-p) yerine doğrudan olasılıkların ortalamasını alıyor!`
- **Görev Gerçek Deney:** 3 fonksiyon için de kuralları ihlal eden gerçekçi kusurlu başlangıç kodları sağlandı; boş `return {}` bırakılmadı. Her starter testi geçemeyecek şekilde kurgulandı.

### C. AST Tabanlı Kopya Koruması
- Gerçek deney test adımına `ast.walk(ast.parse(src))` analizi eklendi.
- `referans`, `veri_ayrimi_dogrula_referans`, `sinif_olcumleri_referans`, `belirsizlik_ozeti_referans`, `getattr`, `kanit_yaz`, `eval`, `exec` ve wildcard (`*`) ithalleri engellendi.

---

## 2. Dört Zorunlu Kontrol Sonuçları

### 1) Validate (Tam Kontrol)
```
1 ders, 9 kontrol · geçen: {'tahmin': 1, 'solution': 4, 'starter': 4}
TEMİZ
```
- Canlı 160 örneklik ikili sınıflandırma veri kümesinde sızıntısız veri ayrımı, sınıf metrikleri ve olasılık belirsizliği hatasız doğrulandı.

### 2) Tahmin Denetimi (`tahmin.py`)
```
ai-guvence-02:2 [ai-guvence/python] uyuşuyor · 3 satır
1 tahmin, 0 şüpheli
```

### 3) Mutasyon Testi (`mutasyon.py`)
```
ai-guvence-02:3 «1 · Eğitim-test kayıtlarını doğrula» 3 mutant, 3 yakalandı
ai-guvence-02:4 «2 · Sınıf ölçümlerini taban referansına çevir» 18 mutant, 18 yakalandı
ai-guvence-02:5 «3 · Olasılıkların belirsizlik özetini üret» 14 mutant, 14 yakalandı
toplam 35 mutant, 0 geçen
```

### 4) Kopya Sondası (`kopya_sonda.py`)
- Sonda 1 (doğrudan referans ithali): `fail → korunuyor`
- Sonda 2 (getattr ile referans alma): `fail → korunuyor`
- Sonda 3 (wildcard import ile referans alma): `fail → korunuyor`

---

## 3. Özet
`ai-guvence-02` dersi iş emrindeki tüm gereksinimleri (Purple tablosu, `[!NOT]`, 895 kelimelik derin anlatım, 4 kusurlu starter, AST kopya koruması) eksiksiz karşılamaktadır ve 4 denetim kontrolünün tamamını başarıyla geçmiştir. Bağımsız denetçi `claude-opus` incelemesine hazırdır.
