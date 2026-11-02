# GEMINI İYİLEŞTİRME RAPORU — ai-guvence-05

**Ders:** `tracks/ai-guvence/lessons/ai-guvence-05-tekrarlanabilirlik-ve-kanit-paketi.md`  
**Başlık:** Tekrarlanabilirlik ve Kanıt Paketi  
**Yazar:** gemini  
**Tarih:** 2026-11-02  
**Mevcut Puan:** 89 → **Hedef:** ≥ 90 (A Notu)  
**Denetçi:** claude-opus (bağımsız denetçi)

---

## 1. Yapılan İyileştirmeler (İş Emri & Standart Maddeleri)

### A. Giriş Anlatımı & Purple Standardı
- **Kelime Sayısı ve Teknik Derinlik:** Giriş anlatımı 984 kelimeye çıkarıldı.
  - Yapay zeka sistemlerinde ve MLOps süreçlerinde tekrarlanabilirlik (reproducibility), denetlenebilirlik (auditability) ve adli bilişim (forensics) gereksinimleri ayrıntılandırıldı.
  - Aracın altında ne olur: 3 adımlı doğrulama döngüsü (deney manifestosunun doğrulanması ve iç ortam sözlüğünün kopyalanması, kriptografik dosya kanıtlarının toplanması, göreli yol ve 64 karakter küçük harf SHA-256 denetimi, küme birleşimi $B \cup G$ üzerinden `eksik`, `eklenen`, `degisti` fark analizi ve `tekrarlanabilir` / `fark_var` karar mekanizması).
  - Çıktı nasıl okunur: Karar metni, değişiklik sayısı ve yola göre alfabetik sıralı fark listesi.
  - Saldırgan ne dener: Gizli arka kapı (trojan/backdoor) enjekte edip dosya boyutunu aynı tutarak boyut kontrollerini atlatma, dizin aşımı (path traversal / `../`) ile yetkisiz dosya yolları ekleme, ortam sürümü ve tohum manipülasyonu.
  - Savunma neden kırılır: Yalnızca dosya boyutuna veya yalnızca rastgelelik tohumuna güvenme hatası, gevşek yol doğrulaması (Windows `\`, `//`, `.`, `..` sızıntıları), SHA-256 büyük harf kabulü, determinizm yanılsaması (birebir aynı özetin metodolojik doğruluğu kanıtlamaması).
  - Sık yapılan geliştirici tuzakları: `ortam` iç sözlüğünü kopyalamadan döndürerek dış mutasyona izin verme, Python `bool` tipinin `int` alt sınıfı olması tuzağı (`isinstance(True, int) == True`), gözlemlenen paketin boş liste olabileceğini unutup hata fırlatma, deterministik sıralama yapmama.
- **Purple Standart Tablosu:** 3 sütunlu standart tablo eksiksiz korundu (`| Gerçek araç / model ne gösterir | Bu ders ne kullanır | Ne söyleyemez? |`).
- **Sentetik Sınır Uyarısı (`[!NOT]`):** Standart `> [!NOT]` bloğunda sentetik veriler, temiz kopya yeniden yazımı ve diskte üretilen canlı `scikit-learn` modellerinin SHA-256 özet deneyinin kapsamı açıkça ifade edildi.

### B. Kusurlu Başlangıç Kodları (KUSURLU BAŞLANGIÇ KODU)
- **Görev 1:** `# KUSURLU BAŞLANGIÇ KODU: iç ortam sözlüğünü kopyalamadan ve alanları denetlemeden döndürüyor!`
- **Görev 2:** `# KUSURLU BAŞLANGIÇ KODU: yol geçişini (..) ve SHA-256 biçimini denetlemeden sıralamadan döndürüyor!`
- **Görev 3:** `# KUSURLU BAŞLANGIÇ KODU: yalnız dosya sayılarını karşılaştırıp içerik/boyut farklarını gözden kaçırıyor!`
- **Görev Gerçek Deney:** 3 fonksiyon için de kuralları ihlal eden gerçekçi kusurlu başlangıç kodları sağlandı; boş `return {}` bırakılmadı. Her starter testi geçemeyecek şekilde kurgulandı.

### C. AST Tabanlı Kopya Koruması
- Gerçek deney test adımına `ast.walk(ast.parse(src))` analizi eklendi.
- `referans`, `kanit_manifestu_dogrula_referans`, `dosya_kanitlarini_dogrula_referans`, `kanit_fark_raporu_referans`, `getattr`, `kanit_yaz`, `eval`, `exec` ve wildcard (`*`) ithalleri engellendi.

---

## 2. Dört Zorunlu Kontrol Sonuçları

### 1) Validate (Tam Kontrol)
```
1 ders, 9 kontrol · geçen: {'tahmin': 1, 'solution': 4, 'starter': 4}
TEMİZ
```
- Disk üzerinde canlı eğitilen `scikit-learn` modellerinin `model_agirlik.json` ve `cikti/metrik.json` dosyalarının gerçek SHA-256 özetleri hatasız doğrulandı.

### 2) Tahmin Denetimi (`tahmin.py`)
```
ai-guvence-05:2 [ai-guvence/python] uyuşuyor · 3 satır
1 tahmin, 0 şüpheli
```

### 3) Mutasyon Testi (`mutasyon.py`)
```
ai-guvence-05:3 «1 · Deney manifestini doğrula» 14 mutant, 14 yakalandı
ai-guvence-05:4 «2 · Dosya kanıtlarını doğrula ve sırala» 6 mutant, 6 yakalandı
ai-guvence-05:5 «3 · İki kanıt paketinin farkını raporla» 10 mutant, 10 yakalandı
toplam 30 mutant, 0 geçen
```

### 4) Kopya Sondası (`kopya_sonda.py`)
- Sonda 1 (doğrudan referans ithali): `fail → korunuyor`
- Sonda 2 (getattr ile referans alma): `fail → korunuyor`
- Sonda 3 (wildcard import ile referans alma): `fail → korunuyor`

---

## 3. Özet
`ai-guvence-05` dersi iş emrindeki tüm gereksinimleri (Purple tablosu, `[!NOT]`, 984 kelimelik derin anlatım, 4 kusurlu starter, AST kopya koruması) eksiksiz karşılamaktadır ve 4 denetim kontrolünün tamamını başarıyla geçmiştir. Bağımsız denetçi `claude-opus` incelemesine hazırdır.
