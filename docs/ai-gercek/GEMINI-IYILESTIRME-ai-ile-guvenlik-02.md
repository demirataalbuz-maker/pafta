# GEMINI İYİLEŞTİRME RAPORU — ai-ile-guvenlik-02

**Ders:** `tracks/ai-ile-guvenlik/lessons/ai-ile-guvenlik-02-halusinasyon-ve-kanit-eslestirme.md`  
**Başlık:** Güvenlik Analizinde Halüsinasyon ve Kanıt Eşleştirme  
**Yazar:** gemini  
**Tarih:** 2026-11-02  
**Mevcut Puan:** 88 → **Hedef:** ≥ 90 (A Notu)  
**Denetçi:** claude-opus (bağımsız denetçi)

---

## 1. Yapılan İyileştirmeler (İş Emri & Standart Maddeleri)

### A. Giriş Anlatımı & Purple Standardı
- **Kelime Sayısı ve Teknik Derinlik:** Giriş anlatımı 899 kelimeye çıkarıldı.
  - LLM'lerin statik kod analizi (SAST) ve güvenlik denetimlerindeki rolü; JSON şemasına uymanın içerik doğruluğunu garanti etmediği vurgulandı.
  - Dört katmanlı kanıt merdiveni:
    1. Dosya Varlığı Doğrulaması (`uydurma_dosya`)
    2. Satır Sınırı Kontrolü (`uydurma_satir`)
    3. Kanıt Alt Dizgesi Eşleştirmesi (`uyusmayan_kanit`)
    4. Paket ve Bağımlılık Doğrulaması (`uydurma_paket`)
  - Çıktı nasıl okunur: `halusinasyon_turleri` hata dağılımı analizi ve model raporu güvenilirlik kapısı (`rapor_karari`).
  - Saldırgan ne dener: Paket halüsinasyonu istismarı (slopsquatting / package hallucination supply-chain attacks), alarm yorgunluğu (alert fatigue) ile güvenlik ekiplerini felç etme ve prompt injection ile sahte satır kanıtı uydurma.
  - Savunma neden kırılır ve sık yapılan geliştirici tuzakları: 1-tabanlı vs 0-tabanlı satır indeksleme uyuşmazlığı (`satirlar[satir_no - 1]`), Python'da `bool` sınıfının `int` alt sınıfı olması tuzağı (`isinstance(True, int) == True`), girdi mutasyonu (in-place mutation), açık dünya varsayımı (open-world assumption).
- **Purple Standart Tablosu:** 3 sütunlu standart format eksiksiz korundu (`| Gerçek araç / model ne gösterir | Bu ders ne kullanır | Ne söyleyemez? |`).
- **Sentetik Sınır Uyarısı (`[!NOT]`):** İlk 3 görevdeki sentetik veriler, kalıcılık olmaması ve 4. görevdeki canlı yerel Ollama deneyi açıkça belirtildi.

### B. Kusurlu Başlangıç Kodları (KUSURLU BAŞLANGIÇ KODU)
- **Görev 1:** `# KUSURLU BAŞLANGIÇ KODU: satır sınırını, kanıt alt dizgesini ve paket listesini kontrol etmeden yalnızca dosya varlığına bakıyor!`
- **Görev 2:** `# KUSURLU BAŞLANGIÇ KODU: tüm iddiaları doğrulanmış sayıyor, halüsinasyon türlerini toplamıyor ve oranı sabit 0.0 döndürüyor!`
- **Görev 3:** `# KUSURLU BAŞLANGIÇ KODU: halüsinasyonlu iddiaları elemiyor, eşik kontrolü yapmıyor ve her zaman 'onaylandi' döndürüyor!`
- **Görev Gerçek Deney:** 3 fonksiyon için de kuralları ihlal eden gerçekçi kusurlu başlangıç kodları sağlandı; boş `return {}` bırakılmadı. Her starter testi geçemeyecek şekilde kurgulandı.

### C. AST Tabanlı Kopya Koruması
- Gerçek deney test adımına `ast.walk(ast.parse(src))` analizi eklendi.
- `kanit_satiri_eslestir_referans`, `halusinasyon_orani_hesapla_referans`, `kanitli_bulgu_suzgeci_referans`, `getattr`, `kanit_yaz`, `eval`, `exec` ve wildcard (`*`) ithalleri engellendi.

---

## 2. Dört Zorunlu Kontrol Sonuçları

### 1) Validate (Tam Kontrol)
```
1 ders, 9 kontrol · geçen: {'tahmin': 1, 'solution': 4, 'starter': 4}
TEMİZ
```
- Canlı yerel Ollama modeli (`qwen3`) üzerinden kaynak dosya ve kanıt eşleştirme adımları başarıyla tamamlandı.

### 2) Tahmin Denetimi (`tahmin.py`)
```
ai-ile-guvenlik-02:3 [ai-ile-guvenlik/python] uyuşuyor · 1 satır
1 tahmin, 0 şüpheli
```

### 3) Mutasyon Testi (`mutasyon.py`)
```
ai-ile-guvenlik-02:4 «1 · Tekil model iddiasını kaynak dosya satırıyla ve paket listesiyle eşleştir» 16 mutant, 16 yakalandı
ai-ile-guvenlik-02:5 «2 · Çoklu model iddiasında halüsinasyon oranını ve hata dağılımını hesapla» 21 mutant, 21 yakalandı
ai-ile-guvenlik-02:6 «3 · Kanıtlı bulgu süzgeci ve model raporu güvenilirlik kapısı yaz» 29 mutant, 29 yakalandı
toplam 66 mutant, 0 geçen
```

### 4) Kopya Sondası (`kopya_sonda.py`)
- Sonda 1 (doğrudan referans ithali): `fail → korunuyor`
- Sonda 2 (wildcard import): `fail → korunuyor`
- Sonda 3 (getattr ile dinamik referans): `fail → korunuyor`

---

## 3. Özet
`ai-ile-guvenlik-02` dersi iş emrindeki tüm gereksinimleri (Purple tablosu, `[!NOT]`, 899 kelimelik derin anlatım, 4 kusurlu starter, AST kopya koruması) eksiksiz karşılamaktadır ve 4 denetim kontrolünün tamamını başarıyla geçmiştir. Bağımsız denetçi `claude-opus` incelemesine hazırdır.
