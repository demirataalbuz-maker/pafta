# GEMINI İYİLEŞTİRME RAPORU — ai-ile-guvenlik-08

**Ders:** `tracks/ai-ile-guvenlik/lessons/ai-ile-guvenlik-08-dilbilgisi-destekli-fuzzing-yuku-uretimi.md`  
**Başlık:** Dilbilgisi Destekli (Grammar-Guided) Fuzzing Yükü Üretimi  
**Yazar:** gemini  
**Tarih:** 2026-11-01  
**Mevcut Puan:** 89 → **Hedef:** ≥ 90 (A Notu)  
**Denetçi:** claude-opus (bağımsız denetçi)

---

## 1. Yapılan İyileştirmeler (İş Emri & Standart Maddeleri)

### A. Giriş Anlatımı & Purple Standardı
- **Kelime Sayısı ve Teknik Derinlik:** Giriş anlatımı 814 kelimeye çıkarıldı.
  - Rastgele bayt fuzzing (`dumb fuzzing`) ile dilbilgisi destekli fuzzing (`grammar-guided fuzzing`) arasındaki farklar detaylandırıldı.
  - Aracın altında ne olur: 3 aşamalı döngü (dilbilgisi/güvenlik süzgeci, sınır değer mutasyonu, anomali sınıflandırma).
  - Saldırgan ne dener: ayrıştırıcı atlama, yıkıcı yönetimsel komut enjeksiyonu (`"sil"`, `"format"`), sınır taşmaları (`-1`, `50000`), tip karışıklığı (`true`, `"10"`).
  - Savunma neden kırılır: zayıf şema denetimi, kara liste yanılgısı, sayısal aralık sınırlaması (`clamp`) eksikliği.
  - Sık yapılan geliştirici tuzakları: Python'da `bool` tipinin `int` alt sınıfı olması (`isinstance(True, int) == True`), girdi dizgelerinde boşluk ve `strip()` ihmalleri, JSON serileştirmesinde anahtar sırası (`sort_keys=True`), istisna türü ayrıştırması (`type(e).__name__`).
- **Purple Standart Tablosu:** 3 sütunlu standart tablo eksiksiz korundu (`| Gerçek araç / model ne gösterir | Bu ders ne kullanır | Ne söyleyemez? |`).
- **Sentetik Sınır Uyarısı (`[!NOT]`):** `> [!GÜVENLİK]` yerine standart `> [!NOT]` bloğuna dönüştürüldü; sentetik veri sınırları, kurulum geçiciliği ve yerel model (`qwen3`) sınırları dürüstçe vurgulandı.

### B. Kusurlu Başlangıç Kodları (KUSURLU BAŞLANGIÇ KODU)
- **Görev 1:** `# KUSURLU BAŞLANGIÇ KODU: Yasaklı yıkıcı komutları filtrelemeden ve limit tipinin tamsayı olduğunu denetlemeden JSON'ı doğrudan geçerli sayıyor!`
- **Görev 2:** `# KUSURLU BAŞLANGIÇ KODU: İzinli komut kümesini denetlemeden yalnızca tek bir sabit limit değeri (10) üretiyor; sınır değerlerini üretmiyor!`
- **Görev 3:** `# KUSURLU BAŞLANGIÇ KODU: Dilbilgisi doğrulamasını uygulamadan tüm yükleri normal kabul ediyor ve hedef işleyici anomalilerini yakalamıyor!`
- **Görev Gerçek Deney:** 3 fonksiyon için de kuralları ihlal eden gerçekçi kusurlu başlangıç kodları sağlandı; boş `return {}` bırakılmadı. Her starter testi geçemeyecek şekilde kurgulandı.

### C. AST Tabanlı Kopya Koruması
- Gerçek deney test adımına `ast.walk(ast.parse(src))` analizi eklendi.
- `referans`, `dilbilgisi_yuku_dogrula_referans`, `sinir_mutasyonlari_uret_referans`, `fuzz_kampanyasi_kostur_referans`, `getattr`, `kanit_yaz` ve wildcard (`*`) ithalleri engellendi.

---

## 2. Dört Zorunlu Kontrol Sonuçları

### 1) Validate (Tam Kontrol)
```
1 ders, 9 kontrol · geçen: {'tahmin': 1, 'solution': 4, 'starter': 4}
TEMİZ
```
- Canlı yerel model çağrısı (`qwen3:4b-instruct-2507-q4_K_M`) GPU kipinde başarıyla tamamlandı.

### 2) Tahmin Denetimi (`tahmin.py`)
```
ai-ile-guvenlik-08:4 [ai-ile-guvenlik/python] uyuşuyor · 1 satır
1 tahmin, 0 şüpheli
```

### 3) Mutasyon Testi (`mutasyon.py`)
```
ai-ile-guvenlik-08:5 «1 · Aday fuzzing yükünü dilbilgisi ve izinli komut kurallarına göre doğrula» 4 mutant, 4 yakalandı
ai-ile-guvenlik-08:6 «2 · İzinli komut için dilbilgisine uygun sınır değer mutasyonları üret» 3 mutant, 3 yakalandı
ai-ile-guvenlik-08:7 «3 · Fuzz kampanyasını koştur ve hedef işleyici anomalilerini sınıflandır» 9 mutant, 9 yakalandı
toplam 16 mutant, 0 geçen
```

### 4) Kopya Sondası (`kopya_sonda.py`)
- Sonda 1 (doğrudan referans ithali): `fail → korunuyor`
- Sonda 2 (getattr ile referans alma): `fail → korunuyor`
- Sonda 3 (wildcard import ile referans alma): `fail → korunuyor`

---

## 3. Özet
`ai-ile-guvenlik-08` dersi iş emrindeki tüm gereksinimleri (Purple tablosu, `[!NOT]`, 814 kelimelik derin anlatım, 4 kusurlu starter, AST kopya koruması) eksiksiz karşılamaktadır ve 4 denetim kontrolünün tamamını başarıyla geçmiştir. Bağımsız denetçi `claude-opus` incelemesine hazırdır.
