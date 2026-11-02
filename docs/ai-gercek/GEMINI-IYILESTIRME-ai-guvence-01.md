# GEMINI İYİLEŞTİRME RAPORU — ai-guvence-01

**Ders:** `tracks/ai-guvence/lessons/ai-guvence-01-ml-guvenligi-deney-defteri.md`  
**Başlık:** ML Güvenliği Deney Defteri  
**Yazar:** gemini  
**Tarih:** 2026-11-02  
**Mevcut Puan:** 88 → **Hedef:** ≥ 90 (A Notu)  
**Denetçi:** claude-opus (bağımsız denetçi)

---

## 1. Yapılan İyileştirmeler (İş Emri & Standart Maddeleri)

### A. Giriş Anlatımı & Purple Standardı
- **Kelime Sayısı ve Teknik Derinlik:** Giriş anlatımı 1039 kelimeye çıkarıldı.
  - Güvenlik ve MLSecOps çalışmalarında deney defteri (experiment ledger / tracking) zorunluluğu, yazılım birim testlerinden farkı ve güvenlik deneylerinin dondurulması gereken 4 boyutu (Veri Manifestosu, Model ve Hiperparametre Tanımı, Tehdit Modeli ve Varsayımları, Ölçüm Protokolü) açıklandı.
  - Çoklu tohum protokolü ve donanım bağımlılıkları sınırı: Tek bir tohumun yanıltıcı "sahte dayanıklılık" (gradient masking) yaratma riski, CPU SIMD talimat setleri (AVX-512 vs AVX2), GPU kayan nokta atomik toplama sıraları ve BLAS kütüphane sürümlerinin (OpenBLAS vs MKL) determinizm üzerindeki etkileri detaylandırıldı.
  - Metrik setinin güvenlik açısından anlamı: Yalnızca genel `dogruluk` kaydetmenin körlüğü, `dogruluk`, `f1`, `asr` (Attack Success Rate) ve `fpr` (False Positive Rate) metriklerinin savunma/saldırı dengesindeki rolleri incelendi.
  - Kapsam doğrulaması ve matris tamlığı: Her `(olcut, tekrar)` çiftinin benzersizliği ve tüm `1..beklenen_tekrar` uzayının eksiksiz denetlenmesi.
  - Güvenlik mühendislerinin sık düştüğü tuzaklar: Kayıp koşuları sıfır varsayma hatası, Python'da `bool` tipinin `int` alt sınıfı olması tuzağı, `math.isnan()` / `math.isinf()` denetimleri, veri yapılarında girdi mutasyonu (in-place mutation) riskleri.
- **Purple Standart Tablosu:** 3 sütunlu standart format eksiksiz korundu (`| Gerçek araç / model ne gösterir | Bu ders ne kullanır | Ne söyleyemez? |`).
- **Sentetik Sınır Uyarısı (`[!NOT]`):** İlk 3 görevdeki `veri/plan.json` ve `veri/olcumler.json` sentetik veri temsilleri, kalıcılık olmaması ve 4. görevdeki canlı 3 tohumlu `LogisticRegression` eğitim döngüsü açıkça belirtildi.

### B. Kusurlu Başlangıç Kodları (KUSURLU BAŞLANGIÇ KODU)
- **Görev 1:** `# KUSURLU BAŞLANGIÇ KODU: şema ve alan doğrulaması yapmadan doğrudan girdi sözlüğünü döndürüyor!`
- **Görev 2:** `# KUSURLU BAŞLANGIÇ KODU: ölçümleri sıralamadan ve aralık/yinelenme denetimi yapmadan döndürüyor!`
- **Görev 3:** `# KUSURLU BAŞLANGIÇ KODU: eksik ölçüt-tekrar çiftlerini aramadan her zaman 'tamam' döndürüyor!`
- **Görev Gerçek Deney:** 3 fonksiyon için de kuralları ihlal eden gerçekçi kusurlu başlangıç kodları sağlandı; boş `return {}` bırakılmadı. Her starter testi geçemeyecek şekilde kurgulandı.

### C. AST Tabanlı Kopya Koruması
- Gerçek deney test adımına `ast.walk(ast.parse(src))` analizi eklendi.
- `deney_plani_dogrula_referans`, `olcumleri_dogrula_referans`, `deney_kapsam_raporu_referans`, `getattr`, `kanit_yaz`, `eval`, `exec` ve wildcard (`*`) ithalleri engellendi.

---

## 2. Dört Zorunlu Kontrol Sonuçları

### 1) Validate (Tam Kontrol)
```
1 ders, 9 kontrol · geçen: {'tahmin': 1, 'solution': 4, 'starter': 4}
TEMİZ
```
- Canlı 3 tohumlu `LogisticRegression` döngüsü ve 12 canlı ölçüm üzerinde plan doğrulama, sıralama ve kapsam raporu başarıyla doğrulandı.

### 2) Tahmin Denetimi (`tahmin.py`)
```
ai-guvence-01:2 [ai-guvence/python] uyuşuyor · 3 satır
1 tahmin, 0 şüpheli
```

### 3) Mutasyon Testi (`mutasyon.py`)
```
ai-guvence-01:3 «1 · Deney planını doğrula» 9 mutant, 9 yakalandı
ai-guvence-01:4 «2 · Tekrarlı ölçümleri doğrula ve sırala» 19 mutant, 19 yakalandı
ai-guvence-01:5 «3 · Deney kapsamındaki eksikleri raporla» 25 mutant, 25 yakalandı
toplam 53 mutant, 0 geçen
```

### 4) Kopya Sondası (`kopya_sonda.py`)
- Sonda 1 (doğrudan referans ithali): `fail → korunuyor`
- Sonda 2 (wildcard import): `fail → korunuyor`
- Sonda 3 (getattr ile dinamik referans): `fail → korunuyor`

---

## 3. Özet
`ai-guvence-01` dersi iş emrindeki tüm gereksinimleri (Purple tablosu, `[!NOT]`, 1039 kelimelik derin anlatım, 4 kusurlu starter, AST kopya koruması) eksiksiz karşılamaktadır ve 4 denetim kontrolünün tamamını başarıyla geçmiştir. Bağımsız denetçi `claude-opus` incelemesine hazırdır.
